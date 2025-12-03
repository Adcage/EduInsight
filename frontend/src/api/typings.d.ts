declare namespace API {
  type LoginResponseModel = {
    /** Message 登录结果消息 */
    message: string
    /** 用户信息 */
    user: UserResponseModel
  }

  type MessageResponseModel = {
    /** Error Code 错误代码 */
    error_code?: string | null
    /** Message 响应消息 */
    message: string
  }

  type orderApiGetParams = {
    /** 订单状态 */
    status?: OrderStatusEnum | null
    /** 用户ID */
    userId?: number | null
    /** 开始日期 */
    startDate?: string | null
    /** 结束日期 */
    endDate?: string | null
    /** 页码 */
    page?: number
    /** 每页数量 */
    perPage?: number
  }

  type orderApiIntOrderIdCancelDeleteParams = {
    /** 订单ID */
    orderId: number
  }

  type orderApiIntOrderIdGetParams = {
    /** 订单ID */
    orderId: number
  }

  type orderApiIntOrderIdPutParams = {
    /** 订单ID */
    orderId: number
  }

  type OrderCreateModel = {
    /** Items 订单项列表 */
    items: OrderItemCreateModel[]
    /** Notes 订单备注 */
    notes?: string | null
    /** Shippingaddress 收货地址 */
    shippingAddress?: string | null
  }

  type OrderItemCreateModel = {
    /** Productid 产品ID */
    productId: number
    /** Quantity 数量 */
    quantity: number
  }

  type OrderStatusEnum = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'

  type OrderUpdateModel = {
    /** Notes 订单备注 */
    notes?: string | null
    /** Shippingaddress 收货地址 */
    shippingAddress?: string | null
    /** 订单状态 */
    status?: OrderStatusEnum | null
  }

  type PasswordChangeModel = {
    /** Confirm Password 确认新密码 */
    confirm_password: string
    /** New Password 新密码 */
    new_password: string
    /** Old Password 原密码 */
    old_password: string
  }

  type productApiGetParams = {
    /** 产品分类 */
    category?: string | null
    /** 最低价格 */
    minPrice?: number | string | null
    /** 最高价格 */
    maxPrice?: number | string | null
    /** 仅显示有库存商品 */
    inStockOnly?: boolean | null
    /** 页码 */
    page?: number
    /** 每页数量 */
    perPage?: number
  }

  type productApiIntProductIdDeleteParams = {
    /** 产品ID */
    productId: number
  }

  type productApiIntProductIdGetParams = {
    /** 产品ID */
    productId: number
  }

  type productApiIntProductIdPutParams = {
    /** 产品ID */
    productId: number
  }

  type ProductCreateModel = {
    /** Category 产品分类 */
    category?: string | null
    /** Description 产品描述 */
    description?: string | null
    /** Name 产品名称 */
    name: string
    /** Price 产品价格 */
    price: number | string
    /** Stock 库存数量 */
    stock?: number
  }

  type ProductUpdateModel = {
    /** Category 产品分类 */
    category?: string | null
    /** Description 产品描述 */
    description?: string | null
    /** Isactive 是否激活 */
    isActive?: boolean | null
    /** Name 产品名称 */
    name?: string | null
    /** Price 产品价格 */
    price?: number | string | null
    /** Stock 库存数量 */
    stock?: number | null
  }

  type userApiGetParams = {
    /** 页码 */
    page?: number
    /** 每页数量 */
    per_page?: number
    /** 角色筛选 */
    role?: UserRoleEnum | null
    /** 状态筛选 */
    status?: boolean | null
    /** 搜索关键词（用户名、真实姓名、邮箱） */
    search?: string | null
  }

  type userApiIntUserIdActivatePostParams = {
    /** 用户ID */
    user_id: number
  }

  type userApiIntUserIdDeactivatePostParams = {
    /** 用户ID */
    user_id: number
  }

  type userApiIntUserIdGetParams = {
    /** 用户ID */
    user_id: number
  }

  type userApiIntUserIdPutParams = {
    /** 用户ID */
    user_id: number
  }

  type UserListResponseModel = {
    /** Page 当前页码 */
    page?: number
    /** Pages 总页数 */
    pages: number
    /** Per Page 每页数量 */
    per_page?: number
    /** Total 用户总数 */
    total: number
    /** Users 用户列表 */
    users: UserResponseModel[]
  }

  type UserLoginModel = {
    /** Login Identifier 登录标识符（邮箱/用户名/工号） */
    login_identifier: string
    /** Password 密码 */
    password: string
  }

  type UserProfileModel = {
    /** Avatar 头像URL */
    avatar?: string | null
    /** Class Id 班级ID */
    class_id?: number | null
    /** Created At 注册时间 */
    created_at: string
    /** Email 邮箱地址 */
    email: string
    /** Last Login Time 最后登录时间 */
    last_login_time?: string | null
    /** Phone 手机号码 */
    phone?: string | null
    /** Real Name 真实姓名 */
    real_name: string
    /** Role 用户角色 */
    role: string
    /** User Code 工号/学号 */
    user_code: string
    /** Username 用户名 */
    username: string
  }

  type UserRegisterModel = {
    /** Class Id 班级ID（学生角色时使用） */
    class_id?: number | null
    /** Email 邮箱地址 */
    email: string
    /** Password 密码 */
    password: string
    /** Phone 手机号码 */
    phone?: string | null
    /** Real Name 真实姓名 */
    real_name: string
    /** 用户角色 */
    role?: UserRoleEnum
    /** User Code 工号/学号 */
    user_code: string
    /** Username 用户名 */
    username: string
  }

  type UserResponseModel = {
    /** Avatar 头像URL */
    avatar?: string | null
    /** Class Id 班级ID */
    class_id?: number | null
    /** Created At 创建时间 */
    created_at: string
    /** Email 邮箱地址 */
    email: string
    /** Id 用户ID */
    id: number
    /** Last Login Time 最后登录时间 */
    last_login_time?: string | null
    /** Phone 手机号码 */
    phone?: string | null
    /** Real Name 真实姓名 */
    real_name: string
    /** Role 用户角色 */
    role: string
    /** Status 账户状态 */
    status: boolean
    /** Updated At 更新时间 */
    updated_at: string
    /** User Code 工号/学号 */
    user_code: string
    /** Username 用户名 */
    username: string
  }

  type UserRoleEnum = 'admin' | 'teacher' | 'student'

  type UserStatsModel = {
    /** Active Users 活跃用户数 */
    active_users: number
    /** Admin Count 管理员数量 */
    admin_count: number
    /** Inactive Users 非活跃用户数 */
    inactive_users: number
    /** Student Count 学生数量 */
    student_count: number
    /** Teacher Count 教师数量 */
    teacher_count: number
    /** Total Users 用户总数 */
    total_users: number
  }

  type UserUpdateModel = {
    /** Avatar 头像URL */
    avatar?: string | null
    /** Email 邮箱地址 */
    email?: string | null
    /** Phone 手机号码 */
    phone?: string | null
    /** Real Name 真实姓名 */
    real_name?: string | null
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
