# Faculty Visit Guide · 导师拜访指南

按学校整理潜在导师与科研合作对象，方便手机查阅研究方向、联系方式和拜访地址。纯 HTML / CSS / JavaScript，无需登录或安装。

- 在线入口：[导师拜访指南](https://qclawq.github.io/faculty-visit-guide/)
- GitHub 仓库：[QclawQ/faculty-visit-guide](https://github.com/QclawQ/faculty-visit-guide)
- 本地维护目录：`~/Developer/faculty-visit-guide`

| 学校 | 在线阅读 | 数据目录 |
| --- | --- | --- |
| 西湖大学 · 16 位 | [西湖名单](https://qclawq.github.io/faculty-visit-guide/westlake/) | [westlake/](westlake/) |
| 北京大学 · 26 位 | [北大名单](https://qclawq.github.io/faculty-visit-guide/pku/) | [pku/](pku/) |

2026-09-15：原仓库 `gfn-v-9f2c7a` 改名为 `faculty-visit-guide`，本地迁入 `Developer`。请更新手机收藏；GitHub 会重定向旧仓库链接，但不会自动重定向旧 GitHub Pages 网页地址（[官方说明](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)）。各学校子目录与老师条目锚点不变。

原西湖混合名单中的周沛劼归入北大，42 位老师不重复。Secret Gist 不再更新或作为入口；历史版本未删除。Markdown 仅用于仓库维护说明，不再提供另一套阅读版名单。

2026-09-15 补充：郭天南（西湖第 7 位，蛋白组与虚拟细胞）、梁希同（北大第 26 位，神经与行为扩展）。两人的 Scholar 身份与官网已交叉核对，代表作通过 Crossref 核对；原始 JSON 与查询地址保存在各校 `sources/`，可从网页条目的“更多”下载。

## 文件结构

```text
AGENTS.md                # 本项目的维护范围与约定
schools.json             # 学校 slug 和显示顺序
index.html               # 生成的学校目录
westlake/
  school.json            # 校名、城市、更新日期与说明
  records.json           # 唯一可编辑名单源；数组顺序即建议联系顺序
  index.html             # 生成的网页
pku/
  school.json
  records.json
  index.html
  research-data.json     # 2026-09-15 原始研究资料快照，不作为当前名单源
  crossref-sequence.json # 原始检索快照
assets/                  # 两校共用样式及搜索／干湿筛选
scripts/build.py         # Python 标准库静态构建和校验
tests/                   # 内容、链接、转义与扩展性检查
```

## 修改与预览

只编辑对应学校的 `records.json`、`school.json`；不要直接编辑生成的 `index.html`。

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests
python3 scripts/build.py --check
python3 -m http.server 8768 --bind 127.0.0.1
```

浏览器打开 `http://127.0.0.1:8768/`。修改后重新构建并刷新。提交数据、共用代码和生成页面到 `main`，现有 GitHub Pages 从仓库根目录发布。`--check` 只检查，不写文件；CI 也会检查是否忘记重新生成。

## 增加学校

1. 新建小写目录（例如 `tsinghua/`），加入 `school.json` 和 `records.json`；可参考现有两校，或 `scripts/record.example.json` 的记录格式。
2. `school.json` 填写 `name`、`shortName`、`city`、`updated`（YYYY-MM-DD）、`summary`，可加 `note`。
3. 将目录名追加到根目录 `schools.json`。
4. 运行构建与测试，然后提交。首页、各校导航和人数自动更新，无需改页面模板；新网址为 `/<repo>/<学校目录>/`。

每位老师必填 `id`、`name`、`en`、`unit`、`fields`、`fit`、`kindCode`、`kindNote`、`kindSource`、`official`、`address`、`officeStatus`。`id` 用稳定的小写英文标识；同一人只放一所学校，跨校任职用 `affiliationNote` 说明。邮箱、实验室、Scholar、详细研究及地址来源可选。

## 内容口径与隐私

- `dry` → 干（计算／理论主导）；`wet` → 湿（实验主导）；`mixed` → 综合（计算与实验结合）。这是基于公开研究的粗分类，不保证每个项目均有自建湿实验平台；分类依据留在条目中。
- 保留原建议联系顺序，不新增权重或分数。研究匹配建议不是招生意向或合作承诺。
- 办公室、实验室、机构通信地址、校区线索明确区分，无法核实就注明。地址日期是该字段的核对日期，不代表全站重新实地确认。
- 西湖本次更新校正原发杰、张垲、付向东姓名；移除未知地址的误导性地图，并保留历史信息待确认说明。
- `Scholar 检索` 只是搜索入口；只有有匹配来源的个人主页才标为 `Google Scholar`。
- 这是公开仓库和公开网页。`noindex` 和 `robots.txt` 不能保护隐私；不放私人邮件、成绩单、日历、访问安排、联系状态或密钥。
- 默认正文静态生成，不依赖 JavaScript；搜索与筛选为渐进增强。链接使用相对路径，适用于 GitHub Pages 项目子目录。
