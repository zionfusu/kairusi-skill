#!/usr/bin/env python3
"""Kairusi MCP 的本地命令行客户端。

保存的 Bearer Token 仅存放在用户主目录，脚本不会输出 Token。
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_SERVER = "https://mcp.kairusi.com/mcp"
SKILL_VERSION = "1.2.3"
CONFIG_DIR = Path(os.environ.get("KAIRUSI_SKILL_HOME", "~/.config/kairusi-skill")).expanduser()
TOKEN_FILE = CONFIG_DIR / "token"
SERVER_FILE = CONFIG_DIR / "server"


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    raise SystemExit(code)


def load_config() -> tuple[str, str]:
    if not TOKEN_FILE.exists():
        fail("未授权。请先访问 https://mcp.kairusi.com/authorize 获取配置，然后运行 configure 保存 Bearer Token。")
    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not token:
        fail("本地 Token 为空。请重新运行 configure。")
    server = SERVER_FILE.read_text(encoding="utf-8").strip() if SERVER_FILE.exists() else DEFAULT_SERVER
    return token, server.rstrip("/")


def write_private(path: Path, value: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + "\n", encoding="utf-8")
    if os.name != "nt":
        os.chmod(path, 0o600)


def configure(args: argparse.Namespace) -> None:
    server = args.server.rstrip("/") if args.server else DEFAULT_SERVER
    print("请从 Kairusi 授权页生成的 MCP 配置中复制 Bearer 后面的 Token。")
    token = getpass.getpass("Bearer Token（输入不回显）: ").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if len(token) < 20:
        fail("Token 格式无效，未保存任何内容。")
    write_private(TOKEN_FILE, token)
    write_private(SERVER_FILE, server)
    print(json.dumps({"ok": True, "message": "Kairusi MCP 已授权", "server": server, "token": "已安全保存"}, ensure_ascii=False))


def http_json(url: str, body: dict[str, Any], token: str, session_id: str | None = None) -> tuple[dict[str, Any], dict[str, str]]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {token}",
        "X-Kairusi-Skill-Version": SKILL_VERSION,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            response_headers = {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
            message = detail.get("error", {}).get("message") or detail.get("message") or raw
        except json.JSONDecodeError:
            message = raw or f"HTTP {exc.code}"
        fail(f"Kairusi MCP 请求失败：{message}", exc.code)
    except URLError as exc:
        fail(f"无法连接 Kairusi MCP：{exc.reason}")

    try:
        return json.loads(raw), response_headers
    except json.JSONDecodeError:
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip()), response_headers
        fail("MCP 返回了无法解析的响应。")


def initialize(token: str, server: str) -> str:
    response, headers = http_json(server, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "kairusi-skill", "version": SKILL_VERSION},
        },
    }, token)
    if "error" in response:
        fail(response["error"].get("message", "MCP 初始化失败。"))
    session_id = headers.get("mcp-session-id")
    if not session_id:
        fail("MCP 初始化成功但没有返回会话 ID。")
    return session_id


def call_method(method: str, params: dict[str, Any]) -> dict[str, Any]:
    token, server = load_config()
    session_id = initialize(token, server)
    response, _ = http_json(server, {"jsonrpc": "2.0", "id": 2, "method": method, "params": params}, token, session_id)
    if "error" in response:
        fail(response["error"].get("message", "MCP 请求失败。"))
    return response.get("result", {})


def list_tools(_: argparse.Namespace) -> None:
    result = call_method("tools/list", {})
    tools = [{"name": item.get("name"), "description": item.get("description")} for item in result.get("tools", [])]
    print(json.dumps({"ok": True, "tools": tools}, ensure_ascii=False, indent=2))


def call_tool(args: argparse.Namespace) -> None:
    try:
        arguments = json.loads(args.arguments)
    except json.JSONDecodeError as exc:
        fail(f"--arguments 必须是 JSON 对象：{exc}")
    if not isinstance(arguments, dict):
        fail("--arguments 必须是 JSON 对象。")
    result = call_method("tools/call", {"name": args.tool, "arguments": arguments})
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False, indent=2))


def status(_: argparse.Namespace) -> None:
    if not TOKEN_FILE.exists():
        print(json.dumps({"ok": False, "authorized": False, "server": DEFAULT_SERVER}, ensure_ascii=False))
        return
    server = SERVER_FILE.read_text(encoding="utf-8").strip() if SERVER_FILE.exists() else DEFAULT_SERVER
    print(json.dumps({"ok": True, "authorized": True, "server": server, "skill_version": SKILL_VERSION, "token": "已保存，不显示"}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Kairusi MCP 本地客户端")
    sub = parser.add_subparsers(dest="command", required=True)

    configure_parser = sub.add_parser("configure", help="交互式保存 Kairusi Bearer Token")
    configure_parser.add_argument("--server", default=DEFAULT_SERVER, help="MCP 地址")
    configure_parser.set_defaults(func=configure)

    status_parser = sub.add_parser("status", help="查看授权状态，不显示 Token")
    status_parser.set_defaults(func=status)

    tools_parser = sub.add_parser("list-tools", help="列出日刻、Todo 与日历工具")
    tools_parser.set_defaults(func=list_tools)

    call_parser = sub.add_parser("call", help="调用一个 Kairusi MCP 工具")
    call_parser.add_argument("--tool", required=True, help="工具名，例如 calendar_list_calendars")
    call_parser.add_argument("--arguments", default="{}", help="JSON 参数对象")
    call_parser.set_defaults(func=call_tool)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
