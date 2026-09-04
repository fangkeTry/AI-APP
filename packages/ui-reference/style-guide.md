# AI-APP 前端风格指南 v2（codex/dsh 生成 UI 时必须遵守）

> 2026-09-04 用户定案（v2：暗色改为护眼低饱和蓝，品牌色相统一）。
> 配套：`design-tokens.json`（单一源）、`styleboard.html`（视觉对照：Light=组合 1，Dark=6c）。
> 双端通用：Web（React+Tailwind）与原生（Expo+NativeWind）同一套 tokens 语义。

## 1. 结构基线（一律如此）

- 基底 = **Apple 明亮留白**：大留白、浅色分层、字阶克制、圆角、**主按钮胶囊形**、卡片 hairline 边框无重阴影。
- **Light 模式** = Apple 蓝 `#0071e3` + 白底（styleboard 组合 1）。
- **Dark 模式** = **护眼低饱和蓝**（styleboard 6c）：暖炭底 `#16130f`、暖白低亮文字 `#d9d2c6`、强调 `#6fa3d8`（与日间同色相低亮版）。默认跟随系统，可手动切换。
- 移动优先：断点从手机起；触控目标 ≥44px；弱设备可用（CSS-first、无重型动效）。

## 2. 禁止项（红线）

- ❌ 政企/后台密集风：粗边框、表格化堆砌、厚重渐变、企业蓝灰配色。
- ❌ 高饱和大色块、花哨动效库（Aceternity/Magic 只允许摘用轻量局部）。
- ❌ 引入整库组件依赖（一律拷贝本地、按需）。
- ❌ 图标字体；只允许 SVG 线性图标（lucide 风格），按需引入。
- ❌ 暗色模式用纯黑背景 + 纯白文字（眩光）；禁止大面积高饱和蓝紫强调。

## 3. 护眼原则（暗色模式硬性要求）

- 背景**不用纯黑**：用暖炭 `#16130f` 系（带暖色相，降低眩光）。
- 文字**不用纯白**：正文 `#d9d2c6`（亮度 ~80%）、次级降为 `textSecondary`。
- 强调色**低饱和**：暗底用 `#6fa3d8` 系，避免高能亮蓝紫大面积出现；强调仅小面积点缀。
- 层级靠**亮度差**表达，不靠边框与高饱和色。

## 4. 组件形态速查（细节值全在 tokens）

| 组件 | 规范 |
|---|---|
| 主按钮 | pill 胶囊、`accent` 底；Light 用 `onAccent=#fff`，Dark 用 `onAccent=#16130f`（深字浅钮，护眼）；hover 用 `accentHover`；最小高度 44px |
| 次按钮 | ghost：透明底、hairline 边框、`text` 文字 |
| 卡片 | `surface` 底 + hairline 边框 + radius md~lg；阴影用 `shadowCard`（极轻） |
| 输入框 | `surfaceSoft` 底或带边框；聚焦 = accent 描边 2px；placeholder = `textTertiary` |
| 徽章/标签 | `accentSoft` 底 + accent 文字，pill |
| 导航 | 透明底 + 文字链接；logo 用 accent 圆角小方块 |
| 列表 | 行距 ≥ spacing lg；次级信息 `textSecondary` |

## 5. 排版

- 系统字体栈（见 tokens `fontFamily.ui`），**不引入网络字体**（弱设备+中文体积）。
- 字号层级：正文 base(15) / 次级 sm(13) / 标题 xl~3xl；标题用 semibold，正文 regular。
- 层级靠亮度/字重差表达，不靠边框。

## 6. 生成清单（codex 每次产出 UI 前自查）

1. 结构是否 Apple 明亮留白（留白是否够大、阴影是否过重）？
2. 颜色是否全部来自 tokens（不许硬编码近似色）？Light/Dark 是否都可用？
3. 暗色是否满足护眼三原则（非纯黑底/非纯白字/低饱和强调）？
4. 是否移动优先（先手机后 PC 断点）、触控 ≥44px？
5. 是否零新增重量级依赖、图标为按需 SVG？
6. 与 styleboard Light=组合 1 / Dark=6c 的氛围是否一致？

## 7. 样式来源

- tokens：`packages/ui-reference/design-tokens.json`
- 视觉对照：`packages/ui-reference/styleboard.html`（Light=组合 1，Dark=6c 护眼低饱和蓝）

