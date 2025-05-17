"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.db import router
from django.urls import path

from django.conf import settings
from . import views
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs pour Action
    path('api/actions/', views.ActionListCreate.as_view(), name='action-list-create'),
    path('api/actions/<int:pk>/', views.ActionDetail.as_view(), name='action-detail'),

    # URLs pour CodeCenter
    path('api/codecenters/', views.CodeCenterListCreate.as_view(), name='codecenter-list-create'),
    path('api/codecenters/<int:pk>/', views.CodeCenterDetail.as_view(), name='codecenter-detail'),

    # URLs pour ProductImage
    path('api/productimages/', views.ProductImageListCreate.as_view(), name='productimage-list-create'),
    path('api/productimages/<int:pk>/', views.ProductImageDetail.as_view(), name='productimage-detail'),

    # URLs pour Role
    path('api/roles/', views.RoleListCreate.as_view(), name='role-list-create'),
    path('api/roles/<int:pk>/', views.RoleDetail.as_view(), name='role-detail'),

    # URLs pour User
    path('api/users/', views.UserListCreate.as_view(), name='user-list-create'),
    path('api/users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),

    # URLs pour Product
    path('api/products/', views.ProductListCreate.as_view(), name='product-list-create'),
    path('api/products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),

    # URLs pour Subscription
    path('api/subscriptions/', views.SubscriptionListCreate.as_view(), name='subscription-list-create'),
    path('api/subscriptions/<int:pk>/', views.SubscriptionDetail.as_view(), name='subscription-detail'),
    
    path('api/user-connexion/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/user-deconnexion/', views.LogoutView.as_view(), name='deconnexion'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
