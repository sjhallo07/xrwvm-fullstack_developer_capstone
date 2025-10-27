from django.urls import path
from .dealerships import proxy_views

urlpatterns = [
    path("api/dealers/", proxy_views.fetch_dealers, name="api_dealers"),
    path("api/dealer/<int:dealer_id>/", proxy_views.fetch_dealer_by_id, name="api_dealer_by_id"),
    path("api/reviews/dealer/<int:dealer_id>/", proxy_views.fetch_reviews_for_dealer, name="api_reviews_by_dealer"),
    path("api/review/add/", proxy_views.insert_review, name="api_insert_review"),
]
