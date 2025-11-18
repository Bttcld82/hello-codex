# Password Recovery Feature

## Overview

This feature allows users who have forgotten their password to reset it securely using a time-limited token.

## User Flow

1. **Request Password Reset**
   - User clicks "Password dimenticata?" link on the login page
   - User enters their email address
   - System generates a secure token (valid for 1 hour)
   - In production: Token link is sent via email
   - In development: Token link is displayed on screen

2. **Reset Password**
   - User clicks the reset link (or navigates to it)
   - User enters a new password (minimum 8 characters)
   - User confirms the new password
   - System validates the token and updates the password
   - User is redirected to login page with success message

3. **Login with New Password**
   - User logs in with their email and new password

## Security Features

- Tokens are generated using `secrets.token_urlsafe(32)` for cryptographic security
- Tokens expire after 1 hour
- Tokens are single-use (cleared after successful password reset)
- The system doesn't reveal whether an email exists in the database (security best practice)
- Password must be at least 8 characters long
- Password confirmation is required

## Database Schema

Two new fields have been added to the `people` table:
- `reset_token` (VARCHAR(100), nullable): Stores the password reset token
- `reset_token_expiry` (DATETIME, nullable): Stores when the token expires

## Migration

For existing databases, run the migration script:

```bash
python scripts/add_password_reset_fields.py
```

Or recreate the database:

```bash
python -m flask --app app.py init-db
```

## API Endpoints

### Request Password Reset
- **URL**: `/request-password-reset`
- **Methods**: GET, POST
- **Access**: Public (unauthenticated users only)

### Reset Password
- **URL**: `/reset-password/<token>`
- **Methods**: GET, POST
- **Access**: Public (unauthenticated users only)

## Future Enhancements

To make this production-ready, you should:

1. **Email Integration**
   - Install an email library (e.g., `flask-mail`)
   - Configure SMTP settings
   - Send reset links via email instead of displaying them

2. **Rate Limiting**
   - Implement rate limiting on password reset requests
   - Prevent abuse and brute-force attacks

3. **Logging**
   - Log password reset requests and completions
   - Monitor for suspicious activity

4. **UI Improvements**
   - Add client-side validation
   - Show password strength indicator
   - Add loading states for better UX

## Testing

Run the password recovery tests:

```bash
python -m pytest tests/test_password_recovery.py -v
```

All password recovery functionality is covered by 13 comprehensive tests.
