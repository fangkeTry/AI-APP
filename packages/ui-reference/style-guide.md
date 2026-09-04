# AI-APP 前端风格指南 v1（codex/dsh 生成 UI 时必须遵守）

> 2026-09-04 用户定案。配套：`design-tokens.json`（单一源）、`styleboard.html`（视觉对照）。
> 双端通用：Web（React+Tailwind）与原生（Expo+NativeWind）同一套 tokens 语义。

## 1. 结构基线（一律如此）

- 基底 = **Apple 明亮留白**：大留白、浅色分层、字阶克制、圆角、**主按钮胶囊形**、卡片 hairline 边框无重阴影。
- **Light 模式** = Apple 蓝 `#0071e3` + 白底（styleboard 组合 1）。
- **Dark 模式** = 炭黑底 `#0e0e12` + 紫罗兰 `#7c6cf0`（styleboard 组合 3），默认跟随系统。
- 移动优先：断点从手机起；触控目标 ≥44px；弱设备可用（CSS-first、无重型动效）。

## 2. 禁止项（红线）

- ❌ 政企/后台密集风：粗边框、表格化堆砌、厚重渐变、企业蓝灰配色。
- ❌ 高饱和大色块、花哨动效库（Aceternity/Magic 只允许摘用轻量局部）。
- ❌ 引入整库组件依赖（一律拷贝本地、按需）。
- ❌ 图标字体；只允许 SVG 线性图标（lucide 风格），按需引入。

## 3. 组件形态速查（细节值全在 tokens）

| 组件 | 规范 |
|---|---|
| 主按钮 | pill 胶囊、`accent` 底、`onAccent` 文字；hover 用 `accentHover`；最小高度 44px |
| 次按钮 | ghost：透明底、hairline 边框、`text` 文字 |
| 卡片 | `surface` 底 + hairline 边框 + radius md~lg；阴影用 `shadowCard`（极轻） |
| 输入框 | `surfaceSoft` 底或带边框；聚焦 = accent 描边 2px；placeholder = `textTertiary` |
| 徽章/标签 | `accentSoft` 底 + accent 文字，pill |
| 导航 | 透明底 + 文字链接；logo 用 accent 圆角小方块 |
| 列表 | 行距 ≥ spacing lg；次级信息 `textSecondary` |

## 4. 排版

- 系统字体栈（见 tokens `fontFamily.ui`），**不引入网络字体**（弱设备+中文体积）。
- 字号层级：正文 base(15) / 次级 sm(13) / 标题 xl~3xl；标题用 semibold，正文 regular。
- Dark 模式层级靠**亮度差**（text / textSecondary / textTertiary），不靠边框。

## 5. 生成清单（codex 每次产出 UI 前自查）

1. 结构是否 Apple 明亮留白（留白是否够大、阴影是否过重）？
2. 颜色是否全部来自 tokens（不许硬编码近似色）？Light/Dark 是否都可用？
3. 是否移动优先（先手机后 PC 断点）、触控 ≥44px？
4. 是否零新增重量级依赖、图标为按需 SVG？
5. 与 styleboard 组合 1/3 的氛围是否一致？

## 6. 样式来源

- tokens：`packages/ui-reference/design-tokens.json`
- 视觉对照：`packages/ui-reference/styleboard.html`（组合 1 = Light，组合 3 = Dark）
