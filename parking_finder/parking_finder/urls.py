"""
URL configuration for parking_finder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from parking_app.views import UserViewSet, LoginViewSet, ParkingViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user/register")
# router.register(r"user/logins", LoginViewSet, basename="user/login")
router.register(r"parking", ParkingViewSet, basename="parking")

schema_view = get_schema_view(
    openapi.Info(
        title="Parking Lot APIs",
        default_version="v1",
        description="Parking Lot APIs",
        contact=openapi.Contact(email="test@example.com"),
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/", include(router.urls)),
    path("api/login", LoginViewSet.as_view()),
]
