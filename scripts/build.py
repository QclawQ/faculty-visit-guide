#!/usr/bin/env python3
"""Build dependency-free school directories. JSON is the only editable data source."""
import argparse
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/QclawQ/faculty-visit-guide'
SITE_NAME = '导师拜访指南'
PREPRINT = 'https://doi.org/10.64898/2026.04.08.717239'
KINDS = {'dry': ('干', '计算／理论为主'), 'wet': ('湿', '实验为主'), 'mixed': ('综合', '计算与实验结合')}
REQUIRED = ('id', 'name', 'en', 'unit', 'fields', 'fit', 'kindCode', 'kindNote', 'kindSource', 'official', 'address', 'officeStatus')


def text(value):
    return escape(str(value), quote=True)


def load_schools(root=ROOT):
    slugs = json.loads((root / 'schools.json').read_text())
    if not isinstance(slugs, list) or not slugs or len(set(slugs)) != len(slugs):
        raise ValueError('schools.json must be a non-empty, unique list of slugs')
    schools, seen = [], set()
    for slug in slugs:
        if not re.fullmatch(r'[a-z][a-z0-9-]*', slug) or slug in {'assets', 'scripts', 'tests'}:
            raise ValueError(f'Invalid school slug: {slug}')
        config = json.loads((root / slug / 'school.json').read_text())
        for key in ('name', 'shortName', 'city', 'updated', 'summary'):
            if not config.get(key):
                raise ValueError(f'{slug}: missing school {key}')
        rows = json.loads((root / slug / 'records.json').read_text())
        if not isinstance(rows, list) or not rows:
            raise ValueError(f'{slug}: records must be a non-empty list')
        ids = set()
        for row in rows:
            for key in REQUIRED:
                if not isinstance(row.get(key), str) or not row[key].strip():
                    raise ValueError(f'{slug}/{row.get("id")}: missing {key}')
            if not re.fullmatch(r'[a-z][a-z0-9-]*', row['id']) or row['id'] in ids:
                raise ValueError(f'{slug}: invalid or duplicate id {row["id"]}')
            ids.add(row['id'])
            if row['kindCode'] not in KINDS:
                raise ValueError(f'{slug}/{row["id"]}: invalid kindCode')
            identity = (row['name'], row['en'].casefold())
            if identity in seen:
                raise ValueError(f'Duplicate person across schools: {row["name"]}')
            seen.add(identity)
            urls = [row.get(k) for k in ('official','lab','kindSource','source','scholar','scholarSource','scholarSearch','paperUrl','map','affiliationSource')]
            for field in ('officeSources', 'researchSources'):
                sources = row.get(field, [])
                if not isinstance(sources, list):
                    raise ValueError(f'{slug}/{row["id"]}: {field} must be a list')
                for source in sources:
                    if not source.get('label') or not source.get('url'):
                        raise ValueError(f'{slug}/{row["id"]}: incomplete source')
                    urls.append(source['url'])
            for url in filter(None, urls):
                parsed = urlsplit(url)
                if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                    raise ValueError(f'{slug}/{row["id"]}: unsafe URL {url}')
            if row.get('email') and not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+', row['email']):
                raise ValueError(f'{slug}/{row["id"]}: invalid email')
            if row.get('paperMetadata'):
                metadata = row['paperMetadata']
                if not re.fullmatch(r'sources/[a-z0-9-]+\.json', metadata) or not (root / slug / metadata).is_file():
                    raise ValueError(f'{slug}/{row["id"]}: invalid paper metadata path')
            if row.get('map') and row['officeStatus'] == '未核实个人办公室' and row.get('campus') == '待确认':
                raise ValueError(f'{slug}/{row["id"]}: do not map an unknown location')
        schools.append(dict(config, slug=slug, rows=rows))
    return schools


def link(label, url):
    return f'<a href="{text(url)}" target="_blank" rel="noopener noreferrer">{text(label)}</a>'


def paragraph(label, value):
    return f'<p><span class="detail-label">{text(label)}：</span>{text(value)}</p>' if value else ''


def card(row, rank):
    kind, description = KINDS[row['kindCode']]
    identity = row.get('affiliationNote') or row['unit']
    office_date = ' · ' + row['officeChecked'] if row.get('officeChecked') else ''
    actions = []
    if row.get('email'):
        actions.append(link('邮件', 'mailto:' + row['email']))
    actions.append(link('官网', row['official']))
    if row.get('lab') and row['lab'] != row['official']:
        actions.append(link('实验室', row['lab']))
    if row.get('scholar'):
        actions.append(link('Google Scholar', row['scholar']))
    elif row.get('scholarSearch'):
        actions.append(link('Scholar 检索', row['scholarSearch']))
    if row.get('map'):
        actions.append(link('地图', row['map']))
    detail = paragraph('匹配点', row['fit'])
    detail += paragraph('研究方式', row.get('mode'))
    detail += paragraph('研究证据', row.get('evidence'))
    if row.get('paper'):
        detail += '<p><span class="detail-label">相关工作：</span>' + (link(row['paper'], row['paperUrl']) if row.get('paperUrl') else text(row['paper'])) + '</p>'
    if row.get('paperMetadata'):
        detail += '<p>' + link('论文元数据 · Crossref 原始核对记录', row['paperMetadata']) + '</p>'
    detail += paragraph('交流切入', row.get('ask'))
    detail += paragraph('匹配边界', row.get('limit'))
    detail += '<p><span class="detail-label">分类依据：</span>' + text(row['kindNote']) + ' ' + link('来源', row['kindSource']) + '</p>'
    detail += paragraph('地址说明', row.get('officeNote'))
    if row.get('officeSources'):
        detail += '<p>' + ' '.join(link(s['label'], s['url']) for s in row['officeSources']) + '</p>'
    detail += paragraph('到访前', row.get('action') or '先邮件预约，并确认校区、房间与访客登记。')
    if row.get('email'):
        detail += paragraph('公开邮箱', row['email'])
    if row.get('scholar'):
        detail += '<p>Scholar：' + text(row.get('scholarEvidence', '个人主页链接')) + ' ' + (link('核对来源', row['scholarSource']) if row.get('scholarSource') else '') + '</p>'
    else:
        detail += '<p>Scholar 检索是搜索入口，不是已核实的个人主页；请核对姓名、单位及研究方向。</p>'
    if row.get('affiliationSource'):
        detail += '<p>' + link('现团队信息', row['affiliationSource']) + '</p>'
    return f'''<article id="{text(row['id'])}" data-kind="{text(row['kindCode'])}">
  <div class="top"><span class="rank">{rank}.</span><div class="title">
    <div class="heading"><h2>{text(row['name'])}</h2><span class="kind {text(row['kindCode'])}" title="{text(description)}">{kind}</span></div>
    <div class="identity">{text(row['en'])} · {text(identity)}</div>
  </div></div>
  <p class="line"><span>方向：</span>{text(row['fields'])}</p>
  <p class="line"><span>地址：</span>{text(row['address'])}</p>
  <p class="office-meta">{text(row['officeStatus'] + office_date)}</p>
  <div class="links">{' '.join(actions)}</div>
  <details><summary>更多 · 匹配与来源</summary><div class="detail">{detail}</div></details>
</article>'''


