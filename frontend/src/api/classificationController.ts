// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 分析并分类资料 分析并分类资料</br></br>对指定资料进行内容分析，提取关键词并推荐分类。</br>- 高置信度 (>0.7): 自动应用分类</br>- 中等置信度 (0.5-0.7): 需要用户确认</br>- 低置信度 (<0.5): 不推荐分类 POST /api/v1/materials/${param0}/classify */
export async function materialApiIntMaterialIdClassifyPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdClassifyPostParams,
  options?: { [key: string]: any }
) {
  const { materialId: param0, ...queryParams } = params
  return request<API.ClassifyMaterialResponseModel>(`/api/v1/materials/${param0}/classify`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 获取资料关键词 获取资料关键词</br></br>返回资料的关键词列表，包含关键词和权重。</br>如果关键词尚未提取，会自动进行提取。 GET /api/v1/materials/${param0}/keywords */
export async function materialApiIntMaterialIdKeywordsGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdKeywordsGetParams,
  options?: { [key: string]: any }
) {
  const { materialId: param0, ...queryParams } = params
  return request<API.KeywordResponseModel>(`/api/v1/materials/${param0}/keywords`, {
    method: 'GET',
    params: {
      // topN has a default value: 10
      topN: '10',
      ...queryParams,
    },
    ...(options || {}),
  })
}

/** 获取标签建议 获取标签建议</br></br>根据资料内容和关键词推荐相关标签。</br>返回最多5个标签建议，包括现有标签和新建议的标签。 POST /api/v1/materials/${param0}/suggest-tags */
export async function materialApiIntMaterialIdSuggestTagsPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiIntMaterialIdSuggestTagsPostParams,
  options?: { [key: string]: any }
) {
  const { materialId: param0, ...queryParams } = params
  return request<API.TagSuggestionResponseModel>(`/api/v1/materials/${param0}/suggest-tags`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 接受分类建议 接受分类建议</br></br>接受指定的分类建议，将建议的分类应用到资料。 POST /api/v1/materials/classification-logs/${param0}/accept */
export async function materialApiClassificationLogsIntLogIdAcceptPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiClassificationLogsIntLogIdAcceptPostParams,
  options?: { [key: string]: any }
) {
  const { logId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/materials/classification-logs/${param0}/accept`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 拒绝分类建议 拒绝分类建议</br></br>拒绝指定的分类建议，保持资料原有分类不变。 POST /api/v1/materials/classification-logs/${param0}/reject */
export async function materialApiClassificationLogsIntLogIdRejectPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.materialApiClassificationLogsIntLogIdRejectPostParams,
  options?: { [key: string]: any }
) {
  const { logId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/materials/classification-logs/${param0}/reject`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}
