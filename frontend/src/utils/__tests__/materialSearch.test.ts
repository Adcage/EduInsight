/**
 * Property-based tests for material search functionality
 * Using fast-check for property-based testing
 * 
 * **Feature: student-material-center-profile, Property 3: Search result relevance**
 * **Feature: student-material-center-profile, Property 4: Search clear restoration**
 * **Validates: Requirements 2.1, 2.3**
 */
import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import {
  materialMatchesSearch,
  searchMaterials,
  searchClearRestoresOriginal,
  type Material
} from '../materialSearch'

// File types used in the system
const fileTypes = ['pdf', 'doc', 'ppt', 'xls', 'image', 'video', 'archive', 'text', 'other']

// Non-whitespace string generator
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
  keywords: fc.option(fc.string({ maxLength: 200 }), { nil: undefined }),
  categoryId: fc.option(fc.integer({ min: 1, max: 50 }), { nil: null }),
  courseId: fc.option(fc.integer({ min: 1, max: 50 }), { nil: null })
})

describe('Material Search - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 3: Search result relevance**
   * **Validates: Requirements 2.1**
   * 
   * Property 3: Search result relevance
   * For any search keyword and any list of materials, all returned results SHALL contain
   * the keyword in at least one of: title, description, or keywords field.
   */
  it('Property 3: All search results should contain the keyword in title, description, or keywords', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        nonWhitespaceString,
        (materials, keyword) => {
          const results = searchMaterials(materials, keyword)
          
          // Every result must match the search criteria
          return results.every(material => materialMatchesSearch(material, keyword))
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * **Feature: student-material-center-profile, Property 4: Search clear restoration**
   * **Validates: Requirements 2.3**
   * 
   * Property 4: Search clear restoration
   * For any material list state, after performing a search and then clearing the search input,
   * the displayed list SHALL equal the original unfiltered list.
   */
  it('Property 4: Clearing search should restore the original material list', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        nonWhitespaceString,
        (materials, keyword) => {
          return searchClearRestoresOriginal(materials, keyword)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Empty search returns all materials
   */
  it('Empty search should return all materials', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        (materials) => {
          const results = searchMaterials(materials, '')
          return results.length === materials.length
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Search results are a subset of original materials
   */
  it('Search results should be a subset of original materials', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        nonWhitespaceString,
        (materials, keyword) => {
          const results = searchMaterials(materials, keyword)
          const originalIds = new Set(materials.map(m => m.id))
          
          return results.every(material => originalIds.has(material.id))
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Search is case-insensitive
   */
  it('Search should be case-insensitive', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        nonWhitespaceString,
        (materials, keyword) => {
          const lowerResults = searchMaterials(materials, keyword.toLowerCase())
          const upperResults = searchMaterials(materials, keyword.toUpperCase())
          
          // Same number of results regardless of case
          return lowerResults.length === upperResults.length
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Material with keyword in title always matches
   */
  it('Material with keyword in title should always match', () => {
    fc.assert(
      fc.property(
        nonWhitespaceString,
        fc.string({ minLength: 0, maxLength: 50 }),
        fc.string({ minLength: 0, maxLength: 50 }),
        (keyword, prefix, suffix) => {
          const material: Material = {
            id: 1,
            title: `${prefix}${keyword}${suffix}`,
            fileName: 'test.pdf',
            fileSize: 1000,
            fileType: 'pdf'
          }
          
          return materialMatchesSearch(material, keyword)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Material with keyword in description always matches
   */
  it('Material with keyword in description should always match', () => {
    fc.assert(
      fc.property(
        nonWhitespaceString,
        fc.string({ minLength: 0, maxLength: 50 }),
        fc.string({ minLength: 0, maxLength: 50 }),
        (keyword, prefix, suffix) => {
          const material: Material = {
            id: 1,
            title: 'Test Material',
            description: `${prefix}${keyword}${suffix}`,
            fileName: 'test.pdf',
            fileSize: 1000,
            fileType: 'pdf'
          }
          
          return materialMatchesSearch(material, keyword)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Material with keyword in keywords field always matches
   */
  it('Material with keyword in keywords field should always match', () => {
    fc.assert(
      fc.property(
        nonWhitespaceString,
        fc.string({ minLength: 0, maxLength: 50 }),
        fc.string({ minLength: 0, maxLength: 50 }),
        (keyword, prefix, suffix) => {
          const material: Material = {
            id: 1,
            title: 'Test Material',
            keywords: `${prefix}${keyword}${suffix}`,
            fileName: 'test.pdf',
            fileSize: 1000,
            fileType: 'pdf'
          }
          
          return materialMatchesSearch(material, keyword)
        }
      ),
      { numRuns: 100 }
    )
  })
})
