# Design Document: Student Material Center & Profile Page

## Overview

本设计文档描述学生端资料中心和个人资料详情页面的技术实现方案。这两个功能模块基于现有的 Vue 3 + TypeScript + Ant Design Vue 前端架构，复用已有的后端 API 接口和组件，实现学生浏览学习资料和管理个人信息的功能。

### 技术栈

- **前端框架**: Vue 3 + TypeScript + Vite
- **UI 组件库**: Ant Design Vue
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: 基于 Axios 的 request 封装
- **日期处理**: dayjs

### 功能范围

1. **学生端资料中心**: 资料列表展示、分类筛选、搜索、下载、预览、详情查看
2. **个人资料页面**: 信息展示、信息编辑、密码修改、头像上传

### 复用现有组件

学生端资料中心将复用以下已有组件：

- `MaterialCard.vue` - 资料卡片组件
- `SearchBar.vue` - 搜索栏组件
- `CategoryTree.vue` - 分类树组件
- `TagCloud.vue` - 标签云组件
- `AdvancedFilter.vue` - 高级筛选组件
- `FilePreview.vue` - 文件预览组件

### 复用现有 Store

- `useMaterialStore` - 资料状态管理
- `useCategoryStore` - 分类状态管理
- `useAuthStore` - 用户认证状态管理

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                         │
├─────────────────────────────────────────────────────────────────┤
│  Pages                                                          │
│  ├── student/materials/                                         │
│  │   ├── MaterialCenter.vue      # 资料中心主页面               │
│  │   └── MaterialDetail.vue      # 资料详情页面                 │
│  └── shared/                                                    │
│      └── profile/                                               │
│          └── ProfilePage.vue     # 个人资料页面                 │
├─────────────────────────────────────────────────────────────────┤
│  Components (复用已有)                                          │
│  ├── materials/                                                 │
│  │   ├── MaterialCard.vue        # 资料卡片组件 (已存在)        │
│  │   ├── SearchBar.vue           # 搜索组件 (已存在)            │
│  │   ├── CategoryTree.vue        # 分类树组件 (已存在)          │
│  │   ├── TagCloud.vue            # 标签云组件 (已存在)          │
│  │   ├── AdvancedFilter.vue      # 高级筛选组件 (已存在)        │
│  │   └── preview/FilePreview.vue # 文件预览组件 (已存在)        │
│  └── profile/ (新建)                                            │
│      ├── ProfileInfo.vue         # 个人信息展示组件             │
│      ├── ProfileEditForm.vue     # 信息编辑表单组件             │
│      ├── PasswordChangeForm.vue  # 密码修改表单组件             │
│      └── AvatarUpload.vue        # 头像上传组件                 │
├─────────────────────────────────────────────────────────────────┤
│  Stores (Pinia) - 复用已有                                      │
│  ├── material.ts                 # 资料状态管理 (已存在)        │
│  ├── category.ts                 # 分类状态管理 (已存在)        │
│  └── auth.ts                     # 用户认证状态 (已存在)        │
├─────────────────────────────────────────────────────────────────┤
│  API Layer - 复用已有                                           │
│  ├── materialController.ts       # 资料 API (已存在)            │
│  ├── categoryController.ts       # 分类 API (已存在)            │
│  ├── authController.ts           # 认证 API (已存在)            │
│  └── userController.ts           # 用户 API (已存在)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (Flask API)                         │
│  已实现的接口:                                                   │
│  - GET /api/v1/materials              # 获取资料列表            │
│  - GET /api/v1/materials/{id}         # 获取资料详情            │
│  - GET /api/v1/materials/{id}/download # 下载资料               │
│  - GET /api/v1/materials/{id}/preview  # 预览资料               │
│  - GET /api/v1/materials/search       # 搜索资料                │
│  - GET /api/v1/auth/get_loginuser     # 获取当前用户            │
│  - POST /api/v1/auth/change-password  # 修改密码                │
│  - PUT /api/v1/users/{id}             # 更新用户信息            │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. 学生端资料中心页面 (student/materials/MaterialCenter.vue)

