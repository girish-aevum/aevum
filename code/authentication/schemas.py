"""
OpenAPI Schema definitions for Authentication endpoints
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    UserRegistrationSerializer,
    ForgotPasswordSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
    ProfileImageSerializer,
    UserProfileSerializer
)

# Common response schemas
COMMON_RESPONSES = {
    'unauthorized': {
        'description': 'Unauthorized - authentication required',
        'content': {
            'application/json': {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'example': 'Authentication credentials were not provided.'}
                }
            }
        }
    },
    'validation_error': {
        'description': 'Bad request - validation errors',
        'content': {
            'application/json': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Validation failed'},
                    'details': {'type': 'object', 'example': {'field': ['Error message']}}
                }
            }
        }
    }
}

# Authentication endpoint schemas
def get_health_schema():
    return extend_schema(
        tags=['Authentication'],
        summary='Health Check',
        description='Check if the authentication service is running'
    )

def get_register_schema():
    return extend_schema(
        operation_id='register_user',
        summary='User Registration',
        description='Register a new user account with automatic profile creation',
        tags=['Authentication'],
        request=UserRegistrationSerializer,
        responses={
            201: {
                'description': 'Registration successful',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Registration successful'},
                            'user': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 1},
                                    'username': {'type': 'string', 'example': 'newuser'},
                                    'email': {'type': 'string', 'example': 'user@example.com'},
                                    'first_name': {'type': 'string', 'example': 'John'},
                                    'last_name': {'type': 'string', 'example': 'Doe'}
                                }
                            },
                            'tokens': {
                                'type': 'object',
                                'properties': {
                                    'access': {'type': 'string', 'description': 'JWT access token'},
                                    'refresh': {'type': 'string', 'description': 'JWT refresh token'}
                                }
                            }
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error']
        }
    )

def get_login_schema():
    return extend_schema(
        operation_id='login_user',
        summary='User Login',
        description='Authenticate user with username and password, returns JWT tokens',
        tags=['Authentication'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Username or email', 'example': 'testuser'},
                    'password': {'type': 'string', 'description': 'User password', 'example': 'testpass123'}
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: {
                'description': 'Login successful',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Login successful'},
                            'user': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 1},
                                    'username': {'type': 'string', 'example': 'testuser'},
                                    'email': {'type': 'string', 'example': 'test@example.com'},
                                    'first_name': {'type': 'string', 'example': 'John'},
                                    'last_name': {'type': 'string', 'example': 'Doe'}
                                }
                            },
                            'tokens': {
                                'type': 'object',
                                'properties': {
                                    'access': {'type': 'string', 'description': 'JWT access token'},
                                    'refresh': {'type': 'string', 'description': 'JWT refresh token'}
                                }
                            }
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error'],
            401: {
                'description': 'Unauthorized - invalid credentials',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string', 'example': 'Invalid credentials'}
                        }
                    }
                }
            }
        }
    )

def get_logout_schema():
    return extend_schema(
        operation_id='logout_user',
        summary='User Logout',
        description='Logout user by blacklisting the refresh token',
        tags=['Authentication'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh_token': {
                        'type': 'string',
                        'description': 'JWT refresh token to blacklist',
                        'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                    }
                },
                'required': ['refresh_token']
            }
        },
        responses={
            200: {
                'description': 'Logout successful',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Logout successful'}
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error']
        }
    )

def get_forgot_password_schema():
    return extend_schema(
        operation_id='forgot_password',
        summary='Forgot Password',
        description='Request password reset email for a user account',
        tags=['Authentication'],
        request=ForgotPasswordSerializer,
        responses={
            200: {
                'description': 'Password reset email sent successfully',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Password reset email sent successfully'}
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error']
        }
    )

def get_validate_reset_token_schema():
    return extend_schema(
        operation_id='validate_reset_token',
        summary='Validate Reset Token',
        description='Check if a password reset token is valid and not expired',
        tags=['Authentication'],
        parameters=[
            OpenApiParameter(
                name='token',
                description='Password reset token to validate',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            )
        ],
        responses={
            200: {
                'description': 'Token is valid',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'valid': {'type': 'boolean', 'example': True},
                            'message': {'type': 'string', 'example': 'Token is valid'},
                            'user_info': {
                                'type': 'object',
                                'properties': {
                                    'email': {'type': 'string', 'example': 'user@example.com'},
                                    'username': {'type': 'string', 'example': 'johndoe'}
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Token is invalid or expired',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'valid': {'type': 'boolean', 'example': False},
                            'error': {'type': 'string', 'example': 'Invalid or expired reset token'}
                        }
                    }
                }
            }
        }
    )

def get_reset_password_schema():
    return extend_schema(
        operation_id='reset_password',
        summary='Reset Password',
        description='Reset user password using the token received via email',
        tags=['Authentication'],
        request=PasswordResetSerializer,
        responses={
            200: {
                'description': 'Password reset successful',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Password reset successful'}
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error']
        }
    )

def get_change_password_schema():
    return extend_schema(
        operation_id='change_password',
        summary='Change Password',
        description='Change password for authenticated user',
        tags=['Authentication'],
        request=ChangePasswordSerializer,
        responses={
            200: {
                'description': 'Password changed successfully',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Password changed successfully'}
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error'],
            401: COMMON_RESPONSES['unauthorized']
        }
    )

def get_profile_schema():
    return extend_schema(
        tags=['Authentication'],
        operation_id='get_my_profile',
        summary='Get User Profile',
        description='Retrieve the authenticated user\'s profile information including profile image',
        responses={
            200: {
                'description': 'Profile retrieved successfully',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'profile_image': {'type': 'string', 'format': 'binary', 'description': 'Profile image file'},
                            'profile_image_url': {'type': 'string', 'format': 'uri', 'description': 'Full URL to profile image'},
                            'date_of_birth': {'type': 'string', 'format': 'date', 'example': '1990-01-01'},
                            'first_name': {'type': 'string', 'example': 'John'},
                            'last_name': {'type': 'string', 'example': 'Doe'},
                            'email': {'type': 'string', 'example': 'john@example.com'},
                            'phone_number': {'type': 'string', 'example': '+1234567890'},
                            'blood_group': {'type': 'string', 'example': 'O+'},
                        }
                    }
                }
            }
        }
    )

def get_profile_image_update_schema():
    return extend_schema(
        tags=['Authentication'],
        operation_id='update_profile_image',
        summary='Update Profile Image',
        description='Upload or update the authenticated user\'s profile image',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'profile_image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Profile image file (max 5MB, formats: JPG, PNG, GIF)'
                    }
                },
                'required': ['profile_image']
            }
        },
        responses={
            200: {
                'description': 'Profile image updated successfully',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Profile image updated successfully'},
                            'profile_image': {'type': 'string', 'example': '/media/profile_images/user_1_profile.jpg'},
                            'profile_image_url': {
                                'type': 'string',
                                'format': 'uri',
                                'example': 'http://localhost:8000/media/profile_images/user_1_profile.jpg'
                            }
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error'],
            401: COMMON_RESPONSES['unauthorized']
        }
    )

def get_profile_image_delete_schema():
    return extend_schema(
        operation_id='delete_profile_image',
        summary='Delete Profile Image',
        description='Remove the authenticated user\'s profile image',
        responses={
            200: {
                'description': 'Profile image deleted successfully',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Profile image deleted successfully'}
                        }
                    }
                }
            },
            404: {
                'description': 'No profile image found',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string', 'example': 'No profile image found'}
                        }
                    }
                }
            }
        }
    ) 