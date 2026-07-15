# afi-platform 协作开发指南（给项目管理者 + 协作者）

> 你第一次做多人协作研发的项目管理，不懂 PR/merge/冲突。这份文档把概念到流程全讲清楚，按它做就行。
> 适用：afi-platform（Python，GitHub `zhangjun221/afi-platform`）。小研究团队（几人），不上重型工程流程。
> 配套：`README.md`（Setup）、`CONTRIBUTING.md`（backlog + 怎么领任务）。

---

## 第一部分：先懂概念（大白话，没做过 git 协作就读这）

### git 是什么——"带存档点的文件夹同步"
- **commit** = 存档点。每次 commit = 给整个项目拍一张快照，附一句说明。
- **仓库 (repo)** = 这个带存档历史的文件夹。
- **本地 (local)** = 你电脑上的副本；**远程 (remote/origin)** = GitHub 上的那一份。
- **push** = 把本地新存档推到 GitHub；**pull** = 把 GitHub 上的新存档拉到本地。两人协作就是互相 push/pull。

### branch（分支）——"平行宇宙"
- `main` 分支 = 主线，**永远要是能跑的稳定版本**，大家不直接往它上面写。
- 每做一件新活，从 main 开一条新分支（叫 feature 分支），在自己分支上随便改随便 commit，不影响别人。
- 改完把分支合回 main——这就叫"合并"。

### merge（合并）与 conflict（冲突）
- **merge** = 把你分支的改动合进 main。
- **冲突 (conflict)** = 你和另一个人改了**同一个文件的同一处**，git 不知道留谁的，停下来让你手动选。冲突不可怕，下面有解法。
- 只要大家改的是**不同文件 / 同文件不同位置**，git 自动合，不冲突。

### PR（Pull Request）——"申请合并"
- PR = "我这条分支改完了，请管理者审一下，批准后合并进 main"。
- PR 不是直接改 main，而是一个**审批单**：上面显示你改了哪些文件、和 main 差在哪、别人能逐行评论。
- 你（管理者）看完点 Approve + Merge，改动才进 main。**这是防止坏代码进主线的核心机制**。

### review（审批）
- 在 PR 页面上逐行看代码、留评论；觉得 OK 点 **Approve**；要改点 **Request changes**。
- 至少 1 个 Approve 才能 Merge（这条由"分支保护"强制，见第三部分）。

### fork（外部协作者用，你大概率不用）
- **fork** = 把仓库复制一份到协作者自己 GitHub 账号下，改完从他那发 PR 过来。
- **collaborator** = 你直接把人加进仓库（Settings → Collaborators），他能直接 push 分支到你的仓库，不用 fork。
- 小团队推荐：**直接加 collaborator**（不用 fork，少一层）。下面流程按这个写。如果有人你不想给写权限，让他 fork + PR 也行。

### 一句话心智模型
> 每人各自开分支干活 → 改完发 PR → 管理者 review 批准 → squash 合进 main → main 永远稳定能跑。冲突偶发，手动解。CI 自动跑测试兜底。

---

## 第二部分：推荐的协作模型（小团队，够用不重）

### 分支约定
- `main`：稳定主线，**只通过 PR 进，不直接 push**（分支保护强制）。
- feature 分支命名：`feat/<简述>`（新功能）、`fix/<简述>`（修 bug）、`docs/<简述>`（文档）、`test/<简述>`（测试）。
  - 例：`feat/relationship-space`、`fix/gini-formula`、`docs/backlog-b3`。
- 分支寿命短：一个分支做一件事，合并后删掉。

### 合并方式：Squash merge（推荐）
- GitHub PR 的 Merge 按钮有三种：**Merge / Squash / Rebase**。
- 推荐 **Squash merge**：把你分支上的好几个 commit 压成 1 个干净 commit 进 main。
  - 好处：main 历史干净（每个 PR = 1 commit），好回溯；你分支上随便写脏 commit 都没关系。
- 在 GitHub 仓库 Settings → General → Pull Requests 里只勾选 "Allow squash merging"，关掉另两种，避免选错。

### Commit message 规范（轻量）
- 格式：`类型: 简述`，类型用 feat/fix/docs/chore/test/refactor。
  - 例：`feat: RelationshipSpace env (M7 真算)`、`fix: _resolve_tick 读 step.count 不读 agent.tick`、`docs: 加 B3 backlog 细节`。
- squash merge 时，GitHub 用 PR 标题做 commit message——让协作者把 PR 标题写成这个格式即可。

---

## 第三部分：防"合并出问题"的机制（核心，必做）

这是你问"怎么保证大家同时修改合到一起不出问题"的答案——**靠这 4 道闸，不靠人自觉**：

### 闸 1：分支保护（Branch Protection）——强制 PR + review
在 GitHub `Settings → Branches → Branch protection rules → Add rule`，对 `main` 设：
- ☑ Require a pull request before merging（禁止直接 push main）
- ☑ Require approvals: 1（至少 1 人 approve 才能合，你审）
- ☑ Require status checks to pass（CI 测试过了才能合，见闸 2）
- ☑ Require branches to be up to date（合并前必须和最新 main 同步，减少冲突）
- ☐ 不要勾 "Require approvals" 太多（小团队 1 个够）

