# FRONTEND_REDESIGN.md — 前端视觉改造任务

> 本文件供 Claude Code 执行。改造原则：**换皮不换骨**。
> 所有 `src/api/`、`src/stores/`、组件内的业务逻辑、API 调用代码**一律不动**，只重写视觉层。

---

## 设计定调

**风格**：简洁、严肃、专业。参考中国明代工笔画与官窑瓷器配色，克制典雅。

**核心禁止项**（违反即返工）：
- 禁止渐变背景（`background: linear-gradient(...)` 全部删除）
- 禁止毛玻璃效果（`backdrop-filter` 全部删除）
- 禁止 `font-weight: 600` 或 `700`，只允许 `400` 和 `500`
- 禁止圆角超过 `8px`（卡片最大 `12px`）
- 禁止 `box-shadow` 扩散半径超过 `8px`
- 禁止硬编码颜色值（所有颜色必须通过 `var(--...)` 引用）
- 禁止深色主题

---

## 第一步：重写 tokens.css

路径：`frontend/src/styles/tokens.css`

**完整替换为以下内容**：

```css
/* ============================================
   官窑瓷器设计系统 — Design Tokens
   命名规范：--meeting-{category}-{variant}
   ============================================ */

:root {
  /* ---------- 背景色 ---------- */
  --meeting-bg-base: #F8F6F1;        /* 宣纸白，页面底色 */
  --meeting-bg-surface: #FFFFFF;     /* 卡片/面板底色 */
  --meeting-bg-sidebar: #2C3A3F;     /* 墨青，侧边栏底色 */
  --meeting-bg-sidebar-hover: #3A5A6B; /* 侧边栏 hover */
  --meeting-bg-sidebar-active: #3A5A6B; /* 侧边栏激活项 */
  --meeting-bg-subtle: #F2EFE8;      /* 输入框、代码块底色 */

  /* ---------- 主色 ---------- */
  --meeting-color-primary: #3A5A6B;       /* 官青深，主操作色 */
  --meeting-color-primary-hover: #2C4A5A; /* 主色 hover 加深 */
  --meeting-color-primary-light: #7A9E9A; /* 汝窑青，点缀/次要 */
  --meeting-color-primary-bg: #EAF0EE;   /* 主色浅底，选中背景 */

  /* ---------- 文字色 ---------- */
  --meeting-text-primary: #2C2C2A;   /* 墨字，主文字 */
  --meeting-text-secondary: #5F5E5A; /* 次要文字，说明 */
  --meeting-text-tertiary: #888780;  /* 占位符、提示 */
  --meeting-text-sidebar: #A8B8B4;   /* 侧边栏普通导航项 */
  --meeting-text-sidebar-active: #EAF0EE; /* 侧边栏激活项文字 */
  --meeting-text-on-primary: #EAF0EE; /* 主色按钮上的文字 */

  /* ---------- 边框色 ---------- */
  --meeting-border-base: #C8C4B8;    /* 瓷灰，通用边框 */
  --meeting-border-light: #DDD9D0;   /* 更浅的分割线 */
  --meeting-border-focus: #3A5A6B;   /* 输入框聚焦边框 */

  /* ---------- 语义色 ---------- */
  /* 成功/已完成 */
  --meeting-color-success: #2A5A42;
  --meeting-color-success-bg: #E1EDE8;
  --meeting-color-success-border: #7ABFA0;
  /* 警告/进行中 */
  --meeting-color-warning: #5A4A1A;
  --meeting-color-warning-bg: #EDE8D8;
  --meeting-color-warning-border: #C9A84C;
  /* 危险/录音 */
  --meeting-color-danger: #C25A5A;
  --meeting-color-danger-dark: #A04040;
  --meeting-color-danger-bg: #F0E8E8;
  --meeting-color-danger-border: #D08080;
  /* 信息/次要 */
  --meeting-color-info: #3A5A6B;
  --meeting-color-info-bg: #EAF0EE;
  --meeting-color-info-border: #7A9E9A;

  /* ---------- 赭石点缀色（用于术语库、标签等） ---------- */
  --meeting-color-accent: #8B7355;
  --meeting-color-accent-bg: #F2EBE0;

  /* ---------- 字号 ---------- */
  --meeting-font-size-xs: 11px;
  --meeting-font-size-sm: 12px;
  --meeting-font-size-base: 13px;
  --meeting-font-size-md: 14px;
  --meeting-font-size-lg: 16px;
  --meeting-font-size-xl: 18px;
  --meeting-font-size-2xl: 22px;

  /* ---------- 字重（只允许这两个值）---------- */
  --meeting-font-weight-normal: 400;
  --meeting-font-weight-medium: 500;

  /* ---------- 行高 ---------- */
  --meeting-line-height-tight: 1.4;
  --meeting-line-height-base: 1.6;
  --meeting-line-height-loose: 1.8;

  /* ---------- 间距（8px 基础网格）---------- */
  --meeting-space-1: 4px;
  --meeting-space-2: 8px;
  --meeting-space-3: 12px;
  --meeting-space-4: 16px;
  --meeting-space-5: 20px;
  --meeting-space-6: 24px;
  --meeting-space-8: 32px;
  --meeting-space-10: 40px;
  --meeting-space-12: 48px;

  /* ---------- 圆角（不超过 12px）---------- */
  --meeting-radius-sm: 4px;   /* 标签、小控件 */
  --meeting-radius-md: 6px;   /* 按钮、输入框 */
  --meeting-radius-lg: 8px;   /* 卡片、面板 */
  --meeting-radius-xl: 12px;  /* 模态框（最大值，不可超过）*/

  /* ---------- 阴影（扩散半径不超过 8px）---------- */
  --meeting-shadow-sm: 0 1px 4px rgba(44, 58, 63, 0.08);
  --meeting-shadow-md: 0 2px 8px rgba(44, 58, 63, 0.10);

  /* ---------- 过渡 ---------- */
  --meeting-transition-fast: 120ms ease;
  --meeting-transition-base: 200ms ease;
  --meeting-transition-slow: 280ms ease; /* 不超过 300ms */

  /* ---------- 布局 ---------- */
  --meeting-sidebar-width: 200px;
  --meeting-topbar-height: 56px;
}
```

