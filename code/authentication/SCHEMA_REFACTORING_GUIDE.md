# Schema Refactoring Guide

## 🎯 Why Refactor OpenAPI Schemas?

### ❌ Before: Inline Schema Definitions

**Problems with inline schemas:**
- **Code duplication** across multiple views
- **Hard to maintain** - changes require updating multiple places
- **Verbose views** - business logic mixed with documentation
- **Inconsistent responses** across similar endpoints
- **Difficult to reuse** common response patterns

**Example of problematic inline schema:**
```python
@extend_schema(
    operation_id='login_user',
    summary='User Login',
    description='Authenticate user with username and password, returns JWT tokens',
    tags=['Authentication'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Username or email'},
                'password': {'type': 'string', 'description': 'User password'}
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
                                'id': {'type': 'integer'},
                                'username': {'type': 'string'},
                                'email': {'type': 'string'}
                            }
                        },
                        'tokens': {
                            'type': 'object',
                            'properties': {
                                'access': {'type': 'string'},
                                'refresh': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - validation errors',
            'content': {
                'application/json': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'},
                        'details': {'type': 'object'}
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized - invalid credentials',
            'content': {
                'application/json': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Business logic here...
```

### ✅ After: Centralized Schema Functions

**Benefits of centralized schemas:**
- **DRY Principle** - Define once, use everywhere
- **Easy maintenance** - Update in one place
- **Clean views** - Focused on business logic
- **Consistent APIs** - Reusable response patterns
- **Type safety** - Better IDE support and validation

**Example of clean refactored view:**
```python
@get_login_schema()
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Clean business logic without schema clutter
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Username and password are required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    # ... rest of logic
```

## 📁 File Structure

```
authentication/
├── views.py           # Clean business logic
├── schemas.py         # ✨ Centralized OpenAPI schemas
├── serializers.py     # Data validation
├── models.py          # Database models
└── urls.py           # URL routing
```

## 🔧 Schema Functions Architecture

### 1. Common Response Patterns

```python
# Reusable response schemas
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
```

### 2. Individual Schema Functions

```python
def get_login_schema():
    return extend_schema(
        operation_id='login_user',
        summary='User Login',
        description='Authenticate user with username and password, returns JWT tokens',
        tags=['Authentication'],
        request=LoginSerializer,  # Use serializer for request
        responses={
            200: {
                'description': 'Login successful',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'Login successful'},
                            'user': USER_RESPONSE_SCHEMA,  # Reusable user schema
                            'tokens': TOKEN_RESPONSE_SCHEMA  # Reusable token schema
                        }
                    }
                }
            },
            400: COMMON_RESPONSES['validation_error'],  # Reuse common response
            401: COMMON_RESPONSES['unauthorized']       # Reuse common response
        }
    )
```

## 🚀 Usage in Views

### Function-Based Views
```python
@get_login_schema()
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Clean business logic
    pass
```

### Class-Based Views
```python
@get_profile_schema()
class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
```

### Method-Specific Schemas
```python
class ProfileImageUpdateView(generics.UpdateAPIView):
    # ... class definition

    @get_profile_image_delete_schema()
    def delete(self, request, *args, **kwargs):
        # Method-specific schema
        pass
```

## 📊 Benefits Comparison

| Aspect | Inline Schemas | Centralized Schemas |
|--------|---------------|-------------------|
| **Maintainability** | ❌ Update multiple places | ✅ Update once |
| **Readability** | ❌ Views cluttered | ✅ Clean business logic |
| **Consistency** | ❌ Easy to diverge | ✅ Enforced consistency |
| **Reusability** | ❌ Copy-paste errors | ✅ True reusability |
| **Testing** | ❌ Hard to test schemas | ✅ Test schemas separately |
| **IDE Support** | ❌ Poor autocomplete | ✅ Better type hints |

## 🔄 Migration Strategy

### Step 1: Create schemas.py
```python
# authentication/schemas.py
def get_endpoint_schema():
    return extend_schema(
        # Move existing schema here
    )
```

### Step 2: Update views.py
```python
# Before
@extend_schema(...)
def my_view(request):
    pass

# After
from .schemas import get_endpoint_schema

@get_endpoint_schema()
def my_view(request):
    pass
```

### Step 3: Test and verify
```bash
python manage.py shell -c "from authentication.schemas import *; print('✅ Schemas imported')"
```

## 🎯 Best Practices

### 1. **Naming Convention**
```python
# ✅ Good naming
def get_login_schema():
def get_register_schema():
def get_profile_update_schema():

# ❌ Avoid
def login_docs():
def schema_for_login():
```

### 2. **Group Related Schemas**
```python
# User management schemas
def get_register_schema():
def get_login_schema():
def get_logout_schema():

# Profile management schemas
def get_profile_schema():
def get_profile_update_schema():
def get_profile_image_schema():
```

### 3. **Reuse Common Components**
```python
# Define once, use everywhere
USER_RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'username': {'type': 'string'},
        'email': {'type': 'string'}
    }
}

def get_login_schema():
    return extend_schema(
        responses={
            200: {
                'content': {
                    'application/json': {
                        'properties': {
                            'user': USER_RESPONSE_SCHEMA  # ✅ Reuse
                        }
                    }
                }
            }
        }
    )
```

## ✅ Results

After refactoring, your authentication system has:

1. **Clean Views** - Business logic is clear and focused
2. **Maintainable Schemas** - Update once, apply everywhere
3. **Consistent APIs** - All endpoints follow the same patterns
4. **Better Documentation** - Centralized and comprehensive
5. **Easier Testing** - Schema functions can be tested independently

## 🏆 Recommendations

1. **Always use schema functions** for new endpoints
2. **Gradually migrate** existing inline schemas
3. **Create common response patterns** for reuse
4. **Document schema functions** with clear docstrings
5. **Test schema functions** separately from views

This approach scales much better as your API grows and makes maintenance significantly easier! 