from rest_framework.pagination import PageNumberPagination

class RecipePagination(PageNumberPagination):
    """Paginate the number of retrived recipes to a limit of 20 per page."""
    page_size = 20

class RateAndReviewPagination(PageNumberPagination):
    """Paginate the number of retrived rate and reviews to a limit of 30 per page."""
    page_size = 30

class FollowingFeedPagination(PageNumberPagination):
    """Paginate the number of retrived recipes to a limit of 20 per page."""
    page_size = 20

class FavoriteFeedPagination(PageNumberPagination):
    """Paginate the number of retrived recipes to a limit of 20 per page."""
    page_size = 20