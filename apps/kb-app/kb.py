#!/usr/bin/env python3
"""本机使用的 SQLite 知识库。"""

import argparse
import html
import json
import mimetypes
import re
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


APP_DIR = Path(__file__).resolve().parent
DEFAULT_DB = APP_DIR / "kb.db"


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


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class ConflictError(Exception):
    """保存时数据库中的内容已被其他写入修改。"""


class SQLiteStore:
    """SQLite 数据访问层；连接按操作创建，供多线程 HTTP 服务安全使用。"""

    def __init__(self, db_path, migration_dir=None):
        self.db_path = Path(db_path).resolve()
        self.migration_dir = Path(migration_dir).resolve() if migration_dir else self.db_path.parent / "kb_data"
        db_existed = self.db_path.exists()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        if not db_existed:
            imported, _, _ = self.import_directory(self.migration_dir, preserve_mtime=True)
            if imported:
                print(f"已从 kb_data 导入 {imported} 篇", flush=True)

    def connect(self):
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self):
        with self.connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS notes(
                title TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                created TEXT NOT NULL,
                updated TEXT NOT NULL
            )""")

    def list_notes(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT title, updated FROM notes ORDER BY updated DESC, title ASC").fetchall()
        return [dict(row) for row in rows]

    def get_note(self, title):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT title, content, created, updated FROM notes WHERE title = ?", (title,)
            ).fetchone()
        return dict(row) if row else None

    def save(self, title, content, original_content=None, timestamp=None):
        if not valid_title(title):
            raise ValueError("invalid title")
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        now = timestamp or utc_now()
        with self.connect() as connection:
            # 先取得写锁，再重查当前值，避免并发请求绕过冲突检测。
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT content FROM notes WHERE title = ?", (title,)).fetchone()
            if row:
                if row["content"] != content and original_content != row["content"]:
                    raise ConflictError
                connection.execute("UPDATE notes SET content = ?, updated = ? WHERE title = ?", (content, now, title))
            else:
                connection.execute(
                    "INSERT INTO notes(title, content, created, updated) VALUES (?, ?, ?, ?)",
                    (title, content, now, now),
                )

    def search(self, query):
        if not query:
            return []
        with self.connect() as connection:
            rows = connection.execute(
                """SELECT title, content FROM notes
                   WHERE instr(title, ?) > 0 OR instr(content, ?) > 0
                   ORDER BY updated DESC, title ASC""",
                (query, query),
            ).fetchall()
        results = []
        for row in rows:
            content = row["content"]
            content_pos = content.find(query)
            pos = max(content_pos, 0)
            start, end = max(0, pos - 40), min(len(content), pos + len(query) + 40)
            snippet = ("…" if start else "") + content[start:end].replace("\n", " ") + ("…" if end < len(content) else "")
            if not snippet:
                snippet = "标题匹配"
            results.append({"title": row["title"], "snippet": snippet})
        return results

    def import_directory(self, source_dir, preserve_mtime=False):
        source_dir = Path(source_dir)
        imported = skipped = unchanged = 0
        if not source_dir.is_dir():
            return imported, skipped, unchanged
        for path in sorted(source_dir.glob("*.md")):
            if not path.is_file() or not valid_title(path.stem):
                skipped += 1
                continue
            content = path.read_text(encoding="utf-8")
            existing = self.get_note(path.stem)
            if existing:
                if existing["content"] == content:
                    unchanged += 1
                else:
                    skipped += 1
                continue
            timestamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat() if preserve_mtime else None
            self.save(path.stem, content, timestamp=timestamp)
            imported += 1
        return imported, skipped, unchanged

    def export_directory(self, target_dir):
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            rows = connection.execute("SELECT title, content FROM notes ORDER BY title ASC").fetchall()
        for row in rows:
            (target_dir / f"{row['title']}.md").write_text(row["content"], encoding="utf-8")
        return len(rows)

    def backup(self, target_path):
        target_path = Path(target_path).resolve()
        if target_path == self.db_path:
            raise ValueError("备份文件不能与当前数据库相同")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as source, sqlite3.connect(target_path) as target:
            source.backup(target)


class Handler(BaseHTTPRequestHandler):
    store = None
    web_dir = APP_DIR / "web" / "dist"

    def parse_request(self):
        # curl 可直接发送中文 URL；先编码高位字节，避免 Latin-1 控制字符被误判为空白。
        self.raw_requestline = re.sub(rb"[\x80-\xff]", lambda match: f"%{match.group(0)[0]:02X}".encode("ascii"), self.raw_requestline)
        return super().parse_request()

    def parsed_url(self):
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
            self.send_json({"notes": self.store.list_notes()})
        elif parsed.path == "/api/note":
            name = parse_qs(parsed.query).get("name", [""])[0]
            if not name.endswith(".md") or not valid_title(name[:-3]):
                return self.send_error_json(400, "无效的笔记名称")
            note = self.store.get_note(name[:-3])
            if not note:
                return self.send_error_json(404, "笔记不存在")
            self.send_json({"title": note["title"], "content": note["content"], "content_html": render_markdown(note["content"])})
        elif parsed.path == "/api/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self.send_json({"results": self.store.search(query)})
        elif parsed.path.startswith("/api/"):
            self.send_error_json(404, "接口不存在")
        else:
            self.send_static(parsed.path)

    def do_POST(self):
        if self.parsed_url().path != "/api/save":
            return self.send_error_json(404, "接口不存在")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 2 * 1024 * 1024:
                return self.send_error_json(413, "笔记内容过大")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return self.send_error_json(400, "JSON 格式错误")
        title, content = data.get("title"), data.get("content")
        if not valid_title(title):
            return self.send_error_json(400, "标题不能为空，且不能含 /、\\ 或 ..")
        if not isinstance(content, str):
            return self.send_error_json(400, "content 必须是字符串")
        try:
            self.store.save(title, content, data.get("original_content"))
        except ConflictError:
            return self.send_error_json(409, "同名笔记已存在且内容不同")
        self.send_json({"ok": True})

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def parse_args():
    parser = argparse.ArgumentParser(description="本地 Web 知识库")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--export", dest="export_dir", type=Path, metavar="目录")
    actions.add_argument("--import", dest="import_dir", type=Path, metavar="目录")
    actions.add_argument("--backup", dest="backup_file", type=Path, metavar="文件")
    return parser.parse_args()


def main():
    args = parse_args()
    store = SQLiteStore(args.db)
    if args.export_dir:
        count = store.export_directory(args.export_dir)
        print(f"已导出 {count} 篇到 {args.export_dir}")
        return
    if args.import_dir:
        imported, skipped, unchanged = store.import_directory(args.import_dir)
        print(f"导入完成：新增 {imported} 篇，跳过冲突/无效 {skipped} 篇，内容相同 {unchanged} 篇")
        return
    if args.backup_file:
        store.backup(args.backup_file)
        print(f"已备份到 {args.backup_file}")
        return
    Handler.store = store
    address = ("127.0.0.1", args.port)
    print(f"http://127.0.0.1:{args.port}", flush=True)
    try:
        ThreadingHTTPServer(address, Handler).serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
