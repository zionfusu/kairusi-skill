# Kairusi 产品映射

当需要确认工具选择、字段或权限语义时读取本文件。以运行时 MCP 返回的工具 schema 为最终准则。

## 统一授权

用户在 `https://mcp.kairusi.com/authorize` 选择日刻、Todo 和日历后，会生成一份统一 MCP 配置。若某一产品未被勾选或会话失效，其命名空间工具会要求重新授权。不要要求用户提供密码、会话 ID 或 Bearer Token。

| 工具前缀 | 产品 | 管理对象 |
|---|---|---|
| `rike_` | 日刻 | 日记本、模板、标签、九宫格日记 |
| `todo_` | Todo | 项目、清单、任务、子任务 |
| `calendar_` | 日历 | 日历、日程、提醒、重复规则 |

## 日刻

先用 `rike_list_resources` 获取日记本、模板和标签 UUID。日记单元格包含内容和从 1 开始的排序；更新日记时保留现有单元格 UUID。读取日记使用 `rike_list_notes` 与 `rike_get_note_detail`，写入使用 `rike_create_note`、`rike_update_note`，删除使用 `rike_delete_note`。

## Todo

先用 `todo_list_projects` 获取清单 UUID。读取任务使用 `todo_list_tasks` 或 `todo_search_tasks`；创建和修改任务使用 `todo_create_task`、`todo_update_task`；完成状态使用 `todo_set_task_completed`。删除使用 `todo_delete_task`，必须在用户明确确认后设置 `confirmed: true`。

## 日历

先用 `calendar_list_calendars` 获取日历 UUID 与 `can_write` 权限。仅当 `can_write` 为 true 时才可写入。读取或搜索日程使用 `calendar_list_events` 和 `calendar_search_events`；创建和修改使用 `calendar_create_event`、`calendar_update_event`。删除使用 `calendar_delete_event`，必须先核对目标标题和开始时间，再取得用户明确确认。

日程范围查询使用 UTC ISO 8601 时间，并传入用户的 IANA 时区。个人日历、公共日历、所有者或参与者身份本身不等同于写入权限。

## 统一安全规则

创建、更新和完成状态变更必须来自用户明确意图。删除日记、任务或日程前，始终先读取或搜索目标，并向用户展示名称与日期/时间后请求确认。不要因“清理”“删旧的”等模糊措辞执行删除或跨产品同步。
