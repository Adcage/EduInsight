/**
 * 主题管理组合函数
 */

import {computed, ref} from 'vue'

export type ThemeType = 'light' | 'dark'

const THEME_STORAGE_KEY = 'learning-study-theme'

// 全局主题状态
const currentTheme = ref<ThemeType>('light')

/**
 * 主题管理组合函数
 */
export function useTheme() {
    // 切换主题
    const toggleTheme = () => {
        const newTheme: ThemeType = currentTheme.value === 'light' ? 'dark' : 'light'
        setTheme(newTheme)
    }

    // 设置主题
    const setTheme = (theme: ThemeType) => {
        currentTheme.value = theme
        document.documentElement.setAttribute('data-theme', theme)
        localStorage.setItem(THEME_STORAGE_KEY, theme)
    }

    // 获取系统主题偏好
    const getSystemTheme = (): ThemeType => {
        if (typeof window !== 'undefined' && window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        }
        return 'light'
    }

    // 初始化主题
    const initTheme = () => {
        // 优先从 localStorage 读取
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeType

        if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
            setTheme(savedTheme)
        } else {
            // 如果没有保存的主题，使用系统主题偏好
            const systemTheme = getSystemTheme()
            setTheme(systemTheme)
        }
    }

    // 监听系统主题变化
    const watchSystemTheme = () => {
        if (typeof window !== 'undefined' && window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

            const handleChange = (e: MediaQueryListEvent) => {
                // 只有在没有手动设置主题时才跟随系统
                const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
                if (!savedTheme) {
                    setTheme(e.matches ? 'dark' : 'light')
                }
            }

            mediaQuery.addEventListener('change', handleChange)

            // 返回清理函数
            return () => {
                mediaQuery.removeEventListener('change', handleChange)
            }
        }

        return () => {
        }
    }

    // 计算属性
    const isDark = computed(() => currentTheme.value === 'dark')
    const isLight = computed(() => currentTheme.value === 'light')

    // 主题名称
    const themeName = computed(() => {
        return currentTheme.value === 'light' ? '亮色模式' : '暗色模式'
    })

    return {
        // 状态
        currentTheme: computed(() => currentTheme.value),
        isDark,
        isLight,
        themeName,

        // 方法
        toggleTheme,
        setTheme,
        initTheme,
        watchSystemTheme,
        getSystemTheme
    }
}

// 自动初始化主题（在应用启动时调用）
export function initializeTheme() {
    const {initTheme, watchSystemTheme} = useTheme()

    // 初始化主题
    initTheme()

    // 监听系统主题变化
    const cleanup = watchSystemTheme()

    return cleanup
}
