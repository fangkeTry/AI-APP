# 任务简报：kb-app 存储层迁移 SQLite（数据可靠性 + 测试/CI 补课）

> 生成方：dsh 设计（2026-09-04）｜执行方：codex（`scripts/codex-run.sh`）
> 简报路径：AI-APP/apps/kb-app/docs/storage-sqlite.brief.md
> 工作目录：/home/fangke/dsh-test/projects/AI-APP（整个仓库：改 kb-app、加 CI workflow）
> 依据约定：dsh 工作区 AGENTS.md §10（存储默认 SQLite / 工程化分档基线 / 提交规范）；决策记录 `AI-APP/docs/indie-ruleset-research-2026-09-04.md` §6 P1/P2/P4/P5

## 1. 背景与设计

kb-app 是独立开发通用约束集的 demo 试验场。业界裁决（[sqlite.org: SQLite 竞争的是 fopen()](https://www.sqlite.org/whentouse.html)）：本地单应用数据的默认存储是 **SQLite**，不是裸文件。用户已拍板：**kb-app 也迁移 SQLite**（md 文件只作导入/导出通道），并随迁移补齐可靠性（原子写/备份）、测试、CI——这是"能上线"基线的最小闭环。

**目标架构**：
- 主存储：`kb.db`（SQLite，标准库 `sqlite3`，WAL 模式）——事务保证原子写、单文件可拷贝备份；
- `kb_data/*.md`：不再读写，仅作为**导入/导出通道**与旧数据迁移源（迁移后原文件保留=用户自带备份）；
- 前端 `web/`：**零改动**（API 契约与返回结构保持兼容）；
- 服务端 `kb.py`：拆出 store 层（SQLite 读写），HTTP 层保留；新增 CLI 动作（导出/导入/备份）。

## 2. 目标与范围

- 目标：存储迁移 SQLite + 行为/API 完全兼容（列表/新建/编辑/markdown 渲染/搜索/409 冲突）+ 迁移工具 + 备份/恢复文档 + 单元测试 + GitHub Actions CI。
- 范围外：前端 UI 改动；删除/重命名/标签等功能；多人/同步；ORM 或任何新依赖（仅标准库）；不引重型测试框架。

## 3. 需求清单

- [ ] R1 store 层（SQLite，`apps/kb-app/kb.py` 内实现或拆文件均可）：
  - `kb.db` 单文件；`PRAGMA journal_mode=WAL`、`busy_timeout`（多线程 http 服务并发写安全，save 用事务 + 写前重查）；
  - 表 `notes(title TEXT UNIQUE NOT NULL, content TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL)`（时间戳 ISO-8601 UTC，同现有格式）；标题校验沿用 `valid_title`；
  - 写路径：插入/更新走事务；"同名不同内容且无 original_content 匹配"→ 409（读当前值比对，语义与现状一致）。
- [ ] R2 API 兼容（返回结构不变，前端零改动）：
  - `GET /api/list`：按 updated 倒序 `{notes:[{title,updated}]}`；
  - `GET /api/note?name=<标题>.md`：`{title, content, content_html}`（渲染逻辑沿用现有 `render_markdown`）；不存在 404；
  - `POST /api/save`：`{title, content, original_content?}`；成功 `{ok:true}`，409 文案沿用"同名笔记已存在且内容不同"；
  - `GET /api/search?q=`：行为对齐现状（标题或正文子串命中 + 上下文摘要 snippet + 空正文"标题匹配"），实现可用 LIKE 保持语义；命中后 snippet 用 Python 现逻辑生成。
- [ ] R3 首次自动迁移：`kb.db` 不存在且 `kb_data/` 下有 `*.md` → 启动/首次 CLI 时自动导入全部（文件名=标题、内容=正文、created=updated=文件 mtime），**不删除原 md**，stdout 报告"已从 kb_data 导入 N 篇"。
- [ ] R4 CLI（`python3 kb.py` 互斥动作，默认启动服务）：
  - `--export <目录>`：全部笔记导出为 `<标题>.md` 到该目录（UTF-8，可覆盖同名文件）；
  - `--import <目录>`：批量导入该目录 `*.md`（同名已存在且内容不同→跳过并计数报告，不覆盖）；
  - `--backup <文件>`：用 SQLite backup API 生成一致性备份文件（不依赖停服）；
  - db 路径：`--db <路径>`，默认 `apps/kb-app/kb.db`（基于 `__file__` 解析，任意 cwd 可跑）；服务模式 `--port` 保留。
- [ ] R5 文档：`apps/kb-app/README.md` 更新——数据形态节（SQLite 单文件 + md 通道）、「备份与恢复」节（备份=`python3 kb.py --backup xxx.db` 或拷 `kb.db`；恢复=放回/`--import`；含演练命令）、启动方式不变（`./start.sh` 已兼容）；接口表说明保持。`.gitignore` 追加 `kb.db*`（含 -wal/-shm）。
- [ ] R6 测试（`apps/kb-app/tests/test_kb.py`，`unittest`，无网络）：store 层（save/list/note/search 子串/409/updated 更新）、迁移（造 md → 自动导入）、导出→导入回环、backup 文件可再打开且内容一致；跑 `python3 -m unittest discover tests -v` 全绿。
- [ ] R7 CI：`AI-APP/.github/workflows/kb-app.yml`——path 过滤 `apps/kb-app/**`；job：setup-python 3.12 → `cd apps/kb-app && python3 -m unittest discover tests`；另一步（或同 job）node 20 + `cd apps/kb-app/web && npm ci && npm run build`（验证前端仍可构建，不跑前端测试）。

## 4. 涉及文件

- 修改：`apps/kb-app/kb.py`、`apps/kb-app/README.md`、`apps/kb-app/.gitignore`
- 新增：`apps/kb-app/tests/test_kb.py`、`AI-APP/.github/workflows/kb-app.yml`
- 禁止改动：`apps/kb-app/web/` 源码、`packages/ui-reference/`、`kb_data/` 内容（迁移只读不删）、其他 app、`start.sh`（若确有兼容问题才允许最小改动并说明）

## 5. 验收标准（codex 必须实际执行并贴结果）

```bash
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app
# 1) 单测全绿
python3 -m unittest discover tests -v
# 2) 迁移：临时造旧格式数据 → 首次启动自动导入
mkdir -p /tmp/kb-mig/kb_data && printf '# a\n\n内容A。' > /tmp/kb-mig/kb_data/迁移笔记A.md
cd /tmp/kb-mig && python3 /home/fangke/dsh-test/projects/AI-APP/apps/kb-app/kb.py --db /tmp/kb-mig/kb.db --export /tmp/kb-mig/out  # 触发自动迁移并导出
ls /tmp/kb-mig/out/            # 应含 迁移笔记A.md
# 3) API 回归（另起服务，沿用旧验收集）
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app && python3 kb.py --port 8787 &
curl -s -X POST http://127.0.0.1:8787/api/save -H 'Content-Type: application/json' \
  -d '{"title":"pilot笔记","content":"# 标题\n\n风格**验证**笔记。"}'                      # {"ok":true}
curl -s 'http://127.0.0.1:8787/api/search?q=风格'                                        # 命中 pilot笔记
curl -s -X POST http://127.0.0.1:8787/api/save -H 'Content-Type: application/json' \
  -d '{"title":"pilot笔记","content":"另一内容"}'                                          # 409
curl -s http://127.0.0.1:8787/ | grep -i '<div id="root"'                                  # 前端托管仍在
# 测完 kill 服务（记住 PID，勿 pkill 自匹配）
# 4) 导出→清库→导入 回环内容一致；--backup 文件 sqlite3 可打开
# 5) CI：AI-APP/.github/workflows/kb-app.yml 能被 python yaml 解析（Actions 本体由 GitHub 跑）
# 6) cd apps/kb-app/web && npm run build  # 前端零改动也应构建通过
```

浏览器手动项（可选）：① 搜索/新建/编辑/409 提示与旧版一致；② 无控制台报错。最后清理临时文件与测试数据（`/tmp/kb-mig`、db 测试文件、kb_data 测试残留）。

## 6. 必读文件（先读再做）

- 现有实现：`apps/kb-app/kb.py`（store 逻辑分散在 Handler，需抽层）、`apps/kb-app/README.md`（现"md 文件真源"表述将被改写）、`apps/kb-app/docs/rebuild-frontend.brief.md`（前端 API 用法）
- 约定：dsh 工作区 `AGENTS.md` §10（存储规则/工程化基线/提交规范）；`AI-APP/docs/indie-ruleset-research-2026-09-04.md` §2.1/§6

## 7. 硬性约束

- 不得 `git commit`/`git push`；不得新增第三方依赖（仅标准库 `sqlite3`/`unittest`）；不改前端源码与 ui-reference。
- API 返回结构与文案与现状一致（前端不感知迁移）；409/404/400 语义保持。
- 数据安全优先：任何导入/迁移**不删除、不覆盖**用户原文件与现 db 中不同内容（跳过+报告）；时间戳用 UTC ISO-8601。
- 中文注释；不确定处用最保守方案并回报。

## 8. 输出要求（回报给 dsh）

- 文件清单 + kb.py 结构（store/HTTP/CLI 分层）；关键 diff 摘要；
- 上述验收命令逐条实际输出（单测、迁移、5 接口、回环、backup、build）；
- 遗留问题 / 需要 dsh 决策的点（如 FTS5 全文检索是否作为下一步增强）。