效果：任何人都不能绕过 PR 直接改 main；必须 PR → 你 review → CI 过 → 才合。

### 闸 2：CI 自动测试（GitHub Actions）——每次 PR 自动跑
在仓库加一个 `.github/workflows/ci.yml`，PR 一开就自动跑：
- `python -m afi.cli --help`（CLI 不破）
- `python -c "import afi; from afi.audit import awi, causal, attribution; from afi.world import counterfactual"`（import 不破）
- `python -m afi.cli awi runs/ew_multi/qwen-plus --no-runtime`（只读审计仍通）—— 但这个需要 run 数据，CI 上没有 → 改成跑现有单元测试 + import + CLI help。等 `tests/` 有单测后再加 pytest。
- CI 失败 = PR 不能合。协作者改坏了 import/CLI，你还没看 CI 就先红了，省你 review 时间。

> 我可以帮你建这个 CI 文件 + 开分支保护（见文末"我能帮你做的"）。

### 闸 3：小步提交 + 频繁同步
- 让协作者：一个分支只做一件小事（别一个 PR 改 20 个文件），常 `git pull --rebase origin main`（把最新 main 拉进自己分支）。
- 越频繁同步，冲突越小越好解；攒一周才同步，冲突能大到头疼。

### 闸 4：.gitignore 纪律（已建好）
- `runs/`、`afi_report_*.html`、`.env`、`__pycache__` 等已 gitignore，协作者不会误提交大文件/密钥/run 产物。
- 新人生成物（如新 cache 文件）→ 先加 .gitignore 再写代码，别污染仓库。

---

## 第四部分：协作者怎么提交（步骤，照做）

### 第一次（setup）
```bash
# 1. 你把他加进 collaborator（GitHub Settings → Collaborators → Add）
# 2. 他克隆 + 装环境（见 README Setup）
git clone https://github.com/zhangjun221/afi-platform.git
cd afi-platform
python -m venv .venv && source .venv/bin/activate
pip install -e ".[yaml]"
# AS 后端二选一（见 README）；只做 audit/归因不用 AS
```

### 每次干活的循环
```bash
# 0. 拉最新 main
git checkout main
git pull origin main

# 1. 开分支（命名见第二部分）
git checkout -b feat/relationship-space

# 2. 改代码，小步 commit
#   ...改文件...
git add <改的文件>
git commit -m "feat: RelationshipSpace env 骨架"

# 3. 推分支到 GitHub
git push -u origin feat/relationship-space

# 4. 去 GitHub 网页开 PR（GitHub 会提示 "Compare & pull request"）
#    PR 标题写成 commit 规范格式，描述写改了啥 + 怎么验收的（见 CONTRIBUTING）

# 5. 等 CI 跑 + 管理者 review
#    - 要改的话：本地继续改 → git add/commit → git push（同一分支追加，PR 自动更新）
#    - 同步最新 main（避免冲突）：git fetch origin && git rebase origin/main，再 git push -f

# 6. 管理者 Approve + Squash merge 后，删本地分支
git checkout main && git pull origin main
git branch -d feat/relationship-space
```

### 协作者自检清单（PR 前过一遍）
- [ ] 改的文件没夹带无关改动（一个 PR 一件事）
- [ ] `python -m afi.cli --help` 不报错（本地跑过）
- [ ] `python -c "import afi; ..."` import 干净
- [ ] 没误提交 `runs/`/`.env`/`__pycache__`（gitignore 已挡，但 `git status` 看一眼）
- [ ] commit/PR 标题符合规范
- [ ] 描述写了"怎么验收的"（跑了哪个命令、结果）

---

## 第五部分：你（管理者）怎么审批

### 日常 review 流程
1. 收到 PR 邮件/GitHub 通知 → 进 PR 页面。
2. 看 **Files changed** 标签页：逐文件、逐行看 diff（红=删，绿=加）。
3. 点行号能留评论：`这里变量名建议改`、`没处理 agent_id=None 的情况` 等。
4. 看完：
   - 要改 → **Request changes**（协作者改完会自动重新通知你）。
   - 没问题 → **Approve**。
5. Approve + CI 绿 → 点 **Squash and merge** → 删分支（GitHub 会提示）。

### review 看什么（管理者 checklist）
- **架构不变量没破**：`afi/audit/` 不能 import 后端/AS（后端无关）；这是核心红线（见 CONTRIBUTING 代码约定）。
- **诚实声明没造假**：代理指标标 `[proxy]`、stub 标 `[stub]`，别把代理当真算。
- **没夹带 runs/.env/大 HTML**：CI + gitignore 挡，但看一眼。
- **能跑**：PR 描述里有没有"跑了哪个命令验证过"——没验证的让他先验证。
- **没破坏 main 稳定**：CI 红的别合。

