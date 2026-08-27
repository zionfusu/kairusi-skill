# Kairusi Skill

让 AI 助手通过一个 Kairusi MCP 连接统一管理**日刻日记、Todo 任务和日历日程**。本包同时包含 AI 工作流说明、跨平台 Python 命令行客户端和可复制的命令参考。

## 能力

| 产品 | 主要能力 |
|---|---|
| 日刻 | 读取资源、查看九宫格日记、创建、更新和删除日记。 |
| Todo | 查看项目和清单、搜索任务、创建、更新、完成和删除任务。 |
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

在 `configure` 过程中，从授权页 MCP 配置中复制 Bearer Token。输入不会回显，Token 仅保存在 `~/.config/kairusi-skill/token`，Unix 系统下文件权限为仅当前用户可读写。统一 Kairusi Token 默认有效期为 30 天；若到期，或日刻、Todo、日历中任一产品的登录会话提前失效，请重新访问授权页生成并配置新的 Token。

> 不要把密码、Bearer Token、产品 Session ID 或包含这些信息的终端截图发送给任何人。

## 示例

完成授权后，用户可以对 AI 说：

- “看看我今天有哪些日程。”
- “在工作清单里创建任务：周五提交项目方案。”
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
