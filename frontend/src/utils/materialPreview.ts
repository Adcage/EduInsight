/**
 * Material preview utility functions
 * These functions are extracted for testability
 *
 * **Feature: student-material-center-profile, Property 6: Preview availability by file type**
 * **Validates: Requirements 3.2, 3.3**
 */

export interface Material {
    id: number
    title: string
    fileName: string
    fileSize: number
    fileType: string
}

export interface PreviewAvailability {
    isSupported: boolean
    showDownloadSuggestion: boolean
    fileType: string
}

/**
 * List of file types that support preview
 * PDF and image types are supported for in-browser preview
 */
export const PREVIEW_SUPPORTED_TYPES = [
    'pdf',
    'image',
    'jpg',
    'jpeg',
    'png',
    'gif',
    'bmp',
    'webp',
    'svg'
]

/**
 * Check if a file type supports preview
 * Property 6: Preview availability by file type
 * For any material with file type 'pdf' or 'image', the preview button SHALL be enabled;
 * for other file types, the preview button SHALL be disabled or show a download suggestion.
 *
 * @param fileType - File type to check
 * @returns true if the file type supports preview
 */
export function isPreviewSupported(fileType: string | undefined | null): boolean {
    if (!fileType) return false
    return PREVIEW_SUPPORTED_TYPES.includes(fileType.toLowerCase())
}

/**
 * Get preview availability status for a material
 * @param material - Material to check
 * @returns Preview availability status
 */
export function getPreviewAvailability(material: Material): PreviewAvailability {
    const isSupported = isPreviewSupported(material.fileType)

    return {
        isSupported,
        showDownloadSuggestion: !isSupported,
        fileType: material.fileType
    }
}

/**
 * Check if preview button should be enabled for a material
 * @param material - Material to check
 * @returns true if preview button should be enabled
 */
export function shouldEnablePreviewButton(material: Material): boolean {
    return isPreviewSupported(material.fileType)
}

/**
 * Check if download suggestion should be shown for a material
 * @param material - Material to check
 * @returns true if download suggestion should be shown
 */
export function shouldShowDownloadSuggestion(material: Material): boolean {
    return !isPreviewSupported(material.fileType)
}

/**
 * Get MIME content type for a file type
 * @param fileType - File type
 * @returns MIME content type string
 */
export function getContentType(fileType: string): string {
    const typeMap: Record<string, string> = {
        pdf: 'application/pdf',
        image: 'image/*',
        jpg: 'image/jpeg',
        jpeg: 'image/jpeg',
        png: 'image/png',
        gif: 'image/gif',
        bmp: 'image/bmp',
        webp: 'image/webp',
        svg: 'image/svg+xml'
    }
    return typeMap[fileType.toLowerCase()] || 'application/octet-stream'
}
