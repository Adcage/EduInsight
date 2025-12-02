declare namespace API {
  type LoginModel = {
    /** Email 用户邮箱 */
    email: string
    /** Password 密码 */
    password: string
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

  type RegisterModel = {
    /** Email 用户邮箱 */
    email: string
    /** Name 用户姓名 */
    name: string
    /** Password 密码 */
    password: string
    /** Phone 手机号码 */
    phone?: string | null
  }

  type userApiIntUserIdDeleteParams = {
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

  type UserCreateModel = {
    /** Age 年龄 */
    age?: number | null
    /** Email 用户邮箱 */
    email: string
    /** Name 用户姓名 */
    name: string
    /** Password 密码 */
    password: string
    /** Phone 手机号码 */
    phone?: string | null
  }

  type UserUpdateModel = {
    /** Age 年龄 */
    age?: number | null
    /** Email 用户邮箱 */
    email?: string | null
    /** Name 用户姓名 */
    name?: string | null
    /** Phone 手机号码 */
    phone?: string | null
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
