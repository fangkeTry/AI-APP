# AI-APP 前端 UI 策略与资源调研（2026-09-04）

> 目标：批量生成前后端 app；前端 UI 风格保持一致；公用代码**只作参考示例、不耦合使用**。
> 技术栈定案：**React + Tailwind CSS**（用户 2026-09-04 确认）。
> 本文件基于 2026-09-04 网络检索（官方源/GitHub/技能市场），时效性结论以当天为准；
> 选型落地前需到各仓库现场核对版本、维护活跃度与许可证。

## 1. 组织模型定案：copy-paste + tokens + registry + skills

| 层 | 职责 | 选型 |
|---|---|---|
| 组件代码 | 拷进每个 app（**不装依赖、不耦合**） | shadcn/ui 模型 |
| 风格一致性 | 设计 tokens（CSS 变量：颜色/字阶/圆角/阴影/间距）+ 风格指南文档 | 自建 `packages/ui-reference/` |
| 生成加速 | codex/dsh 生成时引用"风格指南 + 组件示例" | Agent Skills（SKILL.md） |
| 沉淀分发 | 自建组件市场，供各 app `shadcn add` 拉取 | shadcn 自定义 registry |

理由：shadcn copy-paste 与"参考不耦合"天然一致；tokens 保证跨 app 一致；
skills 让 codex 生成即符合风格；registry 使沉淀可复用。

## 2. 组件库/设计系统对比（React + Tailwind 视角）

