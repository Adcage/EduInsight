// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 用户登录 用户登录获取JWT令牌 POST /api/v1/auth/login */
export async function authApiLoginPost(body: API.LoginModel, options?: { [key: string]: any }) {
  return request<any>('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取当前用户信息 获取当前用户信息 - 需要JWT认证 GET /api/v1/auth/profile */
export async function authApiProfileGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/auth/profile', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 刷新访问令牌 刷新访问令牌 POST /api/v1/auth/refresh */
export async function authApiRefreshPost(options?: { [key: string]: any }) {
  return request<any>('/api/v1/auth/refresh', {
    method: 'POST',
    ...(options || {}),
  })
}

/** 用户注册 用户注册 POST /api/v1/auth/register */
export async function authApiRegisterPost(body: API.RegisterModel, options?: { [key: string]: any }) {
  return request<any>('/api/v1/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}
