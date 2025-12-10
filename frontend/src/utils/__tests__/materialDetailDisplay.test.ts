/**
 * Property-based tests for material detail display functionality
 * Using fast-check for property-based testing
 *
 * **Feature: student-material-center-profile, Property 7: Material detail display completeness**
 * **Validates: Requirements 4.1**
 */
import {describe, it} from 'vitest'
import fc from 'fast-check'
import {
    extractMaterialDetailDisplayInfo,
    formatDateTime,
    formatFileSize,
    getFileTypeText,
    type MaterialDetail,
    type MaterialTag,
    validateMaterialDetailDisplay
} from '../materialDetailDisplay'

// File types used in the system
const fileTypes = ['pdf', 'doc', 'ppt', 'xls', 'image', 'video', 'archive', 'text', 'other']

// Generate ISO date strings directly to avoid date conversion issues
const isoDateArbitrary = fc.tuple(
    fc.integer({min: 2020, max: 2030}),
    fc.integer({min: 1, max: 12}),
    fc.integer({min: 1, max: 28}),
    fc.integer({min: 0, max: 23}),
    fc.integer({min: 0, max: 59}),
    fc.integer({min: 0, max: 59})
).map(([year, month, day, hour, minute, second]) =>
    `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:${String(second).padStart(2, '0')}.000Z`
)

// Non-whitespace string generator for titles (materials must have valid titles)
const nonWhitespaceString = fc.string({minLength: 1, maxLength: 100})
    .filter(s => s.trim().length > 0)

// Tag arbitrary
const tagArbitrary: fc.Arbitrary<MaterialTag> = fc.record({
    id: fc.integer({min: 1, max: 10000}),
    name: nonWhitespaceString
})

// Material detail arbitrary with valid data
const materialDetailArbitrary: fc.Arbitrary<MaterialDetail> = fc.record({
    id: fc.integer({min: 1, max: 10000}),
    title: nonWhitespaceString,
    description: fc.option(fc.string({maxLength: 1000}), {nil: undefined}),
    fileName: fc.string({minLength: 1, maxLength: 100}),
    fileSize: fc.integer({min: 0, max: 100000000}),
    fileType: fc.constantFrom(...fileTypes),
    downloadCount: fc.option(fc.integer({min: 0, max: 10000}), {nil: undefined}),
    viewCount: fc.option(fc.integer({min: 0, max: 10000}), {nil: undefined}),
    createdAt: fc.option(isoDateArbitrary, {nil: undefined}),
    updatedAt: fc.option(isoDateArbitrary, {nil: undefined}),
    categoryId: fc.option(fc.integer({min: 1, max: 1000}), {nil: undefined}),
    categoryName: fc.option(fc.string({minLength: 1, maxLength: 50}), {nil: undefined}),
    uploaderId: fc.option(fc.integer({min: 1, max: 10000}), {nil: undefined}),
    uploaderName: fc.option(fc.string({minLength: 1, maxLength: 50}), {nil: undefined}),
    tags: fc.option(fc.array(tagArbitrary, {minLength: 0, maxLength: 10}), {nil: undefined})
})


describe('Material Detail Display - Property Tests', () => {
    /**
     * **Feature: student-material-center-profile, Property 7: Material detail display completeness**
     * **Validates: Requirements 4.1**
     *
     * Property 7: Material detail display completeness
     * For any material, the detail view SHALL display the full description,
     * all associated tags, uploader information, and complete file metadata.
     */
    it('Property 7: Material detail should display all required information', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)

                    // Validate all required fields are present
                    return validateMaterialDetailDisplay(displayInfo)
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Title is preserved in display info
     */
    it('Title should be preserved in display info', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)
                    return displayInfo.title === material.title
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Description is preserved or defaults to "暂无描述"
     */
    it('Description should be preserved or default to "暂无描述"', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)
                    if (material.description) {
                        return displayInfo.description === material.description
                    }
                    return displayInfo.description === '暂无描述'
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Tags are preserved as string array
     */
    it('Tags should be preserved as string array', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)

                    if (!material.tags || material.tags.length === 0) {
                        return displayInfo.tags.length === 0
                    }

                    // All tag names should be preserved
                    const expectedTagNames = material.tags.map(t => t.name)
                    return displayInfo.tags.length === expectedTagNames.length &&
                        displayInfo.tags.every((name, i) => name === expectedTagNames[i])
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Uploader name is preserved or defaults to "未知"
     */
    it('Uploader name should be preserved or default to "未知"', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)

                    if (material.uploaderName) {
                        return displayInfo.uploaderName === material.uploaderName
                    }
                    if (material.uploader?.realName) {
                        return displayInfo.uploaderName === material.uploader.realName
                    }
                    return displayInfo.uploaderName === '未知'
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Category name is preserved or defaults to "未分类"
     */
    it('Category name should be preserved or default to "未分类"', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)

                    if (material.categoryName) {
                        return displayInfo.categoryName === material.categoryName
                    }
                    return displayInfo.categoryName === '未分类'
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: File metadata is complete
     */
    it('File metadata should be complete', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)

                    // File name should be preserved
                    const fileNameValid = displayInfo.fileName === (material.fileName || '')

                    // File size should be formatted
                    const fileSizeValid = displayInfo.fileSize.length > 0

                    // File type text should be present
                    const fileTypeValid = displayInfo.fileTypeText.length > 0

                    return fileNameValid && fileSizeValid && fileTypeValid
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: File size formatting produces valid output
     */
    it('File size formatting should produce valid output for any non-negative size', () => {
        fc.assert(
            fc.property(
                fc.integer({min: 0, max: 1000000000000}),
                (bytes) => {
                    const formatted = formatFileSize(bytes)
                    // Should contain a number and a unit
                    return /^\d+(\.\d+)?\s+(B|KB|MB|GB)$/.test(formatted)
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Date time formatting produces valid date string or empty string
     */
    it('Date time formatting should produce valid date time string', () => {
        fc.assert(
            fc.property(
                isoDateArbitrary,
                (dateStr) => {
                    const formatted = formatDateTime(dateStr)
                    // Should be in YYYY-MM-DD HH:mm:ss format or empty
                    return formatted === '' || /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(formatted)
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: File type text is always a non-empty string
     */
    it('File type text should always be a non-empty string', () => {
        fc.assert(
            fc.property(
                fc.constantFrom(...fileTypes),
                (fileType) => {
                    const text = getFileTypeText(fileType)
                    return typeof text === 'string' && text.length > 0
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Unknown file types default to '其他'
     */
    it('Unknown file types should default to "其他"', () => {
        fc.assert(
            fc.property(
                fc.string({minLength: 1, maxLength: 20}).filter(s => !fileTypes.includes(s)),
                (unknownType) => {
                    const text = getFileTypeText(unknownType)
                    return text === '其他'
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Download and view counts are non-negative
     */
    it('Download and view counts should be non-negative', () => {
        fc.assert(
            fc.property(
                materialDetailArbitrary,
                (material) => {
                    const displayInfo = extractMaterialDetailDisplayInfo(material)
                    return displayInfo.downloadCount >= 0 && displayInfo.viewCount >= 0
                }
            ),
            {numRuns: 100}
        )
    })
})