---

## 第二步：覆盖 Element Plus 主题

路径：`frontend/src/styles/el-theme.css`（若不存在则新建，并在 `main.ts` 中 import）

```css
/* Element Plus 主题覆盖 — 官窑瓷器风格 */
:root {
  /* 主色系 */
  --el-color-primary: #3A5A6B;
  --el-color-primary-light-3: #7A9E9A;
  --el-color-primary-light-5: #A8C4C0;
  --el-color-primary-light-7: #D0E4E0;
  --el-color-primary-light-8: #E1EEEC;
  --el-color-primary-light-9: #EAF0EE;
  --el-color-primary-dark-2: #2C4A5A;

  /* 成功/警告/危险 */
  --el-color-success: #2A5A42;
  --el-color-warning: #5A4A1A;
  --el-color-danger: #C25A5A;
  --el-color-info: #5F5E5A;

  /* 文字 */
  --el-text-color-primary: #2C2C2A;
  --el-text-color-regular: #5F5E5A;
  --el-text-color-secondary: #888780;
  --el-text-color-placeholder: #B4B2A9;

  /* 边框 */
  --el-border-color: #C8C4B8;
  --el-border-color-light: #DDD9D0;
  --el-border-color-lighter: #E8E4DC;
  --el-border-color-extra-light: #F2EFE8;

  /* 背景 */
  --el-bg-color: #FFFFFF;
  --el-bg-color-page: #F8F6F1;
  --el-bg-color-overlay: #FFFFFF;
  --el-fill-color-blank: #FFFFFF;
  --el-fill-color: #F8F6F1;
  --el-fill-color-light: #F2EFE8;
  --el-fill-color-lighter: #F8F6F1;

  /* 圆角 */
  --el-border-radius-base: 6px;
  --el-border-radius-small: 4px;
  --el-border-radius-round: 999px;

  /* 字号 */
  --el-font-size-base: 13px;
  --el-font-size-small: 12px;
  --el-font-size-large: 14px;

  /* 阴影 */
  --el-box-shadow: 0 2px 8px rgba(44, 58, 63, 0.10);
  --el-box-shadow-light: 0 1px 4px rgba(44, 58, 63, 0.08);

  /* 禁用所有 Element Plus 的 font-weight: bold/600/700 */
  --el-font-weight-primary: 500;
}

/* 去掉 el-button 的多余阴影 */
.el-button { box-shadow: none !important; }
.el-button:hover { box-shadow: none !important; }

/* 输入框聚焦边框 */
.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px #3A5A6B inset !important;
}
```

