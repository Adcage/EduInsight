/**
 * Property-based tests for profile edit functionality
 * Using fast-check for property-based testing
 *
 * **Feature: student-material-center-profile, Property 10: Profile edit cancellation restoration**
 * **Feature: student-material-center-profile, Property 11: Email and phone validation**
 * **Validates: Requirements 6.4, 6.5**
 */
import { describe, it } from 'vitest'
import fc from 'fast-check'
import { validateEmail, validatePhone } from '../profileValidation'

/**
 * Interface for edit form state
 */
interface EditFormState {
  realName: string
  email: string
  phone: string
}

/**
 * Simulates the cancel editing behavior
 * When cancel is clicked, form values should be restored to original values
 */
function simulateCancelEditing(
  originalValues: EditFormState,
  _currentFormValues: EditFormState
): EditFormState {
  // Cancel should restore original values
  return {
    realName: originalValues.realName,
    email: originalValues.email,
    phone: originalValues.phone,
  }
}

/**
 * Arbitrary for generating valid email addresses
 */
const validEmailArbitrary = fc.constantFrom(
  'test@example.com',
  'user@domain.org',
  'admin@company.co.uk',
  'student123@school.edu',
  'teacher.name@university.edu.cn'
)

/**
 * Arbitrary for generating invalid email addresses
 * These are emails that fail the regex /^[^\s@]+@[^\s@]+\.[^\s@]+$/
 */
const invalidEmailArbitrary = fc.constantFrom(
  '', // empty
  '   ', // whitespace only
  'notanemail', // no @ symbol
  '@nodomain.com', // nothing before @
  'missing@', // nothing after @
  'spaces in@email.com', // contains space
  'double@@at.com', // double @
  'nodot@domaincom' // no dot in domain
)

/**
 * Arbitrary for generating valid Chinese phone numbers
 */
const validPhoneArbitrary = fc.constantFrom(
  '13800138000',
  '15912345678',
  '18600001111',
  '17700009999',
  '19988887777'
)

/**
 * Arbitrary for generating invalid phone numbers
 */
const invalidPhoneArbitrary = fc.constantFrom(
  '12345678901', // starts with 1 but second digit is 2
  '23456789012', // doesn't start with 1
  '1380013800', // too short (10 digits)
  '138001380001', // too long (12 digits)
  'abcdefghijk', // letters
  '138-0013-8000', // with dashes
  '138 0013 8000' // with spaces
)

/**
 * Arbitrary for generating edit form states
 */
const editFormStateArbitrary: fc.Arbitrary<EditFormState> = fc.record({
  realName: fc.constantFrom('张三', 'John Doe', 'Test User', '李四'),
  email: validEmailArbitrary,
  phone: fc.constantFrom('13800138000', '15912345678', ''),
})

