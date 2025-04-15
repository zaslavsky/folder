from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Estate, Booking, Review, Visit, SearchHistory

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class EstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = [
            'id', 'title', 'description', 'location', 'price', 'is_active', 'owner'
        ]
        read_only_fields = ['owner']

    def to_representation(self, instance):
        # Customize the output representation to include the owner's ID
        representation = super().to_representation(instance)
        representation['owner'] = instance.owner.id
        return representation

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def to_representation(self, instance):
        # Customize the output representation to include the tenant's ID
        representation = super().to_representation(instance)
        representation['tenant'] = instance.tenant.id
        return representation

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def to_representation(self, instance):
        # Customize the output representation to include the reviewer's ID
        representation = super().to_representation(instance)
        representation['reviewer'] = instance.reviewer.id
        return representation

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'
