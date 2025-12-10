declare namespace API {
  type AddInterventionModel = {
    /** Description 干预内容描述 */
    description: string
    /** Expectedeffect 预期效果 */
    expectedEffect?: string | null
    /** Interventiondate 干预日期(默认今天) */
    interventionDate?: string | null
    /** Interventiontype 干预方式(talk/tutoring/homework/other) */
    interventionType: string
    /** Predictionid 预警ID */
    predictionId: number
  }

  type BasicStatisticsModel = {
    /** Averagescore 平均分 */
    averageScore: number
    /** Excellentrate 优秀率(%) */
    excellentRate: number
    /** Maxscore 最高分 */
    maxScore: number
    /** Medianscore 中位数 */
    medianScore: number
    /** Minscore 最低分 */
    minScore: number
    /** Passrate 及格率(%) */
    passRate: number
    /** Stddeviation 标准差 */
    stdDeviation: number
    /** Totalcount 总人数 */
    totalCount: number
  }

  type BatchDeleteModel = {
    /** Userids 要删除的用户ID列表 */
    userIds: number[]
  }

  type BatchImportResponseModel = {
    /** Errors 错误信息列表 */
    errors?: string[]
    /** Failedcount 失败数量 */
    failedCount: number
    /** Message 响应消息 */
    message: string
    /** Successcount 成功导入数量 */
    successCount: number
    /** Totalcount 总数量 */
    totalCount: number
  }

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

  type ExamTypeEnum = 'daily' | 'midterm' | 'final' | 'homework'

  type GeneratePredictionModel = {
    /** Classid 班级ID(可选) */
    classId?: number | null
    /** Courseid 课程ID */
    courseId: number
  }

  type GeneratePredictionResponseModel = {
    /** Highriskcount 高风险人数 */
    highRiskCount: number
    /** Lowriskcount 低风险人数 */
    lowRiskCount: number
    /** Mediumriskcount 中风险人数 */
    mediumRiskCount: number
    /** Noriskcount 无风险人数 */
    noRiskCount: number
    /** Predictedcount 成功预测数 */
    predictedCount: number
    /** Predictions 预测详情列表 */
    predictions: Record<string, any>[]
    /** Skippedcount 跳过人数(成绩不足) */
    skippedCount: number
    /** Totalstudents 总学生数 */
    totalStudents: number
  }

  type gradeApiCourseStudentsGetParams = {
    /** 课程ID */
    courseId: number
  }

  type gradeApiExportGetParams = {
    /** 课程ID */
    courseId: number
    /** 考试类型筛选 */
    examType?: ExamTypeEnum | null
  }

  type gradeApiGetParams = {
    /** 页码 */
    page?: number
    /** 每页数量 */
    perPage?: number
    /** 课程ID筛选 */
    courseId?: number | null
    /** 学生ID筛选 */
    studentId?: number | null
    /** 考试类型筛选 */
    examType?: ExamTypeEnum | null
  }

  type gradeApiIntGradeIdDeleteParams = {
    /** 成绩ID */
    gradeId: number
  }

  type gradeApiIntGradeIdPutParams = {
    /** 成绩ID */
    gradeId: number
  }

  type gradeApiStudentMyGradesGetParams = {
    /** 页码 */
    page?: number
    /** 每页数量 */
    perPage?: number
    /** 课程ID筛选 */
    courseId?: number | null
    /** 考试类型筛选 */
    examType?: ExamTypeEnum | null
  }

  type gradeApiTemplateGetParams = {
    /** 课程名称 */
    courseName?: string | null
  }

  type GradeCreateModel = {
    /** Courseid 课程ID */
    courseId: number
    /** Examdate 考试日期 */
    examDate?: string | null
    /** Examname 考试名称 */
    examName?: string | null
    /** 考试类型 */
    examType: ExamTypeEnum
    /** Fullscore 满分 */
    fullScore?: number
    /** Remark 备注 */
    remark?: string | null
    /** Score 分数 */
    score: number
    /** Studentid 学生ID */
    studentId: number
    /** Weight 权重 */
    weight?: number
  }

  type GradeDetailResponseModel = {
    /** Courseid 课程ID */
    courseId: number
    /** Coursename 课程名称 */
    courseName?: string | null
    /** Createdat 创建时间 */
    createdAt: string
    /** Examdate 考试日期 */
    examDate?: string | null
    /** Examname 考试名称 */
    examName?: string | null
    /** Examtype 考试类型 */
    examType: string
    /** Fullscore 满分 */
    fullScore: number
    /** Id 成绩ID */
    id: number
    /** Ispass 是否及格 */
    isPass: boolean
    /** Percentage 百分比 */
    percentage: number
    /** Remark 备注 */
    remark?: string | null
    /** Score 分数 */
    score: number
    /** Studentcode 学号 */
    studentCode?: string | null
    /** Studentid 学生ID */
    studentId: number
    /** Studentname 学生姓名 */
    studentName?: string | null
    /** Updatedat 更新时间 */
    updatedAt: string
    /** Weight 权重 */
    weight: number
  }

  type GradeImportResultModel = {
    /** Errors 错误列表 */
    errors?: Record<string, any>[]
    /** Failcount 失败数量 */
    failCount: number
    /** Skipcount 跳过重复数量 */
    skipCount: number
    /** Successcount 成功导入数量 */
    successCount: number
    /** Totalrows 总行数 */
    totalRows: number
    /** Warnings 警告列表 */
    warnings?: Record<string, any>[]
  }

  type GradeListResponseModel = {
    /** Grades 成绩列表 */
    grades: GradeDetailResponseModel[]
    /** Page 当前页码 */
    page?: number
    /** Pages 总页数 */
    pages: number
    /** Perpage 每页数量 */
    perPage?: number
    /** Total 成绩总数 */
    total: number
  }

  type GradeUpdateModel = {
    /** Fullscore 满分 */
    fullScore?: number | null
    /** Remark 备注 */
    remark?: string | null
    /** Score 分数 */
    score?: number | null
    /** Weight 权重 */
    weight?: number | null
  }

  type HistoricalGradeModel = {
    /** Examdate 考试日期 */
    examDate: string
    /** Examname 考试名称 */
    examName?: string | null
    /** Examtype 考试类型 */
    examType: string
    /** Score 分数 */
    score: number
  }

  type InterventionModel = {
    /** Actualeffect 实际效果 */
    actualEffect?: string | null
    /** Createdat 创建时间 */
    createdAt: string
    /** Description 干预内容 */
    description: string
    /** Expectedeffect 预期效果 */
    expectedEffect?: string | null
    /** Id 干预ID */
    id: number
    /** Interventiondate 干预日期 */
    interventionDate: string
    /** Interventiontype 干预方式 */
    interventionType: string
    /** Predictionid 预警ID */
    predictionId: number
    /** Studentfeedback 学生反馈 */
    studentFeedback?: string | null
    /** Teacherid 教师ID */
    teacherId: number
    /** Teachername 教师姓名 */
    teacherName: string
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
    /** Message 消息内容 */
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

  type predictionApiInterventionsIntInterventionIdPutParams = {
    /** 干预ID */
    intervention_id: number
  }

  type predictionApiIntPredictionIdGetParams = {
    /** 预警ID */
    prediction_id: number
  }

  type predictionApiListGetParams = {
    /** 课程ID */
    courseId: number
    /** 班级ID(可选) */
    classId?: number | null
    /** 风险等级筛选(high/medium/low/none) */
    riskLevel?: string | null
  }

  type predictionApiStudentMyWarningsIntPredictionIdGetParams = {
    /** 预警ID */
    prediction_id: number
  }

  type PredictionDetailModel = {
    /** Confidence 置信度(%) */
    confidence: number
    /** Courseid 课程ID */
    courseId: number
    /** Coursename 课程名称 */
    courseName: string
    /** Createdat 创建时间 */
    createdAt: string
    /** Historicalgrades 历史成绩列表 */
    historicalGrades: HistoricalGradeModel[]
    /** Id 预警ID */
    id: number
    /** Interventions 干预记录列表 */
    interventions: InterventionModel[]
    /** Issent 是否已发送通知 */
    isSent: boolean
    /** Predictedscore 预测分数 */
    predictedScore: number
    /** Predictiondate 预测日期 */
    predictionDate: string
    /** Risklevel 风险等级 */
    riskLevel: string
    /** Studentcode 学号 */
    studentCode: string
    /** Studentemail 学生邮箱 */
    studentEmail?: string | null
    /** Studentid 学生ID */
    studentId: number
    /** Studentname 学生姓名 */
    studentName: string
  }

  type ScoreDistributionModel = {
    /** Excellentcount 优秀(90-100)人数 */
    excellentCount: number
    /** Excellentrate 优秀率(%) */
    excellentRate: number
    /** Failcount 不及格(0-59)人数 */
    failCount: number
    /** Failrate 不及格率(%) */
    failRate: number
    /** Goodcount 良好(80-89)人数 */
    goodCount: number
    /** Goodrate 良好率(%) */
    goodRate: number
    /** Mediumcount 中等(70-79)人数 */
    mediumCount: number
    /** Mediumrate 中等率(%) */
    mediumRate: number
    /** Passcount 及格(60-69)人数 */
    passCount: number
    /** Passrate 及格率(%) */
    passRate: number
  }

  type SendNotificationModel = {
    /** Predictionids 预警ID列表 */
    predictionIds: number[]
  }

  type SendNotificationResponseModel = {
    /** Failedcount 失败数 */
    failedCount: number
    /** Successcount 成功数 */
    successCount: number
    /** Total 总数 */
    total: number
  }

  type statisticsApiCourseGetParams = {
    /** 课程ID */
    courseId: number
    /** 班级ID(可选,用于更细致的统计) */
    classId?: number | null
    /** 考试类型筛选(可选,支持枚举值或'comprehensive') */
    examType?: string | null
  }

  type StatisticsResponseModel = {
    /** 基础统计 */
    basicStatistics: BasicStatisticsModel
    /** Classname 班级名称 */
    className?: string | null
    /** Coursename 课程名称 */
    courseName: string
    /** Examtypefilter 考试类型筛选 */
    examTypeFilter?: string | null
    /** 分数段分布 */
    scoreDistribution: ScoreDistributionModel
    /** Trenddata 趋势数据 */
    trendData: TrendDataPointModel[]
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

  type TrendDataPointModel = {
    /** Averagescore 平均分 */
    averageScore: number
    /** Examdate 考试日期 */
    examDate: string
    /** Examname 考试名称 */
    examName?: string | null
    /** Examtype 考试类型 */
    examType: string
    /** Maxscore 最高分 */
    maxScore: number
    /** Minscore 最低分 */
    minScore: number
  }

  type UpdateInterventionModel = {
    /** Actualeffect 实际效果 */
    actualEffect?: string | null
    /** Description 干预内容描述 */
    description?: string | null
    /** Expectedeffect 预期效果 */
    expectedEffect?: string | null
    /** Studentfeedback 学生反馈 */
    studentFeedback?: string | null
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

  type userApiListGetParams = {
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

  type UserCreateModel = {
    /** Classid 班级ID(学生角色时使用) */
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
    role: UserRoleEnum
    /** Usercode 工号/学号 */
    userCode: string
    /** Username 用户名 */
    username: string
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
    /** Id 用户ID */
    id: number
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

  type UserRoleEnum = 'ADMIN' | 'TEACHER' | 'STUDENT'

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