---

## 第三步：重写 AppLayout.vue

路径：`frontend/src/layouts/AppLayout.vue`（或项目现有的 layout 文件）

**结构要求**：
```
┌──────────────────────────────────────────────────┐
│  侧边栏 (200px, 墨青 #2C3A3F)                    │
│  ┌────────────────────────────────────────────┐  │
│  │ Logo区域 (底部 0.5px 分割线)               │  │
│  │ 导航分组标签 (11px uppercase 赭石色)       │  │
│  │ 导航项 (激活态：#3A5A6B 底色，汝窑青左竖条)│  │
│  └────────────────────────────────────────────┘  │
│  主内容区 (flex:1, 宣纸白 #F8F6F1)               │
│  ┌────────────────────────────────────────────┐  │
│  │ 顶部栏 (56px, 白底, 底部 0.5px 分割线)     │  │
│  │ 页面内容区 (<router-view>)                 │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

**侧边栏导航项激活态**：左侧 2px 竖条（`border-left: 2px solid #7A9E9A`），背景 `#3A5A6B`，文字 `#EAF0EE`。

**侧边栏 Logo 区**：产品名 13px/500/`#EAF0EE`，副标题 11px/400/`#7A9E9A`。

---

## 第四步：逐页改造（按顺序执行）

### 4.1 录音工作台页（最高优先级）

**文件**：`frontend/src/views/RecordingView.vue`（或对应文件名）

**视觉规格**：

**步骤条**：
- 4 步：录音 → 转录 → 选模板 → 生成报告
- 已完成步骤：`#E1EDE8` 底色，`#2A5A42` 文字，✓ 图标
- 当前步骤：`#EAF0EE` 底色，`#3A5A6B` 文字，加粗数字
- 未开始：`#F2EFE8` 底色，`#888780` 文字

**录音控件区**：
- 未录音状态：空心圆按钮，`border: 2px solid #C25A5A`，内部圆点 `#C25A5A`
- 录音中状态：实心圆背景 `#C25A5A`，内部方形停止图标，脉冲动画（`opacity` 0.7→1 循环，1.2s）
- 已完成状态：`#E1EDE8` 底色，绿色打勾，显示时长

**波形显示**（录音中）：
- 16 根竖条，宽 3px，圆角 2px，颜色 `#7A9E9A`
- 高度随机在 6–28px 之间动态变化（CSS animation，各条错峰）

**会议信息表单**：
- 字段：会议名称、会议日期、参会人员
- `el-input` 使用覆盖后的主题，label 11px/500/`#888780` uppercase

**模板选择**：
- 圆角胶囊标签（`border-radius: 999px`）
- 未选：`border: 0.5px solid #C8C4B8`，`#5F5E5A` 文字
- 已选：`background: #3A5A6B`，`#EAF0EE` 文字

---

### 4.2 会议列表页

