// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 用户登录 用户登录 POST /api/v1/auth/login */
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

/** 获取用户信息 获取用户信息 GET /api/v1/auth/profile/${param0} */
export async function authApiProfileIntUserIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.authApiProfileIntUserIdGetParams,
  options?: { [key: string]: any }
) {
  const { user_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/auth/profile/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
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
