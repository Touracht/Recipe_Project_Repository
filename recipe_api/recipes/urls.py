from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, RateAndReviewViewSet, RecipeAndReviewsListView, AddToFavoritesView, RemoveFromFavoritesView, FollowingFeedView, FavoriteFeedView

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'reviews', RateAndReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:recipe_id>/reviews/', RecipeAndReviewsListView.as_view(), name='recipe-reviews'),
    path('<int:pk>/favorite/', AddToFavoritesView.as_view(), name='favourite'),
    path('<int:pk>/undo favorite/', RemoveFromFavoritesView.as_view(), name='undo favourite'),
    path('FollowingFeedView/', FollowingFeedView.as_view(), name='FollowingFeedView'),
    path('FavoriteFeedView/', FavoriteFeedView.as_view(), name='FavoriteFeed'),
]
