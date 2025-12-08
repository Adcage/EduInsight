// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取标签列表 获取标签列表</br></br>支持分页，按使用次数降序排序。 GET /api/v1/material-tags */
export async function tagApiGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/material-tags', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 创建标签 创建资料标签</br></br>标签名称必须唯一。 POST /api/v1/material-tags */
export async function tagApiPost(body: API.MaterialTagCreateModel, options?: { [key: string]: any }) {
  return request<API.MaterialTagResponseModel>('/api/v1/material-tags', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取标签详情 获取标签详情</br></br>返回指定标签的详细信息。 GET /api/v1/material-tags/${param1} */
export async function tagApiIntTagIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.tagApiIntTagIdGetParams,
  options?: { [key: string]: any }
) {
  const { tagId: param0, tag_id: param1, ...queryParams } = params
  return request<API.MaterialTagResponseModel>(`/api/v1/material-tags/${param1}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 删除标签 删除标签</br></br>只能删除未被使用的标签。</br>只有管理员和教师可以删除标签。 DELETE /api/v1/material-tags/${param1} */
export async function tagApiIntTagIdDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.tagApiIntTagIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { tagId: param0, tag_id: param1, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/material-tags/${param1}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 获取热门标签 获取热门标签</br></br>返回使用次数最多的标签。 GET /api/v1/material-tags/popular */
export async function tagApiPopularGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/material-tags/popular', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 搜索标签 搜索标签</br></br>根据关键词模糊搜索标签名称。 GET /api/v1/material-tags/search */
export async function tagApiSearchGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/material-tags/search', {
    method: 'GET',
    ...(options || {}),
  })
}
