import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import {
    materialApiGet,
    materialApiIntMaterialIdDelete,
    materialApiIntMaterialIdGet,
    materialApiIntMaterialIdPut,
    materialApiSearchGet,
    materialApiUploadPost
} from '@/api/materialController'

export interface Material {
    id: number
    title: string
    description?: string
    fileName: string
    filePath: string
    fileSize: number
    fileType: string
    courseId?: number
    uploaderId: number
    categoryId?: number
    downloadCount: number
    viewCount: number
    keywords?: string
    autoClassified: boolean
    createdAt: string
    updatedAt: string
    // Response fields from backend (MaterialDetailResponseModel)
    categoryName?: string
    uploaderName?: string
    tags?: Array<{
        id: number
        name: string
        usageCount?: number
    }>
    // Legacy or alternative fields (kept for compatibility if needed)
    category?: {
        id: number
        name: string
    }
    uploader?: {
        id: number
        realName: string
    }
}

export interface MaterialListParams {
    page?: number
    perPage?: number
    courseId?: number
    categoryId?: number
    uploaderId?: number
    fileType?: string
    keyword?: string
    sortBy?: string
    order?: 'asc' | 'desc'
}

export const useMaterialStore = defineStore('material', () => {
    // 状态
    const materials = ref<Material[]>([])
    const currentMaterial = ref<Material | null>(null)
    const total = ref(0)
    const loading = ref(false)
    const filters = ref<MaterialListParams>({
        page: 1,
        perPage: 20,
        courseId: undefined,
        categoryId: undefined,
        fileType: undefined,
        keyword: ''
    })

    // 缓存
    const materialCache = ref<Map<number, { data: Material; timestamp: number }>>(new Map())
    const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

    // 计算属性
    const hasMore = computed(() => {
        return materials.value.length < total.value
    })

    const isEmpty = computed(() => {
        return materials.value.length === 0 && !loading.value
    })

    // 获取资料列表
    const fetchMaterials = async (params?: MaterialListParams) => {
        loading.value = true
        try {
            const queryParams = {...filters.value, ...params}
            const response = await materialApiGet(queryParams as any)
            const data = (response as any).data?.data || (response as any).data

            materials.value = data.items || []
            total.value = data.total || 0

            // 更新过滤器
            if (params) {
                filters.value = {...filters.value, ...params}
            }

            return {items: materials.value, total: total.value}
        } catch (error: any) {
            console.error('获取资料列表失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 获取资料详情（带缓存）
    const fetchMaterialDetail = async (id: number, forceRefresh = false) => {
        // 检查缓存
        if (!forceRefresh) {
            const cached = materialCache.value.get(id)
            if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
                currentMaterial.value = cached.data
                return cached.data
            }
        }

        loading.value = true
        try {
            const response = await materialApiIntMaterialIdGet({materialId: id})
            const data = (response as any).data?.data || (response as any).data

            currentMaterial.value = data

            // 更新缓存
            materialCache.value.set(id, {
                data,
                timestamp: Date.now()
            })

            return data
        } catch (error: any) {
            console.error('获取资料详情失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 上传资料
    const uploadMaterial = async (formData: FormData) => {
        try {
            const response = await materialApiUploadPost({
                data: formData,
                headers: {'Content-Type': 'multipart/form-data'}
            })
            const data = (response as any).data?.data || (response as any).data

            // 添加到列表开头
            materials.value.unshift(data)
            total.value += 1

            return data
        } catch (error: any) {
            console.error('上传资料失败:', error)
            throw error
        }
    }

    // 更新资料
    const updateMaterial = async (id: number, updateData: any) => {
        try {
            const response = await materialApiIntMaterialIdPut(
                {materialId: id},
                updateData
            )
            const data = (response as any).data?.data || (response as any).data

            // 更新列表中的资料
            const index = materials.value.findIndex(m => m.id === id)
            if (index !== -1) {
                materials.value[index] = data
            }

            // 更新当前资料
            if (currentMaterial.value?.id === id) {
                currentMaterial.value = data
            }

            // 更新缓存
            materialCache.value.set(id, {
                data,
                timestamp: Date.now()
            })

            return data
        } catch (error: any) {
            console.error('更新资料失败:', error)
            throw error
        }
    }

    // 删除资料
    const deleteMaterial = async (id: number) => {
        try {
            await materialApiIntMaterialIdDelete({materialId: id})

            // 从列表中移除
            materials.value = materials.value.filter(m => m.id !== id)
            total.value -= 1

            // 清除缓存
            materialCache.value.delete(id)

            // 清除当前资料
            if (currentMaterial.value?.id === id) {
                currentMaterial.value = null
            }
        } catch (error: any) {
            console.error('删除资料失败:', error)
            throw error
        }
    }

    // 搜索资料
    const searchMaterials = async (keyword: string, params?: MaterialListParams) => {
        loading.value = true
        try {
            const queryParams = {
                q: keyword,
                page: params?.page || 1,
                perPage: params?.perPage || 20,
                ...params
            }
            const response = await materialApiSearchGet({params: queryParams})
            const data = (response as any).data?.data || (response as any).data

            materials.value = data.items || []
            total.value = data.total || 0

            return {items: materials.value, total: total.value}
        } catch (error: any) {
            console.error('搜索资料失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 重置过滤器
    const resetFilters = () => {
        filters.value = {
            page: 1,
            perPage: 20,
            courseId: undefined,
            categoryId: undefined,
            fileType: undefined,
            keyword: ''
        }
    }

    // 清除缓存
    const clearCache = () => {
        materialCache.value.clear()
    }

    // 清除过期缓存
    const clearExpiredCache = () => {
        const now = Date.now()
        materialCache.value.forEach((value, key) => {
            if (now - value.timestamp >= CACHE_DURATION) {
                materialCache.value.delete(key)
            }
        })
    }

    return {
        // 状态
        materials,
        currentMaterial,
        total,
        loading,
        filters,

        // 计算属性
        hasMore,
        isEmpty,

        // 方法
        fetchMaterials,
        fetchMaterialDetail,
        uploadMaterial,
        updateMaterial,
        deleteMaterial,
        searchMaterials,
        resetFilters,
        clearCache,
        clearExpiredCache
    }
})
