import {computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {message} from 'ant-design-vue'
import {useAuthStore} from '@/stores/auth'
import {getDefaultHomeByRole} from '@/utils/roleRoutes'

/**
 * 认证相关组合式函数
 * 封装认证逻辑和错误处理
 */
export function useAuth() {
    const authStore = useAuthStore()
    const router = useRouter()
    const route = useRoute()

    /**
     * 用户登录
     * @param credentials 登录凭证
     */
    const login = async (credentials: API.UserLoginModel) => {
        try {
            // 调用 store 的 login 方法
            await authStore.login(credentials)

            // 获取重定向路径
            const redirect =
                (route.query.redirect as string) ||
                authStore.redirectPath ||
                getDefaultHomeByRole(authStore.user?.role)

            // 清除保存的重定向路径
            authStore.clearRedirectPath()

            // 跳转到目标页面
            await router.push(redirect)

            // 显示成功提示
            message.success('登录成功')
        } catch (error) {
            // 处理登录错误
            handleLoginError(error)
            throw error
        }
    }

    /**
     * 用户登出
     */
    const logout = async () => {
        try {
            await authStore.logout()
            await router.push('/login')
            message.success('已退出登录')
        } catch (error) {
            console.error('Logout failed:', error)
            message.error('登出失败，请重试')
            throw error
        }
    }

    /**
     * 检查登录状态
     */
    const checkAuth = async () => {
        if (!authStore.isLoggedIn) {
            try {
                await authStore.checkLoginStatus()
            } catch (error) {
                console.error('Check auth status failed:', error)
                // 静默失败，不显示错误提示
            }
        }
    }

    /**
     * 处理登录错误
     * @param error 错误对象
     */
    function handleLoginError(error: any) {
        const status = error.response?.status
        const errorMessage = error.response?.data?.message

        switch (status) {
            case 401:
                message.error('用户名或密码错误')
                break
            case 500:
                message.error('服务器错误，请稍后重试')
                break
            case 0:
            case undefined:
                handleNetworkError(error)
                break
            default:
                message.error(errorMessage || '登录失败，请重试')
        }
    }

    /**
     * 处理网络错误
     * @param error 错误对象
     */
    function handleNetworkError(error: any) {
        if (!error.response) {
            // 网络错误或请求超时
            if (error.code === 'ECONNABORTED') {
                message.error('网络连接超时，请检查网络')
            } else if (error.message?.includes('Network Error')) {
                message.error('网络连接失败，请检查网络')
            } else {
                message.error('服务暂时不可用，请稍后重试')
            }
        }
    }


    return {
        // 响应式状态
        user: computed(() => authStore.user),
        isLoggedIn: computed(() => authStore.isLoggedIn),
        isAdmin: computed(() => authStore.isAdmin),
        isTeacher: computed(() => authStore.isTeacher),
        isStudent: computed(() => authStore.isStudent),
        userDisplayName: computed(() => authStore.userDisplayName),
        loading: computed(() => authStore.loading),

        // 方法
        login,
        logout,
        checkAuth
    }
}
