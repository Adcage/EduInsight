import {beforeEach, describe, expect, it, vi} from 'vitest'
import {createPinia, setActivePinia} from 'pinia'
import {useAuth} from '../useAuth'
import {useAuthStore} from '@/stores/auth'
import * as authController from '@/api/authController'

// Mock Vue Router
const mockPush = vi.fn()
const mockRoute = {query: {}}
vi.mock('vue-router', () => ({
    useRouter: () => ({push: mockPush}),
    useRoute: () => mockRoute
}))

// Mock Ant Design Vue message
vi.mock('ant-design-vue', () => ({
    message: {
        success: vi.fn(),
        error: vi.fn(),
        warning: vi.fn()
    }
}))

// Mock API calls
vi.mock('@/api/authController', () => ({
    authApiLoginPost: vi.fn(),
    authApiLogoutPost: vi.fn(),
    authApiStatusGet: vi.fn(),
    authApiGetLoginuserGet: vi.fn()
}))

describe('useAuth Composable', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        localStorage.clear()
        vi.clearAllMocks()
        mockRoute.query = {}
    })

    describe('login', () => {
        it('should login successfully and redirect to default home', async () => {
            const mockUser: API.UserResponseModel = {
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

            vi.mocked(authController.authApiLoginPost).mockResolvedValue({
                data: {message: '登录成功', user: mockUser}
            } as any)

            const {login} = useAuth()
            const credentials: API.UserLoginModel = {
                loginIdentifier: 'teacher1',
                password: 'password123'
            }

            await login(credentials)

            expect(mockPush).toHaveBeenCalledWith('/teacher/materials')
        })

        it('should redirect to saved redirect path after login', async () => {
            const mockUser: API.UserResponseModel = {
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

            vi.mocked(authController.authApiLoginPost).mockResolvedValue({
                data: {message: '登录成功', user: mockUser}
            } as any)

            const authStore = useAuthStore()
            authStore.setRedirectPath('/student/grades')

            const {login} = useAuth()
            await login({loginIdentifier: 'student1', password: 'password123'})

            expect(mockPush).toHaveBeenCalledWith('/student/grades')
            expect(authStore.redirectPath).toBe('')
        })

        it('should handle login error with 401 status', async () => {
            const error = {
                response: {
                    status: 401,
                    data: {message: 'Invalid credentials'}
                }
            }

            vi.mocked(authController.authApiLoginPost).mockRejectedValue(error)

            const {login} = useAuth()

            await expect(login({
                loginIdentifier: 'wrong',
                password: 'wrong'
            })).rejects.toThrow()
        })
    })

    describe('logout', () => {
        it('should logout successfully and redirect to login page', async () => {
            vi.mocked(authController.authApiLogoutPost).mockResolvedValue({} as any)

            const authStore = useAuthStore()
            authStore.user = {
                id: 1,
                username: 'test',
                userCode: 'T001',
                email: 'test@test.com',
                realName: '测试',
                role: 'teacher',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true

            const {logout} = useAuth()
            await logout()

            expect(authStore.user).toBeNull()
            expect(authStore.isLoggedIn).toBe(false)
            expect(mockPush).toHaveBeenCalledWith('/login')
        })
    })

    describe('checkAuth', () => {
        it('should check auth status when not logged in', async () => {
            vi.mocked(authController.authApiStatusGet).mockResolvedValue({} as any)
            vi.mocked(authController.authApiGetLoginuserGet).mockResolvedValue({
                data: {
                    username: 'test',
                    userCode: 'T001',
                    email: 'test@test.com',
                    realName: '测试',
                    role: 'teacher',
                    createdAt: '2024-01-01'
                }
            } as any)

            const {checkAuth} = useAuth()
            await checkAuth()

            expect(authController.authApiStatusGet).toHaveBeenCalled()
        })

        it('should not check auth status when already logged in', async () => {
            const authStore = useAuthStore()
            authStore.isLoggedIn = true

            const {checkAuth} = useAuth()
            await checkAuth()

            expect(authController.authApiStatusGet).not.toHaveBeenCalled()
        })
    })

    describe('computed properties', () => {
        it('should expose reactive user properties', () => {
            const authStore = useAuthStore()
            const {user, isLoggedIn, isAdmin, isTeacher, isStudent} = useAuth()

            expect(user.value).toBeNull()
            expect(isLoggedIn.value).toBe(false)
            expect(isAdmin.value).toBe(false)
            expect(isTeacher.value).toBe(false)
            expect(isStudent.value).toBe(false)

            authStore.user = {
                id: 1,
                username: 'admin',
                userCode: 'A001',
                email: 'admin@test.com',
                realName: '管理员',
                role: 'admin',
                status: true,
                createdAt: '2024-01-01',
                updatedAt: '2024-01-01'
            }
            authStore.isLoggedIn = true

            expect(user.value).toEqual(authStore.user)
            expect(isLoggedIn.value).toBe(true)
            expect(isAdmin.value).toBe(true)
            expect(isTeacher.value).toBe(false)
            expect(isStudent.value).toBe(false)
        })
    })
})
