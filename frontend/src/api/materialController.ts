// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取资料列表 获取资料列表</br></br>支持分页、筛选和排序：</br>- 按课程筛选</br>- 按分类筛选</br>- 按上传者筛选</br>- 按文件类型筛选</br>- 关键词搜索 GET /api/v1/materials */
export async function materialApiGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiGetParams,
  options?: { [key: string]: any }
) {
  return request<API.MaterialListResponseModel>('/api/v1/materials', {
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

/** 获取资料详情 获取资料详情</br></br>返回资料的完整信息，包括关联的标签、分类、课程等。 GET /api/v1/materials/${param1} */
export async function materialApiIntMaterialIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdGetParams,
  options?: { [key: string]: any }
) {
  const { materialId: param0, material_id: param1, ...queryParams } = params
  return request<API.MaterialDetailResponseModel>(`/api/v1/materials/${param1}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新资料信息 更新资料信息</br></br>只有资料的上传者可以更新。</br>可以更新标题、描述、分类和标签。 PUT /api/v1/materials/${param1} */
export async function materialApiIntMaterialIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdPutParams,
  body: API.MaterialUpdateModel,
  options?: { [key: string]: any }
) {
  const { materialId: param0, material_id: param1, ...queryParams } = params
  return request<API.MaterialResponseModel>(`/api/v1/materials/${param1}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除资料 删除资料</br></br>只有资料的上传者可以删除。</br>删除资料会同时删除文件和数据库记录。 DELETE /api/v1/materials/${param1} */
export async function materialApiIntMaterialIdDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { materialId: param0, material_id: param1, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/materials/${param1}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 下载资料 下载资料文件</br></br>返回文件流，浏览器会自动下载文件。 GET /api/v1/materials/${param1}/download */
export async function materialApiIntMaterialIdDownloadGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdDownloadGetParams,
  options?: { [key: string]: any }
) {
  const { materialId: param0, material_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/materials/${param1}/download`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 搜索资料 搜索资料</br></br>在资料标题、描述和关键词中搜索。 GET /api/v1/materials/search */
export async function materialApiSearchGet(options?: { [key: string]: any }) {
  return request<API.MaterialListResponseModel>('/api/v1/materials/search', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取资料统计信息 获取资料统计信息</br></br>包括：</br>- 资料总数</br>- 总大小</br>- 总下载次数</br>- 总浏览次数</br>- 按类型统计</br>- 按分类统计</br>- 最近上传</br>- 热门资料 GET /api/v1/materials/statistics */
export async function materialApiStatisticsGet(options?: { [key: string]: any }) {
  return request<API.MaterialStatsModel>('/api/v1/materials/statistics', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 上传资料 上传资料文件</br></br>支持的文件类型：PDF、Word、PPT、Excel、图片、压缩包等。</br>最大文件大小：100MB POST /api/v1/materials/upload */
export async function materialApiUploadPost(options?: { [key: string]: any }) {
  return request<API.MaterialResponseModel>('/api/v1/materials/upload', {
    method: 'POST',
    ...(options || {}),
  })
}
