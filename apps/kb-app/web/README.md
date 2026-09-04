# kb-app Web 前端

React + Vite + TypeScript + Tailwind 前端。颜色、字阶、间距、圆角、动效与布局尺寸均映射自仓库 `packages/ui-reference/design-tokens.json`。

## 构建与运行

```bash
cd apps/kb-app/web
npm install
npm run build
cd ..
python3 kb.py --port 8787
```

打开 <http://127.0.0.1:8787>。Python 服务会托管 `web/dist` 并提供 `/api/*` 文件 API；未构建时首页会返回构建提示。

开发时可分别运行 Python 服务和 `npm run dev`，Vite 会把 `/api` 代理到 `127.0.0.1:8787`。
