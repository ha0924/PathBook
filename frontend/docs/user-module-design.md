# 前端用户模块 MVP 设计

---

## 一、模块定位

前端用户模块负责：
1. **身份认证** — 登录 / 注册 / 退出
2. **用户画像** — 首次 onboarding 画像配置 + "我的偏好"页管理

技术方案采用 **Vue 3 + Vite + TypeScript**，面向移动端 H5 优先设计，后续可封装为原生 App（通过 WebView 或独立原生客户端）。

---

## 二、目录结构

```
frontend/
├── index.html                # Vite 入口 HTML
├── package.json              # 依赖管理
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── src/
│   ├── main.ts              # 应用入口
│   ├── App.vue              # 根组件
│   ├── router/
│   │   └── index.ts         # Vue Router 配置 + 路由守卫
│   ├── stores/
│   │   ├── auth.ts          # 认证状态（Pinia）
│   │   └── user.ts          # 用户画像状态
│   ├── api/
│   │   ├── request.ts       # Axios 封装（拦截器 + Token 注入）
│   │   ├── auth.ts          # 认证相关接口
│   │   └── profile.ts       # 画像相关接口
│   ├── views/
│   │   ├── Login.vue        # 登录页
│   │   ├── Register.vue     # 注册页
│   │   ├── Onboarding.vue   # 画像配置页
│   │   ├── Home.vue         # 首页
│   │   └── Profile.vue      # 我的偏好页
│   ├── components/          # 可复用组件
│   │   ├── ChipSelector.vue # chip 选择器
│   │   ├── Toast.vue        # 轻提示
│   │   └── CityPicker.vue   # 城市选择器（会话级）
│   ├── styles/
│   │   ├── variables.css    # 设计变量（继承 demo）
│   │   └── global.css       # 全局样式
│   └── utils/
│       └── storage.ts       # localStorage 封装
├── public/                  # 静态资源
└── docs/
    └── user-module-design.md  # 本文档
```

---

## 三、页面设计

### 3.1 登录页（`data-screen="login"`）

**布局：**
- 品牌区：Logo "路" + "欢迎回来" + 副标题
- 表单区：用户名 input + 密码 input
- 操作区：登录按钮（primary-btn）+ "还没有账号？去注册"（text-link）
- 错误反馈：Toast 提示

**交互：**
- 输入校验：用户名非空、密码非空
- 登录成功 → 存 token → 跳转 home（或首次登录跳转 onboarding）
- 登录失败 → Toast 显示"用户名或密码错误"

### 3.2 注册页（`data-screen="register"`）

**布局：**
- AppBar：返回箭头 + "创建账号"
- 表单区：用户名 + 密码 + 确认密码
- 操作区：注册按钮

**校验规则：**
- 用户名 3~50 字符
- 密码 ≥ 6 位
- 确认密码一致
- 实时校验 + 提交时二次校验

**交互：**
- 注册成功 → Toast "注册成功" → 跳转 login
- 用户名已存在 → Toast "用户名已被使用"

### 3.3 画像配置页（`Onboarding.vue`）

**改造内容：**
- "完成配置" 按钮 → 调用 `POST /api/v1/user/profile/init`
- 收集选中的 chip 值，序列化为 UserProfile JSON
- 跳过 → 使用默认画像，仍调接口（空 body 表示使用默认值）
- 需要登录后才能进入（路由守卫）
- 首次登录自动跳转此页（后端 /me 返回 `has_profile: false`）

**收集的画像字段：**

| 字段 | UI 组件 | 说明 |
|------|---------|------|
| home_cities | 多选 chip | 常驻城市列表（可多选，仅冷启动参考，可选） |
| budget_level | 单选 chip | 人均预算档位 |
| transport_preferences | 多选 chip | 交通偏好 |
| queue_tolerance_minutes | 滑块/单选 | 排队容忍度 |
| walking_tolerance_meters | 滑块/单选 | 步行容忍度 |
| food_preferences | 多选 chip | 餐饮偏好 |
| leisure_preferences | 多选 chip | 休闲偏好 |

