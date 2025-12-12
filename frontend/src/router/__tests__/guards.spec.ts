import {beforeEach, describe, expect, it} from 'vitest'
import type {Router} from 'vue-router'
import {createMemoryHistory, createRouter} from 'vue-router'
import {createPinia, setActivePinia} from 'pinia'
import {setupRouterGuards} from '../guards'
import {useAuthStore} from '@/stores/auth'

describe('Router Guards', () => {
    let router: Router
    let authStore: ReturnType<typeof useAuthStore>

    beforeEach(() => {
        setActivePinia(createPinia())
        authStore = useAuthStore()
        localStorage.clear()

        // Create a test router with some routes
        router = createRouter({
            history: createMemoryHistory(),
            routes: [
                {
                    path: '/login',
                    name: 'Login',
                    component: {template: '<div>Login</div>'}
                },
                {
                    path: '/protected',
                    name: 'Protected',
                    component: {template: '<div>Protected</div>'},
                    meta: {requiresAuth: true}
                },
                {
                    path: '/public',
                    name: 'Public',
                    component: {template: '<div>Public</div>'}
                },
                {
                    path: '/teacher/materials',
                    name: 'TeacherMaterials',
                    component: {template: '<div>Teacher Materials</div>'},
                    meta: {requiresAuth: true}
                }
            ]
        })

        setupRouterGuards(router)
    })

    describe('未登录用户访问受保护路由', () => {
        it('should redirect to login page', async () => {
            authStore.isLoggedIn = false

            await router.push('/protected')
            await router.isReady()

            expect(router.currentRoute.value.path).toBe('/login')
            expect(router.currentRoute.value.query.redirect).toBe('/protected')
            expect(authStore.redirectPath).toBe('/protected')
        })

        it('should allow access to public routes', async () => {
            authStore.isLoggedIn = false

            await router.push('/public')
            await router.isReady()

            expect(router.currentRoute.value.path).toBe('/public')
        })
    })

    describe('已登录用户访问登录页', () => {
        it('should redirect to default home based on role', async () => {
            authStore.user = {
                id: 1,
                username: 'teacher1',
                userCode: 'T001',
                email: 'teacher@test.com',
                realName: '教师一',
                role: 'teacher',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true

            await router.push('/login')
            await router.isReady()

            expect(router.currentRoute.value.path).toBe('/teacher/materials')
        })

        it('should redirect to saved redirect path', async () => {
            authStore.user = {
                id: 1,
                username: 'teacher1',
                userCode: 'T001',
                email: 'teacher@test.com',
                realName: '教师一',
                role: 'teacher',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true
            authStore.setRedirectPath('/teacher/materials')

            await router.push('/login')
            await router.isReady()

            expect(router.currentRoute.value.path).toBe('/teacher/materials')
            expect(authStore.redirectPath).toBe('')
        })

        it('should redirect to query redirect path', async () => {
            authStore.user = {
                id: 1,
                username: 'student1',
                userCode: 'S001',
                email: 'student@test.com',
                realName: '学生一',
                role: 'student',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true

            await router.push('/login?redirect=/protected')
            await router.isReady()

            expect(router.currentRoute.value.path).toBe('/protected')
        })
    })

    describe('已登录用户访问受保护路由', () => {
        it('should allow access', async () => {
            authStore.user = {
                id: 1,
                username: 'teacher1',
                userCode: 'T001',
                email: 'teacher@test.com',
                realName: '教师一',
                role: 'teacher',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true

            await router.push('/protected')
            await router.isReady()

            expect(router.currentRoute.value.path).toBe('/protected')
        })
    })

    describe('重定向路径保存和恢复', () => {
        it('should save redirect path when accessing protected route while not logged in', async () => {
            authStore.isLoggedIn = false

            await router.push('/teacher/materials')
            await router.isReady()

            expect(authStore.redirectPath).toBe('/teacher/materials')
            expect(localStorage.getItem('redirectPath')).toBe('/teacher/materials')
        })

        it('should clear redirect path after successful redirect', async () => {
            authStore.user = {
                id: 1,
                username: 'teacher1',
                userCode: 'T001',
                email: 'teacher@test.com',
                realName: '教师一',
                role: 'teacher',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true
            authStore.setRedirectPath('/protected')

            await router.push('/login')
            await router.isReady()

            expect(authStore.redirectPath).toBe('')
            expect(localStorage.getItem('redirectPath')).toBeNull()
        })
    })
})
