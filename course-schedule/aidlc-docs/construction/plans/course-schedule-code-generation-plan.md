# Code Generation Plan — course-schedule

单元：course-schedule（隐式单一单元，greenfield）
工作区根：`D:\Documents\PythonProject\aidlc-skills\course-schedule`（代码在工作区根，NEVER aidlc-docs/）
技术栈：Vue 3（Composition API + `<script setup>`）+ Vite + Vitest（单元测试）；无后端、无 Pinia
输入：inception/requirements/requirements.md + construction/course-schedule/functional-design/*（BR-1 ~ BR-16）
环境已确认：node v24.14.0 / npm 11.9.0

## 需求可追溯性
- FR-1 课表查看（周/日视图、学期设置、周次计算、单双周）→ Step 2, 3, 5
- FR-2 课程增删改（含节次时间表）→ Step 2, 3, 5
- FR-3 上课提醒 → Step 2, 5
- FR-4 localStorage 持久化 + JSON 导入导出 → Step 2, 5
- NFR-1 响应式 → Step 5；NFR-2 技术栈 → Step 1

## 生成步骤

### Step 1: 项目脚手架（greenfield）
- [ ] `package.json`（vue、vite、@vitejs/plugin-vue、vitest、@vue/test-utils、jsdom 依赖与 scripts）
- [ ] `vite.config.js`（vue 插件 + vitest 配置 + `server.host: '127.0.0.1'`）
- [ ] `index.html`、`src/main.js`、`src/App.vue` 骨架
- [ ] `.gitignore`（node_modules、dist）

### Step 2: 业务逻辑层生成（技术无关核心，纯函数模块）
- [ ] `src/logic/week.js` — 周次计算 BR-1~BR-4（学期对齐周一、currentWeek、周次显示判定）
- [ ] `src/logic/conflict.js` — 冲突检测 BR-7（含单双周区间相交）
- [ ] `src/logic/validation.js` — 表单/数据校验 BR-5、BR-15（导入校验）
- [ ] `src/logic/colors.js` — 调色板与最少使用分配 BR-9
- [ ] `src/logic/schedule.js` — 课表过滤/排序（周视图、日视图取数）
- [ ] `src/logic/defaultTimes.js` — 默认 12 节模板
- [ ] `src/logic/storage.js` — localStorage 读写、JSON 导出/导入序列化 BR-14/15

### Step 3: 业务逻辑单元测试
- [ ] `tests/logic/week.test.js`、`conflict.test.js`、`validation.test.js`、`colors.test.js`、`schedule.test.js`、`storage.test.js`（Vitest，覆盖 BR-1~BR-9、BR-14/15 关键路径与边界：学期外、单双周组合、冲突相交矩阵）

### Step 4: 业务逻辑摘要
- [ ] `aidlc-docs/construction/course-schedule/code/business-logic-summary.md`

### Step 5: 前端组件生成
- [ ] `src/store/useScheduleStore.js` — 单一 reactive store + deep watch 持久化
- [ ] `src/components/AppHeader.vue` — 视图切换/周导航/设置入口
- [ ] `src/components/ScheduleGrid.vue` + `CourseBlock.vue` — 周视图网格
- [ ] `src/components/DayView.vue` — 日视图
- [ ] `src/components/CourseFormModal.vue` — 添加/编辑（内联校验 + 冲突警告确认）
- [ ] `src/components/CourseDetailModal.vue` — 详情 + 编辑/删除
- [ ] `src/components/SettingsPanel.vue` + `SectionTimeEditor.vue` — 学期/提醒/节次表/导入导出
- [ ] `src/components/ReminderBanner.vue`、`ConfirmDialog.vue`
- [ ] `src/reminder/reminder.js` — 每分钟检查、Notification API + 页面内降级 BR-10~BR-13
- [ ] 响应式样式（移动端 ≤768px 紧凑化，NFR-1）
- [ ] 所有交互元素加 `data-testid`（Automation Friendly Code Rules）

### Step 6: 前端组件单元测试
- [ ] `tests/components/` 关键组件测试（CourseFormModal 校验与冲突流、ScheduleGrid 渲染过滤、useScheduleStore 持久化）

### Step 7: 前端组件摘要
- [ ] `aidlc-docs/construction/course-schedule/code/frontend-components-summary.md`

### Step 8: 文档与部署制品
- [ ] `course-schedule/README.md`（安装、运行、构建、功能说明）
- [ ] 部署说明：纯静态构建 `npm run build` → `dist/`（无需 CI/CD）

## 完成标准
- 全部步骤 [x]；`npm install && npm run test && npm run build` 在 Build & Test 阶段验证
- 功能覆盖 FR-1 ~ FR-4 与 BR-1 ~ BR-16
