#!/usr/bin/env python3
"""本机使用的单文件 Markdown 知识库。"""

import argparse
import html
import json
import mimetypes
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def valid_title(title):
    return isinstance(title, str) and bool(title.strip()) and "/" not in title and "\\" not in title and ".." not in title and "\x00" not in title


def inline(text):
    """先转义，再渲染少量安全的行内语法。"""
    parts = re.split(r"(`[^`\n]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            out.append("<code>" + html.escape(part[1:-1]) + "</code>")
            continue
        part = html.escape(part)
        part = re.sub(r"\[([^]\n]+)\]\(([^)\s]+)\)", safe_link, part)
        part = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", part)
        out.append(part)
    return "".join(out)


def safe_link(match):
    label, url = match.groups()
    if not re.match(r"^(https?://|mailto:)", html.unescape(url), re.I):
        url = "#"
    return '<a href="{}" rel="noopener noreferrer">{}</a>'.format(url, label)


def render_markdown(source):
    lines, output, paragraph = source.splitlines(), [], []
    in_code, code_lines, in_list = False, [], False

    def flush_paragraph():
        if paragraph:
            output.append("<p>" + inline("\n".join(paragraph)).replace("\n", "<br>") + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for line in lines:
        if line.startswith("```"):
            if in_code:
                output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
            else:
                flush_paragraph(); close_list()
            in_code = not in_code
        elif in_code:
            code_lines.append(line)
        elif re.match(r"^#{1,3} ", line):
            flush_paragraph(); close_list(); level = len(line) - len(line.lstrip("#"))
            output.append(f"<h{level}>" + inline(line[level + 1:]) + f"</h{level}>")
        elif re.match(r"^[-*] ", line):
            flush_paragraph()
            if not in_list:
                output.append("<ul>"); in_list = True
            output.append("<li>" + inline(line[2:]) + "</li>")
        elif not line.strip():
            flush_paragraph(); close_list()
        else:
            close_list(); paragraph.append(line)
    if in_code:
        output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    flush_paragraph(); close_list()
    return "\n".join(output)


class Handler(BaseHTTPRequestHandler):
    data_dir = Path("kb_data")
    web_dir = Path(__file__).resolve().parent / "web" / "dist"

    def parse_request(self):
        # curl 可直接发送中文 URL；先编码高位字节，避免 Latin-1 控制字符被误判为空白。
        self.raw_requestline = re.sub(
            rb"[\x80-\xff]",
            lambda match: f"%{match.group(0)[0]:02X}".encode("ascii"),
            self.raw_requestline,
        )
        return super().parse_request()

    def parsed_url(self):
        # curl 可直接发送中文 URL；http.server 会先按 Latin-1 解读请求行。
        try:
            request_path = self.path.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            request_path = self.path
        return urlparse(request_path)

    def send_json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json({"error": message}, status)

    def send_static(self, request_path):
        """只从构建目录读取文件；SPA 子路径回退到 index.html。"""
        if not self.web_dir.is_dir():
            body = "前端尚未构建，请先在 web 目录运行 npm run build。".encode("utf-8")
            self.send_response(503); self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            return
        relative = request_path.lstrip("/") or "index.html"
        target = (self.web_dir / relative).resolve()
        try:
            target.relative_to(self.web_dir.resolve())
        except ValueError:
            return self.send_error_json(404, "文件不存在")
        if not target.is_file():
            target = self.web_dir / "index.html"
        body = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self.send_response(200); self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        parsed = self.parsed_url()
        if parsed.path == "/api/list":
            notes = [{"title": p.stem, "updated": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()} for p in self.data_dir.glob("*.md") if p.is_file()]
            notes.sort(key=lambda n: n["updated"], reverse=True); self.send_json({"notes": notes})
        elif parsed.path == "/api/note":
            name = parse_qs(parsed.query).get("name", [""])[0]
            if not name.endswith(".md") or not valid_title(name[:-3]):
                return self.send_error_json(400, "无效的笔记名称")
            path = self.data_dir / name
            if not path.is_file(): return self.send_error_json(404, "笔记不存在")
            content = path.read_text(encoding="utf-8")
            self.send_json({"title": path.stem, "content": content, "content_html": render_markdown(content)})
        elif parsed.path == "/api/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            results = []
            if query:
                for path in self.data_dir.glob("*.md"):
                    content = path.read_text(encoding="utf-8")
                    title_pos, content_pos = path.stem.find(query), content.find(query)
                    if title_pos >= 0 or content_pos >= 0:
                        pos = max(content_pos, 0)
                        start, end = max(0, pos - 40), min(len(content), pos + len(query) + 40)
                        snippet = ("…" if start else "") + content[start:end].replace("\n", " ") + ("…" if end < len(content) else "")
                        if not snippet: snippet = "标题匹配"
                        results.append({"title": path.stem, "snippet": snippet})
            self.send_json({"results": results})
        elif parsed.path.startswith("/api/"):
            self.send_error_json(404, "接口不存在")
        else:
            self.send_static(parsed.path)

    def do_POST(self):
        if self.parsed_url().path != "/api/save": return self.send_error_json(404, "接口不存在")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 2 * 1024 * 1024: return self.send_error_json(413, "笔记内容过大")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return self.send_error_json(400, "JSON 格式错误")
        title, content = data.get("title"), data.get("content")
        if not valid_title(title): return self.send_error_json(400, "标题不能为空，且不能含 /、\\ 或 ..")
        if not isinstance(content, str): return self.send_error_json(400, "content 必须是字符串")
        path = self.data_dir / (title + ".md")
        if path.exists():
            old = path.read_text(encoding="utf-8")
            if old != content and data.get("original_content") != old:
                return self.send_error_json(409, "同名笔记已存在且内容不同")
        path.write_text(content, encoding="utf-8"); self.send_json({"ok": True})

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser(description="本地 Web 知识库")
    parser.add_argument("--port", type=int, default=8787); parser.add_argument("--dir", default="kb_data")
    args = parser.parse_args(); Handler.data_dir = Path(args.dir); Handler.data_dir.mkdir(parents=True, exist_ok=True)
    address = ("127.0.0.1", args.port); print(f"http://127.0.0.1:{args.port}", flush=True)
    try: ThreadingHTTPServer(address, Handler).serve_forever()
    except KeyboardInterrupt: pass


if __name__ == "__main__":
    main()
