import {computed, ref} from 'vue'
import {defineStore} from 'pinia'
import {authApiGetLoginuserGet, authApiLoginPost, authApiLogoutPost, authApiStatusGet} from '@/api/authController'

/**
 * 认证状态管理 Store
 *
 * 管理用户登录状态、用户信息和重定向路径
 */
export const useAuthStore = defineStore('auth', () => {
    // ========== State ==========

    /** 当前登录用户信息 */
    const user = ref<API.UserResponseModel | null>(null)

    /** 登录状态 */
    const isLoggedIn = ref<boolean>(false)

    /** 状态检查加载中 */
    const loading = ref<boolean>(false)

    /** 登录后重定向路径 */
    const redirectPath = ref<string>('')

    // ========== Getters ==========

    /** 是否为管理员 (兼容大小写) */
    const isAdmin = computed(() => user.value?.role?.toLowerCase() === 'admin')

    /** 是否为教师 (兼容大小写) */
    const isTeacher = computed(() => user.value?.role?.toLowerCase() === 'teacher')

    /** 是否为学生 (兼容大小写) */
    const isStudent = computed(() => user.value?.role?.toLowerCase() === 'student')

    /** 用户显示名称 */
    const userDisplayName = computed(() => user.value?.realName || user.value?.username || '')

    /** 默认头像 */
    const defaultAvatar = computed(() => {
        if (!user.value) return ''
        // 使用用户真实姓名或用户名的首字母作为默认头像
        const name = user.value.realName || user.value.username
        return name ? name.charAt(0).toUpperCase() : 'U'
    })

    // ========== Actions ==========

    /**
     * 用户登录
     * @param credentials 登录凭证
     */
    async function login(credentials: API.UserLoginModel): Promise<void> {
        try {
            loading.value = true
            const response = await authApiLoginPost(credentials)

            // 设置用户信息和登录状态
            user.value = response.data.user
            isLoggedIn.value = true

            // 持久化到 localStorage
            localStorage.setItem('user', JSON.stringify(response.data.user))
            localStorage.setItem('isLoggedIn', 'true')
        } catch (error) {
            // 清除状态
            clearUser()
            throw error
        } finally {
            loading.value = false
        }
    }

    /**
     * 用户登出
     */
    async function logout(): Promise<void> {
        try {
            loading.value = true
            await authApiLogoutPost()
        } finally {
            // 无论 API 调用成功与否，都要清除本地状态
            clearUser()
            loading.value = false
        }
    }

    /**
     * 检查登录状态
     * 从服务器验证当前会话是否有效
     */
    async function checkLoginStatus(): Promise<void> {
        try {
            loading.value = true
            await authApiStatusGet()

            // 如果状态检查成功，尝试获取用户信息
            if (!user.value) {
                await fetchCurrentUser()
            }

            isLoggedIn.value = true
        } catch {
            // 会话无效，清除本地状态
            clearUser()
            isLoggedIn.value = false
        } finally {
            loading.value = false
        }
    }

    /**
     * 获取当前用户信息
     */
    async function fetchCurrentUser(): Promise<void> {
        try {
            loading.value = true
            const response = await authApiGetLoginuserGet()
            const userProfile = response.data
            console.log(userProfile);
            const userResponse: API.UserResponseModel = {
                id: user.value?.id || 0,
                username: userProfile.username,
                userCode: userProfile.userCode,
                email: userProfile.email,
                realName: userProfile.realName,
                role: userProfile.role,
                avatar: userProfile.avatar,
                phone: userProfile.phone,
                classId: userProfile.classId,
                status: user.value?.status ?? true,
                lastLoginTime: userProfile.lastLoginTime,
                createdAt: userProfile.createdAt,
                updatedAt: user.value?.updatedAt || new Date().toISOString()
            }

            user.value = userResponse
            isLoggedIn.value = true

            // 持久化到 localStorage
            localStorage.setItem('user', JSON.stringify(userResponse))
            localStorage.setItem('isLoggedIn', 'true')
        } catch (error) {
            console.error('Failed to fetch current user:', error)
            clearUser()
            throw error
        } finally {
            loading.value = false
        }
    }

    /**
     * 设置重定向路径
     * @param path 目标路径
     */
    function setRedirectPath(path: string): void {
        redirectPath.value = path
        localStorage.setItem('redirectPath', path)
    }

    /**
     * 清除重定向路径
     */
    function clearRedirectPath(): void {
        redirectPath.value = ''
        localStorage.removeItem('redirectPath')
    }

    /**
     * 清除用户信息
     */
    function clearUser(): void {
        user.value = null
        isLoggedIn.value = false
        localStorage.removeItem('user')
        localStorage.removeItem('isLoggedIn')
    }

    /**
     * 从 localStorage 恢复状态
     * 应在应用启动时调用
     */
    function restoreState(): void {
        try {
            const savedUser = localStorage.getItem('user')
            const savedIsLoggedIn = localStorage.getItem('isLoggedIn')
            const savedRedirectPath = localStorage.getItem('redirectPath')

            if (savedUser && savedIsLoggedIn === 'true') {
                user.value = JSON.parse(savedUser)
                isLoggedIn.value = true
            }

            if (savedRedirectPath) {
                redirectPath.value = savedRedirectPath
            }
        } catch (error) {
            console.error('Failed to restore auth state:', error)
            clearUser()
        }
    }

    // 初始化时恢复状态
    restoreState()

    return {
        // State
        user,
        isLoggedIn,
        loading,
        redirectPath,

        // Getters
        isAdmin,
        isTeacher,
        isStudent,
        userDisplayName,
        defaultAvatar,

        // Actions
        login,
        logout,
        checkLoginStatus,
        fetchCurrentUser,
        setRedirectPath,
        clearRedirectPath,
        clearUser,
        restoreState
    }
})
