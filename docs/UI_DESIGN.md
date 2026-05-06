# UI_DESIGN.md — 会议记录AI工具前端设计规范

> 本文件是项目前端开发的视觉设计权威文档。
> 所有前端开发必须遵守本规范。新增页面或组件前，必须先阅读本文件。
> 本文件与 `frontend/src/styles/tokens.css` 保持同步，如有冲突以本文件为准。

---

## 1. 设计哲学

### 1.1 定调

**简洁、严肃、专业。参考中国明代工笔画与官窑瓷器配色，克制典雅。**

这是一个企业内部工具，服务于真实的工作场景（会议记录、纪要生成）。设计不应分散注意力，应让用户专注于内容本身。

具体体现为：
- 配色取法官窑青白釉——低饱和、有温度、不刺眼
- 排版克制——字重轻、行距宽、留白足
- 交互安静——动画短促、反馈精准、没有多余的装饰

### 1.2 受众

企业内部员工，在 PC 浏览器上使用，偶尔在手机上查看报告。主力场景是桌面端，设计以桌面为主。

### 1.3 不做什么

以下风格与本项目气质不符，**严禁出现**：

- 科技感渐变（蓝紫色 `linear-gradient`）
- 毛玻璃效果（`backdrop-filter: blur`）
- 高饱和强对比配色（RGB 纯色按钮）
- 大圆角卡片（`border-radius > 12px`）
- 重投影（`box-shadow` 扩散半径 `> 8px`）
- 粗体标题（`font-weight: 600` 或 `700`）
- 全大写装饰文字（正文中的 `text-transform: uppercase`）
- 深色主题

---

## 2. 颜色系统

### 2.1 核心色板

所有颜色通过 CSS 变量引用，定义在 `frontend/src/styles/tokens.css`。**禁止在组件中硬编码任何颜色值。**

#### 背景色

| 变量 | 色值 | 用途 |
|------|------|------|
| `--meeting-bg-base` | `#F8F6F1` | 宣纸白，页面底色 |
| `--meeting-bg-surface` | `#FFFFFF` | 卡片、面板、弹窗底色 |
| `--meeting-bg-sidebar` | `#2C3A3F` | 墨青，侧边栏底色 |
| `--meeting-bg-sidebar-hover` | `#3A5A6B` | 侧边栏导航项 hover |
| `--meeting-bg-sidebar-active` | `#3A5A6B` | 侧边栏导航项激活 |
| `--meeting-bg-subtle` | `#F2EFE8` | 输入框底色、代码块底色 |

#### 主色

| 变量 | 色值 | 命名 | 用途 |
|------|------|------|------|
| `--meeting-color-primary` | `#3A5A6B` | 官青深 | 主按钮、激活态、焦点边框 |
| `--meeting-color-primary-hover` | `#2C4A5A` | — | 主色 hover 加深 |
| `--meeting-color-primary-light` | `#7A9E9A` | 汝窑青 | 次要强调、图标、波形 |
| `--meeting-color-primary-bg` | `#EAF0EE` | 青白釉 | 选中背景、信息底色 |

#### 文字色

| 变量 | 色值 | 用途 |
|------|------|------|
| `--meeting-text-primary` | `#2C2C2A` | 墨字，主文字 |
| `--meeting-text-secondary` | `#5F5E5A` | 次要文字、描述 |
| `--meeting-text-tertiary` | `#888780` | 占位符、时间戳、辅助信息 |
| `--meeting-text-sidebar` | `#A8B8B4` | 侧边栏普通导航项 |
| `--meeting-text-sidebar-active` | `#EAF0EE` | 侧边栏激活项文字 |
| `--meeting-text-on-primary` | `#EAF0EE` | 主色按钮上的文字 |

#### 边框色

| 变量 | 色值 | 用途 |
|------|------|------|
| `--meeting-border-base` | `#C8C4B8` | 瓷灰，通用边框、卡片描边 |
| `--meeting-border-light` | `#DDD9D0` | 表格行分割线、更轻的分隔 |
| `--meeting-border-focus` | `#3A5A6B` | 输入框聚焦边框 |

#### 语义色

| 语义 | 底色 | 文字色 | 边框色 | 典型用途 |
|------|------|--------|--------|----------|
| 成功/已完成 | `#E1EDE8` | `#2A5A42` | `#7ABFA0` | 纪要已生成徽章 |
| 警告/进行中 | `#EDE8D8` | `#5A4A1A` | `#C9A84C` | 转录中徽章 |
| 危险/录音 | `#F0E8E8` | `#8B3030` | `#D08080` | 录音中徽章、删除确认 |
| 信息/次要 | `#EAF0EE` | `#3A5A6B` | `#7A9E9A` | 说话人标签、提示 |