| 候选 | 定位 | 契合点 | 注意 |
|---|---|---|---|
| [shadcn/ui](https://ui.shadcn.com) | 拷贝式组件 + Tailwind，2026-06 新增 [AI 对话组件](https://ui.shadcn.com/docs/changelog/2026-06-chat-components) | 主推：零耦合、可自建 registry、AI 应用组件齐 | 需维护拷贝 |
| [facebook/astryx](https://github.com/facebook/astryx) | Facebook 开源、agent-ready 设计系统 | 面向 AI 生成的设计系统（新，观察） | 新项目，成熟度待验 |
| [MonkeyUI](https://github.com/MonkeyUI-dev/MonkeyUI) | 提取参考 UI 的"style DNA"注入 AI 生成 UI | 批量一致性利器 | 待现场试用 |
| [Radix](https://www.radix-ui.com) | 无样式原语 | shadcn 底层，需要时直接用原语 | 无样式需自配 |
| [Mantine](https://mantine.dev) | 全功能组件库 | 开箱即用 | 依赖式（耦合） |
| [Chakra](https://github.com/chakra-ui) | 组件库 + 主题系统 | tokens 思路接近 | 依赖式 |
| Ant Design（React 版） | 企业中后台 | 中文生态成熟 | 风格偏企业，设计感一般 |

主选：**shadcn/ui 为底座**；astryx/MonkeyUI 作为 2026 新方向持续跟踪。

## 3. 设计感组件/模板示例库（抄样来源）

- [awesome-shadcn-ui](https://github.com/birobirobiro/awesome-shadcn-ui) — shadcn 生态精选总清单
- [21st.dev](https://github.com/21st-dev) — shadcn 组件市场 + Magic MCP（可接 codex）
- [Aceternity UI](https://ui.aceternity.com) 系动效组件；[Magic UI](https://magicui.design)
- [vercel/registry-starter](https://github.com/vercel/registry-starter) — Vercel 官方 AI-Native 设计系统脚手架（Next.js + shadcn registry）
- [gentelella](https://github.com/ColorlibHQ/gentelella) — 免框架 admin 模板（纯 JS/SCSS）
- [awesome-nextjs](https://github.com/officialrajdeepsingh/awesome-nextjs) — Next.js 生态清单（AI 应用组件等）

## 4. 插件/技能资源清单（全类型）

### 4.1 Agent Skills（推荐主力，dsh/codex 均支持 SKILL.md 标准）
- [LobeHub 技能市场](https://lobehub.com/skills)：[premium-ui-components](https://lobehub.com/skills/itsar-vr-goatedskills-premium-ui-components)、[generative-prefab-ui](https://lobehub.com/skills/prefecthq-prefab-generative-prefab-ui)
- [explainx.ai 的 aceternity-ui skill](https://explainx.ai/skills/secondsky/claude-skills/aceternity-ui)
- [agentskillexchange 的 Snowe UI](https://agentskillexchange.com/skills/snowe-ui-skill/)
- GitHub 直装：[aranx-ai/skills](https://github.com/aranx-ai/skills)（Tailwind 前端打磨）、[universal-design-principles](https://github.com/Deibler/universal-design-principles)（跨 agent 设计原则）
- 计划：自建 `packages/ui-reference/skill/`（风格指南 SKILL.md），codex 生成时自动装载

### 4.2 组件 registry / 市场
- [shadcn 自定义 registry 文档](https://github.com/shadcn-ui/ui/discussions/9949)、示例 [sid-cn](https://github.com/Siddhesh-Agarwal/sid-cn)
- 21st.dev（见 §3）

### 4.3 Figma 设计资源（人工设计/评审参考）
- [Obra shadcn/ui tools（Figma 插件）](https://www.figma.com/community/plugin/1544866255228781486/obra-shadcn-ui-tools)
- [shadcn-ui 组件 Figma 文件（含变量/Tailwind class）](https://www.figma.com/community/file/1342715840824755935/shadcn-ui-components-with-variables-tailwind-classes-updated-january-2026)

### 4.4 中文生态补充
- Ant Design（React/中后台模板，如 [react-antd-multi-tabs-admin](https://github.com/hsl947/react-antd-multi-tabs-admin)）；[AdminLTE 2026 AntD 模板榜](https://adminlte.io/blog/ant-design-admin-templates/)

## 5. 落地路线（后续步骤）

1. **定风格**：选 1 个参考方向（暗色 AI 感 / 明亮简洁 / 渐变玻璃感），从 §3 抄样 + Figma 资源对齐；
2. **建参考层**：`packages/ui-reference/` = `design-tokens.css`（参考）+ `components/`（示例源码）+ `style-guide.md`（风格指南，供 codex）；
3. **验证机制**：写 1 个 pilot app（前端 React+Tailwind），用参考层拷贝生成，评审一致性；
4. **沉淀分发**：把验证过的组件/风格做成 shadcn 自定义 registry + SKILL.md；
5. **批量化**：建立"前端样板（拷贝）＋后端模板"的批量生成流程，每个 app 独立于 apps/ 下。

## 6. 待现场核验项（截至 2026-09-04 检索）

- astryx / MonkeyUI 的成熟度、许可证、维护活跃度；
- 各技能市场条目的更新频率与质量（防陈旧）；
- shadcn 2026-06 chat 组件是否满足对话类 app 需求；
- 所选示例/组件的许可证是否允许拷贝进商业/个人项目。

## 7. 风格约束 v2（用户补充 2026-09-04）

- **排除**：政企/企业软件风格（Ant Design 企业感、后台密集表格风一律不用）。
- **目标**："简洁高级"——无法用语言描述，**必须用视觉锚点指认**（见 §8）。
- **性能红线**：前端资源不能多；需跑在**性能不好的移动设备**上；弱网也要可用。
- **形态**：适配移动端；用户 2026-09-04 定案：**Web + 原生 App 双端**（原生技术选型见 §10）。

## 8. 视觉锚点清单（风格指认用——说不清就看这些）

按 vibe 分组，请用户浏览后指认"像 X"：

- **暗色科技感**：Linear（linear.app）、Arc 浏览器（arc.net）、Raycast（raycast.com）
- **黑白极简**：Vercel（vercel.com，Geist 设计体系）、[Geist 模板](https://huggingface.co/buckets/merve/hermes-agent/tree/skills/creative/popular-web-designs/templates/vercel.md)、Stripe（stripe.com 局部）
- **明亮留白**：Apple（apple.com）、Anthropic（claude.ai）
- **柔和中性**：Notion（notion.so）、Figma（figma.com 局部）
- **轻量玻璃/渐变感（谨慎，动效吃性能）**：Aceternity 精选、Magic UI 精选

组件级样式参考：shadcn/ui **New York** 风格、21st.dev 的 minimal 模板。

相关开源工具：**[StyleSeed](https://fr.news.hada.io/topic?id=28281)**（开源：给 AI 编码工具注入设计感——"说不清的设计感"问题的高性价比解法，列为候选 skill 来源）。

## 9. 轻量化技术约束（弱移动设备 + 手机/PC 双端）

- **CSS-first**：样式尽量走 Tailwind/CSS，动画只用 transform/opacity，避免整页重排；不做重型动效（Aceternity/Magic 只摘局部，不当默认）。
- **依赖最小化**：组件本地拷贝（shadcn 模型）+ 无样式原语（Radix 按需），避免引入整个组件库 JS。
- **图标**：SVG 单色图标集（如 lucide），按需引入，不用图标字体。
- **字体**：系统字体栈优先；自定义字体用 woff2 + subset（中文字体尤其控制体积）。
- **移动优先**：Tailwind 默认移动断点起步（mobile-first）；触控目标 ≥44px；弱网下图片懒加载/占位；首屏不阻塞（CWV 友好——[Tailwind 在 CWV 通过率上领先](https://www.pagespeedmatters.com/resources/data-studies/css-frameworks-core-web-vitals)）。
- **适配策略**：响应式单代码库（PC/手机同源）；可选 PWA（离线/安装）但保持轻量。
- **可直接装载的现成 skill**：[tailwindcss-mobile-first](https://github.com/NeverSight/learn-skills.dev/blob/main/data/skills-md/josiahsiegel/claude-plugin-marketplace/tailwindcss-mobile-first/SKILL.md)、[tailwindcss-responsive-darkmode](https://raw.githubusercontent.com/NeverSight/skills_feed/refs/heads/main/data/skills-md/josiahsiegel/claude-plugin-marketplace/tailwindcss-responsive-darkmode/SKILL.md)——codex/dsh 生成时保证移动优先与响应式。

## 10. 原生 App 技术选型（用户 2026-09-04 定案：Web + 原生双端）

**主选：Expo（React Native）+ NativeWind**，理由：
- 与 Web 端同用 **React + TypeScript**，dsh/codex 批量生成成本最低（一套语言、技能可迁移）；
- Hermes 引擎默认开启，中低端安卓机性能友好；
- Expo 2026 生态持续扩展（[AppJS 2026 发布](https://expo.dev/blog/expo-highlights-new-products-and-plans-for-the-future)）；
- NativeWind v5 = Tailwind for RN（[官方文档](https://www.nativewind.dev/v5)），样式写法和 Web 端一致。

**两端风格一致的关键：单一 tokens 源**——用 [style-dictionary](https://github.com/style-dictionary/style-dictionary)（跨平台样式构建系统）从 `tokens.json` 生成：Web 的 Tailwind theme + 原生的 NativeWind config；`packages/ui-reference/` 内放 tokens 源与两端生成物。

**组件参考层（仍守"拷贝不耦合"）**：Web 抄 shadcn 示例；原生侧参考 Expo 官方模板与轻量组件，本地拷贝进每个 app；不引入重型 UI 框架依赖。样式锚点（§8）对两端通用。

**轻量红线延续**：RN 侧避免重型导航/动画依赖、控制重渲染；图片走缓存优化；包体用 Hermes + 按需组件控制。

**待验证**：RN 具体组件参考集质量参差，先以 1 个 pilot 双端 app 验证"同一 tokens + 两端拷贝"的一致性后再批量。

## 11. 风格定案 v1（用户 2026-09-04）

- **基底（结构层）**：Apple 明亮留白（§8 C 组）——大留白、轻字阶、圆角卡片、胶囊按钮；两端（Web/RN）通用。
- **主色（品牌层）**：**不用 Apple 蓝**（#0071e3 系）；主色为**可替换的语义 token（accent）**。
- **按 app 类型差异化**：结构不变，**色相随类型走**——tokens 分三层：
  - `core`（通用：背景/文字/边框/圆角/间距/字阶，Apple 基底，全 app 一致）
  - `accent`（主色/品牌色，按 app 覆盖）
  - `type-preset`（按 app 类型给出的推荐主色表，如 健康=翠绿、财务=石墨/深青、学习=琥珀、社交=珊瑚…类型清单与配色待用户确认）
- 选色方式：本地风格看板「主色试色条」圈选，避免语言描述。
- 用户反馈（同日）：六色基础候选不够"高级"→ 追加低饱和/深色调候选（香槟金/墨绿/勃艮第/可可棕/陶土赤/深石墨，v2 试色条）；**app 类型先不定，先用一套默认主色跑通 pilot**，`type-preset` 表推迟到类型明确后再补。

## 13. 风格定案 v2（用户 2026-09-04，终版基线）

- **结构**：Apple 明亮留白（§8 C 组），双端通用。
- **Light 模式** = 组合 1：Apple 蓝 `#0071e3` + 白底。
- **Dark 模式** = 6c 护眼低饱和蓝（定案）：暖炭底 `#16130f` + 暖白低亮文字 `#d9d2c6` + 强调 `#6fa3d8`（与日间同色相低亮版，默认跟随系统）。
- **设计取舍记录**：中途曾定 Dark=炭黑+紫罗兰（组合 3），经品牌一致性讨论后收敛——跨模式换色相会稀释品牌，改同色相低亮版；用户补充"夜晚护眼"需求 → 暗色全面采用护眼原则（非纯黑底/非纯白字/低饱和强调/避免大面积高能蓝紫），强调色小面积点缀即可。
- 落地物：`packages/ui-reference/design-tokens.json`（v2，单一源：core/colors.light/colors.dark[护眼]/componentHints）、`packages/ui-reference/style-guide.md`（v2，codex 强制规范含护眼三原则与禁止项）。
- 下一步：用该基线跑 1 个 pilot 双端 app（kb-app 前端重做）验证一致性。

## 14. 产品分级 × 技术选型框架（用户 2026-09-04 确立）

后端选型**按产品类型分级，不搞一刀切**：

| 产品类型 | 特征 | 技术策略 |
|---|---|---|
| **C 端单机/本地付费应用** | 用户一次付费、本地使用 | **无需重型后端**：前端（React/Expo）+ 本地存储（IndexedDB / SQLite / AsyncStorage）；数据留在本机；需要时再加极简同步 |
| **多人平台（B 端或 C 端 SaaS）** | 多用户并发、需支撑 | **Java Spring Boot**（用户主场可 debug + 求职同栈 + 可扩展路径：PostgreSQL/MySQL → Redis/消息队列，均为其熟悉域）；备选 Node/TS |

Python 排除（用户自评难找 bug）。pilot（kb-app）属**第一档**：重做前端为主，后端按本地形态定。

**存储选型决定轴（2026-09-04 业界对照定案，详见 `docs/indie-ruleset-research-2026-09-04.md`）**：
- 本地单应用/单设备数据 → **默认 SQLite**（WAL+事务，需检索加 FTS5；sqlite.org 判定"SQLite 竞争的是 fopen()"）；
- 仅「数据须用户用其他工具直接打开 / markdown 生态互通」→ 开放文件格式（Obsidian 模式），但只作**导入/导出通道**，须在简报写明理由并配套可靠性；
- 多人/上线服务 → client/server 数据库（上表 Spring Boot 档），另按 AGENTS.md §10 工程化基线补红线清单。
- kb-app 已按此定案进入 SQLite 迁移（`apps/kb-app/docs/storage-sqlite.brief.md`）。

## 12. 后续待确认

- 第一批 app 的类型清单（决定 type-preset 表）；
- 主色候选（看板试色条圈选 2-3 个方向）。
