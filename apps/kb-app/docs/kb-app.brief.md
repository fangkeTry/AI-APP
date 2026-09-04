# 任务简报：本地 Web 知识库小站（kb-app）

> 生成方：dsh 设计（2026-09-04）｜执行方：codex（`scripts/codex-run.sh`）
> 用法：`scripts/codex-run.sh docs/tasks/kb-app.brief.md`

## 1. 背景与设计

用最小代码搭一个**本机使用的 Web 知识库小站**，用来验证「dsh 设计 → codex 实现 → dsh 评审」接力闭环。用户已确认形态：本地 Web 页面；数据：管理自己的 markdown 笔记（不索引现有目录）。

**技术选型（求最简单，已定，不要改）**：
- 语言/依赖：**Python 3 标准库单文件**（`http.server`），**零第三方依赖**。
- 结构：`kb-app/kb.py` 一个文件（内嵌 HTML/JS 前端字符串 + HTTP API）；笔记落盘 `kb-app/kb_data/<标题>.md`（UTF-8，目录不存在则自动创建）。
- 只监听 `127.0.0.1`（本机工具，无鉴权、无跨域）。
- markdown 渲染：实现**常用子集**即可（标题 #/##/###、代码围栏、行内代码、加粗、无序列表、链接、段落），其他语法原样显示文本。
- 搜索：对笔记内容做**简单子串匹配**（不引入评分/分词），返回命中笔记的标题 + 第一处命中的上下文摘要（前后各 ~40 字符）。
- 文件名即标题：保存/重名策略见需求 R5。

## 2. 目标与范围

- 目标：浏览器打开即可 ① 看笔记列表 ② 新建/编辑笔记 ③ 看渲染后的正文 ④ 关键词搜索。
- 范围外（明确不做）：用户系统、标签分类、富文本编辑器、导入导出、多端同步、全文评分排序、markdown 全语法支持。

## 3. 需求清单

- [ ] R1 启动：`python3 kb.py [--port 8787] [--dir kb_data]`，默认端口 8787；启动后打印 `http://127.0.0.1:8787`。仅绑定 127.0.0.1。
- [ ] R2 首页（GET /）：返回内嵌的单页 HTML（中文界面），无需外部资源。
- [ ] R3 笔记列表：GET `/api/list` → `{"notes":[{"title":"…","updated":"ISO时间"}]}`，按更新时间倒序。
- [ ] R4 读取正文：GET `/api/note?name=<标题.md>` → `{"title":"…","content_html":"渲染后的 HTML"}`；文件不存在返回 404 JSON。
- [ ] R5 保存：POST `/api/save`（JSON：`{"title":"…","content":"…"}`）→ 写入 `kb_data/<标题>.md`。若同名已存在且内容不同则返回 409（不静默覆盖）；同名同内容返回 200 幂等。标题不允许为空、不允许含 `/` 或 `..`（防路径穿越，服务端必须校验）。
- [ ] R6 新建入口：前端「新建笔记」输入标题 → 打开编辑区（内容 textarea）→「保存」调 R5。已存在标题走「编辑」。
- [ ] R7 编辑入口：点列表项 → 展示渲染正文 + 「编辑」按钮 → 切到 textarea（载入原始 markdown）→ 保存。
- [ ] R8 搜索：GET `/api/search?q=关键词` → `{"results":[{"title":"…","snippet":"…上下文…"}]}`；q 为空返回空数组。
- [ ] R9 数据持久：`kb_data/` 下每个笔记一个 `.md` 文件，进程重启后列表与内容不丢。

## 4. 涉及文件

- 新增：`kb-app/kb.py`（唯一代码文件，目标 ≤ 400 行含内嵌 HTML）
- 新增：`kb-app/.gitignore`（内容：`kb_data/`）
- 运行期自动生成（不要手工创建提交）：`kb-app/kb_data/` 与其中的笔记
- 禁止改动：本仓库其他任何文件（scripts/、docs/、简历等一律不动）

## 5. 验收标准（codex 必须实际执行并贴结果）

```bash
cd /home/fangke/dsh-test/kb-app
python3 -m py_compile kb.py && echo "语法 OK"
python3 kb.py --port 8787 >/tmp/kb.log 2>&1 &
sleep 1
curl -s http://127.0.0.1:8787/api/list                 # 期望 {"notes": []}（或仅含已有笔记）
curl -s -X POST http://127.0.0.1:8787/api/save -H 'Content-Type: application/json' \
  -d '{"title":"测试笔记","content":"# 你好\n\n这是**知识库**测试。\n\n- 列表项一"}'   # 期望 {"ok":true}
curl -s http://127.0.0.1:8787/api/note?name=测试笔记.md   # 期望 content_html 含 <h1> 与 <strong>
curl -s 'http://127.0.0.1:8787/api/search?q=知识库'       # 期望命中 测试笔记
kill %1
python3 kb.py --port 8787 >/tmp/kb2.log 2>&1 & sleep 1
curl -s http://127.0.0.1:8787/api/list                   # 重启后 测试笔记 仍在
kill %1
```

另请手动确认：浏览器打开首页能完成 新建→保存→列表可见→点开渲染正常→搜索命中（可用 curl 代替手动并说明）。

## 6. 硬性约束

- 不得执行 `git commit` / `git push`（提交与检查点由 dsh 侧统一处理）。
- 仅新增第 4 节列出的两个文件；不得改动/新增依赖；不得改动仓库其他文件。
- 必须使用 Python 3 标准库，零第三方依赖。
- 所有文件读写 UTF-8；文件名/路径处理必须防路径穿越（服务端校验，不能只靠前端）。
- 编码风格：清晰、注释用中文简要说明关键点；优先简单直白，不要过度设计。

## 7. 输出要求（回报给 dsh）

- 新增了哪些文件、`kb.py` 行数。
- 第 5 节验收命令的实际输出（逐条贴）。
- 浏览器手动验证结果。
- 遗留问题 / 需要 dsh 决策的点。
