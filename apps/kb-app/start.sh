#!/usr/bin/env bash
# kb-app 本地一键启动脚本（AGENTS.md §10：每个软件必配本地启动脚本）
#
# 行为（幂等，可重复执行）：
#   1. 前置依赖：web/node_modules 缺失 → npm install
#   2. 前端构建：web/dist 缺失，或 web/src 等源码比 dist/index.html 新 → npm run build
#   3. 启动本地服务：python3 kb.py（托管 web/dist + /api 文件 API），前台运行
#
# 用法：
#   ./start.sh             # 默认端口 8787 → http://127.0.0.1:8787
#   PORT=9000 ./start.sh   # 换端口
#   需要强制重建前端：先删除 web/dist 再运行本脚本
#
# 前置：python3、node/npm 可用（首次运行会联网 npm install）。
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8787}"
cd web

# 1) 依赖
if [ ! -d node_modules ]; then
  echo "▶ 首次运行：npm install …"
  npm install
fi

# 2) 构建（源码变更自动重构建；dist 缺失或缺产物时构建）
needs_build=0
if [ ! -f dist/index.html ]; then
  needs_build=1
elif find src index.html vite.config.ts tailwind.config.ts postcss.config.js \
     -newer dist/index.html -print -quit 2>/dev/null | grep -q .; then
  needs_build=1
fi
if [ "$needs_build" -eq 1 ]; then
  echo "▶ 构建前端（npm run build）…"
  npm run build
else
  echo "▶ 前端产物已最新，跳过构建（强制重建请先删除 web/dist）"
fi

# 3) 启动服务
cd ..
echo "▶ 启动 kb.py：http://127.0.0.1:${PORT}（Ctrl+C 退出）"
exec python3 kb.py --port "$PORT"
