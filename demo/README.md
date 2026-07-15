# afi-platform Gradio demo

交互式展示：三个平台（EW/AFI/AS）+ 我们的平台（afi-platform）+ 真实 run 数据的 AWI/审计/跨模型对照。

## 运行

```bash
# 用 AS venv（已装 gradio + matplotlib）
cd <afi-platform 根>
../repo_analysis/AgentSociety/.venv/bin/python demo/app.py
# 浏览器开 http://127.0.0.1:7861
```

依赖：gradio、matplotlib（AS venv 缺，需 `pip install gradio matplotlib`）。其余（afi/agentsociety2/pyyaml/pandas）已在 venv。

## 7 个 tab

| tab | 内容 | 交互? |
|---|---|---|
| ① 总览 | 一句话定位 + 四平台关系图 + 路线 A1-A4 | 静态 |
| ② 三个平台 | EW/AFI/AS 各一卡：是什么/能力/边界/有无代码 | 静态 |
| ③ 我们的平台 | 三层架构 + 与 AS 3 耦合点 + 改进点表（新增功能↔代码） | 静态 |
| ④ AWI 实测 | 选 run → 实时算 AWI 9 族（feasibility badge）+ M1-vs-EW + per-step 时序 | 交互 |
| ⑤ 跨模型对照 | 3 模型 AWI 表 + M4 bar（3.0/4.2/5.6）+ M1-vs-EW bucket | 静态图表 |
| ⑥ 审计报告 | 选 run → 内嵌完整审计 HTML | 交互 |
| ⑦ 怎么用 | CLI 一条龙 + 安全审计研究场景 | 静态 |

## 数据来源

读 `runs/`（本地，不入 git）：`ew_subset`（A2）、`ew_competitive`（A3 预置）、`ew_full`（A4，含能量/犯罪）、`ew_multi/{qwen-plus,qwen-max,qwen-turbo}`（A4 多模型）。
AWI 与审计**实时从 run_dir 文件算**（秒级）；**不做现场 AS 模拟**（太慢/成本高）。

## 设计要点

- **不 fork 不 vendor AS**：demo 跑在 afi-platform 根，`import afi` 走 cwd；custom/envs 由 AS registry 经 `WORKSPACE_PATH` 发现（demo 只读 run 产物，不重新跑 AS）。
- **真实数据**：所有 AWI 数值/对照图来自真实跑过的 run，不是造的。
- **诚实标注**：AWI 表每族带 feasibility badge（实算/代理/待建/退化）；M1-vs-EW 标"方向性非匹配对照"。
