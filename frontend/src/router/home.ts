import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getDefaultHomeByRole } from '@/utils/roleRoutes'

const homeRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    redirect: () => {
      const authStore = useAuthStore()
      if (authStore.isLoggedIn && authStore.user) {
        return getDefaultHomeByRole(authStore.user.role)
      }
      return '/login'
    },
    meta: {
      title: '首页'
    }
  }
]

export default homeRoutes
