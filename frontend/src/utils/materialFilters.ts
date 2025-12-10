/**
 * Material filtering utility functions
 * These functions are extracted for testability
 */

export interface Material {
    id: number
    title: string
    description?: string
    fileName: string
    fileSize: number
    fileType: string
    categoryId?: number | null
    courseId?: number | null
    uploaderId?: number
    downloadCount?: number
    viewCount?: number
    createdAt?: string
    updatedAt?: string
    tags?: Array<{ id: number; name: string }>
    keywords?: string
}

export interface MaterialFilters {
    categoryId?: number | null
    fileType?: string | null
    courseId?: number | null
    tagIds?: number[]
}

/**
 * Filter materials based on the provided filter criteria
 * Property 1: Filter consistency - all displayed materials SHALL match ALL active filter criteria simultaneously
 *
 * @param materials - Array of materials to filter
 * @param filters - Filter criteria to apply
 * @returns Filtered array of materials
 */
export function filterMaterials(materials: Material[], filters: MaterialFilters): Material[] {
    return materials.filter(material => {
        // Category filter
        if (filters.categoryId !== null && filters.categoryId !== undefined) {
            if (material.categoryId !== filters.categoryId) {
                return false
            }
        }

        // File type filter
        if (filters.fileType !== null && filters.fileType !== undefined && filters.fileType !== '') {
            if (material.fileType !== filters.fileType) {
                return false
            }
        }

        // Course filter
        if (filters.courseId !== null && filters.courseId !== undefined) {
            if (material.courseId !== filters.courseId) {
                return false
            }
        }

        // Tag filter - material must have at least one of the selected tags
        if (filters.tagIds && filters.tagIds.length > 0) {
            const materialTagIds = material.tags?.map(t => t.id) || []
            const hasMatchingTag = filters.tagIds.some(tagId => materialTagIds.includes(tagId))
            if (!hasMatchingTag) {
                return false
            }
        }

        return true
    })
}

/**
 * Check if a material matches all active filter criteria
 * Used for validation in property tests
 *
 * @param material - Material to check
 * @param filters - Filter criteria
 * @returns true if material matches all filters
 */
export function materialMatchesFilters(material: Material, filters: MaterialFilters): boolean {
    // Category filter
    if (filters.categoryId !== null && filters.categoryId !== undefined) {
        if (material.categoryId !== filters.categoryId) {
            return false
        }
    }

    // File type filter
    if (filters.fileType !== null && filters.fileType !== undefined && filters.fileType !== '') {
        if (material.fileType !== filters.fileType) {
            return false
        }
    }

    // Course filter
    if (filters.courseId !== null && filters.courseId !== undefined) {
        if (material.courseId !== filters.courseId) {
            return false
        }
    }

    // Tag filter
    if (filters.tagIds && filters.tagIds.length > 0) {
        const materialTagIds = material.tags?.map(t => t.id) || []
        const hasMatchingTag = filters.tagIds.some(tagId => materialTagIds.includes(tagId))
        if (!hasMatchingTag) {
            return false
        }
    }

    return true
}