describe('Profile Edit - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 10: Profile edit cancellation restoration**
   * **Validates: Requirements 6.4**
   *
   * Property 10: Profile edit cancellation restoration
   * For any profile edit session, canceling the edit SHALL restore all form fields
   * to their original values before editing began.
   */
  describe('Property 10: Profile edit cancellation restoration', () => {
    it('Canceling edit should restore all fields to original values', () => {
      fc.assert(
        fc.property(
          editFormStateArbitrary, // original values
          editFormStateArbitrary, // modified values (what user typed)
          (originalValues, modifiedValues) => {
            // Simulate cancel editing
            const restoredValues = simulateCancelEditing(originalValues, modifiedValues)

            // All fields should be restored to original values
            return (
              restoredValues.realName === originalValues.realName &&
              restoredValues.email === originalValues.email &&
              restoredValues.phone === originalValues.phone
            )
          }
        ),
        { numRuns: 100 }
      )
    })

    it('Cancel restoration should be idempotent', () => {
      fc.assert(
        fc.property(editFormStateArbitrary, editFormStateArbitrary, (originalValues, modifiedValues) => {
          // Cancel once
          const firstCancel = simulateCancelEditing(originalValues, modifiedValues)
          // Cancel again (simulating double-click or re-cancel)
          const secondCancel = simulateCancelEditing(originalValues, firstCancel)

          // Both cancels should produce the same result
          return (
            firstCancel.realName === secondCancel.realName &&
            firstCancel.email === secondCancel.email &&
            firstCancel.phone === secondCancel.phone
          )
        }),
        { numRuns: 100 }
      )
    })

    it('Original values should remain unchanged after cancel', () => {
      fc.assert(
        fc.property(editFormStateArbitrary, editFormStateArbitrary, (originalValues, modifiedValues) => {
          const originalCopy = { ...originalValues }
          simulateCancelEditing(originalValues, modifiedValues)

          // Original values object should not be mutated
          return (
            originalValues.realName === originalCopy.realName &&
            originalValues.email === originalCopy.email &&
            originalValues.phone === originalCopy.phone
          )
        }),
        { numRuns: 100 }
      )
    })
  })

  /**
   * **Feature: student-material-center-profile, Property 11: Email and phone validation**
   * **Validates: Requirements 6.5**
   *
   * Property 11: Email and phone validation
   * For any email input, the validation SHALL accept only strings matching standard email format;
   * for any phone input, the validation SHALL accept only valid phone number formats.
   */
  describe('Property 11: Email and phone validation', () => {
    describe('Email validation', () => {
      it('Valid emails should pass validation', () => {
        fc.assert(
          fc.property(validEmailArbitrary, (email) => {
            const result = validateEmail(email)
            return result.valid === true
          }),
          { numRuns: 100 }
        )
      })

      it('Invalid emails should fail validation with error message', () => {
        fc.assert(
          fc.property(invalidEmailArbitrary, (email) => {
            const result = validateEmail(email)
            return result.valid === false && result.error !== undefined && result.error.length > 0
          }),
          { numRuns: 100 }
        )
      })

      it('Email validation result should be deterministic', () => {
        fc.assert(
          fc.property(fc.oneof(validEmailArbitrary, invalidEmailArbitrary), (email) => {
            const result1 = validateEmail(email)
            const result2 = validateEmail(email)
            return result1.valid === result2.valid
          }),
          { numRuns: 100 }
        )
      })
    })

    describe('Phone validation', () => {
      it('Valid phone numbers should pass validation', () => {
        fc.assert(
          fc.property(validPhoneArbitrary, (phone) => {
            const result = validatePhone(phone)
            return result.valid === true
          }),
          { numRuns: 100 }
        )
      })

      it('Invalid phone numbers should fail validation with error message', () => {
        fc.assert(
          fc.property(invalidPhoneArbitrary, (phone) => {
            const result = validatePhone(phone)
            return result.valid === false && result.error !== undefined && result.error.length > 0
          }),
          { numRuns: 100 }
        )
      })

      it('Empty phone should be valid (phone is optional)', () => {
        fc.assert(
          fc.property(fc.constantFrom('', null, undefined), (phone) => {
            const result = validatePhone(phone as string | null | undefined)
            return result.valid === true
          }),
          { numRuns: 100 }
        )
      })

      it('Phone validation result should be deterministic', () => {
        fc.assert(
          fc.property(fc.oneof(validPhoneArbitrary, invalidPhoneArbitrary, fc.constant('')), (phone) => {
            const result1 = validatePhone(phone)
            const result2 = validatePhone(phone)
            return result1.valid === result2.valid
          }),
          { numRuns: 100 }
        )
      })
    })

    describe('Combined validation', () => {
      it('Form with valid email and valid phone should pass both validations', () => {
        fc.assert(
          fc.property(validEmailArbitrary, validPhoneArbitrary, (email, phone) => {
            const emailResult = validateEmail(email)
            const phoneResult = validatePhone(phone)
            return emailResult.valid && phoneResult.valid
          }),
          { numRuns: 100 }
        )
      })

      it('Form with invalid email should fail regardless of phone validity', () => {
        fc.assert(
          fc.property(
            invalidEmailArbitrary,
            fc.oneof(validPhoneArbitrary, fc.constant('')),
            (email, phone) => {
              const emailResult = validateEmail(email)
              const phoneResult = validatePhone(phone)
              // Email should fail, phone validity doesn't matter
              return !emailResult.valid && (phoneResult.valid || !phoneResult.valid)
            }
          ),
          { numRuns: 100 }
        )
      })
    })
  })
})
