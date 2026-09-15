# Business Logic Model — course-schedule

## 1. 课表渲染逻辑

### 周视图
```
输入: 全部课程, currentWeek (BR-3), sectionTimes
1. 用 BR-4 过滤出本周课程
2. 构建 7 列(周一~周日) × N 行(sectionTimes 节数) 网格
3. 每门课程放置到 (dayOfWeek, startSection~endSection) 跨越的格子,
   显示 name + location, 底色为 course.color
4. 今日列高亮
```

### 日视图
```
输入: 全部课程, currentWeek, today.dayOfWeek
1. 用 BR-4 过滤本周课程, 再过滤 dayOfWeek == 今天
2. 按 startSection 升序排列
3. 每门课程显示: 时间段(startSection~endSection 对应的时间), name, teacher, location
```

### 周导航
- 用户可切换查看第 1 ~ totalWeeks 周；默认定位 currentWeek（学期外则定位第 1 周）。

## 2. 课程 CRUD 流程

### 添加/编辑
```
表单提交 → BR-5 校验 → 失败: 内联提示, 终止
                     → 成功: BR-7 冲突检测
                            → 有冲突: 警告对话框(冲突课程+重叠周次)
                                     → 用户确认 → 保存
                                     → 取消 → 返回表单
                            → 无冲突: 保存
保存 → 写入 store → watch 持久化到 localStorage
```
- 添加时按 BR-9 自动分配颜色。

### 删除
```
点击删除 → 确认对话框 → 确认: 移除并持久化
```

## 3. 提醒调度逻辑
```
页面加载 → 请求 Notification 授权(若 notificationEnabled)
启动 setInterval(60s):
  1. today 为学期内(BR-3) 才继续
  2. 取今日课程(同周视图过滤逻辑)
  3. 对每门课: 开始时间 = sectionTimes[startSection].startTime
  4. 若 now >= 开始时间 - reminderMinutes 且 now < 开始时间
     且 (courseId + 日期) 不在已提醒集合 → 触发提醒, 记入已提醒集合
提醒方式: Notification API 可用且已授权 → 系统通知; 否则 → 页面内横幅(BR-11)
```

## 4. 导入导出逻辑

### 导出
```
收集 store 全量数据 → JSON.stringify → Blob 下载 (course-schedule-backup-YYYYMMDD.json)
```

### 导入
```
选择文件 → 解析 JSON → 失败: 提示"文件格式错误"
→ BR-15 校验 → 失败: 提示具体原因, 终止
→ 确认对话框(将覆盖现有数据) → 确认: 全量替换并持久化 → 刷新视图
```

## 5. 数据持久化逻辑
- 单一响应式 store（Vue `reactive`），`watch(store, persist, { deep: true })` 防抖写入 localStorage 键 `course-schedule-data`
- 应用启动时读取并校验；数据缺失或损坏时回退到空初始状态（含默认 12 节模板、默认设置）
