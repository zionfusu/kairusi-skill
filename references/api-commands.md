# Kairusi 命令参考

所有命令使用随包的 `scripts/kairusi_mcp.py`。它通过一个 Kairusi MCP 端点访问日刻、Todo 和日历，不需要也不应直接调用三个产品的内部 API。

## 首次授权

先在 `https://mcp.kairusi.com/authorize` 登录并生成 MCP 配置。复制其中 `Authorization` 的 Bearer Token 后，在本地 Skill 目录运行：

```bash
python3 scripts/kairusi_mcp.py configure
python3 scripts/kairusi_mcp.py status
python3 scripts/kairusi_mcp.py list-tools
python3 scripts/kairusi_mcp.py call --tool kairusi_get_version --arguments '{"skill_version":"1.2.3"}'
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
  "cells": [{"title": "今日记录", "content": "今天完成了项目规划", "order_by": 1}]
}'
```

## Todo

```bash
# 读取项目、文件夹和清单
python3 scripts/kairusi_mcp.py call --tool todo_list_projects --arguments '{}'

# 读取现有标签；创建任务前用返回的 UUID 做场景匹配
python3 scripts/kairusi_mcp.py call --tool todo_list_labels --arguments '{}'

# 创建文件夹
python3 scripts/kairusi_mcp.py call --tool todo_create_folder --arguments '{
  "name": "工作"
}'

# 创建清单。image_url 是 Todo 清单图标 ID；放入文件夹时替换 folder_uuid。
python3 scripts/kairusi_mcp.py call --tool todo_create_list --arguments '{
  "name": "本周任务",
  "image_url": "<图标ID>",
  "folder_uuid": "<文件夹UUID>"
}'

# 搜索任务
python3 scripts/kairusi_mcp.py call --tool todo_search_tasks --arguments '{"keyword": "项目规划"}'

# 系统“收件箱”固定存在，禁止新建。需要查看其 UUID 与默认统计时：
python3 scripts/kairusi_mcp.py call --tool todo_get_default_lists --arguments '{}'

# 用户未指定清单时省略 list_uuid，MCP 会通过 project/get_default_pc 的 data.sjx
# 自动写入该用户的系统“收件箱”，不会创建替代清单。
python3 scripts/kairusi_mcp.py call --tool todo_create_task --arguments '{
  "title": "整理项目计划",
  "belong_date": "2026-08-26",
  "label_uuids": ["<匹配出的标签UUID>"]
}'
```

## 日历

```bash
# 读取日历和写入权限
python3 scripts/kairusi_mcp.py call --tool calendar_list_calendars --arguments '{}'

# 搜索日程
python3 scripts/kairusi_mcp.py call --tool calendar_search_events --arguments '{"keyword": "项目"}'

# 创建日程。目标日历必须 can_write=true；时间使用 UTC ISO 8601。
# 时区参数使用 IANA 名称；MCP 会将其转换为旧日历 API 要求的时区对象，禁止原样写入数据库。
# MCP 按官方 event/commit 契约提交，并通过 event/get_events 回查相同 UUID；回查不到时不会报告成功。
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
