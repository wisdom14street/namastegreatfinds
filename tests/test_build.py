"""Offline regression coverage. Fixture products are synthetic and never published."""
import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.tags = []
        self.feed(path.read_text())

    def find(self, tag, **attrs):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='great-finds-build-')
        cls.root = Path(cls.temp.name)
        for folder in ('scripts', 'site', 'src'):
            shutil.copytree(ROOT / folder, cls.root / folder)
        (cls.root / 'data').mkdir()
        # Cheapest variant is not first. The expensive option is the only markdown.
        cls.variants = [
            {'id': 102, 'title': 'Large', 'price': '75.00', 'compare_at_price': '90.00', 'available': True},
            {'id': 101, 'title': 'Small', 'price': '15.00', 'compare_at_price': None, 'available': True},
            {'id': 103, 'title': 'Sold out', 'price': '5.00', 'compare_at_price': None, 'available': False},
        ]
        products = [{
            'id': 1, 'handle': 'fixture-crystal', 'title': 'Fixture Crystal', 'product_type': 'Crystal',
            'vendor': 'Fixture maker', 'images': [{'src': 'https://cdn.shopify.com/fixture.jpg'}],
            'created_at': '2026-01-01T00:00:00Z', 'variants': cls.variants,
        }]
        cls.source = json.dumps(products)
        (cls.root / 'data/all_products.json').write_text(cls.source)
        cls.build()
        cls.dist = cls.root / 'dist'

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def build(cls, *args):
        subprocess.run(['python3', 'scripts/build.py', *args], cwd=cls.root,
                       check=True, capture_output=True, text=True)

    def test_variant_prices_and_discount_stay_together(self):
        path = self.dist / 'products/fixture-crystal/index.html'
        page = Page(path)
        buy = page.find('button', id='buy')[0]
        self.assertEqual(buy['data-v'], '101')
        self.assertEqual(buy['data-p'], '15.00')
        self.assertIn('hidden', page.find('s', id='cmp')[0])
        self.assertEqual(len(page.find('option')), 3)
        self.assertEqual((self.root / 'data/all_products.json').read_text(), self.source)
        catalog = json.loads((self.dist / 'data/catalog.json').read_text())
        self.assertEqual(catalog[0]['p'], 15)
        self.assertIsNone(catalog[0]['o'])
        import re
        ld = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', path.read_text())]
        product = next(x for x in ld if x['@type'] == 'Product')
        self.assertEqual(product['offers']['price'], '15.00')
        self.assertNotIn('brand', product)  # Do not invent a manufacturer.

    def test_every_internal_link_resolves_even_with_sparse_stock(self):
        missing = set()
        for path in self.dist.rglob('*.html'):
            for a in Page(path).find('a'):
                href = a.get('href', '')
                if href.startswith('/') and not href.startswith('//'):
                    route = urlsplit(href).path
                    dest = self.dist / route.lstrip('/')
                    if route.endswith('/'):
                        dest /= 'index.html'
                    if not dest.exists():
                        missing.add(route)
        self.assertEqual(missing, set())

    def test_bookshop_links_and_contact_match_verified_source(self):
        seen = set()
        for path in self.dist.rglob('*.html'):
            page = Page(path)
            for a in page.find('a'):
                u = urlsplit(a.get('href', ''))
                if u.scheme == 'tel':
                    self.assertEqual(u.path, '+12126450141')
                if u.hostname == 'namastebookshop.com':
                    qs = parse_qs(u.query)
                    self.assertEqual(qs['utm_source'], ['namastegreatfinds.com'])
                    self.assertEqual(qs['utm_medium'], ['referral'])
                    self.assertEqual(qs['utm_campaign'], ['namaste_storefront'])
                    seen.add(qs['utm_content'][0])
        self.assertEqual(seen, {'booking', 'bookshop', 'product'})

    def test_search_metadata_is_unique_and_empty_pages_are_not_indexed(self):
        sitemap = ET.parse(self.dist / 'sitemap.xml')
        urls = [node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn('https://namastegreatfinds.com/products/fixture-crystal/', urls)
        for url in urls:
            path = self.dist / urlsplit(url).path.lstrip('/') / 'index.html'
            self.assertEqual(Page(path).find('link', rel='canonical')[0]['href'], url)
        for path in ('/cart/', '/brands/', '/404.html', '/gifts-under-10/', '/gifts-for/witchy/'):
            self.assertNotIn('https://namastegreatfinds.com' + path, urls)
        for path in self.dist.rglob('*.html'):
            page = Page(path)
            self.assertEqual(len(page.find('meta', property='og:image:alt')), 1)
            self.assertEqual(len(page.find('meta', name='twitter:image:alt')), 1)
            self.assertLessEqual(len(page.find('meta', name='robots')), 1)
            self.assertEqual(len(page.find('meta', name='description')), 1)
        self.assertIn('Sitemap: https://namastegreatfinds.com/sitemap.xml', (self.dist / 'robots.txt').read_text())
        self.assertIn('noindex', Page(self.dist / 'brands/index.html').find('meta', name='robots')[0]['content'])
        self.assertIn('G-Y7R5K9NMW0', (self.dist / 'index.html').read_text())

    def test_z_preview_suppresses_analytics_and_indexing(self):
        self.build('--preview')
        text = (self.dist / 'index.html').read_text()
        self.assertNotIn('googletagmanager.com', text)
        self.assertNotIn('src="/assets/ga.js"', text)
        self.assertIn('noindex,nofollow', text)
        self.assertIn('Disallow: /', (self.dist / 'robots.txt').read_text())

if __name__ == '__main__':
    unittest.main()