**职责**: 作为学生端资料中心的主页面，整合筛选、搜索、列表展示功能。参考教师端 `MaterialCenter.vue` 实现，移除上传和编辑功能。

**State**:

```typescript
interface MaterialCenterState {
  materials: Material[]; // 资料列表
  loading: boolean; // 加载状态
  searchKeyword: string; // 搜索关键词
  selectedTags: number[]; // 选中的标签
  total: number; // 总数
  filters: {
    categoryId: number | null;
    fileType: string | null;
    sortBy: string;
    order: string;
    courseId: number | null;
    dateRange: any;
  };
  pagination: {
    page: number;
    pageSize: number;
  };
}
```

**API 调用方式** (参考教师端):

```typescript
import {
  materialApiGet,
  materialApiIntMaterialIdDownloadGet,
} from "@/api/materialController";
import { useMaterialStore } from "@/stores/material";
import { useCategoryStore } from "@/stores/category";

// 加载资料列表
const loadMaterials = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      sort_by: filters.sortBy,
      order: filters.order,
    };
    if (searchKeyword.value) params.search = searchKeyword.value;
    if (filters.categoryId) params.category_id = filters.categoryId;
    if (filters.fileType) params.file_type = filters.fileType;
    if (selectedTags.value.length > 0)
      params.tag_ids = selectedTags.value.join(",");

    const response = await materialApiGet(params);
    const data = (response as any).data?.data || (response as any).data;
    materials.value = data?.materials || [];
    total.value = data?.total || 0;
  } catch (error: any) {
    message.error(error.message || "加载资料列表失败");
  } finally {
    loading.value = false;
  }
};

// 下载资料
const handleDownload = async (material: any) => {
  try {
    const response = await materialApiIntMaterialIdDownloadGet(
      { materialId: material.id },
      { responseType: "blob" }
    );
    const blob = new Blob([response]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", material.fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    message.success("下载成功");
  } catch (error: any) {
    message.error(error.message || "下载失败");
  }
};
```

### 2. 学生端资料详情页面 (student/materials/MaterialDetail.vue)

**职责**: 展示资料详细信息，提供预览和下载功能。参考教师端 `MaterialDetail.vue` 实现，移除编辑和删除功能。

**State**:

```typescript
interface MaterialDetailState {
  material: Material | null;
  loading: boolean;
  previewModalVisible: boolean;
  keywords: KeywordResponseModel[];
  keywordsLoading: boolean;
}
```

**API 调用方式**:

```typescript
import { useMaterialStore } from "@/stores/material";

const materialStore = useMaterialStore();

// 加载资料详情
const loadMaterialDetail = async () => {
  try {
    await materialStore.fetchMaterialDetail(materialId.value);
    loadKeywords();
  } catch (error: any) {
    message.error(error.message || "加载资料详情失败");
  }
};
```

### 3. 个人资料页面 (shared/profile/ProfilePage.vue)

**职责**: 展示和管理用户个人信息，支持编辑、修改密码、上传头像

**State**:

```typescript
interface ProfilePageState {
  userInfo: UserProfile | null;
  isEditing: boolean;
  editForm: {
    realName: string;
    email: string;
    phone: string;
  };
  loading: boolean;
  avatarUploading: boolean;
  passwordModalVisible: boolean;
}
```

**API 调用方式**:

