#!/usr/bin/env python3
"""本机使用的单文件 Markdown 知识库。"""

import argparse
import html
import json
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PAGE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>本地知识库</title><style>
body{font:16px/1.6 system-ui,sans-serif;max-width:1050px;margin:auto;padding:20px;color:#202124}button,input,textarea{font:inherit}header{display:flex;gap:10px;align-items:center;flex-wrap:wrap}header input{flex:1;min-width:220px;padding:7px}main{display:grid;grid-template-columns:280px 1fr;gap:28px;margin-top:20px}aside{border-right:1px solid #ddd;padding-right:18px}.item{display:block;width:100%;text-align:left;border:0;background:none;padding:8px;cursor:pointer}.item:hover{background:#f2f4f7}.muted{color:#666;font-size:.85em}textarea{box-sizing:border-box;width:100%;min-height:430px;padding:10px}pre{overflow:auto;background:#f5f5f5;padding:12px}code{background:#f5f5f5;padding:2px 4px}pre code{padding:0}.actions{display:flex;gap:8px;margin:10px 0}.error{color:#b00020}@media(max-width:700px){main{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid #ddd}}
</style></head><body>
<header><h1>本地知识库</h1><input id="search" placeholder="搜索笔记内容"><button id="new">新建笔记</button></header>
<main><aside><h2 id="sideTitle">笔记</h2><div id="list"></div></aside><section id="view"><p class="muted">从左侧选择笔记，或新建一篇。</p></section></main>
<script>
const list=document.querySelector('#list'), view=document.querySelector('#view'), search=document.querySelector('#search');
let current=null, original='';
async function api(url,options){const r=await fetch(url,options), data=await r.json();if(!r.ok)throw new Error(data.error||'请求失败');return data}
function button(text,fn){const b=document.createElement('button');b.textContent=text;b.onclick=fn;return b}
async function refresh(){const d=await api('/api/list');document.querySelector('#sideTitle').textContent='笔记';list.replaceChildren();for(const n of d.notes){const b=button(n.title,()=>openNote(n.title));b.className='item';const t=document.createElement('div');t.className='muted';t.textContent=new Date(n.updated).toLocaleString();b.append(t);list.append(b)}}
async function openNote(title){try{const d=await api('/api/note?name='+encodeURIComponent(title+'.md'));current=d.title;original=d.content;const h=document.createElement('h2');h.textContent=d.title;const a=document.createElement('div');a.className='actions';a.append(button('编辑',()=>editor(d.title,d.content)));const body=document.createElement('article');body.innerHTML=d.content_html;view.replaceChildren(h,a,body)}catch(e){showError(e)}}
function editor(title='',content=''){current=title||null;original=content;const h=document.createElement('h2');h.textContent=title?'编辑：'+title:'新建笔记';const ta=document.createElement('textarea');ta.value=content;const a=document.createElement('div');a.className='actions';a.append(button('保存',()=>save(title,ta.value)),button('取消',()=>title?openNote(title):view.replaceChildren()));view.replaceChildren(h,a,ta);ta.focus()}
async function save(title,content){if(!title){title=prompt('请输入标题：')||''}try{await api('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,content,original_content:current===title?original:undefined})});await refresh();await openNote(title)}catch(e){showError(e)}}
function showError(e){const p=document.createElement('p');p.className='error';p.textContent=e.message;view.prepend(p)}
document.querySelector('#new').onclick=()=>{const title=prompt('请输入新笔记标题：');if(title)editor(title,'')};
let timer;search.oninput=()=>{clearTimeout(timer);timer=setTimeout(doSearch,200)};
async function doSearch(){const q=search.value;const d=await api('/api/search?q='+encodeURIComponent(q));document.querySelector('#sideTitle').textContent=q?'搜索结果':'笔记';if(!q)return refresh();list.replaceChildren();for(const x of d.results){const b=button(x.title,()=>openNote(x.title));b.className='item';const s=document.createElement('div');s.className='muted';s.textContent=x.snippet;b.append(s);list.append(b)}}
refresh().catch(showError);
</script></body></html>'''


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
    # 仅放行常见外链协议，避免渲染出 javascript: 链接。
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
    if in_code:  # 未闭合围栏仍按代码显示
        output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    flush_paragraph(); close_list()
    return "\n".join(output)


class Handler(BaseHTTPRequestHandler):
    data_dir = Path("kb_data")

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

    def do_GET(self):
        parsed = self.parsed_url()
        if parsed.path == "/":
            body = PAGE.encode("utf-8"); self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body)
        elif parsed.path == "/api/list":
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
                    content = path.read_text(encoding="utf-8"); pos = content.find(query)
                    if pos >= 0:
                        start, end = max(0, pos - 40), min(len(content), pos + len(query) + 40)
                        snippet = ("…" if start else "") + content[start:end].replace("\n", " ") + ("…" if end < len(content) else "")
                        results.append({"title": path.stem, "snippet": snippet})
            self.send_json({"results": results})
        else:
            self.send_error_json(404, "接口不存在")

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
