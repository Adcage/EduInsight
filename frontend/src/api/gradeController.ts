// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取成绩列表 获取成绩列表</br></br>权限: 教师(查看所有), 学生(查看自己) GET /api/v1/grades */
export async function gradeApiGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiGetParams,
  options?: { [key: string]: any }
) {
  return request<API.GradeListResponseModel>('/api/v1/grades', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // perPage has a default value: 20
      perPage: '20',

      ...params,
    },
    ...(options || {}),
  })
}

/** 创建成绩记录 创建单条成绩记录</br></br>权限: 教师 POST /api/v1/grades */
export async function gradeApiPost(body: API.GradeCreateModel, options?: { [key: string]: any }) {
  return request<API.GradeDetailResponseModel>('/api/v1/grades', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 更新成绩 更新成绩记录</br></br>权限: 教师 PUT /api/v1/grades/${param1} */
export async function gradeApiIntGradeIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiIntGradeIdPutParams,
  body: API.GradeUpdateModel,
  options?: { [key: string]: any }
) {
  const { gradeId: param0, grade_id: param1, ...queryParams } = params
  return request<API.GradeDetailResponseModel>(`/api/v1/grades/${param1}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除成绩 删除成绩记录</br></br>权限: 教师 DELETE /api/v1/grades/${param1} */
export async function gradeApiIntGradeIdDelete(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiIntGradeIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { gradeId: param0, grade_id: param1, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/grades/${param1}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 获取课程学生列表 获取指定课程的学生列表</br></br>权限: 教师</br>返回: 学生列表数组 GET /api/v1/grades/course-students */
export async function gradeApiCourseStudentsGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiCourseStudentsGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/grades/course-students', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 导出成绩Excel 导出成绩到Excel</br></br>权限: 教师 GET /api/v1/grades/export */
export async function gradeApiExportGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiExportGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/grades/export', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** Excel批量导入成绩 Excel批量导入成绩</br></br>权限: 教师 POST /api/v1/grades/import */
export async function gradeApiImportPost(options?: { [key: string]: any }) {
  return request<API.GradeImportResultModel>('/api/v1/grades/import', {
    method: 'POST',
    ...(options || {}),
  })
}

/** 解析Excel文件并验证 解析Excel文件并验证学生是否在课程中</br></br>权限: 教师 POST /api/v1/grades/parse-excel */
export async function gradeApiParseExcelPost(options?: { [key: string]: any }) {
  return request<any>('/api/v1/grades/parse-excel', {
    method: 'POST',
    ...(options || {}),
  })
}

/** 获取学生课程成绩统计 获取学生按课程分组的成绩统计</br></br>权限: 学生 GET /api/v1/grades/student/courses */
export async function gradeApiStudentCoursesGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/grades/student/courses', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取学生个人成绩列表 获取当前学生的个人成绩列表</br></br>权限: 学生 GET /api/v1/grades/student/my-grades */
export async function gradeApiStudentMyGradesGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiStudentMyGradesGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/grades/student/my-grades', {
    method: 'GET',
    params: {
      // page has a default value: 1
      page: '1',
      // perPage has a default value: 20
      perPage: '20',

      ...params,
    },
    ...(options || {}),
  })
}

/** 获取学生总体成绩统计 获取学生的总体成绩统计</br></br>权限: 学生 GET /api/v1/grades/student/statistics */
export async function gradeApiStudentStatisticsGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/grades/student/statistics', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取教师课程列表 获取当前教师的授课课程列表</br></br>权限: 教师</br>返回: 课程列表数组 GET /api/v1/grades/teacher-courses */
export async function gradeApiTeacherCoursesGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/grades/teacher-courses', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 下载Excel导入模板 下载成绩导入Excel模板</br></br>权限: 教师 GET /api/v1/grades/template */
export async function gradeApiTemplateGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.gradeApiTemplateGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/grades/template', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}
