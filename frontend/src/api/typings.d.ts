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
    user_id?: number | null
    /** 开始日期 */
    start_date?: string | null
    /** 结束日期 */
    end_date?: string | null
    /** 页码 */
    page?: number
    /** 每页数量 */
    per_page?: number
  }

  type orderApiIntOrderIdCancelDeleteParams = {
    /** 订单ID */
    order_id: number
  }

  type orderApiIntOrderIdGetParams = {
    /** 订单ID */
    order_id: number
  }

  type orderApiIntOrderIdPutParams = {
    /** 订单ID */
    order_id: number
  }

  type OrderCreateModel = {
    /** Items 订单项列表 */
    items: OrderItemCreateModel[]
    /** Notes 订单备注 */
    notes?: string | null
    /** Shipping Address 收货地址 */
    shipping_address?: string | null
  }

  type OrderItemCreateModel = {
    /** Product Id 产品ID */
    product_id: number
    /** Quantity 数量 */
    quantity: number
  }

  type OrderStatusEnum = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'

  type OrderUpdateModel = {
    /** Notes 订单备注 */
    notes?: string | null
    /** Shipping Address 收货地址 */
    shipping_address?: string | null
    /** 订单状态 */
    status?: OrderStatusEnum | null
  }

  type productApiGetParams = {
    /** 产品分类 */
    category?: string | null
    /** 最低价格 */
    min_price?: number | string | null
    /** 最高价格 */
    max_price?: number | string | null
    /** 仅显示有库存商品 */
    in_stock_only?: boolean | null
    /** 页码 */
    page?: number
    /** 每页数量 */
    per_page?: number
  }

  type productApiIntProductIdDeleteParams = {
    /** 产品ID */
    product_id: number
  }

  type productApiIntProductIdGetParams = {
    /** 产品ID */
    product_id: number
  }

  type productApiIntProductIdPutParams = {
    /** 产品ID */
    product_id: number
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
    /** Is Active 是否激活 */
    is_active?: boolean | null
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