#### 点缀色

| 变量 | 色值 | 命名 | 用途 |
|------|------|------|------|
| `--meeting-color-accent` | `#8B7355` | 赭石 | 术语库标签、被纠错文字 |
| `--meeting-color-accent-bg` | `#F2EBE0` | — | 赭石色对应底色 |
| `--meeting-color-danger` | `#C25A5A` | 朱砂红 | 录音按钮，全页面唯一暖色强调 |

### 2.2 配色使用原则

1. **语义优先**：颜色传达意义，不做装饰。绿色只用于成功，红色只用于危险/录音。
2. **最多 3 色共存**：单个页面的主色调不超过 3 种（不含中性灰和边框色）。
3. **朱砂红极克制**：`#C25A5A` 是全站唯一的暖色强调，只给录音按钮和危险操作使用。
4. **有色背景配深色文字**：有色底色（如徽章）上的文字必须取同色系深色，禁止用纯黑 `#000` 或通用灰。

---

## 3. 字体系统

### 3.1 字体栈

```css
font-family: 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;
```

移动端 Safari 自动使用 PingFang SC，Windows 使用 Microsoft YaHei，均属无衬线字体，符合"清晰可读"要求。

### 3.2 字号规范

| 变量 | 大小 | 用途 |
|------|------|------|
| `--meeting-font-size-xs` | `11px` | 分组标签（uppercase）、极小辅助信息 |
| `--meeting-font-size-sm` | `12px` | 时间戳、说话人标签、表格次要列 |
| `--meeting-font-size-base` | `13px` | 通用正文、导航项、表单输入 |
| `--meeting-font-size-md` | `14px` | 卡片标题、列表项标题 |
| `--meeting-font-size-lg` | `16px` | 页面主标题（`h1`）|
| `--meeting-font-size-xl` | `18px` | 报告正文标题 |
| `--meeting-font-size-2xl` | `22px` | 仅用于特殊数据展示 |

### 3.3 字重规范

**全项目只允许两个字重值：**

| 变量 | 值 | 用途 |
|------|----|------|
| `--meeting-font-weight-normal` | `400` | 所有正文、描述、辅助信息 |
| `--meeting-font-weight-medium` | `500` | 标题、强调、按钮文字、徽章文字 |

**严禁使用 `font-weight: 600`、`700`、`bold`。**

### 3.4 行高规范

| 变量 | 值 | 适用场景 |
|------|----|----------|
| `--meeting-line-height-tight` | `1.4` | 按钮、徽章、单行标题 |
| `--meeting-line-height-base` | `1.6` | 通用正文、列表项 |
| `--meeting-line-height-loose` | `1.8` | 转录文本、报告正文（长文阅读）|

### 3.5 文字大小写

- 所有正文、标题、按钮文字：**句子大小写**（Sentence case）
- 分组标签（如侧边栏 section header）：允许 `text-transform: uppercase`，但限 `11px` + `letter-spacing: 0.06em`
- **禁止 Title Case**（每词首字母大写）
- **禁止全大写正文**

---

## 4. 间距系统

基础单位 `4px`，以 `8px` 为主网格。

| 变量 | 值 | 典型用途 |
|------|----|----------|
| `--meeting-space-1` | `4px` | 图标与文字间距、极小内边距 |
| `--meeting-space-2` | `8px` | 紧凑内边距、行内元素间距 |
| `--meeting-space-3` | `12px` | 列表项内边距、标签 padding |
| `--meeting-space-4` | `16px` | 卡片内边距（紧凑）、表单行距 |
| `--meeting-space-5` | `20px` | 卡片内边距（标准）|
| `--meeting-space-6` | `24px` | 卡片内边距（宽松）、页面区块间距 |
| `--meeting-space-8` | `32px` | 页面 section 间距 |
| `--meeting-space-10` | `40px` | 报告正文内边距 |

---

## 5. 圆角系统

**所有圆角不超过 `12px`，这是硬性限制。**

