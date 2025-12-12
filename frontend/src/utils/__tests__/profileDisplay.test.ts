/**
 * Property-based tests for profile display functionality
 * Using fast-check for property-based testing
 *
 * **Feature: student-material-center-profile, Property 8: Profile display completeness**
 * **Feature: student-material-center-profile, Property 9: Avatar display logic**
 * **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
 */
import {describe, it} from 'vitest'
import fc from 'fast-check'
import {
    formatRoleDisplay,
    getAvatarDisplayUrl,
    isProfileDisplayComplete,
    type ProfileDisplayData,
    shouldShowDefaultAvatar,
} from '../profileValidation'

/**
 * Arbitrary for generating valid profile display data
 */
const validProfileArbitrary: fc.Arbitrary<ProfileDisplayData> = fc.record({
    username: fc.stringMatching(/^[a-zA-Z0-9]{1,20}$/),
    realName: fc.stringMatching(/^[a-zA-Z\u4e00-\u9fa5]{1,10}$/),
    email: fc.constant('test@example.com'),
    phone: fc.option(fc.constant('13800138000'), {nil: null}),
    role: fc.constantFrom('admin', 'teacher', 'student'),
    userCode: fc.stringMatching(/^[A-Z0-9]{4,10}$/),
    createdAt: fc.constant('2024-01-01T00:00:00.000Z'),
    lastLoginTime: fc.option(fc.constant('2024-06-01T12:00:00.000Z'), {nil: null}),
    avatar: fc.option(fc.constant('https://example.com/avatar.jpg'), {nil: null}),
})

/**
 * Arbitrary for generating incomplete profile data (missing required fields)
 */
const incompleteProfileArbitrary: fc.Arbitrary<ProfileDisplayData> = fc.oneof(
    // Missing username
    fc.record({
        username: fc.constant(''),
        realName: fc.constant('Test User'),
        email: fc.constant('test@example.com'),
        phone: fc.constant(null),
        role: fc.constantFrom('admin', 'teacher', 'student'),
        userCode: fc.constant('U001'),
        createdAt: fc.constant('2024-01-01T00:00:00.000Z'),
        lastLoginTime: fc.constant(null),
        avatar: fc.constant(null),
    }),
    // Missing realName
    fc.record({
        username: fc.constant('testuser'),
        realName: fc.constant(''),
        email: fc.constant('test@example.com'),
        phone: fc.constant(null),
        role: fc.constantFrom('admin', 'teacher', 'student'),
        userCode: fc.constant('U001'),
        createdAt: fc.constant('2024-01-01T00:00:00.000Z'),
        lastLoginTime: fc.constant(null),
        avatar: fc.constant(null),
    }),
    // Missing email
    fc.record({
        username: fc.constant('testuser'),
        realName: fc.constant('Test User'),
        email: fc.constant(''),
        phone: fc.constant(null),
        role: fc.constantFrom('admin', 'teacher', 'student'),
        userCode: fc.constant('U001'),
        createdAt: fc.constant('2024-01-01T00:00:00.000Z'),
        lastLoginTime: fc.constant(null),
        avatar: fc.constant(null),
    }),
    // Missing role
    fc.record({
        username: fc.constant('testuser'),
        realName: fc.constant('Test User'),
        email: fc.constant('test@example.com'),
        phone: fc.constant(null),
        role: fc.constant(''),
        userCode: fc.constant('U001'),
        createdAt: fc.constant('2024-01-01T00:00:00.000Z'),
        lastLoginTime: fc.constant(null),
        avatar: fc.constant(null),
    }),
    // Missing userCode
    fc.record({
        username: fc.constant('testuser'),
        realName: fc.constant('Test User'),
        email: fc.constant('test@example.com'),
        phone: fc.constant(null),
        role: fc.constantFrom('admin', 'teacher', 'student'),
        userCode: fc.constant(''),
        createdAt: fc.constant('2024-01-01T00:00:00.000Z'),
        lastLoginTime: fc.constant(null),
        avatar: fc.constant(null),
    }),
    // Missing createdAt
    fc.record({
        username: fc.constant('testuser'),
        realName: fc.constant('Test User'),
        email: fc.constant('test@example.com'),
        phone: fc.constant(null),
        role: fc.constantFrom('admin', 'teacher', 'student'),
        userCode: fc.constant('U001'),
        createdAt: fc.constant(''),
        lastLoginTime: fc.constant(null),
        avatar: fc.constant(null),
    })
)

/**
 * Arbitrary for generating avatar URLs (non-null, non-empty)
 */
const validAvatarArbitrary = fc.constantFrom(
    'https://example.com/avatar1.jpg',
    'https://example.com/avatar2.png',
    'https://cdn.test.com/user/photo.gif',
    'http://localhost:3000/images/avatar.jpg'
)

/**
 * Arbitrary for generating null/empty avatar values
 */
const nullAvatarArbitrary = fc.oneof(
    fc.constant(null),
    fc.constant(undefined),
    fc.constant(''),
    fc.constant('   ')
)

