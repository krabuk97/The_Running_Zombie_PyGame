from __future__ import absolute_import

from django.core import mail
from django.test.utils import override_settings

from tango_comments.models import Comment
from tango_comments.moderation import (moderator, CommentModerator,
    AlreadyModerated)

from . import CommentTestCase
from tests.testapp.models import Entry


class EntryModerator1(CommentModerator):
    email_notification = True

class EntryModerator2(CommentModerator):
    enable_field = 'enable_comments'

class EntryModerator3(CommentModerator):
    auto_close_field = 'pub_date'
    close_after = 7

class EntryModerator4(CommentModerator):
    auto_moderate_field = 'pub_date'
    moderate_after = 7

class EntryModerator5(CommentModerator):
    auto_moderate_field = 'pub_date'
    moderate_after = 0

class EntryModerator6(CommentModerator):
    auto_close_field = 'pub_date'
    close_after = 0


