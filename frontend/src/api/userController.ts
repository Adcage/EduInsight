// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取用户列表 获取用户列表</br></br>支持分页、角色筛选、状态筛选和关键词搜索。</br>只有教师和管理员可以访问。 GET /api/v1/users/ */
export async function userApiGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiGetParams,
  options?: { [key: string]: any }
) {
  return request<API.UserListResponseModel>('/api/v1/users/', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // perPage has a default value: 20
      perPage: '20',

      ...params,
    },
    ...(options || {}),
  })
}

/** 获取指定用户 获取指定用户信息</br></br>只有教师和管理员可以访问。 GET /api/v1/users/${param0} */
export async function userApiIntUserIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdGetParams,
  options?: { [key: string]: any }
) {
  const { userId: param0, ...queryParams } = params
  return request<API.UserResponseModel>(`/api/v1/users/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新用户信息 更新用户信息</br></br>只有管理员可以更新其他用户的信息。 PUT /api/v1/users/${param0} */
export async function userApiIntUserIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdPutParams,
  body: API.UserUpdateModel,
  options?: { [key: string]: any }
) {
  const { userId: param0, ...queryParams } = params
  return request<API.UserResponseModel>(`/api/v1/users/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 激活用户账户 激活用户账户</br></br>只有管理员可以激活用户账户。 POST /api/v1/users/${param0}/activate */
export async function userApiIntUserIdActivatePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdActivatePostParams,
  options?: { [key: string]: any }
) {
  const { userId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/users/${param0}/activate`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 停用用户账户 停用用户账户</br></br>只有管理员可以停用用户账户。 POST /api/v1/users/${param0}/deactivate */
export async function userApiIntUserIdDeactivatePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiIntUserIdDeactivatePostParams,
  options?: { [key: string]: any }
) {
  const { userId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/users/${param0}/deactivate`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 用户API健康检查 用户API健康检查 GET /api/v1/users/health */
export async function userApiHealthGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/users/health', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取用户统计 获取用户统计信息</br></br>只有管理员可以访问。 GET /api/v1/users/stats */
export async function userApiStatsGet(options?: { [key: string]: any }) {
  return request<API.UserStatsModel>('/api/v1/users/stats', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 上传人脸照片 学生上传人脸照片用于人脸识别签到 POST /api/v1/users/face-image */
export async function userApiUploadFaceImage(
  body: { faceImageBase64: string },
  options?: { [key: string]: any }
) {
  return request<{ message: string; faceImagePath?: string }>('/api/v1/users/face-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}
