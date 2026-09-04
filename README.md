# AI-APP

个人 AI 应用 monorepo（2026-09-04 建立）——Vibe Coding 实验场。
仓库约定见 dsh 工作区 AGENTS.md §10。

## 布局

- `apps/<软件名>/` — 各应用（独立子项目，自带 README 与 docs）
- `packages/` — （预留）跨应用共享代码

## 应用清单

| 应用 | 说明 | 技术 |
|---|---|---|
| [apps/kb-app](apps/kb-app/) | 本地 Web 知识库小站：列表/新建/编辑/markdown 渲染/搜索 | Python 3 标准库单文件 |

## 开发流程

dsh 出设计简报（放各应用 `docs/`）→ 用户在终端跑 codex 实现 → dsh 评审打检查点。
codex 启动脚本 `scripts/codex-run.sh` 位于 dsh 工作区（`/home/fangke/dsh-test/`）。
