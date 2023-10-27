import unittest

import re

from django.conf import settings
from django.contrib.auth.models import User

from tango_comments import signals
from tango_comments.models import Comment

from . import CommentTestCase
from tests.testapp.models import Article, Book


post_redirect_re = re.compile(r'^/posted/\?c=(?P<pk>\d+$)')


class CommentViewTests(CommentTestCase):

    def testPostCommentHTTPMethods(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.get("/post/", data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "POST")

    def testPostCommentMissingCtype(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        del data["content_type"]
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostCommentBadCtype(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["content_type"] = "Nobody expects the Spanish Inquisition!"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostCommentMissingObjectPK(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        del data["object_pk"]
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostCommentBadObjectPK(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["object_pk"] = "14"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostInvalidIntegerPK(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["comment"] = "This is another comment"
        data["object_pk"] = '\ufffd'
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostInvalidDecimalPK(self):
        b = Book.objects.get(pk='12.34')
        data = self.getValidData(b)
        data["comment"] = "This is another comment"
        data["object_pk"] = 'cookies'
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testHashTampering(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["security_hash"] = "Nobody expects the Spanish Inquisition!"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testDebugCommentErrors(self):
        """The debug error template should be shown only if DEBUG is True"""
        olddebug = settings.DEBUG

        settings.DEBUG = True
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["security_hash"] = "Nobody expects the Spanish Inquisition!"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "comments/400-debug.html")

        settings.DEBUG = False
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateNotUsed(response, "comments/400-debug.html")

        settings.DEBUG = olddebug


    @unittest.skip('post not working')
    def testPostAsAuthenticatedUser(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data['name'] = data['email'] = ''
        self.client.login(username="normaluser", password="normaluser")
        self.response = self.client.post("/post/", data, REMOTE_ADDR="1.2.3.4")
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.all()[0]
        self.assertEqual(c.ip_address, "1.2.3.4")
        u = User.objects.get(username='normaluser')
        self.assertEqual(c.user, u)
        self.assertEqual(c.user_name, u.get_full_name())
        self.assertEqual(c.user_email, u.email)

    @unittest.skip('post not working')
    def testPreventDuplicateComments(self):
        """Prevent posting the exact same comment twice"""
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        self.client.post("/post/", data)
        self.client.post("/post/", data)
        self.assertEqual(Comment.objects.count(), 1)

        # This should not trigger the duplicate prevention
        self.client.post("/post/", dict(data, comment="My second comment."))
        self.assertEqual(Comment.objects.count(), 2)

    def testWillBePostedSignal(self):
        """
        Test that the comment_will_be_posted signal can prevent the comment from
        actually getting saved
        """
        def receive(sender, **kwargs): return False
        signals.comment_will_be_posted.connect(receive, dispatch_uid="comment-test")
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)
        signals.comment_will_be_posted.disconnect(dispatch_uid="comment-test")

    @unittest.skip("Location not in response")
    def testCommentNext(self):
        """Test the different "next" actions the comment view can take"""
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = post_redirect_re.match(location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

        data["next"] = "/somewhere/else/"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^/somewhere/else/\?c=\d+$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

        data["next"] = "http://badserver/somewhere/else/"
        data["comment"] = "This is another comment with an unsafe next url"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = post_redirect_re.match(location)
        self.assertTrue(match != None, "Unsafe redirection to: %s" % location)

    @unittest.skip("Key error for location. Maybe due to bad post")
    def testCommentDoneView(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = post_redirect_re.match(location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)
        pk = int(match.group('pk'))
        response = self.client.get(location)
        self.assertTemplateUsed(response, "comments/posted.html")
        self.assertEqual(response.context[0]["comment"], Comment.objects.get(pk=pk))

    @unittest.skip("Key error for location. Maybe due to bad post")
    def testCommentNextWithQueryString(self):
        """
        The `next` key needs to handle already having a query string (#10585)
        """
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["next"] = "/somewhere/else/?foo=bar"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^/somewhere/else/\?foo=bar&c=\d+$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

    @unittest.skip("Key error for location. Maybe due to bad post")
    def testCommentPostRedirectWithInvalidIntegerPK(self):
        """
        Tests that attempting to retrieve the location specified in the
        post redirect, after adding some invalid data to the expected
        querystring it ends with, doesn't cause a server error.
        """
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        broken_location = location + "\ufffd"
        response = self.client.get(broken_location)
        self.assertEqual(response.status_code, 200)

    @unittest.skip("Key error for location. Maybe due to bad post")
    def testCommentNextWithQueryStringAndAnchor(self):
        """
        The `next` key needs to handle already having an anchor. Refs #13411.
        """
        # With a query string also.
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["next"] = "/somewhere/else/?foo=bar#baz"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^/somewhere/else/\?foo=bar&c=\d+#baz$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

        # Without a query string
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["next"] = "/somewhere/else/#baz"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^/somewhere/else/\?c=\d+#baz$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)
