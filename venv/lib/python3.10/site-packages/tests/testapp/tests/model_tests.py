from __future__ import absolute_import

from tango_comments.models import Comment

from . import CommentTestCase
from tests.testapp.models import Author, Article


class CommentModelTests(CommentTestCase):
    def testSave(self):
        for c in self.createSomeComments():
            self.assertNotEqual(c.post_date, None)

    def testUserProperties(self):
        c3, c4 = self.createSomeComments()
        self.assertEqual(c3.user, c4.user)

class CommentManagerTests(CommentTestCase):

    def testForModel(self):
        c3, c4 = self.createSomeComments()
        article_comments = list(Comment.objects.for_model(Article).order_by("id"))
        author_comments = list(Comment.objects.for_model(Author.objects.get(pk=1)))
        self.assertEqual(article_comments, [c3])

    def testPrefetchRelated(self):
        c3, c4 = self.createSomeComments()
        # one for comments, one for Articles, one for Author
        with self.assertNumQueries(3):
            qs = Comment.objects.prefetch_related('content_object')
            [c.content_object for c in qs]
