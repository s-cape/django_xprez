from bs4 import BeautifulSoup
from django.test import SimpleTestCase

from xprez.ck_editor.parse_text import parse_text


def _html(html):
    return BeautifulSoup(html, "html5lib").body.decode_contents()


class ParseTextTrailingCleanupTest(SimpleTestCase):
    def assert_parsed(self, source, expected):
        self.assertEqual(parse_text(source), _html(expected))

    def test_removes_trailing_empty_p(self):
        self.assert_parsed("<p></p><p>Hello</p><p></p>", "<p></p><p>Hello</p>")

    def test_removes_trailing_br_and_nbsp_p(self):
        with self.subTest("trailing br"):
            self.assert_parsed("<br><p>x</p><br>", "<br><p>x</p>")
        with self.subTest("trailing nbsp p"):
            self.assert_parsed("<p>End</p><p>&nbsp;</p>", "<p>End</p>")

    def test_keeps_non_trailing_empty_p(self):
        self.assert_parsed("<p></p><p></p><p>End</p>", "<p></p><p></p><p>End</p>")

    def test_keeps_attributed_empty_p_at_end(self):
        self.assert_parsed('<p class="x"></p><p></p>', '<p class="x"></p>')

    def test_removes_trailing_p_with_br_children(self):
        self.assert_parsed("<p>Hi</p><p><br></p>", "<p>Hi</p>")