| 变量 | 值 | 用途 |
|------|----|------|
| `--meeting-radius-sm` | `4px` | 徽章、标签、小控件 |
| `--meeting-radius-md` | `6px` | 按钮、输入框、下拉菜单 |
| `--meeting-radius-lg` | `8px` | 卡片、面板、表格容器 |
| `--meeting-radius-xl` | `12px` | 弹窗、侧抽屉（**全站最大值**）|
| `999px` | — | 胶囊形标签、圆形按钮（仅录音按钮）|

---

## 6. 阴影系统

**`box-shadow` 扩散半径（第三个值）不超过 `8px`。禁止大范围扩散阴影。**

| 变量 | 值 | 用途 |
|------|----|------|
| `--meeting-shadow-sm` | `0 1px 4px rgba(44,58,63,0.08)` | 卡片轻浮起 |
| `--meeting-shadow-md` | `0 2px 8px rgba(44,58,63,0.10)` | 弹窗、下拉菜单 |

通常情况下，**优先用 `border` 而不是 `box-shadow`** 来区分层次。

---

## 7. 布局规范

### 7.1 整体布局

```
┌─────────────────────────────────────────────────────┐
│  侧边栏 (200px fixed, 墨青底色)                      │
├─────────────────────────────────────────────────────┤
│  主内容区 (flex: 1, 宣纸白底色)                      │
│  ┌───────────────────────────────────────────────┐  │
│  │ 顶部栏 (56px fixed, 白底, 底部 0.5px 分割线)  │  │
│  │ 页面内容区 (padding: 24px, scroll)            │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

| 变量 | 值 |
|------|----|
| `--meeting-sidebar-width` | `200px` |
| `--meeting-topbar-height` | `56px` |

### 7.2 侧边栏规范

**底色**：`#2C3A3F`（墨青）

**Logo 区**：
- 产品名：13px / 500 / `#EAF0EE`
- 副标题：11px / 400 / `#7A9E9A`
- 底部：`0.5px solid #3A5A6B` 分割线

**分组标签**（section header）：
- 11px / 500 / `#888780`
- `text-transform: uppercase`
- `letter-spacing: 0.06em`
- `padding: 12px 16px 4px`

**导航项**：
- 普通态：13px / 400 / `#A8B8B4`，`padding: 7px 16px`
- hover：`background: #3A5A6B`，文字 `#EAF0EE`
- 激活态：`background: #3A5A6B`，文字 `#EAF0EE`，**左侧 2px 竖条** `border-left: 2px solid #7A9E9A`，需用 `padding-left: 14px` 补偿

### 7.3 顶部栏规范

- 高度：`56px`
- 背景：`#FFFFFF`
- 底部分割线：`0.5px solid #DDD9D0`
- 左侧：页面标题（14px / 500 / `#2C2C2A`）+ 副标题（12px / 400 / `#888780`）
- 右侧：主操作按钮

### 7.4 页面内容区

- `padding: 24px`
- 内容 `max-width: 1200px`，超宽屏居中
- 报告详情页内容区：`max-width: 780px` 居中（长文阅读适宜宽度）

---

## 8. 核心组件规范

### 8.1 按钮

**主按钮（Primary）**：
```css
background: #3A5A6B;
color: #EAF0EE;
border: none;
border-radius: 6px;
padding: 7px 16px;
font-size: 13px;
font-weight: 500;
transition: background-color 200ms ease;

/* hover */
background: #2C4A5A;
transform: translateY(-1px);

/* active */
transform: translateY(0);
```

**次级按钮（Secondary）**：
```css
background: transparent;
color: #2C2C2A;
border: 0.5px solid #C8C4B8;
border-radius: 6px;
padding: 7px 16px;
font-size: 13px;
font-weight: 400;

/* hover */
border-color: #3A5A6B;
color: #3A5A6B;
```

**文字链接按钮（Text）**：
```css
background: transparent;
border: none;
color: #888780;
font-size: 13px;
font-weight: 400;

/* hover */
color: #3A5A6B;
```

**危险按钮（Danger）**：仅用于删除等不可逆操作。
```css
background: transparent;
border: 0.5px solid #D08080;
color: #8B3030;
border-radius: 6px;
padding: 7px 16px;

/* hover */
background: #F0E8E8;
```

**录音按钮**（特殊圆形大按钮）：
```css
width: 52px;
height: 52px;
border-radius: 50%;
border: 2px solid #C25A5A;  /* 待录音状态 */
background: transparent;

/* 录音中状态 */
background: #C25A5A;
border-color: #C25A5A;
animation: recording-pulse 1.2s ease-in-out infinite;

/* 已完成状态 */
background: #E1EDE8;
border-color: #7ABFA0;
```

