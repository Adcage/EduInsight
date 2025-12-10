/**
 * Property-based tests for material card display functionality
 * Using fast-check for property-based testing
 * 
 * **Feature: student-material-center-profile, Property 2: Material card display completeness**
 * **Validates: Requirements 1.5**
 */
import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import {
  formatFileSize,
  formatDate,
  getFileTypeText,
  extractMaterialCardDisplayInfo,
  validateMaterialCardDisplay,
  type Material
} from '../materialCardDisplay'

// File types used in the system
const fileTypes = ['pdf', 'doc', 'ppt', 'xls', 'image', 'video', 'archive', 'text', 'other']

// Generate ISO date strings directly to avoid date conversion issues
const isoDateArbitrary = fc.tuple(
  fc.integer({ min: 2020, max: 2030 }),
  fc.integer({ min: 1, max: 12 }),
  fc.integer({ min: 1, max: 28 })
).map(([year, month, day]) =>
  `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00.000Z`
)

// Non-whitespace string generator for titles (materials must have valid titles)
const nonWhitespaceString = fc.string({ minLength: 1, maxLength: 100 })
  .filter(s => s.trim().length > 0)

// Material arbitrary with valid data
const materialArbitrary: fc.Arbitrary<Material> = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  title: nonWhitespaceString,
  description: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  fileName: fc.string({ minLength: 1, maxLength: 100 }),
  fileSize: fc.integer({ min: 0, max: 100000000 }),
  fileType: fc.constantFrom(...fileTypes),
  downloadCount: fc.integer({ min: 0, max: 10000 }),
  viewCount: fc.integer({ min: 0, max: 10000 }),
  createdAt: isoDateArbitrary
})

describe('Material Card Display - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 2: Material card display completeness**
   * **Validates: Requirements 1.5**
   * 
   * Property 2: Material card display completeness
   * For any material in the list, the rendered card SHALL contain the material title,
   * file type indicator, file size, upload date, and download count.
   */
  it('Property 2: Material card should display all required information', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const displayInfo = extractMaterialCardDisplayInfo(material)
          
          // Validate all required fields are present
          return validateMaterialCardDisplay(displayInfo)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Title is preserved in display info
   */
  it('Title should be preserved in display info', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const displayInfo = extractMaterialCardDisplayInfo(material)
          return displayInfo.title === material.title
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: File type indicator is always a non-empty string
   */
  it('File type indicator should always be a non-empty string', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...fileTypes),
        (fileType) => {
          const indicator = getFileTypeText(fileType)
          return typeof indicator === 'string' && indicator.length > 0
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: File size formatting produces valid output
   */
  it('File size formatting should produce valid output for any non-negative size', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 1000000000000 }),
        (bytes) => {
          const formatted = formatFileSize(bytes)
          // Should contain a number and a unit
          return /^\d+(\.\d+)?\s+(B|KB|MB|GB)$/.test(formatted)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Download count is preserved as non-negative number
   */
  it('Download count should be preserved as non-negative number', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const displayInfo = extractMaterialCardDisplayInfo(material)
          return displayInfo.downloadCount >= 0 &&
                 displayInfo.downloadCount === (material.downloadCount ?? 0)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Date formatting produces valid date string or empty string
   */
  it('Date formatting should produce valid date string', () => {
    fc.assert(
      fc.property(
        isoDateArbitrary,
        (dateStr) => {
          const formatted = formatDate(dateStr)
          // Should be in YYYY-MM-DD format or empty
          return formatted === '' || /^\d{4}-\d{2}-\d{2}$/.test(formatted)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Unknown file types default to '其他'
   */
  it('Unknown file types should default to "其他"', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 20 }).filter(s => !fileTypes.includes(s)),
        (unknownType) => {
          const indicator = getFileTypeText(unknownType)
          return indicator === '其他'
        }
      ),
      { numRuns: 100 }
    )
  })
})