```typescript
import { useAuthStore } from "@/stores/auth";
import {
  authApiChangePasswordPost,
  authApiGetLoginuserGet,
} from "@/api/authController";
import { userApiIntUserIdPut } from "@/api/userController";

const authStore = useAuthStore();

// 获取用户信息
const loadUserInfo = async () => {
  try {
    await authStore.fetchCurrentUser();
    userInfo.value = authStore.user;
  } catch (error: any) {
    message.error("获取用户信息失败");
  }
};

// 更新用户信息
const handleUpdateProfile = async () => {
  try {
    await userApiIntUserIdPut(
      { userId: userInfo.value.id },
      {
        realName: editForm.realName,
        email: editForm.email,
        phone: editForm.phone,
      }
    );
    await authStore.fetchCurrentUser();
    message.success("更新成功");
    isEditing.value = false;
  } catch (error: any) {
    message.error(error.message || "更新失败");
  }
};

// 修改密码
const handleChangePassword = async (values: PasswordChangeRequest) => {
  try {
    await authApiChangePasswordPost({
      oldPassword: values.currentPassword,
      newPassword: values.newPassword,
    });
    message.success("密码修改成功");
    passwordModalVisible.value = false;
  } catch (error: any) {
    message.error(error.message || "密码修改失败");
  }
};
```

### 4. 密码修改表单组件 (profile/PasswordChangeForm.vue)

**职责**: 处理密码修改的表单验证和提交

**Props**:

```typescript
interface PasswordChangeFormProps {
  visible: boolean;
}
```

**Events**:

- `@update:visible`: 弹窗可见性更新
- `@success`: 密码修改成功

**表单验证规则**:

```typescript
const rules = {
  currentPassword: [{ required: true, message: "请输入当前密码" }],
  newPassword: [
    { required: true, message: "请输入新密码" },
    { min: 6, message: "密码长度不能少于6位" },
  ],
  confirmPassword: [
    { required: true, message: "请确认新密码" },
    { validator: validateConfirmPassword },
  ],
};
```

### 5. 头像上传组件 (profile/AvatarUpload.vue)

**职责**: 处理头像图片的选择、预览和上传

**Props**:

```typescript
interface AvatarUploadProps {
  currentAvatar: string | null;
  maxSize?: number; // 最大文件大小，默认 2MB
}
```

**Events**:

- `@upload-success`: 上传成功，返回新头像 URL
- `@upload-error`: 上传失败

## Data Models

### Material (资料) - 复用已有

```typescript
interface Material {
  id: number;
  title: string;
  description?: string;
  fileName: string;
  filePath: string;
  fileSize: number;
  fileType: string;
  courseId?: number;
  uploaderId: number;
  categoryId?: number;
  downloadCount: number;
  viewCount: number;
  keywords?: string;
  createdAt: string;
  updatedAt: string;
  category?: { id: number; name: string };
  uploader?: { id: number; realName: string };
  tags?: Array<{ id: number; name: string }>;
}
```

### UserProfile (用户资料) - 复用已有

```typescript
interface UserProfile {
  id: number;
  username: string;
  userCode: string;
  email: string;
  phone: string | null;
  realName: string;
  avatar: string | null;
  role: "admin" | "teacher" | "student";
  classId: number | null;
  status: boolean;
  createdAt: string;
  updatedAt: string;
  lastLoginTime: string | null;
}
```

### PasswordChangeRequest

