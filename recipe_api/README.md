recipe_api(Recipe API)

Overview

The Recipe API is a RESTful API designed to allow users to create, manage, and explore various recipes. It provides functionalities such as adding and retrieving recipes, leaving ratings and reviews, and saving favorite recipes. The API uses token-based authentication to ensure secure access to user-specific operations, and it is built on Django and Django REST Framework (DRF).

Key Features

Recipe Management: Users can create, view, update, and delete recipes. Each recipe includes details like a title, description, ingredients, instructions, a picture, and category (e.g., Appetizer, Main Course, Dessert).

User Ratings and Reviews: Users can rate and leave reviews on recipes. Ratings are on a scale of 1-5, and each user can review a recipe only once.

Favorites: Users can add recipes to their favorites list and view or remove them later.
Categories: Recipes can be categorized (e.g., Main Course, Dessert, Vegan), making it easier for users to filter and discover new recipes.

Authentication: The API uses token-based authentication to secure endpoints for recipe creation, rating, reviewing, and managing favorites.

Image Upload: Users can upload images for their recipes using the picture field.
Core Models

Recipe: Stores recipe details including the creator, title, description, ingredients, instructions, category, preparation and cooking time, servings, and an optional image.

RateAndReview: Stores user reviews and ratings for specific recipes.

Favorite: Stores recipes that a user has marked as favorites.

Recipe Endpoints:

GET /api/recipes/: List all recipes.
POST /api/recipes/: Create a new recipe.
GET /api/recipes/{id}/: Retrieve a specific recipe by ID.
PUT /api/recipes/{id}/: Update a recipe.
DELETE /api/recipes/{id}/: Delete a recipe.

Review and Rating Endpoints:

POST /api/reviews/: Add a review and rating for a recipe.
PUT /api/reviews/{id}/: Update a review.
DELETE /api/reviews/{id}/: Delete a review.
GET /api/recipes/{id}/reviews/: List all reviews for a specific recipe.

Favorites Endpoints:

POST /api/recipes/{id}/favorite/: Mark a recipe as a favorite.
DELETE /api/recipes/{id}/undo favorite/: Remove a recipe from favorites.
GET /api/favorites/: List all favorite recipes for the current user.

Feed Endpoints:

GET /api/FollowingFeedView/: View recipes from users the current user is following.
GET /api/FavoriteFeedView/: View all favorite recipes for the current user.
