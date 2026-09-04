# kb-app — 本地 Web 知识库小站

> 建立：2026-09-04（「dsh 设计 → codex 实现 → dsh 评审」闭环第 1 个交付物）
> 技术：前端 React 18 + Vite + TypeScript + Tailwind（`web/`，样式 token 拷贝自 `packages/ui-reference/design-tokens.json`）；服务端 Python 3 标准库零依赖（`kb.py`，SQLite 存储 + JSON API + 前端静态托管）。
> 一键启动：`./start.sh`（详见下文「启动方式」）。
> 设计简报：`docs/kb-app.brief.md`（初版）、`docs/rebuild-frontend.brief.md`（前端重做 pilot）；前端细节另见 `web/README.md`。

## 启动方式

### 方式一：一键启动（推荐）

```bash
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app
./start.sh            # 默认端口 8787 → http://127.0.0.1:8787
PORT=9000 ./start.sh  # 换端口
```

脚本幂等处理全部前置：`web/node_modules` 缺失自动 `npm install`；`web/dist` 缺失或源码比产物新自动 `npm run build`；然后拉起 `kb.py` 托管 `web/dist` + `/api` 文件 API。需要强制重建前端时先删除 `web/dist`。

手动分步（脚本内部逻辑，备查/排障）：

```bash
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app/web
npm install          # 仅首次 / 依赖变更后
npm run build        # 前端源码有改动时必须先重新构建
cd ..
python3 kb.py --port 8787
```

浏览器打开 <http://127.0.0.1:8787>。

- 服务仅监听 `127.0.0.1`，本机工具无鉴权。
- Python 服务托管 `web/dist` 静态产物并提供 `/api/*`；主数据文件固定为本目录的 `kb.db`，从任意工作目录启动均一致。
- 首次启动发现 `kb.db` 尚不存在时，会自动导入同目录 `kb_data/*.md`；原文件保留且之后不再由服务读写。
- 若 `web/dist` 未构建，首页返回 503 提示"请先在 web 目录运行 npm run build"。

### 方式二：开发模式（Vite 热更新）

```bash
# 终端 1：后端（提供 /api 与数据读写）
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app
python3 kb.py --port 8787

# 终端 2：前端 dev server（/api 自动代理到 127.0.0.1:8787）
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app/web
npm run dev
```

浏览器打开 Vite 提示的地址（默认 <http://127.0.0.1:5173>），改 `web/src/` 即时生效。

### 方式三：仅后端 API（不起前端）

```bash
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app
python3 kb.py --port 8787 --db /tmp/kb-test.db
# curl 直接测接口，见下方「HTTP 接口」
```

### 验收自测（改动后快速回归）

```bash
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app
python3 kb.py --port 8787 &   # 记下 PID，测完 kill
curl -s http://127.0.0.1:8787/ | grep -i '<div id="root"'          # React 入口
curl -s -X POST http://127.0.0.1:8787/api/save -H 'Content-Type: application/json' \
  -d '{"title":"测试笔记","content":"# 标题"}'                        # {"ok":true}
curl -s 'http://127.0.0.1:8787/api/search?q=标题'                    # 命中测试笔记
# 测完：kill <PID>；验收建议用 --db 指向临时数据库（防自匹配勿用 pkill -f）
```

## 数据形态与导入导出

`kb.db` 是唯一主存储，使用 SQLite WAL 模式和事务保证写入原子性。`kb_data/*.md` 仅作为旧数据首次迁移源；Markdown 也可通过 CLI 批量导入或导出，不再作为运行时真源。

```bash
python3 kb.py --export /tmp/kb-export       # 全量导出为 UTF-8 Markdown
python3 kb.py --import /tmp/kb-import       # 只新增；同名异内容跳过，不覆盖
python3 kb.py --db /tmp/other.db --export /tmp/other-export
```

`--export`、`--import`、`--backup` 三个动作互斥；未指定动作时启动服务。`--db` 可为每种模式指定数据库，默认路径始终是 `apps/kb-app/kb.db`。

