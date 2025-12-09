declare namespace API {
  type categoryApiIntCategoryIdChildrenGetParams = {
    /** 分类ID */
    categoryId: number
  }

  type categoryApiIntCategoryIdDeleteParams = {
    /** 分类ID */
    categoryId: number
  }

  type categoryApiIntCategoryIdGetParams = {
    /** 分类ID */
    categoryId: number
  }

  type categoryApiIntCategoryIdPutParams = {
    /** 分类ID */
    categoryId: number
  }

  type ClassifyMaterialResponseModel = {
    /** Confidence 置信度 (0-1) */
    confidence: number
    /** Error 错误信息 */
    error?: string | null
    /** Keywords 提取的关键词列表 */
    keywords?: KeywordResponseModel[]
    /** Logid 分类日志ID */
    logId?: number | null
    /** Materialid 资料ID */
    materialId: number
    /** Needsconfirmation 是否需要确认 */
    needsConfirmation: boolean
    /** Shouldautoapply 是否自动应用 */
    shouldAutoApply: boolean
    /** Suggestedcategoryid 建议的分类ID */
    suggestedCategoryId?: number | null
    /** Suggestedcategoryname 建议的分类名称 */
    suggestedCategoryName?: string | null
  }

  type KeywordResponseModel = {
    /** Keyword 关键词 */
    keyword: string
    /** Weight 权重 (0-1) */
    weight: number
  }

  type LoginResponseModel = {
    /** Message 登录结果消息 */
    message: string
    /** 用户信息 */
    user: UserResponseModel
  }

  type materialApiClassificationLogsIntLogIdAcceptPostParams = {
    /** 分类日志ID */
    logId: number
  }

  type materialApiClassificationLogsIntLogIdRejectPostParams = {
    /** 分类日志ID */
    logId: number
  }

  type materialApiGetParams = {
    /** 页码 */
    page?: number
    /** 每页数量 */
    page_size?: number
    /** 课程ID筛选 */
    courseId?: number | null
    /** 分类ID筛选 */
    categoryId?: number | null
    /** 上传者ID筛选 */
    uploaderId?: number | null
    /** 文件类型筛选 */
    fileType?: string | null
    /** 搜索关键词（标题、描述、关键词） */
    search?: string | null
    /** 标签ID列表筛选 */
    tagIds?: number[] | null
    /** 开始日期(YYYY-MM-DD) */
    startDate?: string | null
    /** 结束日期(YYYY-MM-DD) */
    endDate?: string | null
    /** 排序字段(created_at, download_count, view_count, file_size) */
    sortBy?: string
    /** 排序方向(asc, desc) */
    order?: string
  }

  type materialApiIntMaterialIdClassifyPostParams = {
    /** 资料ID */
    materialId: number
  }

  type materialApiIntMaterialIdDeleteParams = {
    /** 资料ID */
    materialId: number
  }

  type materialApiIntMaterialIdDownloadGetParams = {
    /** 资料ID */
    materialId: number
  }

  type materialApiIntMaterialIdGetParams = {
    /** 资料ID */
    materialId: number
  }

  type materialApiIntMaterialIdKeywordsGetParams = {
    /** 资料ID */
    materialId: number
    /** 返回的关键词数量 */
    topN?: number
  }

  type materialApiIntMaterialIdPreviewGetParams = {
    /** 资料ID */
    materialId: number
  }

  type materialApiIntMaterialIdPutParams = {
    /** 资料ID */
    materialId: number
  }

  type materialApiIntMaterialIdSuggestTagsPostParams = {
    /** 资料ID */
    materialId: number
  }

  type MaterialCategoryCreateModel = {
    /** Description 分类描述 */
    description?: string | null
    /** Name 分类名称 */
    name: string
    /** Parentid 父分类ID */
    parentId?: number | null
    /** Sortorder 排序顺序 */
    sortOrder?: number
  }

  type MaterialCategoryResponseModel = {
    /** Createdat 创建时间 */
    createdAt: string
    /** Description 分类描述 */
    description?: string | null
    /** Id 分类ID */
    id: number
    /** Name 分类名称 */
    name: string
    /** Parentid 父分类ID */
    parentId?: number | null
    /** Sortorder 排序顺序 */
    sortOrder: number
    /** Updatedat 更新时间 */
    updatedAt: string
  }

  type MaterialCategoryUpdateModel = {
    /** Description 分类描述 */
    description?: string | null
    /** Name 分类名称 */
    name?: string | null
    /** Parentid 父分类ID */
    parentId?: number | null
    /** Sortorder 排序顺序 */
    sortOrder?: number | null
  }

  type MaterialDetailResponseModel = {
    /** Autoclassified 是否自动分类 */
    autoClassified: boolean
    /** Categoryid 分类ID */
    categoryId?: number | null
    /** Categoryname 分类名称 */
    categoryName?: string | null
    /** Courseid 课程ID */
    courseId?: number | null
    /** Createdat 创建时间 */
    createdAt: string
    /** Description 资料描述 */
    description?: string | null
    /** Downloadcount 下载次数 */
    downloadCount: number
    /** Filename 文件名 */
    fileName: string
    /** Filepath 文件路径 */
    filePath: string
    /** Filesize 文件大小(字节) */
    fileSize: number
    /** Filetype 文件类型 */
    fileType: string
    /** Id 资料ID */
    id: number
    /** Keywords 关键词 */
    keywords?: string | null
    /** Tags 标签列表 */
    tags?: MaterialTagResponseModel[]
    /** Title 资料标题 */
    title: string
    /** Updatedat 更新时间 */
    updatedAt: string
    /** Uploaderid 上传者ID */
    uploaderId: number
    /** Uploadername 上传者姓名 */
    uploaderName?: string | null
    /** Viewcount 浏览次数 */
    viewCount: number
  }

  type MaterialListResponseModel = {
    /** Materials 资料列表 */
    materials: MaterialResponseModel[]
    /** Page 当前页码 */
    page?: number
    /** Pages 总页数 */
    pages: number
    /** Perpage 每页数量 */
    perPage?: number
    /** Total 资料总数 */
    total: number
  }

  type MaterialResponseModel = {
    /** Autoclassified 是否自动分类 */
    autoClassified: boolean
    /** Categoryid 分类ID */
    categoryId?: number | null
    /** Courseid 课程ID */
    courseId?: number | null
    /** Createdat 创建时间 */
    createdAt: string
    /** Description 资料描述 */
    description?: string | null
    /** Downloadcount 下载次数 */
    downloadCount: number
    /** Filename 文件名 */
    fileName: string
    /** Filepath 文件路径 */
    filePath: string
    /** Filesize 文件大小(字节) */
    fileSize: number
    /** Filetype 文件类型 */
    fileType: string
    /** Id 资料ID */
    id: number
    /** Keywords 关键词 */
    keywords?: string | null
    /** Title 资料标题 */
    title: string
    /** Updatedat 更新时间 */
    updatedAt: string
    /** Uploaderid 上传者ID */
    uploaderId: number
    /** Viewcount 浏览次数 */
    viewCount: number
  }

  type MaterialStatsModel = {
    /** Bycategory 按分类统计 */
    byCategory: Record<string, any>
    /** Bytype 按文件类型统计 */
    byType: Record<string, any>
    /** Popularmaterials 热门资料 */
    popularMaterials: MaterialResponseModel[]
    /** Recentuploads 最近上传 */
    recentUploads: MaterialResponseModel[]
    /** Totaldownloads 总下载次数 */
    totalDownloads: number
    /** Totalmaterials 资料总数 */
    totalMaterials: number
    /** Totalsize 总大小(字节) */
    totalSize: number
    /** Totalviews 总浏览次数 */
    totalViews: number
  }

  type MaterialTagCreateModel = {
    /** Name 标签名称 */
    name: string
  }

  type MaterialTagResponseModel = {
    /** Createdat 创建时间 */
    createdAt: string
    /** Id 标签ID */
    id: number
    /** Name 标签名称 */
    name: string
    /** Updatedat 更新时间 */
    updatedAt: string
    /** Usagecount 使用次数 */
    usageCount: number
  }

  type MaterialUpdateModel = {
    /** Categoryid 分类ID */
    categoryId?: number | null
    /** Description 资料描述 */
    description?: string | null
    /** Tags 标签列表 */
    tags?: string[] | null
    /** Title 资料标题 */
    title?: string | null
  }

  type MessageResponseModel = {
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

  type tagApiIntTagIdDeleteParams = {
    /** 标签ID */
    tagId: number
  }

  type tagApiIntTagIdGetParams = {
    /** 标签ID */
    tagId: number
  }

  type TagSuggestionResponseModel = {
    /** Isexisting 是否为现有标签 */
    isExisting: boolean
    /** Relevance 相关度 (0-1) */
    relevance: number
    /** Tagid 标签ID (如果是现有标签) */
    tagId?: number | null
    /** Tagname 标签名称 */
    tagName: string
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
