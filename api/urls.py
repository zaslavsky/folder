from django.urls import path
from .views import RegisterUserView, LoginUserView, EstateListView, EstateDetailView, CreateEstateView, UpdateEstateView, DeleteEstateView, CreateBookingView, RetrieveBookingView, CreateReviewView, SearchHistoryView, VisitorsView

urlpatterns = [
    path('user/register/', RegisterUserView.as_view(), name='user-register'),
    path('user/login/', LoginUserView.as_view(), name='user-login'),
]

# Add routes for estate-related endpoints
urlpatterns += [
    path('estate/', EstateListView.as_view(), name='estate-list'),
    path('estate/<int:pk>/', EstateDetailView.as_view(), name='estate-detail'),
]

# Add routes for creating, updating, and deleting estates
urlpatterns += [
    path('estate/create/', CreateEstateView.as_view(), name='estate-create'),
    path('estate/<int:pk>/update/', UpdateEstateView.as_view(), name='estate-update'),
    path('estate/<int:pk>/delete/', DeleteEstateView.as_view(), name='estate-delete'),
]

# Add route for booking creation
urlpatterns += [
    path('booking/create/', CreateBookingView.as_view(), name='booking-create'),
]

# Add route for retrieving a booking by ID
urlpatterns += [
    path('booking/<int:pk>/', RetrieveBookingView.as_view(), name='booking-retrieve'),
]

# Add routes for reviews, history, and visitors
urlpatterns += [
    path('review/create/', CreateReviewView.as_view(), name='review-create'),
    path('history/', SearchHistoryView.as_view(), name='search-history'),
    path('visitors/', VisitorsView.as_view(), name='visitors-list'),
]
