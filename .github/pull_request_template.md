<!--
协作者：开 PR 前过一遍自检清单，填下面三项。管理者按此 review。
完整流程见 docs/collaboration-guide.md。
-->

## 改了什么
<!-- 一句话说清这个 PR 干了啥（对应 CONTRIBUTING backlog 项编号 B?，如适用） -->

## 怎么验收的
<!-- 跑了哪个命令、输出/结果。例：`python -m afi.cli awi runs/... --no-runtime` 出了 AWI 9 族；或 `pytest tests/test_gini.py` 全绿 -->

## 自检清单
- [ ] 一个 PR 只做一件事，没夹带无关改动
- [ ] `python -m afi.cli --help` 不报错（本地跑过）
- [ ] `python -c "import afi; from afi.audit import attribution; from afi.world import counterfactual"` import 干净
- [ ] 没误提交 `runs/` / `.env` / `__pycache__` / `afi_report_*.html`（git status 看过）
- [ ] commit / PR 标题符合规范（`类型: 简述`，feat/fix/docs/chore/test）

## 架构不变量（管理者会重点查，别破坏）
- [ ] **`afi/audit/` 不 import 后端/AS**（后端无关红线——审计层只读 run_dir）
- [ ] 代理指标标 `[proxy]`、stub 标 `[stub]`，没把代理当真算
- [ ] 借思路不搬代码（AFI/EW/GUARDIAN/Colosseum 不直接 import）