```typescript
interface PasswordChangeRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

Based on the prework analysis, the following correctness properties have been identified:

### Property 1: Filter consistency

_For any_ material list and any combination of filters (category, course, file type), all displayed materials SHALL match ALL active filter criteria simultaneously.
**Validates: Requirements 1.2, 1.3, 1.4**

### Property 2: Material card display completeness

_For any_ material in the list, the rendered card SHALL contain the material title, file type indicator, file size, upload date, and download count.
**Validates: Requirements 1.5**

### Property 3: Search result relevance

_For any_ search keyword and any list of materials, all returned results SHALL contain the keyword in at least one of: title, description, or keywords field.
**Validates: Requirements 2.1**

### Property 4: Search clear restoration

_For any_ material list state, after performing a search and then clearing the search input, the displayed list SHALL equal the original unfiltered list.
**Validates: Requirements 2.3**

### Property 5: Download triggers correct API call

_For any_ material, clicking the download button SHALL initiate a download request with the correct material ID and the downloaded file SHALL have the original filename.
**Validates: Requirements 3.1**

### Property 6: Preview availability by file type

_For any_ material with file type 'pdf' or 'image', the preview button SHALL be enabled; for other file types, the preview button SHALL be disabled or show a download suggestion.
**Validates: Requirements 3.2, 3.3**

### Property 7: Material detail display completeness

_For any_ material, the detail view SHALL display the full description, all associated tags, uploader information, and complete file metadata.
**Validates: Requirements 4.1**

### Property 8: Profile display completeness

_For any_ user profile, the profile page SHALL display username, real name, email, phone, role, user code, account creation date, and last login time.
**Validates: Requirements 5.1, 5.4**

### Property 9: Avatar display logic

_For any_ user with a non-null avatar field, the profile page SHALL display that avatar image; for users with null avatar, a default placeholder SHALL be displayed.
**Validates: Requirements 5.2, 5.3**

### Property 10: Profile edit cancellation restoration

_For any_ profile edit session, canceling the edit SHALL restore all form fields to their original values before editing began.
**Validates: Requirements 6.4**

### Property 11: Email and phone validation

_For any_ email input, the validation SHALL accept only strings matching standard email format; for any phone input, the validation SHALL accept only valid phone number formats.
**Validates: Requirements 6.5**

### Property 12: Password confirmation match

_For any_ password change form submission, if the new password and confirmation password do not match exactly, the form SHALL display a mismatch error and prevent submission.
**Validates: Requirements 7.4**

### Property 13: Avatar file size validation

_For any_ selected image file, if the file size exceeds 2MB, the upload SHALL be rejected with a file size error message.
**Validates: Requirements 8.4**

### Property 14: Avatar upload failure handling

_For any_ failed avatar upload attempt, the error message SHALL be displayed and the previously displayed avatar SHALL remain unchanged.
**Validates: Requirements 8.5**

## Error Handling

### API Error Handling

所有 API 调用使用统一的错误处理模式：

```typescript
try {
  const response = await apiCall(params);
  // 处理成功响应
} catch (error: any) {
  console.error("操作失败:", error);
  message.error(error.message || "操作失败，请稍后重试");
}
```

### 表单验证错误

- 实时验证：输入时即时显示验证错误
- 提交验证：提交前进行完整表单验证
- 错误提示：在对应字段下方显示具体错误信息

### 网络错误

- 显示友好的错误提示
- 提供重试选项
- 保持用户已输入的数据

### 文件操作错误

- 下载失败：显示错误提示，建议稍后重试
- 预览失败：显示错误提示，提供下载替代方案
- 上传失败：显示具体错误原因，保留已选择的文件

## Testing Strategy

### 单元测试 (Vitest)

- 测试工具函数：文件大小格式化、日期格式化、文件类型判断
- 测试表单验证规则：邮箱格式、手机号格式、密码强度
- 测试组件 props 和 events

### 属性测试 (fast-check)

使用 fast-check 库进行属性测试，验证上述正确性属性：

```typescript
import fc from "fast-check";
import { describe, it, expect } from "vitest";

// Property 1: Filter consistency
describe("Filter consistency", () => {
  it("filtered materials should match all active filters", () => {
    fc.assert(
      fc.property(
        fc.array(materialArbitrary),
        fc.option(fc.integer()), // categoryId
        fc.option(fc.string()), // fileType
        (materials, categoryId, fileType) => {
          const filtered = filterMaterials(materials, { categoryId, fileType });
          return filtered.every(
            (m) =>
              (!categoryId || m.categoryId === categoryId) &&
              (!fileType || m.fileType === fileType)
          );
        }
      )
    );
  });
});
```

### 测试覆盖范围

1. **资料中心页面**

   - 资料列表加载和分页
   - 筛选功能
   - 搜索功能
   - 下载和预览功能

2. **个人资料页面**
   - 用户信息展示
   - 编辑功能
   - 密码修改
   - 头像上传

### 属性测试标注格式

每个属性测试必须使用以下格式标注：

```typescript
/**
 * **Feature: student-material-center-profile, Property 1: Filter consistency**
 * **Validates: Requirements 1.2, 1.3, 1.4**
 */
```
