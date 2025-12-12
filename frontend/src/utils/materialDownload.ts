/**
 * Material download utility functions
 * These functions are extracted for testability
 */

export interface Material {
    id: number
    title: string
    fileName: string
    fileSize: number
    fileType: string
}

export interface DownloadRequest {
    materialId: number
}

export interface DownloadResult {
    success: boolean
    fileName: string
    materialId: number
}

/**
 * Create download request parameters for a material
 * Property 5: Download triggers correct API call
 * For any material, clicking the download button SHALL initiate a download request
 * with the correct material ID and the downloaded file SHALL have the original filename.
 *
 * @param material - Material to download
 * @returns Download request parameters
 */
export function createDownloadRequest(material: Material): DownloadRequest {
    return {
        materialId: material.id
    }
}

/**
 * Get the filename for download
 * @param material - Material being downloaded
 * @returns The original filename to use for download
 */
export function getDownloadFileName(material: Material): string {
    return material.fileName
}

/**
 * Validate download request has correct material ID
 * @param request - Download request
 * @param material - Original material
 * @returns true if request has correct material ID
 */
export function validateDownloadRequest(request: DownloadRequest, material: Material): boolean {
    return request.materialId === material.id
}

/**
 * Validate download result has correct filename
 * @param result - Download result
 * @param material - Original material
 * @returns true if result has correct filename
 */
export function validateDownloadResult(result: DownloadResult, material: Material): boolean {
    return result.fileName === material.fileName && result.materialId === material.id
}

/**
 * Simulate download process and return result
 * @param material - Material to download
 * @returns Download result with filename and material ID
 */
export function simulateDownload(material: Material): DownloadResult {
    const request = createDownloadRequest(material)
    const fileName = getDownloadFileName(material)

    return {
        success: true,
        fileName: fileName,
        materialId: request.materialId
    }
}
