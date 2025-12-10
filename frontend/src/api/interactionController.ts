// @ts-ignore
/* eslint-disable */
import request from '@/request'

/**
 * ==================== 投票相关API ====================
 */

/** 创建投票 创建投票（教师）POST /api/v1/polls */
export async function pollApiPost(body: API.PollCreateModel, options?: { [key: string]: any }) {
  return request<API.PollResponseModel>('/api/v1/polls', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取投票列表 获取投票列表 GET /api/v1/polls */
export async function pollApiGet(
  params: API.pollApiGetParams,
  options?: { [key: string]: any }
) {
  return request<API.PollListResponseModel>('/api/v1/polls', {
    method: 'GET',
    params: {
      page: '1',
      perPage: '20',
      ...params,
    },
    ...(options || {}),
  })
}

/** 获取投票详情 获取投票详情 GET /api/v1/polls/${param0} */
export async function pollApiIntPollIdGet(
  params: API.pollApiIntPollIdGetParams,
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<API.PollDetailResponseModel>(`/api/v1/polls/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新投票 更新投票（教师）PUT /api/v1/polls/${param0} */
export async function pollApiIntPollIdPut(
  params: API.pollApiIntPollIdPutParams,
  body: API.PollUpdateModel,
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<API.PollResponseModel>(`/api/v1/polls/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除投票 删除投票（教师）DELETE /api/v1/polls/${param0} */
export async function pollApiIntPollIdDelete(
  params: API.pollApiIntPollIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/polls/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 学生投票 学生投票 POST /api/v1/polls/${param0}/vote */
export async function pollApiIntPollIdVotePost(
  params: API.pollApiIntPollIdVotePostParams,
  body: API.PollVoteModel,
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<API.PollResponseResponseModel>(`/api/v1/polls/${param0}/vote`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 获取投票结果 获取投票结果统计 GET /api/v1/polls/${param0}/results */
export async function pollApiIntPollIdResultsGet(
  params: API.pollApiIntPollIdResultsGetParams,
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<API.PollResultsResponseModel>(`/api/v1/polls/${param0}/results`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 关闭投票 关闭投票（教师）PUT /api/v1/polls/${param0}/close */
export async function pollApiIntPollIdClosePut(
  params: API.pollApiIntPollIdClosePutParams,
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<API.PollResponseModel>(`/api/v1/polls/${param0}/close`, {
    method: 'PUT',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 获取投票响应列表 获取投票的所有响应记录（教师）GET /api/v1/polls/${param0}/responses */
export async function pollApiIntPollIdResponsesGet(
  params: { pollId: number },
  options?: { [key: string]: any }
) {
  const { pollId: param0, ...queryParams } = params
  return request<{
    code: number
    message: string
    data: {
      responses: Array<{
        id: number
        student_id: number
        student_name: string
        student_username: string
        selected_options: number[]
        created_at: string
      }>
      total: number
    }
  }>(`/api/v1/polls/${param0}/responses`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/**
 * ==================== 提问相关API ====================
 */

/** 创建问题 创建问题 POST /api/v1/questions */
export async function questionApiPost(body: API.QuestionCreateModel, options?: { [key: string]: any }) {
  return request<API.QuestionResponseModel>('/api/v1/questions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取问题列表 获取问题列表 GET /api/v1/questions */
export async function questionApiGet(
  params: API.questionApiGetParams,
  options?: { [key: string]: any }
) {
  return request<API.QuestionListResponseModel>('/api/v1/questions', {
    method: 'GET',
    params: {
      page: '1',
      perPage: '20',
      ...params,
    },
    ...(options || {}),
  })
}

/** 获取问题详情 获取问题详情 GET /api/v1/questions/${param0} */
export async function questionApiIntQuestionIdGet(
  params: API.questionApiIntQuestionIdGetParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.QuestionDetailResponseModel>(`/api/v1/questions/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 更新问题 更新问题 PUT /api/v1/questions/${param0} */
export async function questionApiIntQuestionIdPut(
  params: API.questionApiIntQuestionIdPutParams,
  body: API.QuestionUpdateModel,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.QuestionResponseModel>(`/api/v1/questions/${param0}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 删除问题 删除问题 DELETE /api/v1/questions/${param0} */
export async function questionApiIntQuestionIdDelete(
  params: API.questionApiIntQuestionIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/questions/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 回答问题 回答问题（学生）POST /api/v1/questions/${param0}/answers */
export async function questionApiIntQuestionIdAnswersPost(
  params: API.questionApiIntQuestionIdAnswersPostParams,
  body: API.QuestionAnswerCreateModel,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.QuestionAnswerResponseModel>(`/api/v1/questions/${param0}/answers`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...queryParams },
    data: body,
    ...(options || {}),
  })
}

/** 获取问题的所有回答 获取问题的所有回答 GET /api/v1/questions/${param0}/answers */
export async function questionApiIntQuestionIdAnswersGet(
  params: API.questionApiIntQuestionIdAnswersGetParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.QuestionAnswerListResponseModel>(`/api/v1/questions/${param0}/answers`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 采纳答案 采纳答案（教师）PUT /api/v1/questions/${param0}/answers/${param1}/accept */
export async function questionApiIntQuestionIdAnswersIntAnswerIdAcceptPut(
  params: API.questionApiIntQuestionIdAnswersIntAnswerIdAcceptPutParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, answerId: param1, ...queryParams } = params
  return request<API.QuestionAnswerResponseModel>(`/api/v1/questions/${param0}/answers/${param1}/accept`, {
    method: 'PUT',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 删除回答 删除回答 DELETE /api/v1/questions/${param0}/answers/${param1} */
export async function questionApiIntQuestionIdAnswersIntAnswerIdDelete(
  params: API.questionApiIntQuestionIdAnswersIntAnswerIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, answerId: param1, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/questions/${param0}/answers/${param1}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 点赞问题 点赞问题 POST /api/v1/questions/${param0}/like */
export async function questionApiIntQuestionIdLikePost(
  params: API.questionApiIntQuestionIdLikePostParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.LikeResponseModel>(`/api/v1/questions/${param0}/like`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 取消点赞问题 取消点赞问题 DELETE /api/v1/questions/${param0}/like */
export async function questionApiIntQuestionIdLikeDelete(
  params: API.questionApiIntQuestionIdLikeDeleteParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, ...queryParams } = params
  return request<API.LikeResponseModel>(`/api/v1/questions/${param0}/like`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 点赞回答 点赞回答 POST /api/v1/questions/${param0}/answers/${param1}/like */
export async function questionApiIntQuestionIdAnswersIntAnswerIdLikePost(
  params: API.questionApiIntQuestionIdAnswersIntAnswerIdLikePostParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, answerId: param1, ...queryParams } = params
  return request<API.LikeResponseModel>(`/api/v1/questions/${param0}/answers/${param1}/like`, {
    method: 'POST',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 取消点赞回答 取消点赞回答 DELETE /api/v1/questions/${param0}/answers/${param1}/like */
export async function questionApiIntQuestionIdAnswersIntAnswerIdLikeDelete(
  params: API.questionApiIntQuestionIdAnswersIntAnswerIdLikeDeleteParams,
  options?: { [key: string]: any }
) {
  const { questionId: param0, answerId: param1, ...queryParams } = params
  return request<API.LikeResponseModel>(`/api/v1/questions/${param0}/answers/${param1}/like`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/**
 * ==================== 弹幕相关API ====================
 */

/** 发送弹幕 发送弹幕 POST /api/v1/barrages */
export async function barrageApiPost(body: API.BarrageCreateModel, options?: { [key: string]: any }) {
  return request<API.BarrageResponseModel>('/api/v1/barrages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 获取弹幕列表 获取弹幕列表 GET /api/v1/barrages */
export async function barrageApiGet(
  params: API.barrageApiGetParams,
  options?: { [key: string]: any }
) {
  return request<API.BarrageListResponseModel>('/api/v1/barrages', {
    method: 'GET',
    params: {
      page: '1',
      perPage: '20',
      ...params,
    },
    ...(options || {}),
  })
}

/** 获取最近的弹幕 获取最近的弹幕（默认10分钟内）GET /api/v1/barrages/recent */
export async function barrageApiRecentGet(
  params: API.barrageApiRecentGetParams,
  options?: { [key: string]: any }
) {
  return request<API.BarrageListResponseModel>('/api/v1/barrages/recent', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 获取弹幕统计信息 获取弹幕统计信息 GET /api/v1/barrages/statistics */
export async function barrageApiStatisticsGet(
  params: API.barrageApiStatisticsGetParams,
  options?: { [key: string]: any }
) {
  return request<API.BarrageStatisticsResponseModel>('/api/v1/barrages/statistics', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 删除弹幕 删除弹幕 DELETE /api/v1/barrages/${param0} */
export async function barrageApiIntBarrageIdDelete(
  params: API.barrageApiIntBarrageIdDeleteParams,
  options?: { [key: string]: any }
) {
  const { barrageId: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/barrages/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 获取敏感词列表 获取敏感词列表 GET /api/v1/barrages/sensitive-words */
export async function barrageApiSensitiveWordsGet(options?: { [key: string]: any }) {
  return request<API.SensitiveWordsResponseModel>('/api/v1/barrages/sensitive-words', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 添加敏感词 添加敏感词（教师/管理员）POST /api/v1/barrages/sensitive-words */
export async function barrageApiSensitiveWordsPost(
  body: API.SensitiveWordModel,
  options?: { [key: string]: any }
) {
  return request<API.MessageResponseModel>('/api/v1/barrages/sensitive-words', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 删除敏感词 删除敏感词（教师/管理员）DELETE /api/v1/barrages/sensitive-words/${param0} */
export async function barrageApiSensitiveWordsStrWordDelete(
  params: API.barrageApiSensitiveWordsStrWordDeleteParams,
  options?: { [key: string]: any }
) {
  const { word: param0, ...queryParams } = params
  return request<API.MessageResponseModel>(`/api/v1/barrages/sensitive-words/${param0}`, {
    method: 'DELETE',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** 检查内容安全性 检查内容安全性（测试用）POST /api/v1/barrages/check-content */
export async function barrageApiCheckContentPost(
  body: API.ContentCheckModel,
  options?: { [key: string]: any }
) {
  return request<API.ContentCheckResponseModel>('/api/v1/barrages/check-content', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}


/**
 * ==================== 课堂互动-通用API ====================
 */

/** 获取教师课程列表（课堂互动模块专用）GET /api/v1/interaction/common/teacher-courses */
export async function interactionCommonTeacherCoursesGet(options?: { [key: string]: any }) {
  return request<{
    code: number
    message: string
    data: {
      courses: Array<{
        id: number
        name: string
        description?: string
        created_at?: string
      }>
      total: number
    }
  }>('/api/v1/interaction/common/teacher-courses', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取学生课程列表（课堂互动模块专用）GET /api/v1/interaction/common/student-courses */
export async function interactionCommonStudentCoursesGet(options?: { [key: string]: any }) {
  return request<{
    code: number
    message: string
    data: {
      courses: Array<{
        id: number
        name: string
        description?: string
        created_at?: string
      }>
      total: number
    }
  }>('/api/v1/interaction/common/student-courses', {
    method: 'GET',
    ...(options || {}),
  })
}

/** 获取课程学生列表（用于点名提问）GET /api/v1/interaction/common/course/:courseId/students */
export async function interactionCommonCourseStudentsGet(
  params: {
    courseId: number
  },
  options?: { [key: string]: any }
) {
  return request<{
    code: number
    message: string
    data: {
      students: Array<{
        id: number
        username: string
        real_name: string
        class_id: number
        class_name: string
      }>
      total: number
    }
  }>(`/api/v1/interaction/common/course/${params.courseId}/students`, {
    method: 'GET',
    ...(options || {}),
  })
}
