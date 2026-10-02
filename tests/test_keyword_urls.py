import unittest
from urllib.parse import parse_qs, urlsplit

from weibospider.spiders import common


class KeywordURLTests(unittest.TestCase):
    def test_keyword_round_trip(self):
        for keyword in ['丽江', 'C++', 'A&B', '#话题#', '100%20', 'a b', 'x&page=99']:
            with self.subTest(keyword=keyword):
                url = common.build_search_url(keyword, '2022-10-01-00', '2022-10-01-01')
                parts = urlsplit(url)
                self.assertEqual(parts.fragment, '')
                self.assertEqual(parse_qs(parts.query), {
                    'q': [keyword],
                    'timescope': ['custom:2022-10-01-00:2022-10-01-01'],
                    'page': ['1'],
                })

    def test_multi_day_time_range(self):
        url = common.build_search_url('丽江', '2022-10-01-00', '2022-10-07-23')
        parts = urlsplit(url)
        self.assertEqual((parts.scheme, parts.netloc, parts.path),
                         ('https', 's.weibo.com', '/weibo'))
        self.assertEqual(parse_qs(parts.query)['timescope'],
                         ['custom:2022-10-01-00:2022-10-07-23'])


if __name__ == '__main__':
    unittest.main()
