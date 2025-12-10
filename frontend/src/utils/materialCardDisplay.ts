/**
 * Material card display utility functions
 * These functions are extracted for testability
 */

export interface Material {
  id: number
  title: string
  description?: string
  fileName: string
  fileSize: number
  fileType: string
  downloadCount?: number
  viewCount?: number
  createdAt?: string
}

export interface MaterialCardDisplayInfo {
  title: string
  fileTypeIndicator: string
  fileSize: string
  uploadDate: string
  downloadCount: number
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
export function formatFileSize(bytes: number): string {
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
 * @returns Formatted date string (YYYY-MM-DD)
 */
export function formatDate(date?: string): string {
  if (!date) return ''
  try {
    const d = new Date(date)
    if (isNaN(d.getTime())) return ''
    return d.toISOString().split('T')[0]
  } catch {
    return ''
  }
}

/**
 * Get file type display text
 * @param fileType - File type code
 * @returns Display text for file type
 */
export function getFileTypeText(fileType: string): string {
  // Use Object.hasOwn to avoid prototype pollution issues with strings like "toString"
  if (Object.hasOwn(fileTypeTextMap, fileType)) {
    return fileTypeTextMap[fileType]
  }
  return '其他'
}

/**
 * Extract display information from a material for card rendering
 * Property 2: Material card display completeness
 * For any material in the list, the rendered card SHALL contain the material title,
 * file type indicator, file size, upload date, and download count.
 * 
 * @param material - Material object
 * @returns Display information for the material card
 */
export function extractMaterialCardDisplayInfo(material: Material): MaterialCardDisplayInfo {
  return {
    title: material.title,
    fileTypeIndicator: getFileTypeText(material.fileType),
    fileSize: formatFileSize(material.fileSize),
    uploadDate: formatDate(material.createdAt),
    downloadCount: material.downloadCount ?? 0
  }
}

/**
 * Validate that material card display info contains all required fields
 * @param displayInfo - Display information extracted from material
 * @returns true if all required fields are present and valid
 */
export function validateMaterialCardDisplay(displayInfo: MaterialCardDisplayInfo): boolean {
  // Title must be present
  if (!displayInfo.title || displayInfo.title.trim() === '') {
    return false
  }
  
  // File type indicator must be present
  if (!displayInfo.fileTypeIndicator || displayInfo.fileTypeIndicator.trim() === '') {
    return false
  }
  
  // File size must be present (even "0 B" is valid)
  if (!displayInfo.fileSize) {
    return false
  }
  
  // Upload date can be empty string but must be defined
  if (displayInfo.uploadDate === undefined) {
    return false
  }
  
  // Download count must be a non-negative number
  if (typeof displayInfo.downloadCount !== 'number' || displayInfo.downloadCount < 0) {
    return false
  }
  
  return true
}
