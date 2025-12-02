// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取产品列表 获取产品列表 - 支持搜索和分页 GET /api/v1/products/ */
export async function productApiGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.productApiGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/products/', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // perPage has a default value: 10
      perPage: '10',
      ...params,
    },
    ...(options || {}),
  })
}

/** 创建新产品 创建新产品 POST /api/v1/products/ */
export async function productApiPost(body: API.ProductCreateModel, options?: { [key: string]: any }) {
  return request<any>('/api/v1/products/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取指定产品 获取指定产品 - 公开接口 GET /api/v1/products/${param1} */
export async function productApiIntProductIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.productApiIntProductIdGetParams,
  options?: { [key: string]: any }
) {
  const { productId: param0, product_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/products/${param1}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新产品信息 更新产品信息 PUT /api/v1/products/${param1} */
export async function productApiIntProductIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.productApiIntProductIdPutParams,
  body: API.ProductUpdateModel,
  options?: { [key: string]: any }
) {
  const { productId: param0, product_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/products/${param1}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除产品 删除产品 DELETE /api/v1/products/${param1} */
export async function productApiIntProductIdDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.productApiIntProductIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { productId: param0, product_id: param1, ...queryParams } = params
  return request<any>(`/api/v1/products/${param1}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 根据分类获取产品 根据分类获取产品 - 公开接口 GET /api/v1/products/categories/${param0} */
export async function productApiCategoriesStringCategoryGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.productApiCategoriesStringCategoryGetParams,
  options?: { [key: string]: any }
) {
  const { category: param0, ...queryParams } = params
  return request<any>(`/api/v1/products/categories/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}
