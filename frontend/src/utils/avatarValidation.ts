/**
 * Avatar file validation utilities
 *
 * Provides validation functions for avatar file uploads including
 * file type and file size validation.
 */

export interface AvatarValidationResult {
    valid: boolean
    error?: string
}

/**
 * Allowed image MIME types for avatar upload
 */
export const ALLOWED_AVATAR_TYPES = ['image/jpeg', 'image/png', 'image/gif']

/**
 * Allowed file extensions for avatar upload
 */
export const ALLOWED_AVATAR_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']

/**
 * Default maximum file size (2MB)
 */
export const DEFAULT_MAX_AVATAR_SIZE = 2 * 1024 * 1024

/**
 * Validates an avatar file for upload
 *
 * @param file - The file to validate
 * @param maxSize - Maximum allowed file size in bytes (default: 2MB)
 * @returns Validation result with valid flag and optional error message
 */
export function validateAvatarFile(
    file: File,
    maxSize: number = DEFAULT_MAX_AVATAR_SIZE
): AvatarValidationResult {
    // Check if file exists
    if (!file) {
        return {valid: false, error: '请选择文件'}
    }

    // Check file type
    if (!isValidAvatarType(file)) {
        return {
            valid: false,
            error: '请选择有效的图片文件（支持 JPG、PNG、GIF 格式）'
        }
    }

    // Check file size
    if (!isValidAvatarSize(file, maxSize)) {
        const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(1)
        return {
            valid: false,
            error: `文件大小不能超过 ${maxSizeMB}MB`
        }
    }

    return {valid: true}
}

/**
 * Checks if the file type is a valid image type for avatar
 *
 * @param file - The file to check
 * @returns true if the file type is valid
 */
export function isValidAvatarType(file: File): boolean {
    // Check MIME type
    if (ALLOWED_AVATAR_TYPES.includes(file.type)) {
        return true
    }

    // Fallback: check file extension
    const fileName = file.name.toLowerCase()
    return ALLOWED_AVATAR_EXTENSIONS.some(ext => fileName.endsWith(ext))
}

/**
 * Checks if the file size is within the allowed limit
 *
 * @param file - The file to check
 * @param maxSize - Maximum allowed size in bytes
 * @returns true if the file size is valid
 */
export function isValidAvatarSize(file: File, maxSize: number): boolean {
    return file.size <= maxSize
}

/**
 * Formats file size to human-readable string
 *
 * @param bytes - File size in bytes
 * @returns Formatted string (e.g., "1.5 MB")
 */
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'

    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`
}