**文件**：`frontend/src/views/MeetingListView.vue`（或对应文件名）

**视觉规格**：

**列表项**（`el-table` 或自定义卡片）：
- 底色白，行间 `0.5px solid #DDD9D0` 分割线
- hover：行背景变 `#F8F6F1`
- 会议名：13px/500/`#2C2C2A`
- 时间/时长：12px/400/`#888780`

**状态徽章**（三种）：
```
已生成：background #E1EDE8, color #2A5A42, border 0.5px solid #7ABFA0
转录中：background #EDE8D8, color #5A4A1A, border 0.5px solid #C9A84C
录音中：background #F0E8E8, color #8B3030, border 0.5px solid #D08080
```
- 尺寸：11px/500，padding 2px 8px，border-radius 999px

**顶部操作栏**：右侧"新建录音"主按钮，`background #3A5A6B`，`color #EAF0EE`，`border-radius 6px`，`padding 7px 16px`，hover 变 `#2C4A5A`。

---

### 4.3 转录编辑器页

**文件**：`frontend/src/views/TranscriptView.vue`（或对应文件名）

**视觉规格**：

**片段时间轴**（左侧）：
- 时间戳：11px/`#888780`/`font-family: monospace`
- 说话人标签：12px/500/`#3A5A6B`，`background #EAF0EE`，`border-radius 4px`
- 片段文本：13px/400/`#2C2C2A`，`line-height: 1.8`
- 片段间距：`margin-bottom: 16px`，底部 `0.5px solid #DDD9D0`

**编辑状态**：
- 点击片段进入编辑：`border: 0.5px solid #3A5A6B`，`background #F8F6F1`
- 保存按钮：小尺寸，`padding 4px 10px`，主色风格

**已纠错标注**：
- 被替换的术语：`background #F2EBE0`，`color #8B7355`，`border-bottom: 1px solid #8B7355`

---

### 4.4 报告生成/查看页

**文件**：`frontend/src/views/SummaryView.vue`（或对应文件名）

**视觉规格**：

**生成中状态**（流式输出）：
- 全屏中央：圆形进度指示器（纯 CSS，旋转动画），`border: 2px solid #EAF0EE`，`border-top-color: #3A5A6B`
- 文字逐字出现时，光标闪烁效果：`::after { content: '|'; animation: blink 0.8s step-end infinite }`

**报告内容区**：
- 白色卡片容器，`border: 0.5px solid #C8C4B8`，`border-radius 8px`，`padding 32px 40px`
- `max-width: 780px`，居中显示
- 标题：16px/500/`#2C2C2A`
- 正文：14px/400/`#2C2C2A`，`line-height: 1.8`
- 分割线：`0.5px solid #DDD9D0`
- `h2` 章节标题：14px/500/`#3A5A6B`，底部 `0.5px solid #C8C4B8`，`padding-bottom 8px`

**操作按钮区**（右上角）：
- 下载 Word：主色按钮
- 下载 Markdown：次级按钮（`border: 0.5px solid #C8C4B8`，透明底色）
- 重新生成：文字链接样式，`color #888780`，hover `#3A5A6B`

---

### 4.5 模板管理页

**文件**：`frontend/src/views/TemplateView.vue`（或对应文件名）

**视觉规格**：

**模板卡片列表**：
- `display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px`
- 每张卡片：白底，`border: 0.5px solid #C8C4B8`，`border-radius 8px`，`padding 16px 20px`
- 模板名：13px/500/`#2C2C2A`
- 模板描述：12px/400/`#888780`，最多显示 2 行（`-webkit-line-clamp: 2`）
- 底部：最后修改时间（12px/`#B4B2A9`）+ 操作按钮（编辑/删除）

**新建模板按钮**：右上角，主色风格，与列表页一致。

**模板编辑弹窗**：
- `el-dialog`，`width: 640px`
- Prompt 内容用 `el-input type="textarea"`，`rows: 16`，`font-family: monospace`，`font-size: 13px`

