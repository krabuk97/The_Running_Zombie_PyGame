import unittest

from xml.etree import ElementTree as ET

from django.urls import reverse

from . import CommentTestCase


class CommentFeedTests(CommentTestCase):

    @unittest.skip('object() takes no parameters error')
    def test_feed(self):
        response = self.client.get(reverse('comments-feed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rss+xml; charset=utf-8')

        rss_elem = ET.fromstring(response.content)

        self.assertEqual(rss_elem.tag, "rss")
        self.assertEqual(rss_elem.attrib, {"version": "2.0"})

        channel_elem = rss_elem.find("channel")

        title_elem = channel_elem.find("title")
        self.assertEqual(title_elem.text, "example.com comments")

        link_elem = channel_elem.find("link")
        self.assertEqual(link_elem.text, "http://example.com/")

        atomlink_elem = channel_elem.find("{http://www.w3.org/2005/Atom}link")
        self.assertEqual(atomlink_elem.attrib, {"href": "http://example.com/rss/comments/", "rel": "self"})

        self.assertNotContains(response, "A comment for the second site.")
