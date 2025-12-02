// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取用户列表 获取用户列表 - 公开接口 GET /api/v1/users/ */
export async function userApiGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/users/', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 创建新用户 创建新用户 POST /api/v1/users/ */
export async function userApiPost(body: API.UserCreateModel, options?: { [key: string]: any }) {
  return request<any>('/api/v1/users/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取指定用户 获取指定用户 - 公开接口 GET /api/v1/users/${param1} */
export async function userApiIntUserIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdGetParams,
  options?: { [key: string]: any }
) {
  const { userId: param0, user_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/users/${param1}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新用户信息 更新用户信息 PUT /api/v1/users/${param1} */
export async function userApiIntUserIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdPutParams,
  body: API.UserUpdateModel,
  options?: { [key: string]: any }
) {
  const { userId: param0, user_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/users/${param1}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除用户 删除用户 DELETE /api/v1/users/${param1} */
export async function userApiIntUserIdDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { userId: param0, user_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/users/${param1}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 删除用户 GET /api/v1/users/health */
export async function userApiHealthGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/users/health', {
    method: 'GET',
    ...(options || {}),
  })
}