---

### 4.6 术语库页面

**文件**：`frontend/src/views/TermView.vue`（或对应文件名）

**视觉规格**：

**术语列表**：`el-table`，使用覆盖后的 Element Plus 主题即可，无需特殊处理。

**术语标签**：`background #F2EBE0`，`color #8B7355`，`border: 0.5px solid #C9A88A`，`border-radius 4px`，12px/400。

---

## 第五步：全局微交互

在 `frontend/src/styles/global.css`（或 `main.css`）中追加：

```css
/* 全局过渡：所有交互 ≤300ms */
*, *::before, *::after {
  transition-duration: 0s; /* 默认关闭，按需开启 */
}

/* 按钮 hover */
.btn-primary,
.el-button--primary {
  transition: background-color var(--meeting-transition-base),
              transform var(--meeting-transition-fast);
}
.btn-primary:hover,
.el-button--primary:hover {
  transform: translateY(-1px);
}
.btn-primary:active,
.el-button--primary:active {
  transform: translateY(0);
}

/* 卡片/列表行 hover */
.meeting-card,
.el-table__row {
  transition: background-color var(--meeting-transition-fast);
}

/* 录音按钮脉冲动画 */
@keyframes recording-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.75; transform: scale(0.96); }
}
.recording-active {
  animation: recording-pulse 1.2s ease-in-out infinite;
}

/* 页面路由切换 */
.page-enter-active,
.page-leave-active {
  transition: opacity var(--meeting-transition-slow);
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}

/* 光标闪烁（流式输出用）*/
@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.streaming-cursor::after {
  content: '|';
  color: #3A5A6B;
  animation: cursor-blink 0.8s step-end infinite;
}
```

---

## 验收 Checklist（每页完成后必查）

执行完每个页面后，逐条确认：

- [ ] 无硬编码颜色（grep `#[0-9a-fA-F]` 检查，`tokens.css` 和 `el-theme.css` 除外）
- [ ] 无 `font-weight: 600` 或 `700`
- [ ] 无渐变背景（grep `linear-gradient` 或 `radial-gradient`）
- [ ] 无 `backdrop-filter`
- [ ] 圆角未超过 `8px`（卡片可到 `12px`）
- [ ] 所有过渡动画 `transition-duration ≤ 300ms`
- [ ] `box-shadow` 扩散半径 `≤ 8px`
- [ ] 侧边栏导航激活状态正确显示
- [ ] 三种会议状态徽章颜色正确
- [ ] 录音按钮三态（待录/录音中/已完成）视觉正确

---

## 执行顺序总结

```
Step 1: 重写 tokens.css
Step 2: 新建/覆盖 el-theme.css，在 main.ts 中 import
Step 3: 重写 AppLayout.vue（侧边栏 + 顶部栏骨架）
Step 4: 在 global.css 追加全局微交互样式
Step 5: RecordingView.vue（录音工作台）
Step 6: MeetingListView.vue（会议列表）
Step 7: TranscriptView.vue（转录编辑器）
Step 8: SummaryView.vue（报告查看页）
Step 9: TemplateView.vue（模板管理）
Step 10: TermView.vue（术语库）
Step 11: 全站验收，运行 checklist
```

每个 Step 完成后独立 commit，commit message 格式：
`style: redesign [页面名] — 官窑瓷器主题`

---

## 注意事项

1. **不要动** `src/api/`、`src/stores/`、任何 `.ts` 业务逻辑文件
2. **不要动** 后端任何文件
3. 若某页面文件名与本文档不符，以实际文件为准，规格要求不变
4. 若某组件已使用 `scoped` CSS，将 token 引用放在 `:root` 或非 scoped 的全局样式中
5. Element Plus 组件的 `--el-*` 变量覆盖**必须在 `:root` 下定义**，不能放在 scoped 中