> **注意**：城市（当前规划的目标城市）不属于画像，而是会话级上下文，由首页顶部城市选择器管理，存 localStorage，每次请求作为参数传递给后端。`home_cities` 是用户的常驻城市（可多个），仅作为冷启动默认推荐参考。

### 3.4 我的偏好页（`data-screen="profile"`）

**当前状态：** demo 是静态展示。

**改造内容：**
- 进入时调用 `GET /api/v1/user/profile` 填充真实数据
- 每项点击后弹出编辑 Modal（chip 选择器风格）
- 修改后调用 `PATCH /api/v1/user/profile`
- 新增"退出登录"按钮 → 清除 token → 跳转 login
- 显示用户名（从 /me 获取）

---

## 四、认证流程

### 4.1 Token 管理（Pinia Store）

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const TOKEN_KEY = 'xls_access_token'
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

  const isLoggedIn = computed(() => !!token.value)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem(TOKEN_KEY, t)
  }

  function logout() {
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, isLoggedIn, setToken, logout }
})
```

### 4.2 路由守卫

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({ ... })

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.meta.guestOnly && auth.isLoggedIn) {
    next({ name: 'Home' })
  } else {
    next()
  }
})
```

### 4.3 首次登录引导

```typescript
// Login.vue 登录成功后
async function afterLogin() {
  const user = await authApi.getMe()
  if (!user.has_profile) {
    router.push({ name: 'Onboarding' })
  } else {
    router.push({ name: 'Home' })
  }
}
```

---

## 五、API 层

```typescript
// api/request.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// 请求拦截器：注入 Token
http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截器：统一错误处理
http.interceptors.response.use(
  (res) => {
    const { code, data, message } = res.data
    if (code !== 0) {
      if (code === 'AUTH_TOKEN_INVALID' || code === 'AUTH_TOKEN_EXPIRED') {
        const auth = useAuthStore()
        auth.logout()
        router.push({ name: 'Login' })
        return Promise.reject(new Error('Token expired'))
      }
      return Promise.reject({ code, message })
    }
    return data
  },
  (error) => {
    // 网络异常 / 超时统一处理
    return Promise.reject(error)
  }
)

export default http
```

---

## 六、视觉规范

沿用 demo CSS 变量体系，新增表单相关样式：

### 6.1 设计变量（继承自 demo）

```css
:root {
  --paper: #fffaf2;
  --ink: #1a1a1a;
  --muted: #6b7280;
  --line: #e5e7eb;
  --accent: rgba(232, 93, 63, 0.85);
  --accent-light: rgba(232, 93, 63, 0.08);
  --radius: 20px;
  --danger: #ef4444;
  --success: #10b981;
}
```

### 6.2 表单组件

| 组件 | 类名 | 说明 |
|------|------|------|
| 输入框 | `.form-input` | 圆角 20px、纸色背景、focus 橙色光圈 |
| 表单组 | `.form-group` | label + input + error 的容器 |
| 错误文字 | `.form-error` | 红色 12px 提示文字 |
| 表单分隔 | `.form-divider` | "或" 分隔线 |
| 文字链接 | `.text-link` | 橙色下划线链接 |

### 6.3 表单样式定义

```css
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
}

.form-input {
  width: 100%;
  min-height: 52px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  color: var(--ink);
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-light);
}

.form-input::placeholder {
  color: var(--muted);
}

.form-error {
  margin-top: 6px;
  color: var(--danger);
  font-size: 12px;
  min-height: 18px;
}

.text-link {
  color: var(--accent);
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
}

.text-link:hover {
  text-decoration: underline;
}
```

---

## 七、实现顺序

