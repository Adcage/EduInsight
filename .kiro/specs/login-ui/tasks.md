# 登录功能前端界面实现任务列表

## 任务概述

本任务列表将登录功能前端界面的实现分解为一系列可执行的开发任务。每个任务都是独立的、可测试的，并且按照依赖关系排序。

## 任务列表

- [x] 1. 创建认证状态管理 Store

  - 创建 `frontend/src/stores/auth.ts` 文件
  - 实现 AuthState 状态定义（使用 API.UserResponseModel）
  - 实现 getters（isAdmin, isTeacher, isStudent, userDisplayName, defaultAvatar）
  - 实现 actions（login, logout, checkLoginStatus, fetchCurrentUser, setRedirectPath, clearRedirectPath, clearUser）
  - 集成后端 API 调用（authApiLoginPost, authApiLogoutPost, authApiStatusGet, authApiGetLoginuserGet）
  - _需求: 5.1, 5.2, 5.3, 5.4_

- [x] 2. 创建路由守卫

  - 创建 `frontend/src/router/guards.ts` 文件
  - 实现全局前置守卫（beforeEach）
  - 处理未登录访问受保护路由的重定向逻辑
  - 处理已登录用户访问登录页的重定向逻辑
  - 实现重定向路径的保存和恢复
  - 在 `frontend/src/router/index.ts` 中注册路由守卫
  - _需求: 8.1, 8.2, 8.3, 8.4, 1.5_

- [x] 3. 创建 useAuth 组合式函数

  - 创建 `frontend/src/composables/useAuth.ts` 文件
  - 实现 login 方法（调用 authStore.login 并处理重定向）
  - 实现 logout 方法（调用 authStore.logout 并跳转到登录页）
  - 实现 checkAuth 方法（检查登录状态）
  - 实现错误处理函数（handleLoginError, handleNetworkError）
  - 导出响应式计算属性（user, isLoggedIn, isAdmin, isTeacher, isStudent）
  - _需求: 1.2, 1.3, 5.4, 6.1, 6.2, 6.3, 6.4_

- [x] 4. 创建登录页面组件

  - 创建 `frontend/src/pages/auth/LoginPage.vue` 文件
  - 实现登录表单 UI（使用 Ant Design Vue 组件）
  - 实现表单状态管理（使用 API.UserLoginModel 类型）
  - 实现表单验证规则（loginIdentifier 和 password 必填，密码最少 6 位）
  - 实现登录提交处理（调用 useAuth 的 login 方法）
  - 实现 Enter 键提交功能
  - 实现加载状态显示
  - 实现错误提示显示
  - 实现响应式布局（桌面端居中卡片，移动端全屏）
  - _需求: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. 创建用户头像组件

  - 创建 `frontend/src/components/common/UserAvatar.vue` 文件
  - 实现未登录状态显示（登录按钮）
  - 实现已登录状态显示（用户头像或默认图标）
  - 实现下拉菜单（个人信息、退出登录）
  - 实现登出功能（调用 useAuth 的 logout 方法）
  - 实现跳转到登录页功能
  - 实现跳转到个人信息页功能
  - _需求: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 6. 创建认证路由配置

  - 创建 `frontend/src/router/auth.ts` 文件
  - 配置登录页面路由（/login）
  - 设置路由元信息（title, requiresAuth）
  - 导出路由配置
  - _需求: 1.1_

- [x] 7. 集成用户头像组件到主布局

  - 在主布局组件中引入 UserAvatar 组件
  - 将 UserAvatar 组件添加到顶部菜单栏
  - 确保组件在所有页面中可见
  - _需求: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 8. 实现会话持久化

  - 在 auth store 中实现 localStorage 缓存
  - 在应用启动时恢复用户状态
  - 在用户登出时清除缓存
  - _需求: 5.2_

- [x] 9. 实现 HTTP 拦截器会话过期处理

  - 在 `frontend/src/request.ts` 中添加响应拦截器
  - 处理 401 错误（会话过期）
  - 自动清除用户状态并重定向到登录页
  - 保存当前页面路径用于登录后返回
  - _需求: 5.3, 6.1_

- [x] 10. 实现角色路由跳转逻辑

  - 创建 `frontend/src/utils/roleRoutes.ts` 工具文件
  - 实现 getDefaultHomeByRole 函数（根据角色返回默认主页路径）
  - 在 useAuth 的 login 方法中使用该函数
  - _需求: 4.1, 4.2, 4.3, 4.4_

- [x] 11. 添加登录页面样式

  - 实现登录页面的响应式布局样式
  - 实现主题适配（亮色/暗色主题）
  - 实现加载动画和过渡效果
  - 优化移动端显示效果
  - _需求: 3.1, 3.2_

- [x] 12. 测试和调试

  - 测试完整登录流程
  - 测试表单验证
  - 测试错误处理
  - 测试重定向功能
  - 测试会话管理
  - 测试角色路由跳转
  - 测试响应式布局
  - 修复发现的问题
  - _需求: 所有需求_

## 任务依赖关系

```
1 (Auth Store) → 2 (路由守卫) → 6 (路由配置)
1 (Auth Store) → 3 (useAuth) → 4 (登录页面)
1 (Auth Store) → 3 (useAuth) → 5 (用户头像)
5 (用户头像) → 7 (集成到主布局)
1 (Auth Store) → 8 (会话持久化)
1 (Auth Store) → 9 (HTTP拦截器)
3 (useAuth) → 10 (角色路由)
4 (登录页面) → 11 (页面样式)
所有任务 → 12 (测试和调试)
```

## 实现顺序建议

1. 首先实现 Auth Store（任务 1），这是整个功能的核心
2. 然后实现 useAuth 组合式函数（任务 3），封装认证逻辑
3. 接着实现登录页面（任务 4）和用户头像组件（任务 5）
4. 实现路由相关功能（任务 2、6、10）
5. 实现会话管理（任务 8、9）
6. 集成组件到主布局（任务 7）
7. 添加样式优化（任务 11）
8. 最后进行全面测试（任务 12）

## 注意事项

1. 所有组件都使用 Vue 3 Composition API
2. 使用 TypeScript 进行类型检查
3. 使用 `frontend/src/api/typings.d.ts` 中定义的类型
4. 遵循项目现有的代码风格和目录结构
5. 确保所有功能在桌面端和移动端都能正常工作
6. 实现过程中注意错误处理和用户体验
7. 每完成一个任务都要进行基本测试
