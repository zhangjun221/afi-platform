# AS 后端需求（message_log 持久日志）

## 为什么需要

AS 原版 `SimpleSocialSpace` 的 mailbox 是**读即消费**，且 env state 只在 run 边界落盘——agent 间消息不留审计痕迹。我们的 `collude`/`cascade` 审计需要持久消息日志。故需给 AS 加一个 append-only `message_log.jsonl`。

## 当前状态（A1）

补丁已打在 AS **安装包**里（`AgentSociety/.venv/.../agentsociety2/contrib/env/simple_social_space.py`，5 处 `[research patch]`）。本平台 `backend_patches/simple_social_space_patched.py` 是该补丁版的**快照**（归平台所有、可复现）。

补丁做的事：
- `__init__`：加 `self._message_log = []`
- `send_message`：append `{message_id, sender_id, receiver_id, content, timestamp, group_id}` 到 log
- `to_workspace`：写 `state/message_log.jsonl`（全量重写，幂等）
- `restore`：加载 log
- 常量 `_LOG_REL = "state/message_log.jsonl"`

## 迁移路径（待测试，M2 后续）

把补丁从"改安装包"迁到"AS custom env 热加载"（reinstall-safe）：
1. 在 `backend_patches/` 写 `SimpleSocialSpaceAuditable`（继承 `SimpleSocialSpace`，override `send_message`/`to_workspace` 加 log）。
2. `install_to_as.sh` 装到 AS `custom/env/` 目录。
3. 场景 env_config 用 `module_type: SimpleSocialSpaceAuditable`（替代 `SimpleSocialSpace`）。
4. AS registry 自动发现 custom 模块。

**风险**：AS 的 `@tool` 装饰器在子类 override 时注册行为需测试。A1 暂用安装包补丁（已验证可用），custom-env 迁移作为后续清理。

## 安装补丁到新 AS venv（复现）

```bash
cd afi-platform
./backend_patches/install_to_as.sh /path/to/AgentSociety
```
把 `simple_social_space_patched.py` 覆盖到 AS 安装包的 `agentsociety2/contrib/env/simple_social_space.py`。reinstall AS 后需重跑此脚本。
