from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('root', 'Root'),
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'api_customuser'

class Estate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='estates')

    class Meta:
        db_table = 'api_estate'

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ]
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'api_booking'

class Review(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='reviews')
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_review'

class Visit(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='visits')
    visitor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='visits')
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_visit'

class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='search_history')
    query = models.TextField()
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_searchhistory'
