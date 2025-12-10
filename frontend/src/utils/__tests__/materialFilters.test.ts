/**
 * Property-based tests for material filtering functionality
 * Using fast-check for property-based testing
 * 
 * **Feature: student-material-center-profile, Property 1: Filter consistency**
 * **Validates: Requirements 1.2, 1.3, 1.4**
 */
import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import { 
  filterMaterials, 
  materialMatchesFilters,
  type Material, 
  type MaterialFilters 
} from '../materialFilters'

// Arbitrary generators for test data
const fileTypes = ['pdf', 'doc', 'ppt', 'xls', 'image', 'video', 'archive', 'text', 'other']

const tagArbitrary = fc.record({
  id: fc.integer({ min: 1, max: 100 }),
  name: fc.string({ minLength: 1, maxLength: 20 })
})

// Generate ISO date strings directly to avoid date conversion issues
const isoDateArbitrary = fc.tuple(
  fc.integer({ min: 2020, max: 2030 }),
  fc.integer({ min: 1, max: 12 }),
  fc.integer({ min: 1, max: 28 })
).map(([year, month, day]) => 
  `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00.000Z`
)

const materialArbitrary: fc.Arbitrary<Material> = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  title: fc.string({ minLength: 1, maxLength: 100 }),
  description: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  fileName: fc.string({ minLength: 1, maxLength: 100 }),
  fileSize: fc.integer({ min: 1, max: 100000000 }),
  fileType: fc.constantFrom(...fileTypes),
  categoryId: fc.option(fc.integer({ min: 1, max: 50 }), { nil: null }),
  courseId: fc.option(fc.integer({ min: 1, max: 50 }), { nil: null }),
  uploaderId: fc.integer({ min: 1, max: 100 }),
  downloadCount: fc.integer({ min: 0, max: 10000 }),
  viewCount: fc.integer({ min: 0, max: 10000 }),
  createdAt: isoDateArbitrary,
  updatedAt: isoDateArbitrary,
  tags: fc.option(fc.array(tagArbitrary, { minLength: 0, maxLength: 5 }), { nil: undefined }),
  keywords: fc.option(fc.string({ maxLength: 200 }), { nil: undefined })
})

const filtersArbitrary: fc.Arbitrary<MaterialFilters> = fc.record({
  categoryId: fc.option(fc.integer({ min: 1, max: 50 }), { nil: null }),
  fileType: fc.option(fc.constantFrom(...fileTypes), { nil: null }),
  courseId: fc.option(fc.integer({ min: 1, max: 50 }), { nil: null }),
  tagIds: fc.option(fc.array(fc.integer({ min: 1, max: 100 }), { minLength: 0, maxLength: 5 }), { nil: undefined })
})

describe('Material Filters - Property Tests', () => {
  /**
   * **Feature: student-material-center-profile, Property 1: Filter consistency**
   * **Validates: Requirements 1.2, 1.3, 1.4**
   * 
   * Property 1: Filter consistency
   * For any material list and any combination of filters (category, course, file type),
   * all displayed materials SHALL match ALL active filter criteria simultaneously.
   */
  it('Property 1: All filtered materials should match ALL active filter criteria', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        filtersArbitrary,
        (materials, filters) => {
          const filtered = filterMaterials(materials, filters)
          
          // Every filtered material must match all active filters
          return filtered.every(material => materialMatchesFilters(material, filters))
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Filtered results are a subset of original materials
   * The filtered list should only contain materials from the original list
   */
  it('Filtered results should be a subset of original materials', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        filtersArbitrary,
        (materials, filters) => {
          const filtered = filterMaterials(materials, filters)
          const originalIds = new Set(materials.map(m => m.id))
          
          // Every filtered material should exist in original list
          return filtered.every(material => originalIds.has(material.id))
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Empty filters return all materials
   * When no filters are active, all materials should be returned
   */
  it('Empty filters should return all materials', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        (materials) => {
          const emptyFilters: MaterialFilters = {
            categoryId: null,
            fileType: null,
            courseId: null,
            tagIds: []
          }
          
          const filtered = filterMaterials(materials, emptyFilters)
          return filtered.length === materials.length
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Category filter correctness
   * When category filter is active, all results should have matching categoryId
   */
  it('Category filter should only return materials with matching categoryId', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        fc.integer({ min: 1, max: 50 }),
        (materials, categoryId) => {
          const filters: MaterialFilters = { categoryId }
          const filtered = filterMaterials(materials, filters)
          
          return filtered.every(material => material.categoryId === categoryId)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: File type filter correctness
   * When file type filter is active, all results should have matching fileType
   */
  it('File type filter should only return materials with matching fileType', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        fc.constantFrom(...fileTypes),
        (materials, fileType) => {
          const filters: MaterialFilters = { fileType }
          const filtered = filterMaterials(materials, filters)
          
          return filtered.every(material => material.fileType === fileType)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Course filter correctness
   * When course filter is active, all results should have matching courseId
   */
  it('Course filter should only return materials with matching courseId', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        fc.integer({ min: 1, max: 50 }),
        (materials, courseId) => {
          const filters: MaterialFilters = { courseId }
          const filtered = filterMaterials(materials, filters)
          
          return filtered.every(material => material.courseId === courseId)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property: Combined filters are more restrictive
   * Adding more filters should result in equal or fewer results
   */
  it('Adding more filters should result in equal or fewer results', () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary, { minLength: 0, maxLength: 50 }),
        fc.integer({ min: 1, max: 50 }),
        fc.constantFrom(...fileTypes),
        (materials, categoryId, fileType) => {
          const categoryOnlyFilters: MaterialFilters = { categoryId }
          const combinedFilters: MaterialFilters = { categoryId, fileType }
          
          const categoryFiltered = filterMaterials(materials, categoryOnlyFilters)
          const combinedFiltered = filterMaterials(materials, combinedFilters)
          
          return combinedFiltered.length <= categoryFiltered.length
        }
      ),
      { numRuns: 100 }
    )
  })
})
