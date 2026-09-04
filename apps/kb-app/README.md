# kb-app — 本地 Web 知识库小站

> 建立：2026-09-04（「dsh 设计 → codex 实现 → dsh 评审」闭环第 1 个交付物）
> 技术：Python 3 标准库单文件，零第三方依赖。设计简报见 `docs/tasks/kb-app.brief.md`。

## 用法

```bash
cd /home/fangke/dsh-test/kb-app && python3 kb.py [--port 8787] [--dir kb_data]
# 浏览器打开 http://127.0.0.1:8787
```

- 仅监听 `127.0.0.1`，本机工具无鉴权。
- 笔记存为 `kb_data/<标题>.md`（UTF-8，目录自动创建，已 gitignore）。
- 功能：列表 / 新建 / 编辑 / markdown 常用子集渲染 / 关键词搜索（子串匹配，带上下文摘要）。

## HTTP 接口

| 接口 | 说明 |
|---|---|
| `GET /` | 单页前端（内嵌，无外部资源） |
| `GET /api/list` | 笔记列表，按更新时间倒序 |
| `GET /api/note?name=<标题>.md` | 返回原始 markdown + 渲染 HTML；不存在 404 |
| `POST /api/save` | JSON `{title, content, original_content?}`；同名内容不同且无 original_content 时 409 |
| `GET /api/search?q=` | 子串搜索，返回标题 + 上下文摘要 |

## 安全要点（评审确认）

- 标题服务端校验：非空、不含 `/`、`\`、`..`、`\x00`（防路径穿越）。
- HTML 全部经 `html.escape` 后仅放行有限行内语法；链接协议白名单 `https?://`、`mailto:`。
- 单笔记 2MB 上限（413）。

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
