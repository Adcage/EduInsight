// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取订单列表 获取订单列表 - 需要JWT认证 GET /api/v1/orders/ */
export async function orderApiGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.orderApiGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/orders/', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // per_page has a default value: 10
      per_page: '10',
      ...params,
    },
    ...(options || {}),
  })
}

/** 创建新订单 创建新订单 - 需要JWT认证 POST /api/v1/orders/ */
export async function orderApiPost(body: API.OrderCreateModel, options?: { [key: string]: any }) {
  return request<any>('/api/v1/orders/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取指定订单 获取指定订单 - 需要JWT认证 GET /api/v1/orders/${param0} */
export async function orderApiIntOrderIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.orderApiIntOrderIdGetParams,
  options?: { [key: string]: any }
) {
  const { order_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/orders/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新订单信息 更新订单信息 - 需要JWT认证 PUT /api/v1/orders/${param0} */
export async function orderApiIntOrderIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.orderApiIntOrderIdPutParams,
  body: API.OrderUpdateModel,
  options?: { [key: string]: any }
) {
  const { order_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/orders/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 取消订单 取消订单 - 需要JWT认证 DELETE /api/v1/orders/${param0}/cancel */
export async function orderApiIntOrderIdCancelDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.orderApiIntOrderIdCancelDeleteParams,
  options?: { [key: string]: any }
) {
  const { order_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/orders/${param0}/cancel`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 获取订单统计 获取当前用户的订单统计 - 需要JWT认证 GET /api/v1/orders/statistics */
export async function orderApiStatisticsGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/orders/statistics', {
    method: 'GET',
    ...(options || {}),
  })
}