## 备份与恢复

服务运行时推荐使用 SQLite backup API，它能生成事务一致的单文件快照，无需停服：

```bash
python3 kb.py --backup /tmp/kb-backup.db
python3 -c 'import sqlite3; c=sqlite3.connect("/tmp/kb-backup.db"); print(c.execute("PRAGMA integrity_check").fetchone()[0])'
```

也可在服务停止后直接复制 `kb.db`。恢复数据库时先停止服务，将备份文件复制回 `apps/kb-app/kb.db` 后重启；若只有 Markdown 导出，则移走或另存现有数据库后执行导入：

```bash
# 数据库恢复演练（使用临时目标，不触碰正式数据）
python3 kb.py --db /tmp/kb-restore.db --backup /tmp/kb-restore-copy.db
python3 -c 'import sqlite3; c=sqlite3.connect("/tmp/kb-restore-copy.db"); print(c.execute("PRAGMA integrity_check").fetchone()[0])'

# Markdown 恢复到一个新数据库
python3 kb.py --db /tmp/kb-from-md.db --import /tmp/kb-export
```

## 功能

列表（桌面左右分栏 / 移动单列）/ 新建 / 编辑 / markdown 渲染（服务端出 HTML）/ 关键词搜索（标题或正文子串命中，带上下文摘要）；Light（Apple 蓝白）/ Dark（护眼低饱和蓝）跟随系统 + 手动切换（记忆在 localStorage）。

## HTTP 接口

| 接口 | 说明 |
|---|---|
| `GET /`（及任意非 API 路径） | React 单页应用（SPA，子路径回退 index.html）；未构建时 503 |
| `GET /api/list` | 笔记列表，按更新时间倒序 |
| `GET /api/note?name=<标题>.md` | 返回原始 markdown + 渲染 HTML；不存在 404 |
| `POST /api/save` | JSON `{title, content, original_content?}`；同名内容不同且无 original_content 时 409 |
| `GET /api/search?q=` | 子串搜索（标题或正文），返回标题 + 上下文摘要 |
| 其他 `/api/*` | 404 `{"error":"接口不存在"}` |

## 安全与运行边界

- 标题服务端校验：非空、不含 `/`、`\`、`..`、`\x00`（防路径穿越）。
- HTML 全部经 `html.escape` 后仅放行有限行内语法；链接协议白名单 `https?://`、`mailto:`。
- 单笔记 2MB 上限（413）。
- 静态托管只从 `web/dist` 读文件（路径解析后校验在目录内），防目录穿越。
- 本地单机服务只监听 `127.0.0.1`，因此鉴权、TLS、限流在当前档位 N/A；若改为对外或多人服务，必须先补齐这些能力。

## 开发记录 / 已知问题

### 2026-09-04：端口 8787 被占用（Address already in use）

**现象**：验收测试后用户运行 `python3 kb.py` 报 `OSError: [Errno 98] Address already in use`。

**根因**：验收测试用 `python3 kb.py --port 8787 &` 启动的服务进程在测试命令所在 shell 退出后**仍然存活**，
未被清理；且清理时用的 `pkill -f 'kb.py --port 8787'` 模式**匹配到了自身命令行**（bash -c 的完整命令串里
含同样文本），导致清理命令先把自己杀掉（SIGTERM），真正的服务进程反而没被杀干净。

**处理**：`ss -tlnp | grep 8787` 找到 PID → `kill <PID>`（精确匹配 `^python3 kb\.py` 防自匹配）。

**经验（后续测试约定）**：
1. 测试起服务用 `python3 kb.py ... & SRV=$!` 记住 PID，**在同一命令内用 `kill $SRV` 收尾**；
2. 禁用 `pkill -f` 匹配含进程名文本的长命令行（会自匹配自杀）；
3. 交付前检查无残留监听：`ss -tlnp | grep <端口>`。