### 8.2 输入框

继承 Element Plus 覆盖后的主题，额外规范：
- 底色：`#FFFFFF`（普通）或 `#F8F6F1`（页面底色内的输入框）
- 边框：`0.5px solid #C8C4B8`
- 聚焦边框：`0.5px solid #3A5A6B`（无蓝色光晕，`box-shadow: none`）
- placeholder：`#B4B2A9`
- 字号：`13px`

### 8.3 状态徽章

三种会议状态的精确规格：

```css
/* 纪要已生成 */
.badge-done {
  background: #E1EDE8;
  color: #2A5A42;
  border: 0.5px solid #7ABFA0;
}

/* 转录中 */
.badge-processing {
  background: #EDE8D8;
  color: #5A4A1A;
  border: 0.5px solid #C9A84C;
}

/* 录音中 */
.badge-recording {
  background: #F0E8E8;
  color: #8B3030;
  border: 0.5px solid #D08080;
}

/* 通用徽章基础样式 */
.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 999px;
  display: inline-block;
  white-space: nowrap;
}
```

### 8.4 模板选择标签

```css
/* 未选中 */
.tpl-tag {
  border: 0.5px solid #C8C4B8;
  color: #5F5E5A;
  background: transparent;
  border-radius: 999px;
  padding: 5px 14px;
  font-size: 12px;
  font-weight: 400;
  cursor: pointer;
  transition: all 200ms ease;
}

/* 选中 */
.tpl-tag.active {
  background: #3A5A6B;
  color: #EAF0EE;
  border-color: #3A5A6B;
  font-weight: 500;
}
```

### 8.5 卡片

```css
.meeting-card {
  background: #FFFFFF;
  border: 0.5px solid #C8C4B8;
  border-radius: 8px;
  padding: 16px 20px;
}

/* 悬停态（可点击卡片） */
.meeting-card:hover {
  background: #F8F6F1;
  border-color: #B4B2A9;
  transition: background-color 120ms ease, border-color 120ms ease;
}
```

### 8.6 步骤条（录音工作台专用）

4 步线性步骤条，状态分三种：

```css
/* 已完成步骤 */
.step-done {
  background: #E1EDE8;
  color: #2A5A42;
  border: 0.5px solid #7ABFA0;
}

/* 当前步骤 */
.step-active {
  background: #EAF0EE;
  color: #3A5A6B;
  border: 0.5px solid #7A9E9A;
  font-weight: 500;
}

/* 未开始 */
.step-pending {
  background: #F2EFE8;
  color: #888780;
  border: 0.5px solid #DDD9D0;
}
```

### 8.7 弹窗（el-dialog）

- `width: 560px`（标准）或 `640px`（含长文编辑）
- `border-radius: 12px`（允许的最大值）
- 标题：14px / 500 / `#2C2C2A`
- 底部操作按钮：右对齐，取消在左，确认在右

### 8.8 表格（el-table）

- 表头：`background: #F8F6F1`，12px / 500 / `#888780`，`text-transform: uppercase`，`letter-spacing: 0.04em`
- 行高：`48px`
- 行分割线：`0.5px solid #DDD9D0`
- 行 hover：`background: #F8F6F1`
- 操作列按钮：文字链接样式，hover 变主色

---

## 9. 动效规范

### 9.1 过渡时长

**严禁超过 300ms。**

| 变量 | 值 | 适用场景 |
|------|----|----------|
| `--meeting-transition-fast` | `120ms ease` | hover 背景色变化、边框颜色 |
| `--meeting-transition-base` | `200ms ease` | 按钮状态、输入框聚焦 |
| `--meeting-transition-slow` | `280ms ease` | 页面路由切换、弹窗出现 |

### 9.2 允许的动画

```css
/* 录音按钮脉冲（录音中状态） */
@keyframes recording-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.75; transform: scale(0.96); }
}
/* 时长 1.2s，循环 */

/* 音频波形（录音中） */
/* 16 根竖条，各条使用不同 animation-delay（0–0.7s），高度在 6–28px 间变化 */
/* 时长 0.8s，循环，ease-in-out */

/* 流式输出光标 */
@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}
/* 时长 0.8s，step-end，循环 */

/* 页面路由切换 */
/* opacity: 0 → 1，280ms ease */

/* Loading 转圈 */
/* border-top-color 旋转，360deg，600ms linear，循环 */
```

### 9.3 禁止的动效

