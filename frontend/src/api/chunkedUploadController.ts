// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 取消上传 取消上传并清理临时文件 DELETE /api/v1/chunked-upload/${param0} */
export async function chunkedUploadApiUploadIdDelete(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.chunkedUploadApiUploadIdDeleteParams,
    options?: { [key: string]: any }
) {
    const {upload_id: param0, ...queryParams} = params
    return request<API.MessageResponseModel>(`/api/v1/chunked-upload/${param0}`, {
        method: 'DELETE',
        params: {...queryParams},
        ...(options || {}),
    })
}

/** 上传分片 上传单个分片</br></br>请求参数：</br>- upload_id: 上传ID</br>- chunk_index: 分片索引</br>- chunk: 分片文件数据 POST /api/v1/chunked-upload/chunk */
export async function chunkedUploadApiChunkPost(options?: { [key: string]: any }) {
    return request<API.MessageResponseModel>('/api/v1/chunked-upload/chunk', {
        method: 'POST',
        ...(options || {}),
    })
}

/** 初始化分片上传 初始化分片上传</br></br>请求参数：</br>- filename: 文件名</br>- file_size: 文件大小（字节）</br>- total_chunks: 总分片数 POST /api/v1/chunked-upload/init */
export async function chunkedUploadApiInitPost(options?: { [key: string]: any }) {
    return request<API.MessageResponseModel>('/api/v1/chunked-upload/init', {
        method: 'POST',
        ...(options || {}),
    })
}

/** 合并分片 合并所有分片</br></br>请求参数：</br>- upload_id: 上传ID POST /api/v1/chunked-upload/merge */
export async function chunkedUploadApiMergePost(options?: { [key: string]: any }) {
    return request<API.MessageResponseModel>('/api/v1/chunked-upload/merge', {
        method: 'POST',
        ...(options || {}),
    })
}

/** 查询上传状态 查询上传状态</br></br>返回已上传的分片列表和缺失的分片列表。 GET /api/v1/chunked-upload/status/${param0} */
export async function chunkedUploadApiStatusUploadIdGet(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.chunkedUploadApiStatusUploadIdGetParams,
    options?: { [key: string]: any }
) {
    const {upload_id: param0, ...queryParams} = params
    return request<API.MessageResponseModel>(`/api/v1/chunked-upload/status/${param0}`, {
        method: 'GET',
        params: {...queryParams},
        ...(options || {}),
    })
}
