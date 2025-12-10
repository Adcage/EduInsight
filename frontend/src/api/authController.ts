// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 修改密码 修改当前用户密码</br></br>需要提供原密码进行验证。 POST /api/v1/auth/change-password */
export async function authApiChangePasswordPost(body: API.PasswordChangeModel, options?: { [key: string]: any }) {
    return request<API.MessageResponseModel>('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** 获取当前登录用户信息 获取当前登录用户的个人信息 GET /api/v1/auth/get_loginuser */
export async function authApiGetLoginuserGet(options?: { [key: string]: any }) {
    return request<API.UserProfileModel>('/api/v1/auth/get_loginuser', {
        method: 'GET',
        ...(options || {}),
    })
}

/** 认证API健康检查 认证API健康检查 GET /api/v1/auth/health */
export async function authApiHealthGet(options?: { [key: string]: any }) {
    return request<any>('/api/v1/auth/health', {
        method: 'GET',
        ...(options || {}),
    })
}

/** 用户登录 用户登录</br></br>支持多种登录方式：邮箱、用户名、工号/学号。</br>登录成功后会将用户信息存储到session中。 POST /api/v1/auth/login */
export async function authApiLoginPost(body: API.UserLoginModel, options?: { [key: string]: any }) {
    return request<API.LoginResponseModel>('/api/v1/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** 用户登出 用户登出</br></br>清除session中的用户信息。 POST /api/v1/auth/logout */
export async function authApiLogoutPost(options?: { [key: string]: any }) {
    return request<API.MessageResponseModel>('/api/v1/auth/logout', {
        method: 'POST',
        ...(options || {}),
    })
}

/** 用户注册 用户注册</br></br>创建新的用户账户，支持多角色注册。 POST /api/v1/auth/register */
export async function authApiRegisterPost(body: API.UserRegisterModel, options?: { [key: string]: any }) {
    return request<API.UserResponseModel>('/api/v1/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** 检查登录状态 检查用户登录状态</br></br>返回用户是否已登录的信息。 GET /api/v1/auth/status */
export async function authApiStatusGet(options?: { [key: string]: any }) {
    return request<API.MessageResponseModel>('/api/v1/auth/status', {
        method: 'GET',
        ...(options || {}),
    })
}
