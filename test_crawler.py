import io
import sys
import unittest
from unittest.mock import patch
from urllib.error import URLError
from re import match

import crawler


class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.invalid_url = 'htt://olx.com'

    def test_crawler(self):
        output = io.StringIO()
        sys.stdout = output

        html = open('offer.html')
        with patch('crawler.get_html') as mocked_get:
            mocked_get.return_value = html
            crawler.crawler('')
            self.assertTrue(match(r'.*\n.*\n.*\n\n', output.getvalue()))
        html.close()

    def test_link_generator(self):
        html = open('offers_list.html')
        g = crawler.link_generator(html)
        while True:
            try:
                self.assertTrue(match(r'https://', next(g)))
            except StopIteration:
                html.close()
                break

    def test_get_html(self):
        self.assertTrue(crawler.get_html())
        with self.assertRaises(URLError):
            crawler.get_html(self.invalid_url)

    def test_main(self):
        output = io.StringIO()
        sys.stdout = output

        with self.assertRaises(SystemExit) as cm:
            crawler.main([])
            sys.stdout = sys.__stdout__
            self.assertEqual(cm.exception.code, 2)
            self.assertEqual(output.getvalue(),
                             'crawler.py -q <search_query>')

            crawler.main(['-q', ''])
            self.assertEqual(cm.exception.code, 2)
            self.assertEqual(output.getvalue(),
                             'crawler.py -q <search_query>')


if __name__ == '__main__':
    unittest.main()
