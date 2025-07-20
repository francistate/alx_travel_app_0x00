import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Listing(models.Model):
    """
    Model representing a travel listing/property
    """
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('hotel', 'Hotel'),
        ('villa', 'Villa'),
        ('cabin', 'Cabin'),
        ('other', 'Other'),
    ]
    
    listing_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    location = models.CharField(max_length=200, null=False, blank=False)
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment'
    )
    
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        default=1
    )
    
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    
    # Host (Owner of the listing)
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    
    # additional amenities
    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    allows_pets = models.BooleanField(default=False)
    
    # availability
    is_available = models.BooleanField(default=True)
    
    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'listings_listing'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['is_available']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def total_reviews(self):
        """Get total number of reviews"""
        return self.reviews.count()


class Booking(models.Model):
    """
    Model representing a booking for a listing
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # relationships
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # booking details
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    
    # pricing
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # special requests
    special_requests = models.TextField(blank=True, null=True)
    
    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'listings_booking'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date']),
            models.Index(fields=['check_out_date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.listing.title}"
    
    @property
    def duration_days(self):
        """Calculate booking duration in days"""
        return (self.check_out_date - self.check_in_date).days
    
    def clean(self):
        """Custom validation"""
        
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Check-out date must be after check-in date")
        
        if self.number_of_guests > self.listing.max_guests:
            raise ValidationError(
                f"Number of guests ({self.number_of_guests}) exceeds listing capacity ({self.listing.max_guests})"
            )


class Review(models.Model):
    """
    Model representing a review for a listing
    """
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # relationships
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Optional: Link to booking (only guests who booked can review)
    booking = models.OneToOneField(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review'
    )
    
    # review content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    comment = models.TextField()
    
    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'listings_review'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
        # ensure one review per user per listing
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'reviewer'],
                name='unique_review_per_user_per_listing'
            )
        ]
    
    def __str__(self):
        return f"Review by {self.reviewer.username} - {self.rating}/5 stars"