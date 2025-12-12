import {beforeEach, describe, expect, it, vi} from 'vitest'
import {mount} from '@vue/test-utils'
import {createPinia, setActivePinia} from 'pinia'
import LoginPage from '../LoginPage.vue'
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

describe('LoginPage Component', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        localStorage.clear()
        vi.clearAllMocks()
    })

    it('should render login form', () => {
        const wrapper = mount(LoginPage)

        expect(wrapper.find('.login-container').exists()).toBe(true)
        expect(wrapper.find('.login-title').text()).toBe('教学资源管理系统')
        expect(wrapper.find('.login-subtitle').text()).toBe('欢迎登录')
    })

    it('should have login identifier and password inputs', () => {
        const wrapper = mount(LoginPage)

        const inputs = wrapper.findAll('input')
        expect(inputs.length).toBeGreaterThanOrEqual(2)
    })

    it('should have a login button', () => {
        const wrapper = mount(LoginPage)

        const button = wrapper.find('button[type="submit"]')
        expect(button.exists()).toBe(true)
    })

    it('should validate required fields', async () => {
        const wrapper = mount(LoginPage)

        // Try to submit empty form
        const form = wrapper.find('form')
        await form.trigger('submit')

        // Form should not submit with empty fields
        expect(mockPush).not.toHaveBeenCalled()
    })

    it('should validate password minimum length', async () => {
        const wrapper = mount(LoginPage)

        // Set short password
        const passwordInput = wrapper.findAll('input')[1]
        await passwordInput.setValue('12345')

        const form = wrapper.find('form')
        await form.trigger('submit')

        // Form should not submit with short password
        expect(mockPush).not.toHaveBeenCalled()
    })

    it('should submit form with valid credentials', async () => {
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

        const wrapper = mount(LoginPage)

        // Fill in the form
        const inputs = wrapper.findAll('input')
        await inputs[0].setValue('teacher1')
        await inputs[1].setValue('password123')

        // Submit the form
        const form = wrapper.find('form')
        await form.trigger('submit')

        // Wait for async operations
        await new Promise(resolve => setTimeout(resolve, 100))

        expect(authController.authApiLoginPost).toHaveBeenCalledWith({
            loginIdentifier: 'teacher1',
            password: 'password123'
        })
    })

    it('should show loading state during login', async () => {
        vi.mocked(authController.authApiLoginPost).mockImplementation(
            () => new Promise(resolve => setTimeout(resolve, 1000))
        )

        const wrapper = mount(LoginPage)

        const inputs = wrapper.findAll('input')
        await inputs[0].setValue('teacher1')
        await inputs[1].setValue('password123')

        const form = wrapper.find('form')
        await form.trigger('submit')

        // Check loading state
        await wrapper.vm.$nextTick()
        const button = wrapper.find('button[type="submit"]')
        expect(button.attributes('disabled')).toBeDefined()
    })

    it('should handle Enter key press', async () => {
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

        const wrapper = mount(LoginPage)

        const inputs = wrapper.findAll('input')
        await inputs[0].setValue('teacher1')
        await inputs[1].setValue('password123')

        // Trigger Enter key on password input
        await inputs[1].trigger('keyup.enter')

        await new Promise(resolve => setTimeout(resolve, 100))

        expect(authController.authApiLoginPost).toHaveBeenCalled()
    })
})
