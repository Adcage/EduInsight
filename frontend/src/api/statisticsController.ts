// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 获取课程统计分析 获取课程统计分析数据</br></br>权限: 教师(只能查看自己教授的课程)</br></br>参数:</br>- course_id: 课程ID(必填)</br>- class_id: 班级ID(可选,用于更细致的统计)</br>- exam_type: 考试类型(可选,筛选特定类型的考试)</br></br>返回:</br>- basic_statistics: 基础统计(平均分、最高分、最低分、标准差、中位数、及格率、优秀率)</br>- score_distribution: 分数段分布(不及格、及格、中等、良好、优秀的人数和比例)</br>- trend_data: 成绩趋势数据(按考试类型和日期的平均分变化) GET /api/v1/statistics/course */
export async function statisticsApiCourseGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.statisticsApiCourseGetParams,
  options?: { [key: string]: any }
) {
  return request<API.StatisticsResponseModel>('/api/v1/statistics/course', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}
