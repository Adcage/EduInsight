/**
 * Material detail display utility functions
 * These functions are extracted for testability
 *
 * Property 7: Material detail display completeness
 * For any material, the detail view SHALL display the full description,
 * all associated tags, uploader information, and complete file metadata.
 */

export interface MaterialTag {
    id: number
    name: string
}

export interface MaterialUploader {
    id: number
    realName: string
}

export interface MaterialDetail {
    id: number
    title: string
    description?: string
    fileName: string
    fileSize: number
    fileType: string
    downloadCount?: number
    viewCount?: number
    createdAt?: string
    updatedAt?: string
    categoryId?: number
    categoryName?: string
    uploaderId?: number
    uploaderName?: string
    uploader?: MaterialUploader
    tags?: MaterialTag[]
}

export interface MaterialDetailDisplayInfo {
    title: string
    description: string
    fileName: string
    fileSize: string
    fileType: string
    fileTypeText: string
    downloadCount: number
    viewCount: number
    uploadDate: string
    categoryName: string
    uploaderName: string
    tags: string[]
}

// File type text mapping
const fileTypeTextMap: Record<string, string> = {
    pdf: 'PDF',
    doc: 'Word',
    ppt: 'PPT',
    xls: 'Excel',
    text: '文本',
    image: '图片',
    archive: '压缩包',
    video: '视频',
    other: '其他'
}


/**
 * Format file size to human readable string
 * @param bytes - File size in bytes
 * @returns Formatted file size string
 */
export function formatFileSize(bytes?: number): string {
    if (!bytes || bytes <= 0) return '0 B'

    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`
}

/**
 * Format date to display string
 * @param date - ISO date string
 * @returns Formatted date string (YYYY-MM-DD HH:mm:ss)
 */
export function formatDateTime(date?: string): string {
    if (!date) return ''
    try {
        const d = new Date(date)
        if (isNaN(d.getTime())) return ''
        const pad = (n: number) => String(n).padStart(2, '0')
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    } catch {
        return ''
    }
}

/**
 * Get file type display text
 * @param fileType - File type code
 * @returns Display text for file type
 */
export function getFileTypeText(fileType?: string): string {
    if (!fileType) return '其他'
    if (Object.prototype.hasOwnProperty.call(fileTypeTextMap, fileType)) {
        return fileTypeTextMap[fileType] as string
    }
    return '其他'
}

/**
 * Extract display information from a material for detail view rendering
 *
 * Property 7: Material detail display completeness
 * For any material, the detail view SHALL display the full description,
 * all associated tags, uploader information, and complete file metadata.
 *
 * @param material - Material detail object
 * @returns Display information for the material detail view
 */
export function extractMaterialDetailDisplayInfo(material: MaterialDetail): MaterialDetailDisplayInfo {
    return {
        title: material.title || '',
        description: material.description || '暂无描述',
        fileName: material.fileName || '',
        fileSize: formatFileSize(material.fileSize),
        fileType: material.fileType || '',
        fileTypeText: getFileTypeText(material.fileType),
        downloadCount: material.downloadCount ?? 0,
        viewCount: material.viewCount ?? 0,
        uploadDate: formatDateTime(material.createdAt),
        categoryName: material.categoryName || '未分类',
        uploaderName: material.uploaderName || material.uploader?.realName || '未知',
        tags: material.tags?.map(t => t.name) || []
    }
}

/**
 * Validate that material detail display info contains all required fields
 *
 * Property 7: Material detail display completeness
 * For any material, the detail view SHALL display the full description,
 * all associated tags, uploader information, and complete file metadata.
 *
 * @param displayInfo - Display information extracted from material
 * @returns true if all required fields are present and valid
 */
export function validateMaterialDetailDisplay(displayInfo: MaterialDetailDisplayInfo): boolean {
    // Title must be present
    if (!displayInfo.title || displayInfo.title.trim() === '') {
        return false
    }

    // Description must be defined (can be default "暂无描述")
    if (displayInfo.description === undefined) {
        return false
    }

    // File name must be present
    if (!displayInfo.fileName) {
        return false
    }

    // File size must be present (even "0 B" is valid)
    if (!displayInfo.fileSize) {
        return false
    }

    // File type text must be present
    if (!displayInfo.fileTypeText) {
        return false
    }

    // Download count must be a non-negative number
    if (typeof displayInfo.downloadCount !== 'number' || displayInfo.downloadCount < 0) {
        return false
    }

    // View count must be a non-negative number
    if (typeof displayInfo.viewCount !== 'number' || displayInfo.viewCount < 0) {
        return false
    }

    // Upload date can be empty string but must be defined
    if (displayInfo.uploadDate === undefined) {
        return false
    }

    // Category name must be defined (can be default "未分类")
    if (displayInfo.categoryName === undefined) {
        return false
    }

    // Uploader name must be defined (can be default "未知")
    if (displayInfo.uploaderName === undefined) {
        return false
    }

    // Tags must be an array (can be empty)
    if (!Array.isArray(displayInfo.tags)) {
        return false
    }

    return true
}
