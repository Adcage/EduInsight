/**
 * Property-based tests for material preview functionality
 * Using fast-check for property-based testing
 *
 * **Feature: student-material-center-profile, Property 6: Preview availability by file type**
 * **Validates: Requirements 3.2, 3.3**
 */
import {describe, it} from 'vitest'
import fc from 'fast-check'
import {
    getPreviewAvailability,
    isPreviewSupported,
    type Material,
    PREVIEW_SUPPORTED_TYPES,
    shouldEnablePreviewButton,
    shouldShowDownloadSuggestion
} from '../materialPreview'

// File types that support preview (pdf and image types)
const previewSupportedTypes = ['pdf', 'image', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']

// File types that do NOT support preview
const unsupportedTypes = ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'video', 'mp4', 'avi', 'archive', 'zip', 'rar', 'text', 'txt', 'other', 'exe', 'unknown']

// Non-whitespace string generator
const nonWhitespaceString = fc.string({minLength: 1, maxLength: 100})
    .filter(s => s.trim().length > 0)

// Material arbitrary with supported preview types
const materialWithSupportedTypeArbitrary: fc.Arbitrary<Material> = fc.record({
    id: fc.integer({min: 1, max: 10000}),
    title: nonWhitespaceString,
    fileName: nonWhitespaceString,
    fileSize: fc.integer({min: 0, max: 100000000}),
    fileType: fc.constantFrom(...previewSupportedTypes)
})

// Material arbitrary with unsupported preview types
const materialWithUnsupportedTypeArbitrary: fc.Arbitrary<Material> = fc.record({
    id: fc.integer({min: 1, max: 10000}),
    title: nonWhitespaceString,
    fileName: nonWhitespaceString,
    fileSize: fc.integer({min: 0, max: 100000000}),
    fileType: fc.constantFrom(...unsupportedTypes)
})

// Material arbitrary with any file type
const materialArbitrary: fc.Arbitrary<Material> = fc.record({
    id: fc.integer({min: 1, max: 10000}),
    title: nonWhitespaceString,
    fileName: nonWhitespaceString,
    fileSize: fc.integer({min: 0, max: 100000000}),
    fileType: fc.constantFrom(...previewSupportedTypes, ...unsupportedTypes)
})

describe('Material Preview - Property Tests', () => {
    /**
     * **Feature: student-material-center-profile, Property 6: Preview availability by file type**
     * **Validates: Requirements 3.2, 3.3**
     *
     * Property 6: Preview availability by file type
     * For any material with file type 'pdf' or 'image', the preview button SHALL be enabled;
     * for other file types, the preview button SHALL be disabled or show a download suggestion.
     */
    it('Property 6: PDF and image types should have preview enabled', () => {
        fc.assert(
            fc.property(
                materialWithSupportedTypeArbitrary,
                (material) => {
                    const availability = getPreviewAvailability(material)

                    // Preview should be supported for pdf and image types
                    return availability.isSupported === true &&
                        availability.showDownloadSuggestion === false
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * **Feature: student-material-center-profile, Property 6: Preview availability by file type**
     * **Validates: Requirements 3.2, 3.3**
     *
     * For unsupported file types, preview should be disabled and download suggestion shown
     */
    it('Property 6: Unsupported types should show download suggestion', () => {
        fc.assert(
            fc.property(
                materialWithUnsupportedTypeArbitrary,
                (material) => {
                    const availability = getPreviewAvailability(material)

                    // Preview should NOT be supported for unsupported types
                    // Download suggestion should be shown
                    return availability.isSupported === false &&
                        availability.showDownloadSuggestion === true
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: isPreviewSupported returns true for all supported types
     */
    it('isPreviewSupported should return true for all supported file types', () => {
        fc.assert(
            fc.property(
                fc.constantFrom(...previewSupportedTypes),
                (fileType) => {
                    return isPreviewSupported(fileType) === true
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: isPreviewSupported returns false for all unsupported types
     */
    it('isPreviewSupported should return false for all unsupported file types', () => {
        fc.assert(
            fc.property(
                fc.constantFrom(...unsupportedTypes),
                (fileType) => {
                    return isPreviewSupported(fileType) === false
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: isPreviewSupported is case-insensitive
     */
    it('isPreviewSupported should be case-insensitive', () => {
        fc.assert(
            fc.property(
                fc.constantFrom(...previewSupportedTypes),
                (fileType) => {
                    const upperCase = isPreviewSupported(fileType.toUpperCase())
                    const lowerCase = isPreviewSupported(fileType.toLowerCase())
                    const mixedCase = isPreviewSupported(
                        fileType.split('').map((c, i) => i % 2 === 0 ? c.toUpperCase() : c.toLowerCase()).join('')
                    )

                    return upperCase === lowerCase && lowerCase === mixedCase
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: shouldEnablePreviewButton matches isPreviewSupported
     */
    it('shouldEnablePreviewButton should match isPreviewSupported for any material', () => {
        fc.assert(
            fc.property(
                materialArbitrary,
                (material) => {
                    const buttonEnabled = shouldEnablePreviewButton(material)
                    const previewSupported = isPreviewSupported(material.fileType)

                    return buttonEnabled === previewSupported
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: shouldShowDownloadSuggestion is inverse of isPreviewSupported
     */
    it('shouldShowDownloadSuggestion should be inverse of isPreviewSupported', () => {
        fc.assert(
            fc.property(
                materialArbitrary,
                (material) => {
                    const showSuggestion = shouldShowDownloadSuggestion(material)
                    const previewSupported = isPreviewSupported(material.fileType)

                    return showSuggestion === !previewSupported
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Preview availability is consistent across functions
     */
    it('Preview availability should be consistent across all functions', () => {
        fc.assert(
            fc.property(
                materialArbitrary,
                (material) => {
                    const availability = getPreviewAvailability(material)
                    const buttonEnabled = shouldEnablePreviewButton(material)
                    const showSuggestion = shouldShowDownloadSuggestion(material)
                    const previewSupported = isPreviewSupported(material.fileType)

                    // All functions should agree on preview support status
                    return availability.isSupported === previewSupported &&
                        availability.isSupported === buttonEnabled &&
                        availability.showDownloadSuggestion === showSuggestion &&
                        availability.showDownloadSuggestion === !previewSupported
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: PREVIEW_SUPPORTED_TYPES constant matches isPreviewSupported behavior
     */
    it('PREVIEW_SUPPORTED_TYPES constant should match isPreviewSupported behavior', () => {
        fc.assert(
            fc.property(
                fc.constantFrom(...PREVIEW_SUPPORTED_TYPES),
                (fileType) => {
                    return isPreviewSupported(fileType) === true
                }
            ),
            {numRuns: 100}
        )
    })

    /**
     * Property: Empty or null file types should not support preview
     */
    it('Empty or null file types should not support preview', () => {
        fc.assert(
            fc.property(
                fc.constantFrom(null, undefined, ''),
                (fileType) => {
                    return isPreviewSupported(fileType as any) === false
                }
            ),
            {numRuns: 10}
        )
    })
})
