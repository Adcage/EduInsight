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

/** 创建新用户 创建新用户 - 需要JWT认证 POST /api/v1/users/ */
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

/** 获取指定用户 获取指定用户 - 公开接口 GET /api/v1/users/${param0} */
export async function userApiIntUserIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdGetParams,
  options?: { [key: string]: any }
) {
  const { user_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/users/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新用户信息 更新用户信息 - 需要JWT认证 PUT /api/v1/users/${param0} */
export async function userApiIntUserIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdPutParams,
  body: API.UserUpdateModel,
  options?: { [key: string]: any }
) {
  const { user_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/users/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除用户 删除用户 - 需要JWT认证 DELETE /api/v1/users/${param0} */
export async function userApiIntUserIdDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { user_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/users/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}
