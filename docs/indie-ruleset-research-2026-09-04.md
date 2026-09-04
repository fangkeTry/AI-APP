# 通用独立开发约束集 · 业界调研与修订草案（2026-09-04）

> 背景：kb-app 是独立开发通用规则的 **demo 试验场**——探索各种约定，真实开发时按一套通用规则执行。
> 因此约束从探索期就要按「**能真实上线使用**」的规格设计，由**业界通行做法**裁决（不是拍脑袋定）。
> 状态：~~草案~~ → **已定案（2026-09-04 晚，P1–P5 用户拍板）**；定案记录见 §6。规则正文已写入 dsh 工作区 AGENTS.md §10 与简报模板。

## 1. 调研源（按维度，含时效）

| 维度 | 源 | 时效/性质 |
|---|---|---|
| 本地优先（数据所有权） | [Ink & Switch: Local-first software — you own your data](https://www.inkandswitch.com/local-first/)（Martin Kleppmann 等，Onward! 2019 论文） | 该领域定义性文献，至今为本地优先运动基准 |
| 存储选型权威判定 | [SQLite: Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html) | sqlite.org 官方长期维护页 |
| 本地优先同步方案 | [Turso: Building Local-First Apps (offline-first sync)](https://turso.tech/blog/building-local-first-apps-the-complete-guide-to-offline-first-database-sync)、[Expo: offline-first mobile](https://expo.dev/blog/build-offline-first-mobile-apps)、[DoltLite: SQLite 作为 app 文件格式](https://www.dolthub.com/blog/2026-04-27-why-doltlite/) | 2025–2026 |
| 上线生产清单 | [VexFS PRODUCTION_CHECKLIST](https://github.com/lspecian/vexfs/blob/main/PRODUCTION_CHECKLIST.md)、[Cloudflare Workers 安全 skill](https://github.com/secondsky/claude-skills)、[18F secrets 指南](https://guides.18f.org/engineering/security/secrets/) | 社区/官方维护 |
| 后端基线 | [12-factor app](https://12factor.net/)（官方）、REST API 最佳实践（[zernio 2026](https://zernio.com/blog/restful-api-best-practices)） | 12-factor 为长期基准 |
| indie 技术栈 | [Ultimate Indie Hacker Stack 2025 (dev.to)](https://dev.to/killer_scofield_d2f41df11/the-ultimate-indie-hacker-tech-stack-for-2025-1328)、[solo git workflow 2026 (dev.to)](https://dev.to/armorbreak/the-git-workflow-that-actually-works-for-solo-developers-2026-2mna) | 2025–2026 |
| 提交/版本规范 | [Conventional Commits](https://www.conventionalcommits.org/)、[SemVer](https://semver.org/) | 官方规范 |
| Monorepo | [Feature-Sliced: Monorepo guide](https://feature-sliced.design/ru/blog/frontend-monorepo-explained)、Turbo/Nx | 2025 |
| 本地应用分发 | [Conveyor 自更新打包](https://dev.to/fdelporte/javafx-in-action-14-with-mike-hearn-about-conveyor-to-build-self-updating-desktop-app-packages-in-l4g)、electron-updater 指南 | 2025 |

## 2. 关键业界结论

### 2.1 存储与数据层（最影响本 demo 的裁决）

1. **SQLite 官方判定**：「SQLite 不与 client/server 数据库竞争——**SQLite 竞争的是 `fopen()`**」。单应用/单设备的本地数据存储，业界默认就是 SQLite（应用文件格式、桌面工具、<100K hits/天 的网站都适用）。SQLite 强调 economy/efficiency/reliability/independence/simplicity；client/server（MySQL/PostgreSQL）强调的是 scalability/concurrency/centralization。
2. **开放文件格式（markdown 等）只在一种场景胜出**：数据必须能被**用户用其他工具直接打开/生态互通**（Obsidian/Logseq 类，卖点=用户所有权+可迁移+grep 能力）。代价 = 检索/关系/原子写/并发弱，需要自建索引或工具链。
3. **Local-first 七理念**（Ink & Switch）：①Fast ②Multi-device ③Offline ④Collaboration ⑤Longevity（长期保存）⑥Privacy ⑦User control。要点：**「用户能备份/归档/迁移/导出自己的数据」是产品承诺，不是内部实现细节**；传统文件格式天然满足其中多条，代价是多端协作。
4. **备份与迁移是上线红线**（VexFS checklist：Backup mechanism documented + Recovery procedure tested）——不是"以后再说"。

### 2.2 后端/服务上线基线（tier-2 多人/SaaS 档适用）

- 12-factor 仍是基线：配置走环境变量（**secrets 不入库**）、可移植、无状态进程、日志到 stdout。
- 上线 Checklist 红线：输入校验、路径穿越防护、鉴权、**限流**、**TLS**、**结构化日志**、**health 检查**、优雅停机、**重启不丢数据**、备份+恢复演练。
- indie 主流栈（2025-2026）：Next.js+TS+Tailwind+shadcn/ui；Supabase（Postgres）/Firebase；Vercel/Railway/Coolify；GitHub Actions；pnpm+monorepo（Turbo/Nx）。趋势=轻量全栈、即时部署、serverless、组件库拷贝。
- C 端本地发布档另需：自动更新（electron-updater/Conveyor）、崩溃上报（Sentry 类）、代码签名。

### 2.3 测试与 CI（所有档的差距最大项）

- 生产基线：单元测试（>70% 覆盖为常见红线）、关键路径集成测试、回归套件、自动化安全扫描。
- **GitHub Actions 是 solo 开发者 CI 的事实标准**（indie 文章与大量项目一致）。

### 2.4 仓库与开发流程

- **Conventional Commits**（feat:/fix:/docs:/chore:…）是行业提交规范；**SemVer** 版本化。
- solo 开发者流程共识 = **trunk-based**（直接推 main/短分支），GitFlow 对单人过重。
- Monorepo 是 indie 主流（一个仓库管前端+后端+共享包，pnpm workspace/Turbo 提速）。
- Secrets/配置：环境变量注入，绝不入库（12-factor + 18F 指南一致）。

## 3. 现有约束 vs 业界对照（现状 → 差距 → 建议）

| 维度 | kb-app/demo 现状 | 业界通行 | 建议（草案） |
|---|---|---|---|
| 存储选型 | 纯 `kb_data/*.md` 文件（无规则约束） | 本地单应用**默认 SQLite**；文件仅开放格式场景 | **规则化**：本地档默认 SQLite；仅"数据须用户可外部打开/生态互通"才用开放文件格式，且必须配套原子写+备份+导出说明 |
| 写入可靠性 | `write_text` 直接写原文件（崩溃可能半写） | WAL/临时文件+rename/fsync | 规则：写=临时文件+rename（或 SQLite 事务）；kb-app 待改 |
| 备份/恢复 | 口头"拷 kb_data 目录"，无文档无演练 | 文档化 + 恢复演练（红线） | 每软件 README 加「备份与恢复」节；kb-app 补 |
| 数据所有权（产品功能） | 无导出/备份 UI | local-first：导出/备份是产品承诺 | 未来真实产品把"导出为开放格式+备份"当功能做 |
| 测试/CI | 0 测试、0 CI | 单测+集成+CI（GitHub Actions） | demo 阶段逐步补：先 API 冒烟测试→CI（build+test）；规则：每个软件有测试与 CI |
| 输入校验/路径防护 | 有（评审通过） | 红线 | 保持 |
| 鉴权/TLS/限流/日志/health | 无（本地单机 N/A） | tier-2 红线清单 | 分档表：明确哪档必须启用哪些（本地档豁免的写明） |
| start.sh/README | 已配 | —（实践共识） | 保持 |
| 提交规范 | 中文 checkpoint（`checkpoint: xxx`） | Conventional Commits | 待拍板：引入 CC 前缀 or 保持中文语义 |
| 仓库 | monorepo（git 组织） | monorepo+pnpm+Turborepo | 多 app 后引 pnpm workspace；暂不阻塞 |
| 版本化 | 无 tag/无 changelog | SemVer + changelog | 待拍板：何时起用（首个可发布版？） |

## 4. 修订草案（2026-09-04 晚已定案，见 §6）

- **P1 存储规则**：~~本地档默认 SQLite，开放格式场景例外~~ → 定案：**kb-app 也迁移 SQLite**（md 只作导入/导出通道）。
- **P2 数据可靠性补课**：定案：**立即排下一份简报**（内容并入 P1 迁移简报：原子写由 SQLite 承担 + 备份/恢复文档 + 测试 + CI）。
- **P3 提交规范**：定案：**引入轻量 Conventional Commits 前缀**（feat:/fix:/docs:/chore:/refactor:/test: + 中文正文），所有仓库适用。
- **P4 上线基线 + P5 测试/CI**：定案：**写入 AGENTS.md §10 硬性约定** + 更新简报模板必产项。

## 6. 定案记录（2026-09-04）

| 决策点 | 定案 | 落地 |
|---|---|---|
| P1 存储 | **本地档默认 SQLite；kb-app 也迁移 SQLite**，md 仅作导入/导出通道；开放文件格式只允许特例+简报写明理由+配套可靠性 | AGENTS.md §10「存储默认 SQLite」；`apps/kb-app/docs/storage-sqlite.brief.md`（下一份 codex 简报） |
| P2 补课 | **立即排下一份简报**（原子写/备份恢复/测试/CI 随迁移一起做） | 同上简报 |
| P3 提交 | **轻量 Conventional Commits**（feat:/fix:/docs:/chore:/refactor:/test: + 中文正文），原 `checkpoint:` 前缀废止 | AGENTS.md §2 + §10「提交规范」 |
| P4 上线基线 | **写入约定**：每软件单测+CI(GitHub Actions)+README 备份恢复节；tier-2 红线清单（鉴权/限流/TLS/日志/health/优雅停机/重启不丢数据/备份恢复演练/secrets 环境变量）；本地单机档豁免项写明 | AGENTS.md §10「工程化分档基线」；TEMPLATE.brief.md §6 |
| P5 测试/CI | 同上，简报模板列必产项（按档） | TEMPLATE.brief.md §6 |

## 5. 落地路径（拍板后执行）

1. 本草案定稿（改此文件状态为定案或另存定案版）；
2. AGENTS.md §10 增补：存储规则、工程化分档基线、提交规范（若 P3 通过）；
3. `AI-APP/docs/ui-research-2026-09-04.md` §14 产品分级框架扩展（存储选型决定轴 + 各档上线基线）；
4. dsh 简报模板 TEMPLATE.brief.md：必产项加 测试/CI（按档）、备份恢复文档；
5. kb-app 待办简报（P2 内容）；
6. 知识库「工作区开发约定」归档本定案；git 检查点两仓提交推送。