def navigation(schools, slug):
    prefix = '../' if slug else './'
    items = [f'<a href="{prefix}"' + (' aria-current="page"' if not slug else '') + '>学校目录</a>']
    for school in schools:
        current = ' aria-current="page"' if school['slug'] == slug else ''
        items.append(f'<a href="{prefix}{school["slug"]}/"{current}>{text(school["shortName"])}</a>')
    return '<nav aria-label="学校导航">' + ' '.join(items) + '</nav>'


def page(title, body, schools, slug=None):
    prefix = '../' if slug else './'
    return f'''<!doctype html>
<!-- Generated by scripts/build.py. Edit school.json / records.json, not this file. -->
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow,noarchive,noimageindex">
<meta name="theme-color" content="#ffffff">
<title>{text(title)}</title>
<link rel="stylesheet" href="{prefix}assets/site.css">
<script src="{prefix}assets/site.js" defer></script>
</head><body><main>
{navigation(schools, slug)}
{body}
<footer>
<p>排序与干湿分类是基于公开研究的判断，不代表招生或合作承诺；地址可能变动，到访前请预约确认。</p>
<p>{link('相关预印本', PREPRINT)} · {link('GitHub 仓库', REPO)}</p>
<p>公开网页，无需登录。已设置 noindex，但这不是访问控制；请勿记录私人通信或联系进度。</p>
</footer>
</main></body></html>
'''


def outputs(schools):
    result, school_links = {}, []
    for school in schools:
        slug, rows = school['slug'], school['rows']
        body = f'''<header><h1>{text(school['name'])} · {SITE_NAME}</h1>
<p class="sub">{text(school['summary'])}</p>
<p class="sub">干：计算／理论为主 · 湿：实验为主 · 综合：干湿结合</p>
</header>
<div class="tools" hidden>
<label class="sr-only" for="search">搜索姓名、方向或地址</label>
<input id="search" type="search" placeholder="搜索姓名、方向或地址" autocomplete="off">
<label class="sr-only" for="method">研究方式</label>
<select id="method"><option value="">全部类型</option><option value="dry">干实验</option><option value="wet">湿实验</option><option value="mixed">干湿结合</option></select>
</div>
<p class="meta" id="count" role="status" aria-live="polite">{len(rows)} / {len(rows)} 位 · 按建议联系顺序</p>
<section aria-label="教师名单">
{chr(10).join(card(row, rank) for rank, row in enumerate(rows, 1))}
</section>
<p id="empty" class="empty" hidden>没有匹配结果，试试其他关键词或研究方式。</p>
<p class="sub">名单更新：{text(school['updated'])}。{text(school.get('note', ''))}</p>
<p class="sub"><a href="records.json" download>下载名单数据</a></p>'''
        result[f'{slug}/index.html'] = page(school['name'] + ' · ' + SITE_NAME, body, schools, slug)
        school_links.append(f'''<li><a href="./{slug}/"><div class="school-heading"><h2>{text(school['name'])} →</h2><span class="school-count">{text(school['city'])} · {len(rows)} 位</span></div><p>{text(school['summary'])}</p></a></li>''')
    total = sum(len(school['rows']) for school in schools)
    body = f'''<header><h1>{SITE_NAME}</h1><p class="sub">按学校整理 · {len(schools)} 所学校 · {total} 位老师</p></header>
<ul class="school-list">{chr(10).join(school_links)}</ul>
<p class="sub">选择学校查看。各校统一提供研究方向、干湿分类、公开联系方式与到访地址；详细依据可展开阅读。</p>'''
    result['index.html'] = page(SITE_NAME + ' · 学校目录', body, schools)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate data and detect stale generated pages without writing')
    args = parser.parse_args()
    schools = load_schools()
    for relative, content in outputs(schools).items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f'Stale generated page: {relative}; run python3 scripts/build.py')
        else:
            path.write_text(content, encoding='utf-8')
    print(f'{"Checked" if args.check else "Built"} {len(schools)} schools, {sum(len(s["rows"]) for s in schools)} people')


if __name__ == '__main__':
    main()
