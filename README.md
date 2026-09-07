# Kairusi Skill

当前版本：`1.2.2`

让 AI 助手通过一个 Kairusi MCP 连接统一管理**日刻日记、Todo 任务和日历日程**，并从用户账号读取已有 Todo 标签，为任务做智能场景化分类。本包同时包含 AI 工作流说明、跨平台 Python 命令行客户端和可复制的命令参考。

## 能力

| 产品 | 主要能力 |
|---|---|
| 日刻 | 读取资源和模板格子标题、查看九宫格日记、创建、更新和删除日记；写入时自动生成符合接口约定的完整格子数据，并回读确认内容真实保存。 |
| Todo | 查看和创建普通文件夹与清单；读取系统固定的“收件箱”与默认统计；读取已有一级、二级标签；搜索、创建、更新、完成和删除任务；按任务语义绑定已有标签。用户未指定清单的事务自动进入系统“收件箱”，绝不新建或替代收件箱。Skill 不创建、修改或删除标签。 |
| 日历 | 查看可写日历、搜索和查看日程、创建、更新和删除日程。 |
| 跨产品 | 在用户明确要求时，将任务安排到日历或根据日程撰写日记。 |

## 安装

### 方式一：从 GitHub 导入

在支持 GitHub Skill 导入的 AI 应用中添加：

```text
https://github.com/zionfusu/kairusi-skill
```

### 方式二：下载本包

下载 ZIP 或 `.skill` 包并解压到 AI 应用的 Skills 目录。保留完整目录结构，特别是 `scripts/` 和 `references/`。

### 方式三：配置远程 MCP

如果 AI 应用支持 MCP，访问 [Kairusi 授权页](https://mcp.kairusi.com/authorize)，选择日刻、Todo 和日历，登录后将生成的 MCP 配置粘贴到应用设置中。

## 首次授权与本地脚本

本包中的 `scripts/kairusi_mcp.py` 支持没有 MCP 设置界面的 AI 应用通过终端调用 Kairusi。需要 Python 3，不依赖第三方包。

```bash
cd kairusi-skill
python3 scripts/kairusi_mcp.py configure
python3 scripts/kairusi_mcp.py list-tools
python3 scripts/kairusi_mcp.py call --tool calendar_list_calendars --arguments '{}'
```

在 `configure` 过程中，从授权页 MCP 配置中复制 Bearer Token。输入不会回显，Token 仅保存在 `~/.config/kairusi-skill/token`，Unix 系统下文件权限为仅当前用户可读写。统一 Kairusi Token 默认有效期为 30 天；若到期，或日刻、Todo、日历中任一产品的登录会话提前失效，请重新访问授权页生成并配置新的 Token。重新授权会撤销该账号此前的 Token；若配置泄露，可用此方式立即失效旧授权，或在授权结果页点击“立即撤销当前授权”。

> 不要把密码、Bearer Token、产品 Session ID 或包含这些信息的终端截图发送给任何人。

## 示例

完成授权后，用户可以对 AI 说：

- “看看我今天有哪些日程。”
- “创建一个工作文件夹，并在里面新建本周任务清单。”
- “在工作清单里创建任务：周五提交项目方案。”
- “创建任务：晚饭后跑步，并从我已有的标签中自动匹配合适标签。”
- “把这个 Todo 任务安排到明天下午三点。”
- “根据今天的日程写一篇日记。”
- “删除测试日程。”

删除操作必须先由 AI 展示具体目标，并获得用户对该目标的明确确认。

## 目录结构

```text
kairusi-skill/
├── SKILL.md                         # AI 工作流与安全规则
├── README.md                        # 用户安装和使用说明
├── LICENSE.md                       # MIT 许可证
├── scripts/
│   └── kairusi_mcp.py               # 统一 MCP 本地客户端
└── references/
    ├── api-commands.md              # 可复制的命令示例
    └── product-mapping.md           # 日刻、Todo、日历工具映射
```

## 隐私与安全

Kairusi Skill 只在用户主动授权后访问数据。Token 存在用户本地，不被脚本输出或上传；所有服务调用都通过 Kairusi HTTPS MCP 地址进行。请只从官方 GitHub 仓库或 SkillHub 安装，审阅脚本后再使用。

## 许可证

本项目采用 MIT License，详见 `LICENSE.md`。

## 1.2.2 升级说明

补齐日刻格子的标题与内容长度，并在写入后回读核验内容；系统“收件箱”改为专用默认清单接口并禁止重复创建。新增 Skill/MCP 版本协商：Skill 启动后上报自身版本，MCP 返回最低与推荐版本；服务器可通过 `node scripts/version-report.mjs` 查看匿名版本分布。

## 1.2.1 升级说明

修复日历创建日程“假成功”的问题。MCP 严格按照接口文档调用统一的 `event/commit`，并使用 `op_type`、`uuid`、`calendarId`、`startDate`、`endDate` 等约定字段；提交后通过 `event/get_events` 回查相同 UUID，只有实际查到新日程才会报告成功。

## 1.2.0 升级说明

本版本修复日刻日记格子写入和日历时区格式，增加 Todo 已有标签的智能场景匹配、未指定清单时自动进入系统“收件箱”，并将统一授权升级为可持久化、可主动撤销的不透明 Token。升级 MCP 服务后，旧格式 Token 会立即失效，用户需要重新授权一次。
