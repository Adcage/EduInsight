import {defineStore} from 'pinia'
import {computed, ref} from 'vue'

export interface Course {
    id: number
    name: string
    code: string
    description?: string
    teacherId: number
    semester?: string
    academicYear?: string
    credit?: number
    totalHours?: number
    status: number
    createdAt: string
    updatedAt: string
    teacher?: {
        id: number
        realName: string
    }
    materialCount?: number
}

export const useCourseStore = defineStore('course', () => {
    // 状态
    const courses = ref<Course[]>([])
    const currentCourse = ref<Course | null>(null)
    const loading = ref(false)

    // 缓存
    const cacheTimestamp = ref<number>(0)
    const CACHE_DURATION = 10 * 60 * 1000 // 10分钟缓存

    // 计算属性
    const activeCourses = computed(() => {
        return courses.value.filter(course => course.status === 1)
    })

    const courseMap = computed(() => {
        const map = new Map<number, Course>()
        courses.value.forEach(course => {
            map.set(course.id, course)
        })
        return map
    })

    // 获取课程列表
    const fetchCourses = async (forceRefresh = false) => {
        // 检查缓存
        if (!forceRefresh && cacheTimestamp.value > 0) {
            if (Date.now() - cacheTimestamp.value < CACHE_DURATION) {
                return courses.value
            }
        }

        loading.value = true
        try {
            // TODO: 替换为实际的课程API
            // const response = await courseApiGet()
            // const data = (response as any).data?.data || (response as any).data
            // courses.value = Array.isArray(data) ? data : []

            // 临时模拟数据
            courses.value = []
            cacheTimestamp.value = Date.now()

            return courses.value
        } catch (error: any) {
            console.error('获取课程列表失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 获取课程详情
    const fetchCourseDetail = async (id: number) => {
        loading.value = true
        try {
            // TODO: 替换为实际的课程API
            // const response = await courseApiIntCourseIdGet({ courseId: id })
            // const data = (response as any).data?.data || (response as any).data
            // currentCourse.value = data

            currentCourse.value = courseMap.value.get(id) || null
            return currentCourse.value
        } catch (error: any) {
            console.error('获取课程详情失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 创建课程
    const createCourse = async (_courseData: {
        name: string
        code: string
        description?: string
        semester?: string
        academicYear?: string
        credit?: number
        totalHours?: number
    }) => {
        try {
            // TODO: 替换为实际的课程API
            // const response = await courseApiPost(courseData)
            // const data = (response as any).data?.data || (response as any).data

            // 刷新课程列表
            await fetchCourses(true)

            // return data
        } catch (error: any) {
            console.error('创建课程失败:', error)
            throw error
        }
    }

    // 更新课程
    const updateCourse = async (
        _id: number,
        _courseData: Partial<Course>
    ) => {
        try {
            // TODO: 替换为实际的课程API
            // const response = await courseApiIntCourseIdPut({ courseId: _id }, _courseData)
            // const data = (response as any).data?.data || (response as any).data

            // 刷新课程列表
            await fetchCourses(true)

            // return data
        } catch (error: any) {
            console.error('更新课程失败:', error)
            throw error
        }
    }

    // 删除课程
    const deleteCourse = async (_id: number) => {
        try {
            // TODO: 替换为实际的课程API
            // await courseApiIntCourseIdDelete({ courseId: _id })

            // 刷新课程列表
            await fetchCourses(true)
        } catch (error: any) {
            console.error('删除课程失败:', error)
            throw error
        }
    }

    // 根据ID获取课程
    const getCourseById = (id: number): Course | undefined => {
        return courseMap.value.get(id)
    }

    // 清除缓存
    const clearCache = () => {
        cacheTimestamp.value = 0
    }

    return {
        // 状态
        courses,
        currentCourse,
        loading,

        // 计算属性
        activeCourses,
        courseMap,

        // 方法
        fetchCourses,
        fetchCourseDetail,
        createCourse,
        updateCourse,
        deleteCourse,
        getCourseById,
        clearCache
    }
})