| Step | 内容 | 依赖 |
|------|------|------|
| 1 | `npm create vue@latest` 初始化项目（Vue 3 + Vite + TS + Pinia + Router） | 无 |
| 2 | 配置设计变量（CSS variables）+ 全局样式 + 移动端适配 | 无 |
| 3 | 实现 `api/request.ts`（Axios 封装）+ `stores/auth.ts` | 无 |
| 4 | 实现 Login.vue + Register.vue | Step 3 |
| 5 | 配置 Vue Router + 路由守卫（requiresAuth / guestOnly） | Step 3-4 |
| 6 | 实现 Onboarding.vue（画像配置提交） | Step 3 + 后端画像接口 |
| 7 | 实现 Profile.vue（真实数据展示 + 编辑 + 退出） | Step 3 + 后端画像接口 |
| 8 | 实现 Home.vue + 城市选择器（CityPicker 组件） | Step 5 |
| 9 | 联调后端 + 移动端真机适配 | 后端用户模块完成 |

---

## 八、MVP 简化决策

| 决策 | 理由 |
|------|------|
| Vue 3 + Vite + TypeScript | 正式项目，后续持续迭代，需要工程化基础 |
| Pinia 状态管理 | 轻量、TS 友好，适合 MVP 规模 |
| 不引入 UI 组件库 | 设计风格独特（纸质感），自定义组件更灵活 |
| Token 存 localStorage | MVP 够用，后续可升级 httpOnly cookie |
| 不做 token 自动刷新 | 7 天过期，手动重新登录 |
| 不做表单防抖 | MVP 流量小 |
| 不做密码强度指示器 | MVP 只校验最小长度 |
| 城市作为会话上下文 | 存 localStorage（lastUsedCity），不写入画像表 |
| 移动端 H5 优先 | C 端产品移动端为主，响应式适配桌面 |
| 前端校验 + 后端校验双重保障 | 用户体验 + 安全 |

## 八-A、技术栈详情

| 库 | 版本 | 用途 |
|----|------|------|
| Vue | 3.x | UI 框架 |
| Vite | 6.x | 构建工具 |
| TypeScript | 5.x | 类型安全 |
| Vue Router | 4.x | 路由 |
| Pinia | 2.x | 状态管理 |
| Axios | 1.x | HTTP 请求 |

**后续扩展（非 MVP）：**
- iOS SwiftUI / Android 原生客户端
- 或基于 H5 封装为 App（Capacitor / PWA）

---

## 九、后端接口依赖

前端用户模块依赖以下后端接口：

### 9.1 认证接口（已设计）

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册 |
| POST | `/api/v1/auth/login` | 登录，返回 access_token |
| GET | `/api/v1/auth/me` | 获取当前用户信息（含 has_profile） |

### 9.2 画像接口（新增）

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/api/v1/user/profile/init` | 首次画像配置 |
| GET | `/api/v1/user/profile` | 获取当前用户画像 |
| PATCH | `/api/v1/user/profile` | 更新画像字段 |

---

## 十、错误处理

### 10.1 前端错误映射

| 后端 ErrorCode | 前端展示 |
|----------------|----------|
| `USER_ALREADY_EXISTS` | "用户名已被使用" |
| `USER_PASSWORD_TOO_SHORT` | "密码至少需要 6 位" |
| `AUTH_CREDENTIALS_INVALID` | "用户名或密码错误" |
| `AUTH_TOKEN_INVALID` | 自动跳转登录页 |
| `AUTH_TOKEN_EXPIRED` | 自动跳转登录页 |
| `USER_DISABLED` | "账号已被禁用" |
| `PROFILE_ALREADY_INITIALIZED` | 忽略，跳转首页 |

### 10.2 网络错误处理

```typescript
// 响应拦截器中统一处理
// 网络异常 → Toast "网络异常，请稍后重试"
// 500 错误 → Toast "服务器繁忙"
// 超时 → Toast "请求超时，请重试"
```
