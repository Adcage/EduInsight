/**
 * Property-based tests for material download functionality
 * Using fast-check for property-based testing
 * 
 * **Feature: student-material-center-profile, Property 5: Download triggers correct API call**
 * **Validates: Requirements 3.1**
 */
import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import {
  createDownloadRequest,
  getDownloadFileName,
  validateDownloadRequest,
  validateDownloadResult,
  simulateDownload,
  type Material
} from '../materialDownload'

// File types used in the system
const fileTypes = ['pdf', 'doc', 'ppt', 'xls', 'image', 'video', 'archive', 'text', 'other']

// Non-whitespace string generator
const nonWhitespaceString = fc.string({ minLength: 1, maxLength: 100 })
  .filter(s => s.trim().length > 0)

// Material arbitrary with valid data
const materialArbitrary: fc.Arbitrary<Material> = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  title: nonWhitespaceString,
  fileName: nonWhitespaceString,
  fileSize: fc.integer({ min: 0, max: 100000000 }),
  fileType: fc.constantFrom(...fileTypes)
})

describe('Material Download - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 5: Download triggers correct API call**
   * **Validates: Requirements 3.1**
   * 
   * Property 5: Download triggers correct API call
   * For any material, clicking the download button SHALL initiate a download request
   * with the correct material ID and the downloaded file SHALL have the original filename.
   */
  it('Property 5: Download request should have correct material ID and filename', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const result = simulateDownload(material)
          
          // Validate material ID is correct
          const hasCorrectId = result.materialId === material.id
          
          // Validate filename is the original filename
          const hasCorrectFilename = result.fileName === material.fileName
          
          return hasCorrectId && hasCorrectFilename
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Download request contains correct material ID
   */
  it('Download request should contain correct material ID', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const request = createDownloadRequest(material)
          return validateDownloadRequest(request, material)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Download filename matches original filename
   */
  it('Download filename should match original filename', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const fileName = getDownloadFileName(material)
          return fileName === material.fileName
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Download result validation works correctly
   */
  it('Download result validation should correctly identify valid results', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        (material) => {
          const result = simulateDownload(material)
          return validateDownloadResult(result, material)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Download result validation rejects incorrect material ID
   */
  it('Download result validation should reject incorrect material ID', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        fc.integer({ min: 1, max: 10000 }),
        (material, wrongId) => {
          // Skip if wrongId happens to match
          if (wrongId === material.id) return true
          
          const result = {
            success: true,
            fileName: material.fileName,
            materialId: wrongId
          }
          
          return !validateDownloadResult(result, material)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Download result validation rejects incorrect filename
   */
  it('Download result validation should reject incorrect filename', () => {
    fc.assert(
      fc.property(
        materialArbitrary,
        nonWhitespaceString,
        (material, wrongFileName) => {
          // Skip if wrongFileName happens to match
          if (wrongFileName === material.fileName) return true
          
          const result = {
            success: true,
            fileName: wrongFileName,
            materialId: material.id
          }
          
          return !validateDownloadResult(result, material)
        }
      ),
      { numRuns: 100 }
    )
  })
})
