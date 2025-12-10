// @ts-ignore
/* eslint-disable */
import request from '@/request'

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

/** 批量删除用户 批量删除用户(软删除)</br></br>只有管理员可以批量删除用户。 DELETE /api/v1/users/batch-delete */
export async function userApiBatchDeleteDelete(body: API.BatchDeleteModel, options?: { [key: string]: any }) {
  return request<API.BatchImportResponseModel>('/api/v1/users/batch-delete', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 批量导入用户 从Excel文件批量导入用户</br></br>只有管理员可以批量导入用户。</br>Excel文件应包含列: username, user_code, email, real_name, role, phone(可选), class_id(学生必填) POST /api/v1/users/batch-import */
export async function userApiBatchImportPost(options?: { [key: string]: any }) {
  return request<API.BatchImportResponseModel>('/api/v1/users/batch-import', {
    method: 'POST',
    ...(options || {}),
  })
}

/** 创建用户 创建新用户</br></br>只有管理员可以创建用户。 POST /api/v1/users/create */
export async function userApiCreatePost(body: API.UserCreateModel, options?: { [key: string]: any }) {
  return request<API.UserResponseModel>('/api/v1/users/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取用户列表 获取用户列表</br></br>支持分页、角色筛选、状态筛选和关键词搜索。</br>只有教师和管理员可以访问。 GET /api/v1/users/list */
export async function userApiListGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.userApiListGetParams,
  options?: { [key: string]: any }
) {
  return request<API.UserListResponseModel>('/api/v1/users/list', {
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
