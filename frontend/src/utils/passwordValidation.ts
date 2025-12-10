/**
 * Password validation utilities
 * 
 * Provides validation functions for password change forms including
 * password match validation and password strength calculation.
 */

export interface PasswordMatchResult {
  valid: boolean
  error?: string
}

export interface PasswordStrengthResult {
  score: number // 0-4
  percent: number // 0-100
  text: string
  color: string
  status: 'exception' | 'normal' | 'success'
}

/**
 * Validates that new password and confirmation password match
 * 
 * @param newPassword - The new password
 * @param confirmPassword - The confirmation password
 * @returns Validation result with valid flag and optional error message
 */
export function validatePasswordMatch(
  newPassword: string,
  confirmPassword: string
): PasswordMatchResult {
  if (!confirmPassword) {
    return { valid: false, error: '请确认新密码' }
  }
  
  if (newPassword !== confirmPassword) {
    return { valid: false, error: '两次输入的密码不一致' }
  }
  
  return { valid: true }
}

/**
 * Calculates password strength based on various criteria
 * 
 * @param password - The password to evaluate
 * @returns Password strength result with score, text, and visual indicators
 */
export function calculatePasswordStrength(password: string): PasswordStrengthResult {
  if (!password) {
    return {
      score: 0,
      percent: 0,
      text: '',
      color: '#d9d9d9',
      status: 'normal'
    }
  }

  let score = 0
  
  // Length checks
  if (password.length >= 6) score += 1
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  
  // Character variety checks
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^a-zA-Z0-9]/.test(password)) score += 1
  
  // Normalize score to 0-4 range
  const normalizedScore = Math.min(4, Math.floor(score / 2))
  
  type StrengthLevel = Omit<PasswordStrengthResult, 'score'>
  
  const strengthLevels: StrengthLevel[] = [
    { percent: 10, text: '非常弱', color: '#ff4d4f', status: 'exception' },
    { percent: 25, text: '弱', color: '#ff7a45', status: 'exception' },
    { percent: 50, text: '一般', color: '#ffc53d', status: 'normal' },
    { percent: 75, text: '强', color: '#73d13d', status: 'normal' },
    { percent: 100, text: '非常强', color: '#52c41a', status: 'success' }
  ]
  
  const level = strengthLevels[normalizedScore]!
  
  return {
    score: normalizedScore,
    percent: level.percent,
    text: level.text,
    color: level.color,
    status: level.status
  }
}

/**
 * Validates password minimum length
 * 
 * @param password - The password to validate
 * @param minLength - Minimum required length (default: 6)
 * @returns true if password meets minimum length requirement
 */
export function isValidPasswordLength(password: string, minLength: number = 6): boolean {
  return password.length >= minLength
}
