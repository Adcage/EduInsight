declare namespace API {
  type LoginResponseModel = {
    /** Message 登录结果消息 */
    message: string
    /** 用户信息 */
    user: UserResponseModel
  }

  type MessageResponseModel = {
    /** Errorcode 错误代码 */
    errorCode?: string | null
    /** Message 响应消息 */
    message: string
  }

  type PasswordChangeModel = {
    /** Confirmpassword 确认新密码 */
    confirmPassword: string
    /** Newpassword 新密码 */
    newPassword: string
    /** Oldpassword 原密码 */
    oldPassword: string
  }

  type userApiGetParams = {
    /** 页码 */
    page?: number
    /** 每页数量 */
    perPage?: number
    /** 角色筛选 */
    role?: UserRoleEnum | null
    /** 状态筛选 */
    status?: boolean | null
    /** 搜索关键词（用户名、真实姓名、邮箱） */
    search?: string | null
  }

  type userApiIntUserIdActivatePostParams = {
    /** 用户ID */
    userId: number
  }

  type userApiIntUserIdDeactivatePostParams = {
    /** 用户ID */
    userId: number
  }

  type userApiIntUserIdGetParams = {
    /** 用户ID */
    userId: number
  }

  type userApiIntUserIdPutParams = {
    /** 用户ID */
    userId: number
  }

  type UserListResponseModel = {
    /** Page 当前页码 */
    page?: number
    /** Pages 总页数 */
    pages: number
    /** Perpage 每页数量 */
    perPage?: number
    /** Total 用户总数 */
    total: number
    /** Users 用户列表 */
    users: UserResponseModel[]
  }

  type UserLoginModel = {
    /** Loginidentifier 登录标识符（邮箱/用户名/工号） */
    loginIdentifier: string
    /** Password 密码 */
    password: string
  }

  type UserProfileModel = {
    /** Avatar 头像URL */
    avatar?: string | null
    /** Classid 班级ID */
    classId?: number | null
    /** Createdat 注册时间 */
    createdAt: string
    /** Email 邮箱地址 */
    email: string
    /** Lastlogintime 最后登录时间 */
    lastLoginTime?: string | null
    /** Phone 手机号码 */
    phone?: string | null
    /** Realname 真实姓名 */
    realName: string
    /** Role 用户角色 */
    role: string
    /** Usercode 工号/学号 */
    userCode: string
    /** Username 用户名 */
    username: string
  }

  type UserRegisterModel = {
    /** Classid 班级ID（学生角色时使用） */
    classId?: number | null
    /** Email 邮箱地址 */
    email: string
    /** Password 密码 */
    password: string
    /** Phone 手机号码 */
    phone?: string | null
    /** Realname 真实姓名 */
    realName: string
    /** 用户角色 */
    role?: UserRoleEnum
    /** Usercode 工号/学号 */
    userCode: string
    /** Username 用户名 */
    username: string
  }

  type UserResponseModel = {
    /** Avatar 头像URL */
    avatar?: string | null
    /** Classid 班级ID */
    classId?: number | null
    /** Createdat 创建时间 */
    createdAt: string
    /** Email 邮箱地址 */
    email: string
    /** Id 用户ID */
    id: number
    /** Lastlogintime 最后登录时间 */
    lastLoginTime?: string | null
    /** Phone 手机号码 */
    phone?: string | null
    /** Realname 真实姓名 */
    realName: string
    /** Role 用户角色 */
    role: string
    /** Status 账户状态 */
    status: boolean
    /** Updatedat 更新时间 */
    updatedAt: string
    /** Usercode 工号/学号 */
    userCode: string
    /** Username 用户名 */
    username: string
  }

  type UserRoleEnum = 'admin' | 'teacher' | 'student'

  type UserStatsModel = {
    /** Activeusers 活跃用户数 */
    activeUsers: number
    /** Admincount 管理员数量 */
    adminCount: number
    /** Inactiveusers 非活跃用户数 */
    inactiveUsers: number
    /** Studentcount 学生数量 */
    studentCount: number
    /** Teachercount 教师数量 */
    teacherCount: number
    /** Totalusers 用户总数 */
    totalUsers: number
  }

  type UserUpdateModel = {
    /** Avatar 头像URL */
    avatar?: string | null
    /** Email 邮箱地址 */
    email?: string | null
    /** Phone 手机号码 */
    phone?: string | null
    /** Realname 真实姓名 */
    realName?: string | null
    /** Username 用户名 */
    username?: string | null
  }

  type ValidationErrorModel = {
    /** Error context an optional object which contains values required to render the error message. */
    ctx?: Record<string, any> | null
    /** Location the error's location as a list.  */
    loc?: string[] | null
    /** Message a computer-readable identifier of the error type. */
    msg?: string | null
    /** Error Type a human readable explanation of the error. */
    type_?: string | null
  }
}
