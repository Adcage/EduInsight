/**
 * Property-based tests for avatar validation functionality
 * Using fast-check for property-based testing
 * 
 * **Feature: student-material-center-profile, Property 13: Avatar file size validation**
 * **Feature: student-material-center-profile, Property 14: Avatar upload failure handling**
 * **Validates: Requirements 8.4, 8.5**
 */
import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import {
  validateAvatarFile,
  isValidAvatarSize,
  isValidAvatarType,
  ALLOWED_AVATAR_TYPES,
  DEFAULT_MAX_AVATAR_SIZE
} from '../avatarValidation'

/**
 * Creates a mock File object for testing with a fake size
 * Uses Object.defineProperty to set size without creating actual content
 */
function createMockFile(
  name: string,
  size: number,
  type: string
): File {
  // Create a minimal blob
  const blob = new Blob(['x'], { type })
  const file = new File([blob], name, { type })
  
  // Override the size property to avoid creating large files
  Object.defineProperty(file, 'size', {
    value: size,
    writable: false
  })
  
  return file
}

/**
 * Arbitrary for generating valid image file types
 */
const validImageTypeArbitrary = fc.constantFrom(...ALLOWED_AVATAR_TYPES)

/**
 * Arbitrary for generating invalid file types
 */
const invalidFileTypeArbitrary = fc.constantFrom(
  'application/pdf',
  'text/plain',
  'application/zip',
  'video/mp4',
  'audio/mp3',
  'application/json',
  'text/html'
)

/**
 * Arbitrary for generating file names with valid extensions
 */
const validFileNameArbitrary = fc.tuple(
  fc.string({ minLength: 1, maxLength: 20 }).filter(s => /^[a-zA-Z0-9_-]+$/.test(s)),
  fc.constantFrom('.jpg', '.jpeg', '.png', '.gif')
).map(([name, ext]) => name + ext)

/**
 * Arbitrary for generating file names with invalid extensions
 */
const invalidFileNameArbitrary = fc.tuple(
  fc.string({ minLength: 1, maxLength: 20 }).filter(s => /^[a-zA-Z0-9_-]+$/.test(s)),
  fc.constantFrom('.pdf', '.txt', '.doc', '.mp4', '.zip')
).map(([name, ext]) => name + ext)

describe('Avatar Validation - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 13: Avatar file size validation**
   * **Validates: Requirements 8.4**
   * 
   * Property 13: Avatar file size validation
   * For any selected image file, if the file size exceeds 2MB, 
   * the upload SHALL be rejected with a file size error message.
   */
  describe('Property 13: Avatar file size validation', () => {
    it('Files exceeding max size should be rejected with size error', () => {
      fc.assert(
        fc.property(
          validFileNameArbitrary,
          validImageTypeArbitrary,
          // Generate sizes larger than 2MB (2 * 1024 * 1024 = 2097152 bytes)
          fc.integer({ min: DEFAULT_MAX_AVATAR_SIZE + 1, max: DEFAULT_MAX_AVATAR_SIZE + 1000000 }),
          (fileName, fileType, fileSize) => {
            const file = createMockFile(fileName, fileSize, fileType)
            const result = validateAvatarFile(file, DEFAULT_MAX_AVATAR_SIZE)
            
            // Should be invalid with error message about file size
            return !result.valid && result.error !== undefined && result.error.includes('MB')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Files within max size should pass size validation', () => {
      fc.assert(
        fc.property(
          validFileNameArbitrary,
          validImageTypeArbitrary,
          // Generate sizes within limit (1 byte to 2MB)
          fc.integer({ min: 1, max: DEFAULT_MAX_AVATAR_SIZE }),
          (fileName, fileType, fileSize) => {
            const file = createMockFile(fileName, fileSize, fileType)
            
            // Size validation should pass
            return isValidAvatarSize(file, DEFAULT_MAX_AVATAR_SIZE)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('isValidAvatarSize correctly identifies oversized files', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10000000 }), // file size
          fc.integer({ min: 1, max: 10000000 }), // max size
          (fileSize, maxSize) => {
            const file = createMockFile('test.jpg', fileSize, 'image/jpeg')
            const isValid = isValidAvatarSize(file, maxSize)
            
            // Should be valid if and only if fileSize <= maxSize
            return isValid === (fileSize <= maxSize)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * **Feature: student-material-center-profile, Property 14: Avatar upload failure handling**
   * **Validates: Requirements 8.5**
   * 
   * Property 14: Avatar upload failure handling
   * For any failed avatar upload attempt, the error message SHALL be displayed
   * and the previously displayed avatar SHALL remain unchanged.
   * 
   * This property tests that validation failures produce appropriate error messages.
   */
  describe('Property 14: Avatar upload failure handling', () => {
    it('Invalid file types should produce error messages', () => {
      fc.assert(
        fc.property(
          invalidFileNameArbitrary,
          invalidFileTypeArbitrary,
          fc.integer({ min: 1, max: DEFAULT_MAX_AVATAR_SIZE }),
          (fileName, fileType, fileSize) => {
            const file = createMockFile(fileName, fileSize, fileType)
            const result = validateAvatarFile(file, DEFAULT_MAX_AVATAR_SIZE)
            
            // Should be invalid with error message
            return !result.valid && 
                   result.error !== undefined && 
                   typeof result.error === 'string' && 
                   result.error.length > 0
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Validation errors always include descriptive error messages', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            // Invalid type
            fc.tuple(
              invalidFileNameArbitrary,
              invalidFileTypeArbitrary,
              fc.constant(1000) // Use small constant size for invalid type tests
            ),
            // Invalid size
            fc.tuple(
              validFileNameArbitrary,
              validImageTypeArbitrary,
              fc.integer({ min: DEFAULT_MAX_AVATAR_SIZE + 1, max: DEFAULT_MAX_AVATAR_SIZE + 100000 })
            )
          ),
          ([fileName, fileType, fileSize]) => {
            const file = createMockFile(fileName, fileSize, fileType)
            const result = validateAvatarFile(file, DEFAULT_MAX_AVATAR_SIZE)
            
            // If validation fails, error message must be present
            if (!result.valid) {
              return result.error !== undefined && result.error.length > 0
            }
            return true
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Valid files should pass validation without errors', () => {
      fc.assert(
        fc.property(
          validFileNameArbitrary,
          validImageTypeArbitrary,
          fc.integer({ min: 1, max: DEFAULT_MAX_AVATAR_SIZE }),
          (fileName, fileType, fileSize) => {
            const file = createMockFile(fileName, fileSize, fileType)
            const result = validateAvatarFile(file, DEFAULT_MAX_AVATAR_SIZE)
            
            // Should be valid with no error
            return result.valid && result.error === undefined
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * Additional property tests for file type validation
   */
  describe('File type validation properties', () => {
    it('All allowed MIME types should be accepted', () => {
      fc.assert(
        fc.property(
          validFileNameArbitrary,
          validImageTypeArbitrary,
          (fileName, fileType) => {
            const file = createMockFile(fileName, 1000, fileType)
            return isValidAvatarType(file)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Non-image MIME types should be rejected', () => {
      fc.assert(
        fc.property(
          invalidFileNameArbitrary,
          invalidFileTypeArbitrary,
          (fileName, fileType) => {
            const file = createMockFile(fileName, 1000, fileType)
            return !isValidAvatarType(file)
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})
