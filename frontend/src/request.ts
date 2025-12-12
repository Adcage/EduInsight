import axios from 'axios'
import {message} from 'ant-design-vue'
import router from '@/router'

// 自动检测API地址
// 开发环境：使用localhost
// 生产环境或移动端：使用当前访问的主机地址
const getBaseURL = () => {
    // 如果是通过IP访问（非localhost），使用相同的主机地址
    const hostname = window.location.hostname;
    const protocol = window.location.protocol; // 获取当前协议 (http: 或 https:)

    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        // 本地开发环境
        return 'http://localhost:5030';
    } else {
        // 生产环境：使用当前协议和域名（不加端口，由反向代理处理）
        return `${protocol}//${hostname}`;
    }
};

// 创建 Axios 实例
const myAxios = axios.create({
    baseURL: getBaseURL(),
    timeout: 60000,
    withCredentials: true,
})

// 全局请求拦截器
myAxios.interceptors.request.use(
    function (config) {
        // Do something before request is sent
        return config
    },
    function (error) {
        // Do something with request error
        return Promise.reject(error)
    },
)

// 全局响应拦截器
myAxios.interceptors.response.use(
    async function (response) {
        // 对于blob类型的响应,直接返回整个响应对象
        if (response.config.responseType === 'blob') {
            return response
        }
        
        const {data} = response
        // 未登录
        if (data.code === 40100) {
            // 不是获取用户信息的请求，并且用户目前不是已经在用户登录页面，则跳转到登录页面
            if (!response.request.responseURL.includes('user/get/login') && !window.location.pathname.includes('/user/login')) {
                message.warning('请先登录')
                await router.push({
                    path: '/user/login',
                    query: {
                        redirect: window.location.pathname,
                    },
                })
            }
        }
        return response
    },
    async function (error) {
        // 处理 401 错误（会话过期）
        if (error.response?.status === 401) {
            // 动态导入 auth store 以避免循环依赖
            const {useAuthStore} = await import('@/stores/auth')
            const authStore = useAuthStore()

            // 清除用户状态
            authStore.clearUser()

            // 如果不在登录页面，重定向到登录页
            if (!window.location.pathname.includes('/login')) {
                // 保存当前页面路径用于登录后返回
                authStore.setRedirectPath(window.location.pathname)

                message.warning('登录已过期，请重新登录')
                await router.push({
                    path: '/login',
                    query: {
                        redirect: window.location.pathname
                    }
                })
            }
        }

        return Promise.reject(error)
    },
)

export default myAxios
