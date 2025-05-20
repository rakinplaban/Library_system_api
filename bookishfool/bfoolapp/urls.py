from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/books/', BookListAPIView.as_view(), name='books'),
    path('api/books/<int:pk>', BookDetailAPIView.as_view(), name='books_details'),
    path('api/authors/', AuthorListCreateAPIView.as_view(), name='author-list-create'),
    path('api/authors/<int:pk>/', AuthorDetailAPIView.as_view(), name='author-detail'),
    path('api/categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('api/borrow/', BorrowBookAPIView.as_view(), name='borrow-book'),
    path('api/return/', ReturnBookAPIView.as_view(), name='return-book'),
    path('api/users/<int:id>/penalties/', UserPenaltyView.as_view(), name='user-penalties'),
]