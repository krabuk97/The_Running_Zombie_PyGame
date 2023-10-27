from random import randint

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings

from tango_comments.forms import CommentForm
from tango_comments.models import Comment

from tests.testapp.models import Article, Author

# Shortcut
CT = ContentType.objects.get_for_model


# Helper base class for comment tests that need data.
@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',))
class CommentTestCase(TestCase):
    fixtures = ["comment_tests"]
    urls = 'testapp.urls_default'

    
    def get_user(self):
        user_model = get_user_model()
        user = user_model.objects.create(
            username = "frank_nobody_" + str(randint(0, 100)),
            first_name = "Frank",
            last_name = "Nobody",
            email = "fnobody@example.com",
            password = "",
            is_staff = False,
            is_active = True,
            is_superuser = False,
        )
        return user

    def createSomeComments(self):
        user = self.get_user()

        # Two authenticated comments: one on the same Article, and
        # one on a different Author
        
        c3 = Comment.objects.create(
            content_type = CT(Article),
            object_pk = "1",
            user = user,
            user_id = user.id,
            text = "Damn, I wanted to be first.",
            site = Site.objects.get_current(),
        )
        c4 = Comment.objects.create(
            content_type = CT(Author),
            object_pk = "2",
            user = user,
            user_id = user.id,
            text = "You get here first, too?",
            site = Site.objects.get_current(),
        )

        return c3, c4

    def getData(self):
        user = self.get_user()
        return {
            'name'      : user.username,
            'email'     : 'jim.bob@example.com',
            'user'      : user,
            'user_id'   : user.id,
            'url'       : '',
            'text'      : 'This is my comment',
        }

    def getValidData(self, obj):
        f = CommentForm(obj)
        d = self.getData()
        d.update(f.initial)
        return d

from .app_api_tests import *
from .feed_tests import *
from .model_tests import *
from .comment_form_tests import *
from .templatetag_tests import *
from .comment_view_tests import *
from .moderation_view_tests import *
from .comment_utils_moderators_tests import *

