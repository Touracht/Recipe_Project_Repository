from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import Recipe, RateAndReview, Favorite
from .serializers import RecipeSerializer, RateAndReviewSerializer, FavoriteSerializer
from rest_framework import permissions
from .paginations import RecipePagination, RateAndReviewPagination, FollowingFeedPagination, FavoriteFeedPagination
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Recipe-related CRUD operations.

    This viewset provides the ability to:
    - List all recipes (publicly accessible)
    - Retrieve a specific recipe (publicly accessible)
    - Create, update, or delete recipes (only for authenticated users)
    
    Additionally, it supports searching recipes based on various fields and filtering
    results based on cooking time, servings, or preparation time.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination

    def get_permissions(self):
        """
        Determine the permissions required for each action.

        - 'list' and 'retrieve' actions are publicly accessible.
        - All other actions (create, update, delete) require the user to be authenticated.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Handle the creation of a new recipe.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "Recipe created successfully!", "data": serializer.data}, 
                        status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Handle the update of an existing recipe.
        """
        instance = self.get_object()
        if instance.creator != request.user:
            raise PermissionDenied("You do not have permission to edit this recipe.")
        
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Recipe updated successfully!", "data": serializer.data},
                        status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Handle the deletion of a recipe.
        """
        instance = self.get_object()
        if instance.creator != request.user:
            raise PermissionDenied('You do not have permission to delete this recipe')
        
        self.perform_destroy(instance)
        return Response({"message": "Recipe deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Customize the queryset to support searching and filtering.
        """
        queryset = super().get_queryset()

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(category__icontains=search) | 
                Q(ingredients__icontains=search)
            )

        # Optional filters
        cooking_time = self.request.query_params.get('cooking_time', None)
        if cooking_time:
            queryset = queryset.filter(cooking_time__lte=cooking_time)

        servings = self.request.query_params.get('servings', None)
        if servings:
            queryset = queryset.filter(servings__gte=servings)

        preparation_time = self.request.query_params.get('preparation_time', None)
        if preparation_time:
            queryset = queryset.filter(preparation_time__lte=preparation_time)

        return queryset
    
class RecipeAndReviewsListView(generics.ListCreateAPIView):
    """
        The viewset for handling the retrieval of reviews for a specific recipe.
    """
    serializer_class = RateAndReviewSerializer

    def get_queryset(self):
        """
        This method retrieves the list of reviews for a specific recipe based on the 'recipe_id'
        from the URL.
        """
        
        recipe_id = self.kwargs['recipe_id']
        return RateAndReview.objects.filter(recipe_id=recipe_id)


class RateAndReviewViewSet(viewsets.ModelViewSet):
    """
    Viewset for handling Rating and Reviewing related CRUD operations.

    This viewset provides the ability to:
    - List all reviews (publicly accessible)
    - Retrieve a specific review (publicly accessible)
    - Create, update, or delete reviews (only for authenticated users)

    """
    queryset = RateAndReview.objects.all()
    serializer_class = RateAndReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = RateAndReviewPagination
    
    def get_permissions(self):
        """
        Determine the permissions required for each action.

        - 'list' and 'retrieve' actions are publicly accessible.
        - All other actions (create, update, delete) require the user to be authenticated.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
class AddToFavoritesView(generics.GenericAPIView):

    """
    View for handling the addition of recipes to the current user's favorites
    and returns error if one has already been added.

    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer

    def post(self, request, pk):
        recipe_to_add_to_favorites = get_object_or_404(Recipe, pk=pk)

        favorite_instance, created = Favorite.objects.get_or_create(user = request.user, recipe = recipe_to_add_to_favorites)

        if created:
            return Response({'message': 'Recipe added to favorites'}, status=status.HTTP_201_CREATED)
        else: 
            return Response({'message': 'Recipe already added to favorites'}, status=status.HTTP_400_BAD_REQUEST)
        
class RemoveFromFavoritesView(generics.GenericAPIView):
    """
    View for handling the removal of recipes from favorites
    and returns error if ones has not been added.

    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        recipe_to_remove_from_favorites = get_object_or_404(Recipe, pk=pk)

        # Delete the favorite if it exists
        deleted, _ = Favorite.objects.filter(user=request.user, recipe=recipe_to_remove_from_favorites).delete()

        if deleted == 0:
            return Response({'message': 'You have not added this recipe to favorites'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Removed recipe from favorites'}, status=status.HTTP_200_OK)
    
class FollowingFeedView(generics.GenericAPIView):
    """
        A view for handling the retrieval of recipes created by the followed users.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FollowingFeedPagination

    def get(self, request):
        user = request.user
        following_users = user.following.all()  

        #Filter recipes from followed users
        recipes = Recipe.objects.filter(creator__in=following_users).order_by('-updated_date')
        
        # Paginate the queryset
        page = self.paginate_queryset(recipes)
        if page is not None:
            serializer = RecipeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

class FavoriteFeedView(generics.GenericAPIView):
    """
        A view for handling the retrieval of recipes a current user has added to favorites.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FavoriteFeedPagination

    def get(self, request):
        user = request.user
        favorite_recipes = Favorite.objects.filter(user=user).values_list('recipe')
        
        # Filter recipes that the user has favorited
        recipes = Recipe.objects.filter(id__in=favorite_recipes).order_by('-updated_date')

        # Paginate the queryset
        page = self.paginate_queryset(recipes)
        if page is not None:
            serializer = RecipeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)



