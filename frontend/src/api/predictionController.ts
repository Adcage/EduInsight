// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取预警详情 获取预警详情</br></br>权限: 教师</br></br>返回:</br>- 预警详情(包含学生历史成绩和干预记录) GET /api/v1/predictions/${param0} */
export async function predictionApiIntPredictionIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.predictionApiIntPredictionIdGetParams,
  options?: { [key: string]: any }
) {
  const { prediction_id: param0, ...queryParams } = params
  return request<API.PredictionDetailModel>(`/api/v1/predictions/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 生成预警预测 为课程生成预警预测(手动触发)</br></br>权限: 教师(只能为自己教授的课程生成预测)</br></br>参数:</br>- course_id: 课程ID(必填)</br>- class_id: 班级ID(可选,如果指定则只预测该班级学生)</br></br>返回:</br>- 预测结果统计(总学生数、成功预测数、各风险等级人数等) POST /api/v1/predictions/generate */
export async function predictionApiGeneratePost(body: API.GeneratePredictionModel, options?: { [key: string]: any }) {
  return request<API.GeneratePredictionResponseModel>('/api/v1/predictions/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 添加干预记录 添加干预记录</br></br>权限: 教师</br></br>参数:</br>- prediction_id: 预警ID</br>- intervention_date: 干预日期(可选,默认今天)</br>- intervention_type: 干预方式(talk/tutoring/homework/other)</br>- description: 干预内容描述</br>- expected_effect: 预期效果(可选)</br></br>返回:</br>- 干预记录 POST /api/v1/predictions/interventions */
export async function predictionApiInterventionsPost(body: API.AddInterventionModel, options?: { [key: string]: any }) {
  return request<API.InterventionModel>('/api/v1/predictions/interventions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 更新干预记录 更新干预记录(主要用于填写实际效果和学生反馈)</br></br>权限: 教师</br></br>参数:</br>- actual_effect: 实际效果(可选)</br>- student_feedback: 学生反馈(可选)</br>- description: 干预内容(可选)</br>- expected_effect: 预期效果(可选)</br></br>返回:</br>- 更新后的干预记录 PUT /api/v1/predictions/interventions/${param0} */
export async function predictionApiInterventionsIntInterventionIdPut(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.predictionApiInterventionsIntInterventionIdPutParams,
  body: API.UpdateInterventionModel,
  options?: { [key: string]: any }
) {
  const { intervention_id: param0, ...queryParams } = params
  return request<API.InterventionModel>(`/api/v1/predictions/interventions/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 获取预警列表 获取预警列表</br></br>权限: 教师(只能查看自己教授的课程的预警)</br></br>参数:</br>- course_id: 课程ID(必填)</br>- class_id: 班级ID(可选)</br>- risk_level: 风险等级筛选(可选: high/medium/low/none)</br></br>返回:</br>- 预警列表 GET /api/v1/predictions/list */
export async function predictionApiListGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.predictionApiListGetParams,
  options?: { [key: string]: any }
) {
  return request<any>('/api/v1/predictions/list', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 批量发送预警通知 批量发送预警通知给学生</br></br>权限: 教师</br></br>参数:</br>- prediction_ids: 预警ID列表</br></br>返回:</br>- 发送结果统计 POST /api/v1/predictions/send-notifications */
export async function predictionApiSendNotificationsPost(body: API.SendNotificationModel, options?: { [key: string]: any }) {
  return request<API.SendNotificationResponseModel>('/api/v1/predictions/send-notifications', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取学生个人预警列表 获取当前学生的个人预警列表</br></br>权限: 学生</br></br>返回:</br>- 预警列表（按课程分组） GET /api/v1/predictions/student/my-warnings */
export async function predictionApiStudentMyWarningsGet(options?: { [key: string]: any }) {
  return request<any>('/api/v1/predictions/student/my-warnings', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取学生预警详情 获取学生预警详情（包含干预记录）</br></br>权限: 学生（只能查看自己的预警）</br></br>返回:</br>- 预警详情</br>- 干预记录列表 GET /api/v1/predictions/student/my-warnings/${param0} */
export async function predictionApiStudentMyWarningsIntPredictionIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.predictionApiStudentMyWarningsIntPredictionIdGetParams,
  options?: { [key: string]: any }
) {
  const { prediction_id: param0, ...queryParams } = params
  return request<any>(`/api/v1/predictions/student/my-warnings/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}
