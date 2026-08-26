# Kairusi 命令参考

所有命令使用随包的 `scripts/kairusi_mcp.py`。它通过一个 Kairusi MCP 端点访问日刻、Todo 和日历，不需要也不应直接调用三个产品的内部 API。

## 首次授权

先在 `https://mcp.kairusi.com/authorize` 登录并生成 MCP 配置。复制其中 `Authorization` 的 Bearer Token 后，在本地 Skill 目录运行：

```bash
python3 scripts/kairusi_mcp.py configure
python3 scripts/kairusi_mcp.py status
python3 scripts/kairusi_mcp.py list-tools
```

`configure` 会以不回显方式接收 Token，并保存到 `~/.config/kairusi-skill/token`。不要使用 `--token` 参数、环境变量、Shell 历史或聊天消息传递 Token。

## 统一调用格式

```bash
python3 scripts/kairusi_mcp.py call \
  --tool <工具名> \
  --arguments '<JSON对象>'
```

每个命令都会创建短时 MCP 会话；Token 不会出现在输出中。工具参数以 `list-tools` 返回的 schema 为准。

## 日刻

```bash
# 获取日记本、模板和标签；创建日记前必须先执行
python3 scripts/kairusi_mcp.py call --tool rike_list_resources --arguments '{}'

# 最近日记列表
python3 scripts/kairusi_mcp.py call --tool rike_list_notes --arguments '{"limit": 30}'

# 创建九宫格日记。请先替换 UUID。
python3 scripts/kairusi_mcp.py call --tool rike_create_note --arguments '{
  "notebook_uuid": "<日记本UUID>",
  "template_uuid": "<模板UUID>",
  "day": "2026-08-26",
  "cells": [{"content": "今天完成了项目规划", "order_by": 1}]
}'
```

## Todo

```bash
# 读取项目、文件夹和清单
python3 scripts/kairusi_mcp.py call --tool todo_list_projects --arguments '{}'

# 搜索任务
python3 scripts/kairusi_mcp.py call --tool todo_search_tasks --arguments '{"keyword": "项目规划"}'

# 在指定清单创建任务。请先替换 list_uuid。
python3 scripts/kairusi_mcp.py call --tool todo_create_task --arguments '{
  "title": "整理项目计划",
  "list_uuid": "<清单UUID>",
  "belong_date": "2026-08-26"
}'
```

## 日历

```bash
# 读取日历和写入权限
python3 scripts/kairusi_mcp.py call --tool calendar_list_calendars --arguments '{}'

# 搜索日程
python3 scripts/kairusi_mcp.py call --tool calendar_search_events --arguments '{"keyword": "项目"}'

# 创建日程。目标日历必须 can_write=true；时间使用 UTC ISO 8601。
python3 scripts/kairusi_mcp.py call --tool calendar_create_event --arguments '{
  "title": "项目评审",
  "calendar_uuid": "<日历UUID>",
  "color": "#4C8BF5",
  "start_time": "2026-08-26T06:00:00Z",
  "end_time": "2026-08-26T07:00:00Z",
  "start_time_zone": "Asia/Shanghai",
  "end_time_zone": "Asia/Shanghai"
}'
```

## 写入与删除规则

创建或更新前先读取目标对象。对于删除，先通过读取或搜索获得准确 UUID，并让用户对目标名称和日期/时间做出明确确认，再调用对应删除工具并传入 `"confirmed": true`。不要对模糊的清理请求执行删除，也不要自动跨产品复制私密内容。
