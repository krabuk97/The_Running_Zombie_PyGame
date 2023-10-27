from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from voting.managers import VoteManager

SCORES = (
    (u'+1', +1),
    (u'-1', -1),
)


class Vote(models.Model):
    """
    A vote on an object by a User.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT
    )
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')
    vote = models.SmallIntegerField(choices=SCORES)

    objects = VoteManager()

    class Meta:
        app_label = 'voting'
        db_table = 'votes'
        # One vote per user per object
        unique_together = (('user', 'content_type', 'object_id'),)

    def __unicode__(self):
        return u'%s: %s on %s' % (self.user, self.vote, self.object)

    def is_upvote(self):
        return self.vote == 1

    def is_downvote(self):
        return self.vote == -1