### 你也能直接改
- 小改（typo、文档）你可以直接在 GitHub 网页编辑 → 它会自动走 PR（因为 main 保护了）→ 自己 approve（如果你给自己开权限）→ merge。
- 或本地开分支走同样流程。

---

## 第六部分：合并冲突怎么解（必遇，不难）

### 为什么会冲突
你和另一个人改了**同一文件的同一行附近**，git 自动合不了，会在 PR 里标 "This branch has conflicts that must be resolved"。

### 解法 A：GitHub 网页解（最简单，小冲突）
PR 页面有个 "Resolve conflicts" 按钮 → 网页编辑器显示冲突标记：
```
<<<<<<< HEAD
main 上的版本
=======
你的分支的版本
>>>>>>> feat/xxx
```
你删掉不想要的版本 + 删掉 `<<<`/`===`/`>>>` 标记 → 点 "Mark as resolved" + Commit merge。

### 解法 B：本地解（大冲突）
```bash
git fetch origin
git checkout <你的分支>
git rebase origin/main          # 把 main 最新拉进来叠在你分支下
# 有冲突时 git 会停，告诉你哪个文件
# 编辑器打开那个文件，找 <<<<<<< 标记，手动选保留内容，删标记
git add <改好的文件>             # 标记冲突已解
git rebase --continue            # 继续
git push -f origin <你的分支>    # rebase 改了历史，要 force push（只在自己分支上安全！）
```

### 减少冲突的习惯
- 小 PR（一个分支一件事、改几个文件）。
- 频繁 `git pull --rebase origin main` 同步。
- 不同人分工改不同模块（CONTRIBUTING backlog B1-B10 按模块分，天然少冲突）。

### 红线
- **永远不要 `git push -f` 到 main**（分支保护会挡，但别养成习惯）。force push 只在自己 feature 分支上用。

---

## 第七部分：常见场景

### 场景 1：新人加入
1. GitHub Settings → Collaborators → Add（用对方 GitHub 用户名）。
2. 把这份文档 + README + CONTRIBUTING 发给他。
3. 让他先认领 CONTRIBUTING 里一个低门槛任务（B9 单测最适练手）。

### 场景 2：紧急修 bug（hotfix）
- 同样开 `fix/<bug>` 分支 → PR → 你紧急 review → 合。别绕过 PR（即使急，PR 流程只多 2 分钟，值得）。

### 场景 3：发布版本（tag）
- main 稳定时，`git tag v0.1.0 && git push origin v0.1.0`。GitHub 会出 Release 页。
- 研究项目不强制发版，但里程碑（如论文投稿前）打个 tag 好回溯。

### 场景 4：协作者跑不起来 AS
- 只读命令（audit/awi/attribution 无 --counterfactual）不需要 AS，先让他跑这些练手。
- 跑模拟要 AS 后端（pip 装 agentsociety2 或设 AS_HOME）——见 README Setup。

### 场景 5：有人提了破坏架构的 PR（audit 层 import 了后端）
- review 里 Request changes + 评论说明红线（`afi/audit/` 后端无关是不变量）。打回让他改。**别妥协合进去**，合了就要拆。

---

## 第八部分：你作为管理者的日常清单

- [ ] **每周**：看一眼 PR 列表，有积压的及时 review（别让 PR 挂一周，协作者会卡住）。
- [ ] **review 时**：跑 checklist（架构不变量 / 诚实声明 / 能跑 / 没夹带）。
- [ ] **CI 红了**：让协作者先修，别你自己替他修（除非小事）。
- [ ] **里程碑前**：跑一遍 `python -m afi.cli audit runs/...` 确认 main 还能出报告。
- [ ] **新人来**：发这份文档 + README + CONTRIBUTING，让他从 B9（单测）练手。
- [ ] **定期**：看 backlog（CONTRIBUTING B1-B10）有没有人认领、卡住的帮忙。

---

## 第九部分：我（Claude）能帮你做的

如果你想，我可以现在帮你：
1. **建 CI 工作流**（`.github/workflows/ci.yml`）——PR 自动跑 import + CLI help smoke test，红的不让合。
2. **开分支保护**（`gh api` 设 main 的 protection rule：要求 PR + 1 approval + CI 过）。
3. **加一个 PR 模板**（`.github/pull_request_template.md`）——协作者开 PR 时自动填"改了啥/怎么验收/是否破坏架构不变量"。

这三样是"防出问题"的实体机制，建了闸 1+闸 2 就自动生效。说一声我就做。

---

## 一页速查

```
概念：commit=存档 / branch=平行宇宙 / merge=合并 / PR=合并申请 / review=审批 / conflict=同处冲突
模型：直接加 collaborator（不用 fork）→ 开 feat/fix/docs 分支 → PR → 你 review → squash merge → 删分支
四闸：①分支保护(强制PR+review) ②CI(import/CLI smoke) ③小步+频繁同步 ④.gitignore(已建)
红线：audit 层不 import 后端 / 不 force push main / 不提交 runs/.env / 代理指标标 proxy
你做：及时 review / 跑 checklist / 新人从 B9 练手 / 里程碑跑一遍 audit
```
