import copy
import importlib.util
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class Document(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.links, self.ids, self.articles = [], [], 0
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.articles += tag == 'article'
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attr in ('href', 'src'):
            if attr in attrs:
                self.links.append(attrs[attr])


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.schools = build.load_schools()

    def test_current_data_and_no_duplicate_people(self):
        schools = {s['slug']: s for s in self.schools}
        self.assertGreaterEqual(len(schools['westlake']['rows']), 15)
        self.assertGreaterEqual(len(schools['pku']['rows']), 25)
        names = [r['name'] for r in schools['westlake']['rows']]
        for name in ['曹龙兴','曾坚阳','付向东','杨剑','柴继杰','施一公','张垲','孙仁','管坤良','原发杰']:
            self.assertIn(name, names)
        self.assertNotIn('周沛劼', names)
        self.assertIn('周沛劼', [r['name'] for r in schools['pku']['rows']])

    def test_generated_pages_are_current_and_have_static_content(self):
        for path, html in build.outputs(self.schools).items():
            self.assertEqual((ROOT / path).read_text(), html, path)
            doc = Document(html)
            self.assertEqual(len(doc.ids), len(set(doc.ids)), path)
            self.assertIn('noindex', html)
            if path != 'index.html':
                school = next(s for s in self.schools if path.startswith(s['slug'] + '/'))
                self.assertEqual(doc.articles, len(school['rows']))
                for row in school['rows']:
                    self.assertIn(build.text(row['name']), html)

    def test_all_internal_links_resolve(self):
        for path, html in build.outputs(self.schools).items():
            for url in Document(html).links:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (ROOT / path).parent / unquote(parsed.path)
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), f'{path}: broken link {url}')

    def test_html_escapes_untrusted_values(self):
        row = copy.deepcopy(self.schools[0]['rows'][0])
        row['name'] = '<script>alert("x")</script>'
        row['fit'] = '<img src=x onerror=alert(1)>'
        html = build.card(row, 1)
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img', html)
        self.assertIn('&lt;script&gt;', html)

    def test_third_school_requires_no_template_changes(self):
        third = dict(self.schools[0], slug='example', name='示例大学', shortName='示例')
        output = build.outputs(self.schools + [third])
        self.assertIn('example/index.html', output)
        self.assertIn('3 所学校', output['index.html'])
        self.assertIn('../example/', output['pku/index.html'])

    def test_invalid_kind_and_unsafe_url_rejected(self):
        for field, value in [('kindCode','unknown'), ('official','javascript:alert(1)')]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'schools.json').write_text('["example"]')
                (root / 'example').mkdir()
                school = self.schools[0]
                config = {k:v for k,v in school.items() if k not in ('rows','slug')}
                (root / 'example/school.json').write_text(json.dumps(config))
                row = copy.deepcopy(school['rows'][0])
                row[field] = value
                (root / 'example/records.json').write_text(json.dumps([row]))
                with self.assertRaises(ValueError):
                    build.load_schools(root)


if __name__ == '__main__':
    unittest.main()
