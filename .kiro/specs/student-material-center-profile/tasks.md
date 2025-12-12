# Implementation Plan

## Student Material Center & Profile Page

- [x] 1. Set up routing and page structure

  - [x] 1.1 Add student material center routes

    - Add routes for `/student/materials` and `/student/materials/:id` in `router/student.ts`
    - Configure route guards for student role
    - _Requirements: 1.1, 4.1_

  - [x] 1.2 Add shared profile page route

    - Add route for `/profile` accessible by all authenticated users
    - Configure in appropriate router file
    - _Requirements: 5.1_

  - [x] 1.3 Create page file structure

    - Create `pages/student/materials/MaterialCenter.vue` placeholder
    - Create `pages/student/materials/MaterialDetail.vue` placeholder
    - Create `pages/shared/profile/ProfilePage.vue` placeholder
    - _Requirements: 1.1, 5.1_

- [-] 2. Implement Student Material Center page

  - [x] 2.1 Implement MaterialCenter.vue main structure

    - Create page layout with sidebar (tags, categories) and main content area
    - Integrate existing SearchBar, CategoryTree, TagCloud, AdvancedFilter components
    - Implement material list display using existing MaterialCard component
    - Add pagination component
    - Reference teacher's MaterialCenter.vue for implementation patterns
    - _Requirements: 1.1, 1.5_

  - [x] 2.2 Write property test for filter consistency

    - **Property 1: Filter consistency**
    - **Validates: Requirements 1.2, 1.3, 1.4**

  - [x] 2.3 Implement filtering functionality

    - Connect category filter to API calls
    - Connect file type filter to API calls
    - Connect tag filter to API calls
    - Ensure filters work in combination
    - _Requirements: 1.2, 1.3, 1.4_

  - [x] 2.4 Write property test for material card display

    - **Property 2: Material card display completeness**
    - **Validates: Requirements 1.5**

  - [x] 2.5 Implement search functionality

    - Connect SearchBar to API search endpoint
    - Implement search result display
    - Implement search clear to restore full list
    - _Requirements: 2.1, 2.3_

  - [x] 2.6 Write property test for search

    - **Property 3: Search result relevance**
    - **Property 4: Search clear restoration**
    - **Validates: Requirements 2.1, 2.3**

  - [x] 2.7 Implement download functionality

    - Add download handler using materialApiIntMaterialIdDownloadGet
    - Create blob and trigger download with original filename
    - Show success/error messages
    - _Requirements: 3.1, 3.4_

  - [x] 2.8 Write property test for download

    - **Property 5: Download triggers correct API call**
    - **Validates: Requirements 3.1**

  - [x] 2.9 Implement preview functionality

    - Add preview modal using existing FilePreview component
    - Check file type for preview support (pdf, image)
    - Show download suggestion for unsupported types
    - _Requirements: 3.2, 3.3_

  - [x] 2.10 Write property test for preview

    - **Property 6: Preview availability by file type**
    - **Validates: Requirements 3.2, 3.3**

- [x] 3. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Student Material Detail page

  - [x] 4.1 Implement MaterialDetail.vue

    - Create detail page layout with material info display
    - Show full description, tags, uploader info, file metadata
    - Integrate preview modal for supported file types
    - Add download button
    - Reference teacher's MaterialDetail.vue for implementation patterns
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 4.2 Write property test for material detail

    - **Property 7: Material detail display completeness**
    - **Validates: Requirements 4.1**

  - [x] 4.3 Implement related materials section

    - Query materials with same category or tags
    - Display as card list below main content
    - _Requirements: 4.2_

- [x] 5. Implement Profile Page components

  - [x] 5.1 Create AvatarUpload component

    - Create `components/profile/AvatarUpload.vue`
    - Implement file picker limited to image types (jpg, png, gif)
    - Add file size validation (max 2MB)
    - Show preview before upload
    - Handle upload success/error
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 5.2 Write property tests for avatar upload

    - **Property 13: Avatar file size validation**
    - **Property 14: Avatar upload failure handling**
    - **Validates: Requirements 8.4, 8.5**

  - [x] 5.3 Create PasswordChangeForm component

    - Create `components/profile/PasswordChangeForm.vue`
    - Implement form with current password, new password, confirm password fields
    - Add validation rules (required, min length, match)
    - Add password strength indicator
    - Connect to authApiChangePasswordPost API
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 5.4 Write property test for password validation

    - **Property 12: Password confirmation match**
    - **Validates: Requirements 7.4**

- [x] 6. Implement Profile Page main view

  - [x] 6.1 Implement ProfilePage.vue structure

    - Create page layout with user info display section
    - Show username, real name, email, phone, role, user code
    - Show account creation date and last login time
    - Integrate AvatarUpload component
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 6.2 Write property tests for profile display

    - **Property 8: Profile display completeness**
    - **Property 9: Avatar display logic**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

  - [x] 6.3 Implement profile edit functionality

    - Add edit mode toggle
    - Create edit form for editable fields (realName, email, phone)
    - Add real-time validation for email and phone formats
    - Implement save and cancel actions
    - Connect to userApiIntUserIdPut API
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.4 Write property tests for profile edit

    - **Property 10: Profile edit cancellation restoration**
    - **Property 11: Email and phone validation**
    - **Validates: Requirements 6.4, 6.5**

  - [x] 6.5 Integrate password change modal

    - Add "Change Password" button
    - Show PasswordChangeForm in modal
    - Handle success callback
    - _Requirements: 7.1_

- [x] 7. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Add navigation and polish

  - [x] 8.1 Update StudentLayout navigation

    - Add "资料中心" menu item linking to `/student/materials`
    - Add "个人资料" menu item or header dropdown linking to `/profile`
    - _Requirements: 1.1, 5.1_

  - [x] 8.2 Add empty state handling

    - Add empty state display when no materials found
    - Add search suggestions in empty state
    - _Requirements: 2.4_

  - [ ] 8.3 Add loading states
    - Add loading spinners for API calls
    - Add skeleton loading for material cards
    - _Requirements: 1.1_

- [ ] 9. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
