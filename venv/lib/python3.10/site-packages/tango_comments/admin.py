from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, ungettext

from .models import Comment
from .views.moderation import perform_flag, perform_approve, perform_delete

from tango_admin.admin_actions import nuke_users


class UsernameSearch(object):
    """The User object may not be auth.User, so we need to provide
    a mechanism for issuing the equivalent of a .filter(user__username=...)
    search in CommentAdmin.
    """
    def __str__(self):
        return 'user__%s' % get_user_model().USERNAME_FIELD


class CommentsAdmin(admin.ModelAdmin):
    readonly_fields = ("post_date",)

    fieldsets = (
        (None, {'fields': ('content_type', 'object_pk', 'site')}),
        (_('Content'), {'fields': ('user', 'text')}),
        (_('Metadata'), {'fields': ('post_date', 'ip_address', 'is_public', 'is_removed')}),
    )

    list_display = (
        'user',
        'content_type',
        'object_pk',
        'ip_address',
        'post_date',
        'is_public',
        'is_removed'
    )
    list_filter = ('post_date', 'site', 'is_public', 'is_removed')
    date_hierarchy = 'post_date'
    ordering = ('-post_date',)
    raw_id_fields = ('user',)
    search_fields = ('text', UsernameSearch(), 'user__name', 'user__email', 'ip_address')
    actions = ["flag_comments", "approve_comments", "remove_comments", nuke_users]

    def get_actions(self, request):
        actions = super(CommentsAdmin, self).get_actions(request)
        # Only superusers should be able to delete the comments from the DB.
        if not request.user.is_superuser and 'delete_selected' in actions:
            actions.pop('delete_selected')
        if not request.user.has_perm('comments.can_moderate'):
            if 'approve_comments' in actions:
                actions.pop('approve_comments')
            if 'remove_comments' in actions:
                actions.pop('remove_comments')
        return actions

    def flag_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_flag,
                        lambda n: ungettext('flagged', 'flagged', n))
    flag_comments.short_description = _("Flag selected comments")

    def approve_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_approve,
                        lambda n: ungettext('approved', 'approved', n))
    approve_comments.short_description = _("Approve selected comments")

    def remove_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_delete,
                        lambda n: ungettext('removed', 'removed', n))
    remove_comments.short_description = _("Remove selected comments")

    def _bulk_flag(self, request, queryset, action, done_message):
        """
        Flag, approve, or remove some comments from an admin action. Actually
        calls the `action` argument to perform the heavy lifting.
        """
        n_comments = 0
        for comment in queryset:
            action(request, comment)
            n_comments += 1

        msg = ungettext('1 comment was successfully %(action)s.',
                        '%(count)s comments were successfully %(action)s.',
                        n_comments)
        self.message_user(request, msg % {'count': n_comments, 'action': done_message(n_comments)})

admin.site.register(Comment, CommentsAdmin)
