# Frontend Components — course-schedule

技术栈：Vue 3（Composition API + `<script setup>`）+ Vite。无后端，无 API 集成点。状态管理采用单一 reactive store composable（`useScheduleStore`），不引入 Pinia（规模无需）。

## 组件层级

```
App.vue
├── AppHeader                    # 标题、视图切换(周/日)、周导航、设置入口
├── WeekView.vue                 # 周视图
│   └── ScheduleGrid.vue         # 7×N 课表网格
│       └── CourseBlock.vue      # 单个课程块(点击弹详情)
├── DayView.vue                  # 日视图(当天课程列表)
├── CourseFormModal.vue          # 添加/编辑课程表单(模态)
├── CourseDetailModal.vue        # 课程详情 + 编辑/删除入口
├── SettingsPanel.vue            # 设置(学期、提醒、节次时间表、导入导出)
│   └── SectionTimeEditor.vue    # 节次时间编辑
├── ReminderBanner.vue           # 页面内提醒横幅(通知降级方案)
└── ConfirmDialog.vue            # 通用确认对话框(删除/冲突/导入覆盖)
```

## 核心组件定义

### useScheduleStore（composable）
- state: `courses: Course[]`, `semester: SemesterSettings`, `settings: AppSettings`
- getters: `currentWeek`, `coursesInWeek(w)`, `coursesOfDay(date)`
- actions: `addCourse`, `updateCourse`, `deleteCourse`, `importData`, `exportData`, `updateSettings`
- 持久化: deep watch → localStorage

### ScheduleGrid.vue
- props: `week: number`
- emits: `course-click(course)`
- 渲染 BR-4 过滤后的课程块；今日列高亮

### CourseFormModal.vue
- props: `course?: Course`（无则为添加模式）
- emits: `save(course)`, `cancel`
- 表单字段对应 Course 全部可编辑字段；BR-5 内联校验；提交前执行 BR-7 冲突检测，有冲突时经 ConfirmDialog 警告确认（BR-8）

### SettingsPanel.vue
- 学期设置（开始日期 + totalWeeks，BR-2 对齐）
- 提醒设置（reminderMinutes、notificationEnabled + 授权按钮，附 BR-12 说明文案）
- 节次时间表编辑（SectionTimeEditor，BR-16 约束）
- 导入/导出按钮（BR-14/15）

## 关键交互流
1. **查看**：默认进入周视图当前周；左右切换周；切换日视图
2. **添加**：点击空白格或"添加课程"按钮 → CourseFormModal → 校验/冲突确认 → 保存
3. **编辑/删除**：点击课程块 → CourseDetailModal → 编辑进表单 / 删除经确认
4. **提醒**：页面常驻时每分钟检查，触发系统通知或 ReminderBanner
5. **备份**：设置页导出 JSON；导入经校验与覆盖确认

## 响应式设计
- 移动端（≤768px）：周视图网格横向紧凑化（节次行高压缩、课程块只显示课程名）；日视图为主力视图
- 桌面端：完整网格，课程块显示 name + location
