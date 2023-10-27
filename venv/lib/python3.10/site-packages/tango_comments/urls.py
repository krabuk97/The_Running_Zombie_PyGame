from django.urls import path, re_path
from django.contrib.contenttypes.views import shortcut

from .views.comments import post_comment, comment_done
from .views.moderation import flag, flag_done, delete, delete_done, approve, approve_done

urlpatterns = [
    path('post/', post_comment, name='comments-post-comment'),
    path('posted/', comment_done, name='comments-comment-done'),
    # Flag
    re_path(r'^flag/(\d+)/$', flag, name='comments-flag'),
    path('flagged/', flag_done, name='comments-flag-done'),
    # Delete
    re_path(r'^delete/(\d+)/$', delete, name='comments-delete'),
    path('deleted/', delete_done, name='comments-delete-done'),
    # Approve
    re_path(r'^approve/(\d+)/$', approve, name='comments-approve'),
    path('approved/', approve_done, name='comments-approve-done'),

    re_path(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),
]
