"""
URL configuration for aevum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
from ai_companion.admin_views import get_admin_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT Auth - Commented out in favor of custom login/logout endpoints
    # path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # App URLs
    path('api/authentication/', include('authentication.urls')),
    path('api/mental-wellness/', include('mental_wellness.urls')),
    path('api/nutrition/', include('nutrition.urls')),
    path('api/healthcare/', include('healthcare.urls')),
    path('api/dna-profile/', include('dna_profile.urls')),
    path('api/ai-companion/', include('ai_companion.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/smart-journal/', include('smart_journal.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Extend admin site with custom URLs
admin.site.get_urls = lambda: (
    admin.site.get_urls() + 
    get_admin_urls(admin.site)
)
