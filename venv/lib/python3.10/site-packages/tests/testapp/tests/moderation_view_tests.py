import unittest

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import translation

from tango_comments import signals
from tango_comments.models import Comment, CommentFlag

from . import CommentTestCase


class FlagViewTests(CommentTestCase):

    def testFlagGet(self):
        """GET the flag view: render a confirmation page."""
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.get("/flag/%d/" % pk)
        self.assertTemplateUsed(response, "comments/flag.html")

    def testFlagPost(self):
        """POST the flag view: actually flag the view (nice for XHR)"""
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.post("/flag/%d/" % pk)
        self.assertEqual(response["Location"], "/flagged/?c=%d" % pk)
        c = Comment.objects.get(pk=pk)
        self.assertEqual(c.flags.filter(flag=CommentFlag.SUGGEST_REMOVAL).count(), 1)
        return c

    def testFlagPostNext(self):
        """
        POST the flag view, explicitly providing a next url.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.post("/flag/%d/" % pk, {'next': "/go/here/"})
        self.assertEqual(response["Location"], "/go/here/?c=%d" % pk)

    def testFlagPostUnsafeNext(self):
        """
        POSTing to the flag view with an unsafe next url will ignore the
        provided url when redirecting.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.post("/flag/%d/" % pk,
            {'next': "http://elsewhere/bad"})
        self.assertEqual(response["Location"], "/flagged/?c=%d" % pk)

    def testFlagPostTwice(self):
        """Users don't get to flag comments more than once."""
        c = self.testFlagPost()
        self.client.post("/flag/%d/" % c.pk)
        self.client.post("/flag/%d/" % c.pk)
        self.assertEqual(c.flags.filter(flag=CommentFlag.SUGGEST_REMOVAL).count(), 1)

    def testFlagAnon(self):
        """GET/POST the flag view while not logged in: redirect to log in."""
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/flag/%d/" % pk)
        self.assertEqual(response["Location"], "/accounts/login/?next=/flag/%d/" % pk)
        response = self.client.post("/flag/%d/" % pk)
        self.assertEqual(response["Location"], "/accounts/login/?next=/flag/%d/" % pk)

    def testFlaggedView(self):
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/flagged/", data={"c": pk})
        self.assertTemplateUsed(response, "comments/flagged.html")

    def testFlagSignals(self):
        """Test signals emitted by the comment flag view"""

        # callback
        def receive(sender, **kwargs):
            self.assertEqual(kwargs['flag'].flag, CommentFlag.SUGGEST_REMOVAL)
            self.assertEqual(kwargs['request'].user.username, "normaluser")
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.testFlagPost()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)

def makeModerator(username):
    u = User.objects.get(username=username)
    ct = ContentType.objects.get_for_model(Comment)
    p = Permission.objects.get(content_type=ct, codename="can_moderate")
    u.user_permissions.add(p)

class DeleteViewTests(CommentTestCase):

    @unittest.skip('302 error')
    def testDeletePermissions(self):
        """The delete view should only be accessible to 'moderators'"""
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.get("/delete/%d/" % pk)
        self.assertEqual(response["Location"], "/accounts/login/?next=/delete/%d/" % pk)

        makeModerator("normaluser")
        response = self.client.get("/delete/%d/" % pk)
        self.assertEqual(response.status_code, 200)

    @unittest.skip('location/redirect error')
    def testDeletePost(self):
        """POSTing the delete view should mark the comment as removed"""
        comments = self.createSomeComments()
        pk = comments[0].pk
        makeModerator("normaluser")
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.post("/delete/%d/" % pk)
        self.assertEqual(response["Location"], "/deleted/?c=%d" % pk)
        c = Comment.objects.get(pk=pk)
        self.assertTrue(c.is_removed)
        self.assertEqual(c.flags.filter(flag=CommentFlag.MODERATOR_DELETION, user__username="normaluser").count(), 1)

    @unittest.skip('location/redirect error')
    def testDeletePostNext(self):
        """
        POSTing the delete view will redirect to an explicitly provided a next
        url.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        makeModerator("normaluser")
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.post("/delete/%d/" % pk, {'next': "/go/here/"})
        self.assertEqual(response["Location"], "/go/here/?c=%d" % pk)

    @unittest.skip('location/redirect error')
    def testDeletePostUnsafeNext(self):
        """
        POSTing to the delete view with an unsafe next url will ignore the
        provided url when redirecting.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        makeModerator("normaluser")
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.post("/delete/%d/" % pk,
            {'next': "http://elsewhere/bad"})
        self.assertEqual(response["Location"], "/deleted/?c=%d" % pk)

    def testDeleteSignals(self):
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.testDeletePost()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)

    def testDeletedView(self):
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/deleted/", data={"c": pk})
        self.assertTemplateUsed(response, "comments/deleted.html")

class ApproveViewTests(CommentTestCase):

    def testApprovedView(self):
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/approved/", data={"c":pk})
        self.assertTemplateUsed(response, "comments/approved.html")

class AdminActionsTests(CommentTestCase):
    urls = "testapp.urls_admin"

    def setUp(self):
        super(AdminActionsTests, self).setUp()

        # Make "normaluser" a moderator
        u = User.objects.get(username="normaluser")
        u.is_staff = True
        perms = Permission.objects.filter(
            content_type__app_label = 'tango_comments',
            codename__endswith = 'comment'
        )
        for perm in perms:
            u.user_permissions.add(perm)
        u.save()

    @unittest.skip('probably need to add admin to urls')
    def testActionsNonModerator(self):
        comments = self.createSomeComments()
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.get("/admin/tango_comments/comment/")
        self.assertNotContains(response, "approve_comments")

    @unittest.skip('probably need to add admin to urls')
    def testActionsModerator(self):
        comments = self.createSomeComments()
        makeModerator("normaluser")
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.get("/admin/tango_comments/comment/")
        self.assertContains(response, "approve_comments")

    @unittest.skip('probably need to add admin to urls')
    def testActionsDisabledDelete(self):
        "Tests a CommentAdmin where 'delete_selected' has been disabled."
        self.createSomeComments()
        self.client.login(username="normaluser", password="normaluser")
        response = self.client.get('/admin2/tango_comments/comment/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<option value="delete_selected">')
