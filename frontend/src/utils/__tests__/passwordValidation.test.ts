/**
 * Property-based tests for password validation functionality
 * Using fast-check for property-based testing
 * 
 * **Feature: student-material-center-profile, Property 12: Password confirmation match**
 * **Validates: Requirements 7.4**
 */
import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import {
  validatePasswordMatch,
  calculatePasswordStrength,
  isValidPasswordLength
} from '../passwordValidation'

/**
 * Arbitrary for generating valid passwords (at least 6 characters)
 */
const validPasswordArbitrary = fc.string({ minLength: 6, maxLength: 50 })

/**
 * Arbitrary for generating any non-empty string
 */
const nonEmptyStringArbitrary = fc.string({ minLength: 1, maxLength: 50 })

describe('Password Validation - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 12: Password confirmation match**
   * **Validates: Requirements 7.4**
   * 
   * Property 12: Password confirmation match
   * For any password change form submission, if the new password and confirmation 
   * password do not match exactly, the form SHALL display a mismatch error and prevent submission.
   */
  describe('Property 12: Password confirmation match', () => {
    it('Matching passwords should pass validation', () => {
      fc.assert(
        fc.property(
          validPasswordArbitrary,
          (password) => {
            const result = validatePasswordMatch(password, password)
            
            // Same passwords should be valid
            return result.valid === true && result.error === undefined
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Non-matching passwords should fail validation with error message', () => {
      fc.assert(
        fc.property(
          validPasswordArbitrary,
          validPasswordArbitrary.filter(p => p.length > 0),
          (password1, password2) => {
            // Skip if passwords happen to be the same
            if (password1 === password2) return true
            
            const result = validatePasswordMatch(password1, password2)
            
            // Different passwords should be invalid with error message
            return result.valid === false && 
                   result.error !== undefined && 
                   result.error.length > 0
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Empty confirmation password should fail validation', () => {
      fc.assert(
        fc.property(
          validPasswordArbitrary,
          (password) => {
            const result = validatePasswordMatch(password, '')
            
            // Empty confirmation should be invalid
            return result.valid === false && result.error !== undefined
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Password match validation is symmetric for matching passwords', () => {
      fc.assert(
        fc.property(
          validPasswordArbitrary,
          (password) => {
            const result1 = validatePasswordMatch(password, password)
            const result2 = validatePasswordMatch(password, password)
            
            // Same input should always produce same result
            return result1.valid === result2.valid
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Any character difference should cause mismatch', () => {
      fc.assert(
        fc.property(
          validPasswordArbitrary,
          fc.integer({ min: 0, max: 49 }),
          fc.string({ minLength: 1, maxLength: 1 }), // Single character
          (password, position, newChar) => {
            // Ensure position is within password bounds
            const pos = position % password.length
            
            // Create a modified password by changing one character
            const modifiedPassword = 
              password.substring(0, pos) + 
              newChar + 
              password.substring(pos + 1)
            
            // If the modification actually changed the password
            if (password !== modifiedPassword) {
              const result = validatePasswordMatch(password, modifiedPassword)
              return result.valid === false
            }
            
            return true
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * Additional property tests for password strength calculation
   */
  describe('Password strength calculation properties', () => {
    it('Longer passwords should have equal or higher strength', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 20 }),
          fc.string({ minLength: 1, maxLength: 20 }),
          (base, extension) => {
            const shortPassword = base
            const longPassword = base + extension
            
            const shortStrength = calculatePasswordStrength(shortPassword)
            const longStrength = calculatePasswordStrength(longPassword)
            
            // Longer password should have equal or higher score
            return longStrength.score >= shortStrength.score
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Empty password should have zero strength', () => {
      const result = calculatePasswordStrength('')
      expect(result.score).toBe(0)
      expect(result.percent).toBe(0)
    })

    it('Password strength score should be between 0 and 4', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 0, maxLength: 100 }),
          (password) => {
            const result = calculatePasswordStrength(password)
            return result.score >= 0 && result.score <= 4
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Password strength percent should be between 0 and 100', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 0, maxLength: 100 }),
          (password) => {
            const result = calculatePasswordStrength(password)
            return result.percent >= 0 && result.percent <= 100
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Password strength should always have text and color', () => {
      fc.assert(
        fc.property(
          nonEmptyStringArbitrary,
          (password) => {
            const result = calculatePasswordStrength(password)
            return result.text.length > 0 && result.color.length > 0
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * Password length validation properties
   */
  describe('Password length validation properties', () => {
    it('Passwords meeting minimum length should pass', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 20 }), // minLength
          fc.string({ minLength: 1, maxLength: 50 }),
          (minLength, password) => {
            const isValid = isValidPasswordLength(password, minLength)
            return isValid === (password.length >= minLength)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Default minimum length is 6', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 0, maxLength: 20 }),
          (password) => {
            const isValid = isValidPasswordLength(password)
            return isValid === (password.length >= 6)
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})