- 位移超过 `4px` 的平移动画（除 tooltip/dropdown 出现）
- `transform: scale` 超过 `1.05` 的放大
- 颜色渐变动画（`background` 的 `transition` 仅用于 hover 态切换）
- 任何 `animation-duration > 300ms` 的非循环动画

---

## 10. 图标规范

本项目使用 **SVG 内联图标**，不使用图标字体（避免字重不可控问题）。

- 尺寸：`16px × 16px`（行内图标）、`20px × 20px`（导航图标）
- 颜色：通过 `currentColor` 继承父元素文字色，**不单独设置颜色**
- 描边宽度：`1.5px`，`stroke-linecap: round`，`stroke-linejoin: round`
- 填充：优先描边图标（`fill: none`），仅状态指示使用填充图标

---

## 11. 页面级规范速查

### 录音工作台

- 核心交互区垂直居中于内容区上半部
- 步骤条始终可见（吸顶或置于顶部）
- 录音按钮是唯一视觉焦点，周围留白充足（最少 `32px`）

### 会议列表

- 默认按时间倒序，最新的在最上
- 状态徽章右对齐，宽度固定（`min-width: 72px`）避免跳动
- 空状态：居中插图（SVG）+ 提示文字 + 主操作按钮

### 转录编辑器

- 左右两栏布局：左侧时间轴（`320px`）+ 右侧完整文本编辑区
- 被纠错的术语用赭石色底色标注，hover 显示原文 tooltip
- 保存状态：右上角 "已保存" 绿色文字（3s 后自动消失）

### 报告查看页

- 报告内容区 `max-width: 780px` 居中，营造文档阅读感
- 流式输出时，内容从顶部向下逐字出现，不跳屏
- 章节锚点导航（长报告）：右侧悬浮目录，`position: sticky`

### 模板管理

- 卡片网格：`repeat(auto-fill, minmax(280px, 1fr))`
- Prompt 编辑区使用等宽字体（`font-family: monospace`）

### 术语库

- 表格为主，支持搜索过滤
- 术语标签用赭石色系

---

## 12. 代码规范（前端样式部分）

1. **禁止硬编码颜色**：所有颜色值必须通过 `var(--meeting-*)` 引用。
   - 违例检查命令：`grep -r '#[0-9a-fA-F]\{3,6\}' frontend/src/views frontend/src/components --include="*.vue" --include="*.css"`
   - 例外：`tokens.css` 和 `el-theme.css` 本身。

2. **CSS 变量命名**：本项目统一使用 `--meeting-` 前缀，区别于 Element Plus 的 `--el-` 前缀。

3. **Scoped 样式的限制**：组件的 `<style scoped>` 内只写布局和结构，颜色、字号、间距全部用变量。`--meeting-*` 变量定义在 `:root`，scoped 内可以直接 `var()` 引用。

4. **Element Plus 组件样式覆盖**：在 `el-theme.css` 统一覆盖，**禁止在单个组件内用 `:deep()` 覆盖 Element Plus 内部样式**（影响全局一致性）。

5. **每新增一个页面或组件**，完成后必须对照第 12 节的 checklist 自查。

---

## 13. 验收 Checklist

每个页面/组件提交前必须逐项确认：

**颜色**
- [ ] 无硬编码 hex 色值（运行 grep 命令确认）
- [ ] 有色背景上的文字使用同色系深色，非纯黑
- [ ] 朱砂红 `#C25A5A` 仅用于录音按钮和危险操作

**字体**
- [ ] 无 `font-weight: 600` 或 `700`
- [ ] 正文无 `text-transform: uppercase`（分组标签除外）

**布局与圆角**
- [ ] 圆角不超过 `8px`（弹窗最大 `12px`）
- [ ] 无 `linear-gradient` 或 `radial-gradient` 背景
- [ ] 无 `backdrop-filter`

**阴影**
- [ ] `box-shadow` 扩散半径不超过 `8px`
- [ ] 无不必要的 `box-shadow`（优先用 `border`）

**动效**
- [ ] 所有 `transition-duration ≤ 300ms`
- [ ] 非循环动画时长 ≤ 300ms

**组件一致性**
- [ ] 三种状态徽章颜色符合规范
- [ ] 按钮样式（主 / 次 / 文字 / 危险）符合规范
- [ ] 侧边栏激活态有 2px 左竖条

---

*最后更新：2025年*
*与 `frontend/src/styles/tokens.css` 同步维护*
