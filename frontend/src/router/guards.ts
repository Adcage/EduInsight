import type {Router} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import {getDefaultHomeByRole} from '@/utils/roleRoutes'
import {message} from 'ant-design-vue'

/**
 * 设置路由守卫
 * @param router Vue Router 实例
 */
export function setupRouterGuards(router: Router): void {
    /**
     * 全局前置守卫
     * 处理认证和重定向逻辑
     */
    router.beforeEach(async (to, from, next) => {
        const authStore = useAuthStore()

        // 检查路由是否需要认证
        const requiresAuth = to.meta.requiresAuth as boolean | undefined
        const requiredRoles = to.meta.roles as string[] | undefined

        // 如果需要认证但未登录
        if (requiresAuth && !authStore.isLoggedIn) {
            // 保存目标路径用于登录后返回
            authStore.setRedirectPath(to.fullPath)

            // 重定向到登录页,并在 query 中保存重定向路径
            next({
                path: '/login',
                query: {redirect: to.fullPath}
            })
            return
        }

        // 检查角色权限
        if (requiresAuth && authStore.isLoggedIn && requiredRoles && requiredRoles.length > 0) {
            const userRole = authStore.user?.role

            // 统一转换为小写进行比较，兼容大小写
            const normalizedUserRole = userRole?.toLowerCase()
            const normalizedRequiredRoles = requiredRoles.map(r => r.toLowerCase())

            // 如果用户角色不在允许的角色列表中
            if (!normalizedUserRole || !normalizedRequiredRoles.includes(normalizedUserRole)) {
                message.warn(`访问被拒绝: 用户角色 ${userRole} 无权访问 ${to.path}`)

                // 重定向到用户角色对应的默认主页
                const defaultHome = getDefaultHomeByRole(userRole)
                next({
                    path: defaultHome,
                    replace: true
                })
                return
            }
        }

        // 如果已登录访问登录页
        if (to.path === '/login' && authStore.isLoggedIn) {
            // 获取重定向路径
            const redirect = (to.query.redirect as string) || authStore.redirectPath

            // 清除保存的重定向路径
            authStore.clearRedirectPath()

            // 如果有重定向路径，跳转到该路径
            if (redirect && redirect !== '/login') {
                next(redirect)
                return
            }

            // 否则根据角色跳转到默认主页
            const defaultHome = getDefaultHomeByRole(authStore.user?.role)
            next(defaultHome)
            return
        }

        // 其他情况正常放行
        next()
    })
}


