/**
 * Profile validation utilities
 * Used for validating profile edit form fields
 */

/**
 * Email validation result
 */
export interface EmailValidationResult {
  valid: boolean
  error?: string
}

/**
 * Phone validation result
 */
export interface PhoneValidationResult {
  valid: boolean
  error?: string
}

/**
 * Profile display data
 */
export interface ProfileDisplayData {
  username: string
  realName: string
  email: string
  phone: string | null
  role: string
  userCode: string
  createdAt: string
  lastLoginTime: string | null
  avatar: string | null
}

/**
 * Validate email format
 * @param email - Email string to validate
 * @returns Validation result
 */
export function validateEmail(email: string): EmailValidationResult {
  if (!email || email.trim() === '') {
    return { valid: false, error: '请输入邮箱地址' }
  }

  // Standard email regex pattern
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.trim())) {
    return { valid: false, error: '请输入有效的邮箱地址' }
  }

  return { valid: true }
}

/**
 * Validate phone number format (Chinese phone number)
 * @param phone - Phone string to validate
 * @returns Validation result
 */
export function validatePhone(phone: string | null | undefined): PhoneValidationResult {
  // Phone is optional, empty is valid
  if (!phone || phone.trim() === '') {
    return { valid: true }
  }

  // Chinese mobile phone number pattern (11 digits starting with 1)
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone.trim())) {
    return { valid: false, error: '请输入有效的手机号码' }
  }

  return { valid: true }
}

/**
 * Check if profile display data is complete
 * @param profile - Profile data to check
 * @returns True if all required fields are present
 */
export function isProfileDisplayComplete(profile: ProfileDisplayData | null): boolean {
  if (!profile) return false

  // Check all required display fields
  const hasUsername = typeof profile.username === 'string' && profile.username.length > 0
  const hasRealName = typeof profile.realName === 'string' && profile.realName.length > 0
  const hasEmail = typeof profile.email === 'string' && profile.email.length > 0
  const hasRole = typeof profile.role === 'string' && profile.role.length > 0
  const hasUserCode = typeof profile.userCode === 'string' && profile.userCode.length > 0
  const hasCreatedAt = typeof profile.createdAt === 'string' && profile.createdAt.length > 0

  return hasUsername && hasRealName && hasEmail && hasRole && hasUserCode && hasCreatedAt
}

/**
 * Get avatar display URL or null for default
 * @param avatar - Avatar URL from profile
 * @returns Avatar URL if valid, null otherwise
 */
export function getAvatarDisplayUrl(avatar: string | null | undefined): string | null {
  if (!avatar || avatar.trim() === '') {
    return null
  }
  return avatar
}

/**
 * Check if avatar should show default placeholder
 * @param avatar - Avatar URL from profile
 * @returns True if should show default placeholder
 */
export function shouldShowDefaultAvatar(avatar: string | null | undefined): boolean {
  return !avatar || avatar.trim() === ''
}

/**
 * Format role display name
 * @param role - Role string
 * @returns Formatted role name in Chinese
 */
export function formatRoleDisplay(role: string): string {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  }
  return roleMap[role.toLowerCase()] || role
}
