/**
 * 角色路由工具函数
 * 根据用户角色返回对应的默认主页路径
 */

/**
 * 根据用户角色获取默认主页路径
 * @param role 用户角色 ('admin' | 'teacher' | 'student')
 * @returns 默认主页路径
 */
export function getDefaultHomeByRole(role?: string): string {
  switch (role) {
    case 'admin':
      // 管理员跳转到管理员仪表板
      return '/admin/dashboard'
    case 'teacher':
      // 教师跳转到教师资料中心
      return '/teacher/materials'
    case 'student':
      // 学生跳转到学生资料浏览
      return '/student/materials'
    default:
      // 未知角色或未登录跳转到首页
      return '/'
  }
}

/**
 * 检查用户是否有权限访问指定路由
 * @param userRole 用户角色
 * @param requiredRoles 路由要求的角色列表
 * @returns 是否有权限
 */
export function hasRoutePermission(
  userRole?: string,
  requiredRoles?: string[]
): boolean {
  // 如果没有角色要求，所有人都可以访问
  if (!requiredRoles || requiredRoles.length === 0) {
    return true
  }

  // 如果用户没有角色，无权访问
  if (!userRole) {
    return false
  }

  // 检查用户角色是否在要求的角色列表中
  return requiredRoles.includes(userRole)
}
