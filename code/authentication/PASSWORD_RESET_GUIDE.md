# Password Reset & Forgot Password Guide

## Overview

The Aevum Health platform provides a comprehensive password reset and management system with email-based verification, secure token handling, and multiple password management endpoints.

## 🔐 Features

- **Forgot Password**: Email-based password reset initiation
- **Token Validation**: Check if reset tokens are valid before form submission
- **Password Reset**: Secure password reset using email tokens
- **Change Password**: Authenticated users can change their passwords
- **Token Management**: Automatic token expiration and cleanup
- **Email Integration**: HTML and plain text email support

## 📋 API Endpoints

### 1. Forgot Password
**POST** `/api/authentication/forgot-password/`

Initiates the password reset process by sending an email with a reset link.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/authentication/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

---

### 2. Validate Reset Token
**GET** `/api/authentication/validate-reset-token/?token=TOKEN`

Validates if a password reset token is valid and not expired.

**Query Parameters:**
- `token` (required): The password reset token

**Response (200):**
```json
{
  "valid": true,
  "message": "Token is valid",
  "user_info": {
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

**Response (400):**
```json
{
  "valid": false,
  "error": "Invalid or expired reset token"
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/authentication/validate-reset-token/?token=YOUR_TOKEN"
```

---

### 3. Reset Password
**POST** `/api/authentication/reset-password/`

Resets the user's password using a valid token.

**Request:**
```json
{
  "token": "Bg07ekBsIatj8u2V3qOMvmljmo1dOZBIEjK_vQaSkR0",
  "new_password": "newSecurePassword123",
  "confirm_password": "newSecurePassword123"
}
```

**Response (200):**
```json
{
  "message": "Password reset successful"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/authentication/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "new_password": "newPassword123",
    "confirm_password": "newPassword123"
  }'
```

---

### 4. Change Password (Authenticated)
**POST** `/api/authentication/change-password/`

Allows authenticated users to change their password.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newSecurePassword123",
  "confirm_password": "newSecurePassword123"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/authentication/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "current_password": "oldPassword123",
    "new_password": "newPassword123",
    "confirm_password": "newPassword123"
  }'
```

## 🔧 Security Features

### Token Security
- **Unique Tokens**: Each reset token is cryptographically secure (32 bytes, URL-safe)
- **Expiration**: Tokens expire after 1 hour
- **Single Use**: Tokens are invalidated after successful password reset
- **User Isolation**: Tokens are tied to specific users

### Password Validation
- **Strength Requirements**: Uses Django's built-in password validators
- **Minimum Length**: 8 characters minimum
- **Confirmation**: Password confirmation required for all resets

### Email Security
- **HTML & Plain Text**: Supports both email formats
- **Branded Emails**: Professional email templates with Aevum branding
- **Clear Instructions**: User-friendly reset instructions

## 📧 Email Template

The password reset email includes:
- Personalized greeting
- Clear reset button/link
- Backup URL for manual copy-paste
- Expiration warning (1 hour)
- Security advice
- Professional branding

## 🛠 Frontend Integration

### Complete Password Reset Flow

```javascript
// 1. Request password reset
async function requestPasswordReset(email) {
  const response = await fetch('/api/authentication/forgot-password/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return response.json();
}

// 2. Validate token (when user clicks email link)
async function validateResetToken(token) {
  const response = await fetch(`/api/authentication/validate-reset-token/?token=${token}`);
  return response.json();
}

// 3. Reset password
async function resetPassword(token, newPassword, confirmPassword) {
  const response = await fetch('/api/authentication/reset-password/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  });
  return response.json();
}

// 4. Change password (authenticated users)
async function changePassword(currentPassword, newPassword, confirmPassword, accessToken) {
  const response = await fetch('/api/authentication/change-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  });
  return response.json();
}
```

## 🧹 Maintenance

### Cleanup Expired Tokens

Use the management command to clean up old tokens:

```bash
# Dry run to see what would be deleted
python manage.py cleanup_reset_tokens --dry-run

# Delete tokens older than 7 days (default)
python manage.py cleanup_reset_tokens

# Delete tokens older than 30 days
python manage.py cleanup_reset_tokens --days 30
```

### Cron Job Setup (Production)

Add to your crontab to run cleanup daily:
```bash
# Run cleanup daily at 2 AM
0 2 * * * /path/to/venv/bin/python /path/to/project/manage.py cleanup_reset_tokens
```

## 🚨 Error Handling

### Common Error Responses

1. **Invalid Email** (400):
   ```json
   {"error": "No account found with this email address."}
   ```

2. **Invalid Token** (400):
   ```json
   {"valid": false, "error": "Invalid or expired reset token"}
   ```

3. **Password Mismatch** (400):
   ```json
   {"error": "Validation failed", "details": {"non_field_errors": ["Passwords do not match."]}}
   ```

4. **Weak Password** (400):
   ```json
   {"error": "Validation failed", "details": {"new_password": ["This password is too short."]}}
   ```

5. **Email Sending Failed** (500):
   ```json
   {"error": "Failed to send email. Please try again later."}
   ```

## 📊 Admin Interface

Administrators can view and manage password reset tokens through the Django admin:

- **View all tokens**: Active, used, and expired tokens
- **User filtering**: Filter by username or email
- **Token validation**: See which tokens are currently valid
- **Security**: Cannot manually create tokens through admin

## 🔍 Monitoring & Logging

The system automatically logs:
- Password reset requests
- Token generation and usage
- Failed reset attempts
- Email sending status

All sensitive operations are logged for security auditing.

---

## ✅ Complete Authentication System

Your Aevum Health platform now includes:

1. **User Registration** - `/api/authentication/register/`
2. **User Login** - `/api/authentication/login/`
3. **User Logout** - `/api/authentication/logout/`
4. **Profile Management** - `/api/authentication/profile/`
5. **Profile Image Upload** - `/api/authentication/profile/image/`
6. **Forgot Password** - `/api/authentication/forgot-password/`
7. **Validate Reset Token** - `/api/authentication/validate-reset-token/`
8. **Reset Password** - `/api/authentication/reset-password/`
9. **Change Password** - `/api/authentication/change-password/`

The system is production-ready with comprehensive security, validation, and user experience features! 