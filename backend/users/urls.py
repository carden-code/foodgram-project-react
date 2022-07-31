from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users import views  # isort:skip

router = DefaultRouter()

router.register('users', views.UserViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
