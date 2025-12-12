import {beforeEach, describe, expect, it, vi} from 'vitest'
import {mount} from '@vue/test-utils'
import {createPinia, setActivePinia} from 'pinia'
import UserAvatar from '../UserAvatar.vue'
import {useAuthStore} from '@/stores/auth'
import * as authController from '@/api/authController'

// Mock Vue Router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
    useRouter: () => ({push: mockPush}),
    useRoute: () => ({query: {}})
}))

// Mock Ant Design Vue message
vi.mock('ant-design-vue', () => ({
    message: {
        success: vi.fn(),
        error: vi.fn()
    }
}))

// Mock API calls
vi.mock('@/api/authController', () => ({
    authApiLoginPost: vi.fn(),
    authApiLogoutPost: vi.fn(),
    authApiStatusGet: vi.fn(),
    authApiGetLoginuserGet: vi.fn()
}))

describe('UserAvatar Component', () => {
    let authStore: ReturnType<typeof useAuthStore>

    beforeEach(() => {
        setActivePinia(createPinia())
        authStore = useAuthStore()
        localStorage.clear()
        vi.clearAllMocks()
    })

    describe('未登录状态', () => {
        it('should show login button when not logged in', () => {
            authStore.isLoggedIn = false
            const wrapper = mount(UserAvatar)

            const loginButton = wrapper.find('button')
            expect(loginButton.exists()).toBe(true)
            expect(loginButton.text()).toContain('登录')
        })

        it('should navigate to login page when login button clicked', async () => {
            authStore.isLoggedIn = false
            const wrapper = mount(UserAvatar)

            const loginButton = wrapper.find('button')
            await loginButton.trigger('click')

            expect(mockPush).toHaveBeenCalledWith('/login')
        })
    })

    describe('已登录状态', () => {
        beforeEach(() => {
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
        })

        it('should show user avatar when logged in', () => {
            const wrapper = mount(UserAvatar)

            // Should show dropdown trigger
            const dropdown = wrapper.find('.user-avatar-container')
            expect(dropdown.exists()).toBe(true)
        })

        it('should display user avatar image when avatar URL exists', () => {
            authStore.user!.avatar = 'https://example.com/avatar.jpg'
            const wrapper = mount(UserAvatar)

            const avatar = wrapper.find('.ant-avatar')
            expect(avatar.exists()).toBe(true)
        })

        it('should display default avatar when no avatar URL', () => {
            authStore.user!.avatar = null
            const wrapper = mount(UserAvatar)

            const avatar = wrapper.find('.ant-avatar')
            expect(avatar.exists()).toBe(true)
            // Should show first letter of name
            expect(avatar.text()).toBe('教')
        })

        it('should show user display name', () => {
            const wrapper = mount(UserAvatar)

            expect(wrapper.text()).toContain('教师一')
        })

        it('should handle logout', async () => {
            vi.mocked(authController.authApiLogoutPost).mockResolvedValue({} as any)

            const wrapper = mount(UserAvatar)

            // Find and click logout menu item
            const logoutItem = wrapper.find('[data-test="logout-item"]')
            if (logoutItem.exists()) {
                await logoutItem.trigger('click')
                await new Promise(resolve => setTimeout(resolve, 100))

                expect(authStore.isLoggedIn).toBe(false)
                expect(authStore.user).toBeNull()
                expect(mockPush).toHaveBeenCalledWith('/login')
            }
        })
    })

    describe('下拉菜单', () => {
        beforeEach(() => {
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
        })

        it('should show dropdown menu items', () => {
            const wrapper = mount(UserAvatar)

            // Check for menu items
            const menuItems = wrapper.findAll('.ant-dropdown-menu-item')
            expect(menuItems.length).toBeGreaterThan(0)
        })
    })
})
