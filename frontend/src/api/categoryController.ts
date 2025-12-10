// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取分类列表 获取所有分类（平铺列表）</br></br>返回所有分类的平铺列表，按排序序号排序。 GET /api/v1/material-categories */
export async function categoryApiGet(options?: { [key: string]: any }) {
    return request<any>('/api/v1/material-categories', {
        method: 'GET',
        ...(options || {}),
    })
}

/** 创建分类 创建资料分类</br></br>支持创建多级分类，可以指定父分类。</br>只有管理员和教师可以创建分类。 POST /api/v1/material-categories */
export async function categoryApiPost(body: API.MaterialCategoryCreateModel, options?: { [key: string]: any }) {
    return request<API.MaterialCategoryResponseModel>('/api/v1/material-categories', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** 获取分类详情 获取分类详情</br></br>返回指定分类的详细信息。 GET /api/v1/material-categories/${param0} */
export async function categoryApiIntCategoryIdGet(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.categoryApiIntCategoryIdGetParams,
    options?: { [key: string]: any }
) {
    const {categoryId: param0, ...queryParams} = params
    return request<API.MaterialCategoryResponseModel>(`/api/v1/material-categories/${param0}`, {
        method: 'GET',
        params: {...queryParams},
        ...(options || {}),
    })
}

/** 更新分类 更新分类信息</br></br>可以更新分类名称、描述、父分类和排序序号。</br>只有管理员和教师可以更新分类。 PUT /api/v1/material-categories/${param0} */
export async function categoryApiIntCategoryIdPut(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.categoryApiIntCategoryIdPutParams,
    body: API.MaterialCategoryUpdateModel,
    options?: { [key: string]: any }
) {
    const {categoryId: param0, ...queryParams} = params
    return request<API.MaterialCategoryResponseModel>(`/api/v1/material-categories/${param0}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        params: {...queryParams},
        data: body,
        ...(options || {}),
    })
}

/** 删除分类 删除分类</br></br>只能删除没有子分类和关联资料的分类。</br>只有管理员和教师可以删除分类。 DELETE /api/v1/material-categories/${param0} */
export async function categoryApiIntCategoryIdDelete(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.categoryApiIntCategoryIdDeleteParams,
    options?: { [key: string]: any }
) {
    const {categoryId: param0, ...queryParams} = params
    return request<API.MessageResponseModel>(`/api/v1/material-categories/${param0}`, {
        method: 'DELETE',
        params: {...queryParams},
        ...(options || {}),
    })
}

/** 获取子分类 获取子分类</br></br>返回指定分类的所有直接子分类。 GET /api/v1/material-categories/${param0}/children */
export async function categoryApiIntCategoryIdChildrenGet(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.categoryApiIntCategoryIdChildrenGetParams,
    options?: { [key: string]: any }
) {
    const {categoryId: param0, ...queryParams} = params
    return request<any>(`/api/v1/material-categories/${param0}/children`, {
        method: 'GET',
        params: {...queryParams},
        ...(options || {}),
    })
}

/** 获取分类树 获取分类树形结构</br></br>返回树形结构的分类数据，便于前端展示。 GET /api/v1/material-categories/tree */
export async function categoryApiTreeGet(options?: { [key: string]: any }) {
    return request<any>('/api/v1/material-categories/tree', {
        method: 'GET',
        ...(options || {}),
    })
}
