# Faculty Visit Guide · 维护约定

- 本项目是按学校整理的导师与科研合作对象拜访指南，保持手机友好、简洁的静态网页。
- 工作范围限于本仓库；`Developer` 下的 `phd-advisor-search` 等目录是独立项目，不要混合或修改。
- GitHub 账户使用 `QclawQ`，仓库为 `QclawQ/faculty-visit-guide`，继续使用现有 GitHub Pages。不要改变其他项目或全局账户配置。
- 先阅读 `README.md`。名单只编辑各校 `records.json` 与 `school.json`；共用页面由 `scripts/build.py` 生成，不手改 `index.html`。
- 保留已有老师的稳定 `id`、学校路径与相对顺序，除非用户要求调整。新增学校追加到 `schools.json`。
- 研究领域、干湿分类和地址以可追溯的公开来源核验；未确认的办公室明确标注，不能把机构公共地址当作个人办公室。
- 这是公开仓库和网页。不得加入私人邮件、成绩单、联系记录、具体访问安排或密钥；`noindex` 不等于私有访问。
- 修改后运行 `python3 scripts/build.py`、`python3 -m unittest discover -s tests`、`python3 scripts/build.py --check` 与 `git diff --check`。发布后核实 GitHub Pages 状态。