describe('Profile Display - Property Tests', () => {
    /**
     * **Feature: student-material-center-profile, Property 8: Profile display completeness**
     * **Validates: Requirements 5.1, 5.4**
     *
     * Property 8: Profile display completeness
     * For any user profile, the profile page SHALL display username, real name, email,
     * phone, role, user code, account creation date, and last login time.
     */
    describe('Property 8: Profile display completeness', () => {
        it('Complete profiles should pass completeness check', () => {
            fc.assert(
                fc.property(validProfileArbitrary, (profile) => {
                    return isProfileDisplayComplete(profile)
                }),
                {numRuns: 100}
            )
        })

        it('Incomplete profiles should fail completeness check', () => {
            fc.assert(
                fc.property(incompleteProfileArbitrary, (profile) => {
                    return !isProfileDisplayComplete(profile)
                }),
                {numRuns: 100}
            )
        })

        it('Null profile should fail completeness check', () => {
            fc.assert(
                fc.property(fc.constant(null), (profile) => {
                    return !isProfileDisplayComplete(profile)
                }),
                {numRuns: 10}
            )
        })

        it('Profile with all required fields should be complete regardless of optional fields', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('user1', 'user2', 'admin'),
                    fc.constantFrom('张三', 'John', 'Test'),
                    fc.constant('test@example.com'),
                    fc.constantFrom('admin', 'teacher', 'student'),
                    fc.constantFrom('U001', 'T002', 'S003'),
                    fc.constant('2024-01-01T00:00:00.000Z'),
                    fc.option(fc.constant('13800138000'), {nil: null}), // phone (optional)
                    fc.option(fc.constant('2024-06-01T12:00:00.000Z'), {nil: null}), // lastLoginTime (optional)
                    fc.option(fc.constant('https://example.com/avatar.jpg'), {nil: null}), // avatar (optional)
                    (username, realName, email, role, userCode, createdAt, phone, lastLoginTime, avatar) => {
                        const profile: ProfileDisplayData = {
                            username,
                            realName,
                            email,
                            phone,
                            role,
                            userCode,
                            createdAt,
                            lastLoginTime,
                            avatar,
                        }
                        return isProfileDisplayComplete(profile)
                    }
                ),
                {numRuns: 100}
            )
        })
    })

    /**
     * **Feature: student-material-center-profile, Property 9: Avatar display logic**
     * **Validates: Requirements 5.2, 5.3**
     *
     * Property 9: Avatar display logic
     * For any user with a non-null avatar field, the profile page SHALL display that avatar image;
     * for users with null avatar, a default placeholder SHALL be displayed.
     */
    describe('Property 9: Avatar display logic', () => {
        it('Non-null avatar should return the avatar URL', () => {
            fc.assert(
                fc.property(validAvatarArbitrary, (avatar) => {
                    const result = getAvatarDisplayUrl(avatar)
                    return result === avatar
                }),
                {numRuns: 100}
            )
        })

        it('Null/empty avatar should return null for default display', () => {
            fc.assert(
                fc.property(nullAvatarArbitrary, (avatar) => {
                    const result = getAvatarDisplayUrl(avatar as string | null | undefined)
                    return result === null
                }),
                {numRuns: 100}
            )
        })

        it('shouldShowDefaultAvatar returns true for null/empty avatars', () => {
            fc.assert(
                fc.property(nullAvatarArbitrary, (avatar) => {
                    return shouldShowDefaultAvatar(avatar as string | null | undefined)
                }),
                {numRuns: 100}
            )
        })

        it('shouldShowDefaultAvatar returns false for valid avatar URLs', () => {
            fc.assert(
                fc.property(validAvatarArbitrary, (avatar) => {
                    return !shouldShowDefaultAvatar(avatar)
                }),
                {numRuns: 100}
            )
        })

        it('Avatar display logic is consistent: getAvatarDisplayUrl and shouldShowDefaultAvatar are inverses', () => {
            fc.assert(
                fc.property(
                    fc.oneof(validAvatarArbitrary, nullAvatarArbitrary.map((v) => v as string | null)),
                    (avatar) => {
                        const displayUrl = getAvatarDisplayUrl(avatar)
                        const showDefault = shouldShowDefaultAvatar(avatar)
                        // If displayUrl is null, showDefault should be true, and vice versa
                        return (displayUrl === null) === showDefault
                    }
                ),
                {numRuns: 100}
            )
        })
    })

    /**
     * Additional property tests for role display formatting
     */
    describe('Role display formatting', () => {
        it('Known roles should be formatted to Chinese', () => {
            fc.assert(
                fc.property(fc.constantFrom('admin', 'teacher', 'student', 'Admin', 'Teacher', 'Student'), (role) => {
                    const formatted = formatRoleDisplay(role)
                    return ['管理员', '教师', '学生'].includes(formatted)
                }),
                {numRuns: 100}
            )
        })

        it('Unknown roles should return the original value', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('manager', 'guest', 'superuser', 'moderator', 'unknown'),
                    (role) => {
                        const formatted = formatRoleDisplay(role)
                        return formatted === role
                    }
                ),
                {numRuns: 100}
            )
        })
    })
})
