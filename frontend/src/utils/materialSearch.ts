/**
 * Material search utility functions
 * These functions are extracted for testability
 */

export interface Material {
  id: number
  title: string
  description?: string
  fileName: string
  fileSize: number
  fileType: string
  keywords?: string
  categoryId?: number | null
  courseId?: number | null
}

/**
 * Check if a material matches a search keyword
 * Property 3: Search result relevance
 * For any search keyword and any list of materials, all returned results SHALL contain
 * the keyword in at least one of: title, description, or keywords field.
 * 
 * @param material - Material to check
 * @param keyword - Search keyword (case-insensitive)
 * @returns true if material matches the keyword
 */
export function materialMatchesSearch(material: Material, keyword: string): boolean {
  if (!keyword || keyword.trim() === '') {
    return true // Empty search matches all
  }
  
  const searchTerm = keyword.toLowerCase().trim()
  
  // Check title
  if (material.title && material.title.toLowerCase().includes(searchTerm)) {
    return true
  }
  
  // Check description
  if (material.description && material.description.toLowerCase().includes(searchTerm)) {
    return true
  }
  
  // Check keywords
  if (material.keywords && material.keywords.toLowerCase().includes(searchTerm)) {
    return true
  }
  
  return false
}

/**
 * Search materials by keyword
 * @param materials - Array of materials to search
 * @param keyword - Search keyword
 * @returns Filtered array of materials matching the keyword
 */
export function searchMaterials(materials: Material[], keyword: string): Material[] {
  if (!keyword || keyword.trim() === '') {
    return materials // Return all materials for empty search
  }
  
  return materials.filter(material => materialMatchesSearch(material, keyword))
}

/**
 * Simulate search clear restoration
 * Property 4: Search clear restoration
 * For any material list state, after performing a search and then clearing the search input,
 * the displayed list SHALL equal the original unfiltered list.
 * 
 * @param originalMaterials - Original list of materials
 * @param keyword - Search keyword to apply then clear
 * @returns true if clearing search restores original list
 */
export function searchClearRestoresOriginal(originalMaterials: Material[], keyword: string): boolean {
  // Perform search
  const searchResults = searchMaterials(originalMaterials, keyword)
  
  // Clear search (empty keyword)
  const clearedResults = searchMaterials(originalMaterials, '')
  
  // Verify cleared results equal original
  if (clearedResults.length !== originalMaterials.length) {
    return false
  }
  
  // Check all original materials are present
  const clearedIds = new Set(clearedResults.map(m => m.id))
  return originalMaterials.every(m => clearedIds.has(m.id))
}
