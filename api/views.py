from django.core.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    @swagger_auto_schema(request_body=CustomUserSerializer)
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
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
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

class CreateEstateView(generics.CreateAPIView):
    """
    POST estate:
    Create a new estate. Allowed only for landlords.
    """
    serializer_class = EstateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'landlord':
            raise PermissionDenied("Only landlords can create estates.")
        serializer.save(owner=self.request.user)

class UpdateEstateView(generics.UpdateAPIView):
    """
    PATCH estate/{pk}:
    Update an estate. Allowed only for the owner landlord.
    """
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        estate = self.get_object()
        if estate.owner != self.request.user:
            raise PermissionDenied("You are not the owner of this estate.")
        serializer.save()

class DeleteEstateView(generics.DestroyAPIView):
    """
    DELETE estate/{pk}:
    Delete an estate. Allowed only for the owner landlord.
    """
    queryset = Estate.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied("You are not the owner of this estate.")
        instance.delete()

class CreateBookingView(generics.CreateAPIView):
    """
    POST booking/:
    Create a booking for an estate. Allowed only for tenants.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'tenant':
            raise PermissionDenied("Only tenants can create bookings.")
        estate = serializer.validated_data['estate']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        overlapping_bookings = Booking.objects.filter(
            estate=estate,
            status='approved',
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError("Booking dates overlap with an existing approved booking.")
        serializer.save(tenant=self.request.user)

class RetrieveBookingView(generics.RetrieveAPIView):
    """
    GET booking/{pk}:
    Retrieve a booking by ID. Allowed for the tenant who created the booking or the landlord of the related estate.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'tenant':
            return self.queryset.filter(tenant=self.request.user)
        elif self.request.user.role == 'landlord':
            return self.queryset.filter(estate__owner=self.request.user)
        return self.queryset.none()

class CreateReviewView(generics.CreateAPIView):
    """
    POST review:
    Create a review for an estate. Allowed only for tenants with an approved booking and after the check-in date.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'tenant':
            raise PermissionDenied("Only tenants can create reviews.")
        estate = serializer.validated_data['estate']
        booking = Booking.objects.filter(
            estate=estate,
            tenant=self.request.user,
            status='approved',
            check_in__lte=timezone.now()
        ).first()
        if not booking:
            raise serializers.ValidationError("You can only review estates you have booked and checked into.")
        serializer.save(tenant=self.request.user)

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
