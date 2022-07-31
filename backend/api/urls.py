from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views  # isort:skip

router = DefaultRouter()


router.register('recipes',
                views.RecipeViewSet,
                basename='recipe'
                )
router.register('ingredients',
                views.IngredientViewSet,
                basename='ingredient'
                )
router.register('tags',
                views.TagViewSet,
                basename='tag'
                )
router.register('users/subscriptions',
                views.SubscriptionViewSet,
                basename='subscription'
                )
router.register(r'users/(?P<id>\d+)/subscribe',
                views.SubscribeViewSet,
                basename='subscribe'
                )


urlpatterns = [
    path('', include(router.urls)),
]
