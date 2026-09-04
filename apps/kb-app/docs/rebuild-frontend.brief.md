# 任务简报：kb-app 前端重做（pilot · 验证 UI 风格体系）

> 生成方：dsh 设计（2026-09-04）｜执行方：codex（`scripts/codex-run.sh`）
> 简报路径：AI-APP/apps/kb-app/docs/rebuild-frontend.brief.md
> 工作目录：/home/fangke/dsh-test/projects/AI-APP（整个仓库，可读 packages/ui-reference 与现有 kb-app）

## 1. 背景与设计

kb-app（本地 markdown 知识库）原为 Python 单文件（`apps/kb-app/kb.py`，内嵌 HTML 前端）。现作为 AI-APP 风格体系的 **pilot**：**前端重做**为 React + Tailwind，样式必须遵守仓库内风格规范（见 §6 必读文件），验证「tokens 单一源 → 拷贝不耦合 → 双端一致」流程。产品属 tier-1（本地文件形态）：**数据仍是 `kb_data/*.md` 文件**，由极简本地服务提供读写 API。

**目标架构**：
- `apps/kb-app/web/`：React (Vite + TypeScript) + Tailwind 前端（新 UI）。
- 服务端：保留极简 Python 服务（原 API 契约不动，仅剥离内嵌 HTML 前端，改为托管 `web/dist` 静态产物 + 现有 JSON API）。
- `apps/kb-app/kb_data/*.md`：数据唯一真源（不变）。
- 不引入重型后端：本服务仅文件 API，属 tier-1 极简层。

## 2. 目标与范围

- 目标：前端全面重做为新风格（Apple 明亮留白结构；Light=蓝/白；Dark=护眼低饱和蓝），Light/Dark 跟随系统 + 手动切换；移动优先；功能与旧版一致（列表/新建/编辑/markdown 渲染/搜索）。
- 范围外：不做多人/同步/导入导出/标签；不改数据文件格式；不上重型状态管理。

## 3. 需求清单

- [ ] R1 `web/`：Vite + React + TypeScript + Tailwind；组件本地实现（拷贝模型，不引整库 UI 框架）；图标用 lucide-react 按需；字体系统栈。
- [ ] R2 tokens：`design-tokens.json` 的 light/dark 全部映射为 Tailwind theme/CSS 变量；颜色只许用 token（禁硬编码近似色）；Dark 默认跟随 `prefers-color-scheme`，页面提供手动切换（记忆在 localStorage）。
- [ ] R3 页面与交互（调用现有 API 契约：`GET /api/list`、`GET /api/note?name=`、`POST /api/save`、`GET /api/search?q=`）：
  - 列表页（移动端单列，PC 左列表右预览）；搜索框（防抖，子串搜索，命中标题+摘要）；
  - 新建/编辑：标题输入 + markdown 正文 textarea；同名不同内容保存返回 409 时给出明确提示；
  - 查看：渲染 markdown（允许用轻量解析库如 `marked`/`markdown-it`，禁重型 UI 依赖）；渲染样式符合风格指南。
- [ ] R4 服务端：`kb.py` 剥离内嵌 HTML（删 PAGE/前端 JS），新增托管 `web/dist` 静态文件（未构建时提示"请先 npm run build"）；API 原样保留。
- [ ] R5 移动适配：移动优先断点；触控目标 ≥44px；列表/编辑器在小屏可用。

## 4. 涉及文件

- 修改：`apps/kb-app/kb.py`（去前端、托管 dist、API 保留）
- 新增：`apps/kb-app/web/`（React 工程）、`apps/kb-app/web/README.md`（构建/运行说明）
- 禁止改动：`kb_data/` 数据格式、`packages/ui-reference/` 三件套（tokens/guide/styleboard）、仓库其他 app、README 之外的 docs
- 保留：`.gitignore` 追加 `web/node_modules/`、`web/dist/`（在 kb-app/.gitignore 内）

## 5. 验收标准（codex 必须实际执行并贴结果）

```bash
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app/web
npm install && npm run build          # 构建成功、无类型错误
cd /home/fangke/dsh-test/projects/AI-APP/apps/kb-app
python3 kb.py --port 8787 &           # 启动本地服务（托管 dist + API）
curl -s http://127.0.0.1:8787/ | grep -i '<div id="root"'    # 返回 React 入口
curl -s -X POST http://127.0.0.1:8787/api/save -H 'Content-Type: application/json' \
  -d '{"title":"pilot笔记","content":"# 标题\n\n风格**验证**笔记。"}'      # {"ok":true}
curl -s 'http://127.0.0.1:8787/api/search?q=风格'              # 命中 pilot笔记
```

浏览器手动验证：① Light 状态为 Apple 蓝白、系统切暗后（或手动开关）变护眼低饱和蓝暗色；② 手机宽度布局正常；③ 新建→列表→打开→编辑→保存闭环；④ 无控制台报错。最后 `kill` 服务进程，删除测试数据 `kb_data/pilot笔记.md`。

## 6. 必读风格文件（先读再做）

- `packages/ui-reference/style-guide.md`（强制规范 + 禁止项 + 护眼三原则）
- `packages/ui-reference/design-tokens.json`（唯一颜色/尺寸来源）
- `packages/ui-reference/styleboard.html`（视觉对照：Light=组合 1，Dark=6c）

## 7. 硬性约束

- 不得 `git commit` / `git push`（dsh 评审后统一提交）。
- 不新增重量级依赖；不整库引入 UI 框架；不引入网络字体；图标按需。
- 颜色/尺寸全部来自 tokens；暗色满足护眼三原则（非纯黑底、非纯白字、低饱和强调）。
- 中文界面；代码关键处中文注释。
- 不确定处用最保守方案并回报，不擅自扩大改动面。

## 8. 输出要求（回报给 dsh）

- 改/新增文件清单 + `web/` 工程结构；构建与验收命令实际输出逐条贴。
- Light/Dark 与移动端的自测结果（可附浏览器截图路径说明）。
- 遗留问题 / 需要 dsh 决策的点。
