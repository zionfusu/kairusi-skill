# Kairusi 产品映射

当需要确认工具选择、字段或权限语义时读取本文件。以运行时 MCP 返回的工具 schema 为最终准则。

## 统一授权

用户在 `https://mcp.kairusi.com/authorize` 选择日刻、Todo 和日历后，会生成一份统一 MCP 配置。若某一产品未被勾选或会话失效，其命名空间工具会要求重新授权。不要要求用户提供密码、会话 ID 或 Bearer Token。

| 工具前缀 | 产品 | 管理对象 |
|---|---|---|
| `rike_` | 日刻 | 日记本、模板、标签、九宫格日记 |
| `todo_` | Todo | 项目、清单、已有标签、任务、子任务 |
| `calendar_` | 日历 | 日历、日程、提醒、重复规则 |

## 日刻

先用 `rike_list_resources` 获取日记本、模板和标签 UUID。日记单元格包含内容和从 1 开始的排序；更新日记时保留现有单元格 UUID。写入 `note/commit` 时，`childs` 必须是 JSON 字符串，其中每项包含 `note_child_uuid`、`note_uuid`、`order_by`、`content`、`content_h5`、`content_h5_noimg`；MCP 转换层负责补齐这些字段。读取日记使用 `rike_list_notes` 与 `rike_get_note_detail`，写入使用 `rike_create_note`、`rike_update_note`，删除使用 `rike_delete_note`。接口依据：[提交日记](https://docapi.kairusi.com/web/#/14/733)。

## Todo

先用 `todo_list_projects` 获取文件夹与清单结构。系统“收件箱”固定存在，使用 `todo_get_default_lists` 调用 `POST project/get_default_pc`，从响应 `data.sjx` 取得并规范化为 `inbox.list_uuid`，同时返回其余今日、已计划、已完成、已标注等统计。绝不创建“收件箱”或替代收件箱；`todo_create_list` 也会在调用上游前拒绝该名称。创建文件夹使用 `todo_create_folder`，返回的 `folder_uuid` 可用于后续创建普通清单；创建普通清单使用 `todo_create_list`，必须提供 `image_url` 图标 ID，可选传入 `folder_uuid`、`review_freq` 和 `next_review_date`。不要把文件夹 UUID 当成任务所需的清单 UUID。

读取任务使用 `todo_list_tasks` 或 `todo_search_tasks`；创建和修改任务使用 `todo_create_task`、`todo_update_task`。创建任务时 `list_uuid` 可选：用户未指定清单时必须省略，由 MCP 调用 `project/get_default_pc` 并从 `data.sjx` 使用系统收件箱的真实 UUID；不得使用普通清单列表猜测、固定 UUID或创建替代清单。写任务前用 `todo_list_labels` 获取真实标签 UUID，再把场景匹配结果作为 `label_uuids` 传入；更新时该字段表示完整替换列表。完成状态使用 `todo_set_task_completed`。删除使用 `todo_delete_task`，必须在用户明确确认后设置 `confirmed: true`。

标签仅通过 `todo_list_labels` 读取，对应 `POST /label/get_label_list`，返回一级标签及其 `list` 二级标签。Skill 只能从这些已有标签中选择 UUID 并绑定到任务，不提供标签新增、修改或删除能力。接口依据：[标签列表](https://docapi.kairusi.com/web/#/10/410)。

## 日历

先用 `calendar_list_calendars` 获取日历 UUID 与 `can_write` 权限。仅当 `can_write` 为 true 时才可写入。读取或搜索日程使用 `calendar_list_events` 和 `calendar_search_events`；创建和修改使用 `calendar_create_event`、`calendar_update_event`。删除使用 `calendar_delete_event`，必须先核对目标标题和开始时间，再取得用户明确确认。

日程范围查询使用 UTC ISO 8601 时间，并按接口约定把用户的 IANA 时区作为 `zone` 传入。日程新增、修改和删除统一调用 `POST /event/commit`，通过 `op_type` 区分操作，并使用 `uuid`、`calendarId`、`startDate`、`endDate` 等 camelCase 字段。创建和更新工具接收 IANA 时区名称；MCP 转换层必须把它转换为旧日历 API 约定的时区对象，不能把裸字符串直接写入 `startDateZone` 或 `endDateZone`。新增提交后必须通过 `event/get_events` 回查相同 UUID，确认事件真实存在后才可报告成功。接口依据：[新建/编辑/删除日程](https://docapi.kairusi.com/web/#/12/528)、[我的日程列表-pc](https://docapi.kairusi.com/web/#/12/577)。个人日历、公共日历、所有者或参与者身份本身不等同于写入权限。

## 统一安全规则

创建、更新和完成状态变更必须来自用户明确意图。删除日记、任务或日程前，始终先读取或搜索目标，并向用户展示名称与日期/时间后请求确认。不要因“清理”“删旧的”等模糊措辞执行删除或跨产品同步。
