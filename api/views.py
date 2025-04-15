from django.core.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.utils import extend_schema
from .models import CustomUser, Estate, Booking, Review, Visit, SearchHistory
from .serializers import (
    CustomUserSerializer, EstateSerializer, BookingSerializer,
    ReviewSerializer, VisitSerializer, SearchHistorySerializer
)

class RegisterUserView(APIView):
    """
    POST user/register:
    Create a new user with login, password, and role.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="User Registration",
        description="Create a new user with login, password, and role.",
        request=CustomUserSerializer,
        responses={201: CustomUserSerializer},
    )
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(APIView):
    """
    POST user/login:
    Authenticate user and provide JWT credentials.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="User Login",
        description="Authenticate user and provide JWT credentials.",
        request={
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
            },
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'refresh': {'type': 'string'},
                    'access': {'type': 'string'},
                },
            },
        },
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = CustomUser.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Additional views for Estate, Booking, Review, History, and Visitors

class EstateListView(generics.ListAPIView):
    """
    GET estate:
    Returns a paginated list of active estate offers. Saves filter parameters in history for authorized users.
    """
    queryset = Estate.objects.filter(is_active=True)
    serializer_class = EstateSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List Active Estates",
        description="Returns a paginated list of active estate offers.",
        responses={200: EstateSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=request.GET.dict())
        return super().list(request, *args, **kwargs)

class EstateDetailView(generics.RetrieveAPIView):
    """
    GET estate/{pk}:
    Returns a single estate record by ID.
    """
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Retrieve Estate",
        description="Returns a single estate record by ID.",
        responses={200: EstateSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CreateEstateView(generics.CreateAPIView):
    """
    POST estate:
    Create a new estate. Allowed only for landlords.
    """
    serializer_class = EstateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create Estate",
        description="Create a new estate. Allowed only for landlords.",
        request=EstateSerializer,
        responses={201: EstateSerializer},
    )
    def post(self, request, *args, **kwargs):
        if self.request.user.role != 'landlord':
            raise PermissionDenied("Only landlords can create estates.")
        return super().post(request, *args, **kwargs)

class UpdateEstateView(generics.UpdateAPIView):
    """
    PATCH estate/{pk}:
    Update an estate. Allowed only for the owner landlord.
    """
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Update Estate",
        description="Update an estate. Allowed only for the owner landlord.",
        request=EstateSerializer,
        responses={200: EstateSerializer},
    )
    def patch(self, request, *args, **kwargs):
        estate = self.get_object()
        if estate.owner != self.request.user:
            raise PermissionDenied("You are not the owner of this estate.")
        return super().patch(request, *args, **kwargs)

class DeleteEstateView(generics.DestroyAPIView):
    """
    DELETE estate/{pk}:
    Delete an estate. Allowed only for the owner landlord.
    """
    queryset = Estate.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Delete Estate",
        description="Delete an estate. Allowed only for the owner landlord.",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        estate = self.get_object()
        if estate.owner != self.request.user:
            raise PermissionDenied("You are not the owner of this estate.")
        return super().delete(request, *args, **kwargs)

class CreateBookingView(generics.CreateAPIView):
    """
    POST booking/:
    Create a booking for an estate. Allowed only for tenants.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create Booking",
        description="Create a booking for an estate. Allowed only for tenants.",
        request=BookingSerializer,
        responses={201: BookingSerializer},
    )
    def post(self, request, *args, **kwargs):
        if self.request.user.role != 'tenant':
            raise PermissionDenied("Only tenants can create bookings.")
        return super().post(request, *args, **kwargs)

class RetrieveBookingView(generics.RetrieveAPIView):
    """
    GET booking/{pk}:
    Retrieve a booking by ID. Allowed for the tenant who created the booking or the landlord of the related estate.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Retrieve Booking",
        description="Retrieve a booking by ID. Allowed for the tenant who created the booking or the landlord of the related estate.",
        responses={200: BookingSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CreateReviewView(generics.CreateAPIView):
    """
    POST review:
    Create a review for an estate. Allowed only for tenants with an approved booking and after the check-in date.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create Review",
        description="Create a review for an estate. Allowed only for tenants with an approved booking and after the check-in date.",
        request=ReviewSerializer,
        responses={201: ReviewSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class SearchHistoryView(generics.ListAPIView):
    """
    GET history:
    Retrieve the search history for the authenticated tenant.
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'tenant':
            return SearchHistory.objects.filter(user=self.request.user)
        return SearchHistory.objects.none()

class VisitorsView(generics.ListAPIView):
    """
    GET visitors:
    Retrieve all visitor records for estates owned by the landlord.
    """
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'landlord':
            return Visit.objects.filter(estate__owner=self.request.user)
        return Visit.objects.none()
