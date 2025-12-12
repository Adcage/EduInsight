import {beforeEach, describe, expect, it, vi} from 'vitest'
import {createPinia, setActivePinia} from 'pinia'
import {useAuthStore} from '../auth'

// Mock API calls
vi.mock('@/api/authController', () => ({
    authApiLoginPost: vi.fn(),
    authApiLogoutPost: vi.fn(),
    authApiStatusGet: vi.fn(),
    authApiGetLoginuserGet: vi.fn()
}))

describe('Auth Store', () => {
    beforeEach(() => {
        // 创建新的 pinia 实例
        setActivePinia(createPinia())
        // 清除 localStorage
        localStorage.clear()
    })

    it('should initialize with default state', () => {
        const authStore = useAuthStore()

        expect(authStore.user).toBeNull()
        expect(authStore.isLoggedIn).toBe(false)
        expect(authStore.loading).toBe(false)
        expect(authStore.redirectPath).toBe('')
    })

    it('should have correct role getters', () => {
        const authStore = useAuthStore()

        // 初始状态
        expect(authStore.isAdmin).toBe(false)
        expect(authStore.isTeacher).toBe(false)
        expect(authStore.isStudent).toBe(false)

        // 设置管理员用户
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

        expect(authStore.isAdmin).toBe(true)
        expect(authStore.isTeacher).toBe(false)
        expect(authStore.isStudent).toBe(false)
    })

    it('should return correct user display name', () => {
        const authStore = useAuthStore()

        // 无用户时
        expect(authStore.userDisplayName).toBe('')

        // 有真实姓名时
        authStore.user = {
            id: 1,
            username: 'testuser',
            userCode: 'T001',
            email: 'test@test.com',
            realName: '测试用户',
            role: 'student',
            status: true,
            createdAt: '2024-01-01',
            updatedAt: '2024-01-01'
        }

        expect(authStore.userDisplayName).toBe('测试用户')

        // 只有用户名时
        authStore.user.realName = ''
        expect(authStore.userDisplayName).toBe('testuser')
    })

    it('should return correct default avatar', () => {
        const authStore = useAuthStore()

        // 无用户时
        expect(authStore.defaultAvatar).toBe('')

        // 有真实姓名时
        authStore.user = {
            id: 1,
            username: 'testuser',
            userCode: 'T001',
            email: 'test@test.com',
            realName: '张三',
            role: 'student',
            status: true,
            createdAt: '2024-01-01',
            updatedAt: '2024-01-01'
        }

        expect(authStore.defaultAvatar).toBe('张')
    })

    it('should set and clear redirect path', () => {
        const authStore = useAuthStore()

        authStore.setRedirectPath('/test/path')
        expect(authStore.redirectPath).toBe('/test/path')
        expect(localStorage.getItem('redirectPath')).toBe('/test/path')

        authStore.clearRedirectPath()
        expect(authStore.redirectPath).toBe('')
        expect(localStorage.getItem('redirectPath')).toBeNull()
    })

    it('should clear user data', () => {
        const authStore = useAuthStore()

        // 设置用户数据
        authStore.user = {
            id: 1,
            username: 'testuser',
            userCode: 'T001',
            email: 'test@test.com',
            realName: '测试用户',
            role: 'student',
            status: true,
            createdAt: '2024-01-01',
            updatedAt: '2024-01-01'
        }
        authStore.isLoggedIn = true
        localStorage.setItem('user', JSON.stringify(authStore.user))
        localStorage.setItem('isLoggedIn', 'true')

        // 清除用户数据
        authStore.clearUser()

        expect(authStore.user).toBeNull()
        expect(authStore.isLoggedIn).toBe(false)
        expect(localStorage.getItem('user')).toBeNull()
        expect(localStorage.getItem('isLoggedIn')).toBeNull()
    })

    it('should restore state from localStorage', () => {
        const mockUser = {
            id: 1,
            username: 'testuser',
            userCode: 'T001',
            email: 'test@test.com',
            realName: '测试用户',
            role: 'student',
            status: true,
            createdAt: '2024-01-01',
            updatedAt: '2024-01-01'
        }

        // 设置 localStorage
        localStorage.setItem('user', JSON.stringify(mockUser))
        localStorage.setItem('isLoggedIn', 'true')
        localStorage.setItem('redirectPath', '/test/path')

        // 创建新的 store 实例（会自动调用 restoreState）
        const authStore = useAuthStore()

        expect(authStore.user).toEqual(mockUser)
        expect(authStore.isLoggedIn).toBe(true)
        expect(authStore.redirectPath).toBe('/test/path')
    })
})
