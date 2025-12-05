import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  categoryApiGet,
  categoryApiPost,
  categoryApiIntCategoryIdPut,
  categoryApiIntCategoryIdDelete
} from '@/api/categoryController'

export interface Category {
  id: number
  name: string
  parentId?: number
  description?: string
  sortOrder: number
  createdAt: string
  updatedAt: string
  children?: Category[]
  materialCount?: number
}

export const useCategoryStore = defineStore('category', () => {
  // 状态
  const categories = ref<Category[]>([])
  const categoryTree = ref<Category[]>([])
  const loading = ref(false)

  // 缓存
  const cacheTimestamp = ref<number>(0)
  const CACHE_DURATION = 10 * 60 * 1000 // 10分钟缓存

  // 计算属性
  const flatCategories = computed(() => {
    const flatten = (cats: Category[]): Category[] => {
      return cats.reduce((acc, cat) => {
        acc.push(cat)
        if (cat.children && cat.children.length > 0) {
          acc.push(...flatten(cat.children))
        }
        return acc
      }, [] as Category[])
    }
    return flatten(categoryTree.value)
  })

  const categoryMap = computed(() => {
    const map = new Map<number, Category>()
    flatCategories.value.forEach(cat => {
      map.set(cat.id, cat)
    })
    return map
  })

  // 获取分类列表
  const fetchCategories = async (forceRefresh = false) => {
    // 检查缓存
    if (!forceRefresh && cacheTimestamp.value > 0) {
      if (Date.now() - cacheTimestamp.value < CACHE_DURATION) {
        return categoryTree.value
      }
    }

    loading.value = true
    try {
      const response = await categoryApiGet()
      const data = (response as any).data?.data || (response as any).data

      categories.value = Array.isArray(data) ? data : []
      categoryTree.value = buildTree(categories.value)
      cacheTimestamp.value = Date.now()

      return categoryTree.value
    } catch (error: any) {
      console.error('获取分类列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 构建分类树
  const buildTree = (cats: Category[]): Category[] => {
    const map = new Map<number, Category>()
    const roots: Category[] = []

    // 创建映射
    cats.forEach(cat => {
      map.set(cat.id, { ...cat, children: [] })
    })

    // 构建树结构
    cats.forEach(cat => {
      const node = map.get(cat.id)!
      if (cat.parentId === null || cat.parentId === undefined) {
        roots.push(node)
      } else {
        const parent = map.get(cat.parentId)
        if (parent) {
          if (!parent.children) {
            parent.children = []
          }
          parent.children.push(node)
        } else {
          // 如果找不到父节点，作为根节点
          roots.push(node)
        }
      }
    })

    // 按 sortOrder 排序
    const sortTree = (nodes: Category[]) => {
      nodes.sort((a, b) => a.sortOrder - b.sortOrder)
      nodes.forEach(node => {
        if (node.children && node.children.length > 0) {
          sortTree(node.children)
        }
      })
    }
    sortTree(roots)

    return roots
  }

  // 创建分类
  const createCategory = async (categoryData: {
    name: string
    parentId?: number
    description?: string
    sortOrder?: number
  }) => {
    try {
      const response = await categoryApiPost(categoryData)
      const data = (response as any).data?.data || (response as any).data

      // 刷新分类列表
      await fetchCategories(true)

      return data
    } catch (error: any) {
      console.error('创建分类失败:', error)
      throw error
    }
  }

  // 更新分类
  const updateCategory = async (
    id: number,
    categoryData: {
      name?: string
      parentId?: number
      description?: string
      sortOrder?: number
    }
  ) => {
    try {
      const response = await categoryApiIntCategoryIdPut(
        { categoryId: id },
        categoryData
      )
      const data = (response as any).data?.data || (response as any).data

      // 刷新分类列表
      await fetchCategories(true)

      return data
    } catch (error: any) {
      console.error('更新分类失败:', error)
      throw error
    }
  }

  // 删除分类
  const deleteCategory = async (id: number) => {
    try {
      await categoryApiIntCategoryIdDelete({ categoryId: id })

      // 刷新分类列表
      await fetchCategories(true)
    } catch (error: any) {
      console.error('删除分类失败:', error)
      throw error
    }
  }

  // 根据ID获取分类
  const getCategoryById = (id: number): Category | undefined => {
    return categoryMap.value.get(id)
  }

  // 获取分类路径（面包屑）
  const getCategoryPath = (id: number): Category[] => {
    const path: Category[] = []
    let current = categoryMap.value.get(id)

    while (current) {
      path.unshift(current)
      if (current.parentId) {
        current = categoryMap.value.get(current.parentId)
      } else {
        break
      }
    }

    return path
  }

  // 清除缓存
  const clearCache = () => {
    cacheTimestamp.value = 0
  }

  return {
    // 状态
    categories,
    categoryTree,
    loading,

    // 计算属性
    flatCategories,
    categoryMap,

    // 方法
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    getCategoryById,
    getCategoryPath,
    clearCache
  }
})
