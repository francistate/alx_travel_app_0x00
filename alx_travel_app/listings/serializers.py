from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    full_name = serializers.CharField(read_only=True, source='get_full_name')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model
    """
    reviewer = UserSerializer(read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'reviewer', 'reviewer_name', 'rating', 
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """
        Custom validation for rating
        """
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate_comment(self, value):
        """
        Custom validation for comment
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long")
        return value.strip()


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model with nested reviews
    """
    host = UserSerializer(read_only=True)
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'description', 'location', 'price_per_night',
            'property_type', 'max_guests', 'bedrooms', 'bathrooms', 'host', 
            'host_name', 'has_wifi', 'has_parking', 'has_kitchen', 'has_pool', 
            'allows_pets', 'is_available', 'reviews', 'average_rating', 
            'total_reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']
    
    def validate_price_per_night(self, value):
        """
        Custom validation for price
        """
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0")
        if value > 10000:
            raise serializers.ValidationError("Price per night cannot exceed $10,000")
        return value
    
    def validate_max_guests(self, value):
        """
        Custom validation for max guests
        """
        if not 1 <= value <= 20:
            raise serializers.ValidationError("Max guests must be between 1 and 20")
        return value
    
    def create(self, validated_data):
        """
        Create listing with current user as host
        """
        validated_data['host'] = self.context['request'].user
        return super().create(validated_data)


class ListingListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing lists (without reviews)
    """
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'location', 'price_per_night', 'property_type',
            'max_guests', 'bedrooms', 'bathrooms', 'host_name', 'average_rating',
            'total_reviews', 'is_available', 'created_at'
        ]


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model with nested listing and guest info
    """
    listing = ListingListSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True, required=True)
    guest = UserSerializer(read_only=True)
    guest_name = serializers.CharField(source='guest.get_full_name', read_only=True)
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_id', 'guest', 'guest_name',
            'check_in_date', 'check_out_date', 'number_of_guests', 
            'total_price', 'status', 'special_requests', 'duration_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['booking_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Custom validation for booking dates and availability
        """
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        listing_id = data.get('listing_id')
        number_of_guests = data.get('number_of_guests')
        
        # validate dates
        if check_out <= check_in:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        # validate listing exists and is available
        try:
            listing = Listing.objects.get(listing_id=listing_id)
            if not listing.is_available:
                raise serializers.ValidationError("This listing is not available for booking")
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Invalid listing ID")
        
        # Validate guest capacity
        if number_of_guests > listing.max_guests:
            raise serializers.ValidationError(
                f"Number of guests ({number_of_guests}) exceeds listing capacity ({listing.max_guests})"
            )
        
        # check for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            listing=listing,
            status__in=['confirmed', 'pending'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        
        if self.instance:
            # exclude current booking when updating
            conflicting_bookings = conflicting_bookings.exclude(booking_id=self.instance.booking_id)
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError("These dates are not available for booking")
        
        return data
    
    def create(self, validated_data):
        """
        Create booking with current user as guest and calculate total price
        """
        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(listing_id=listing_id)
        
        # calculate total price
        duration = (validated_data['check_out_date'] - validated_data['check_in_date']).days
        total_price = listing.price_per_night * duration
        
        validated_data['listing'] = listing
        validated_data['guest'] = self.context['request'].user
        validated_data['total_price'] = total_price
        
        return super().create(validated_data)


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating bookings
    """
    guest = UserSerializer(read_only=True)
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'guest', 'check_in_date', 'check_out_date',
            'number_of_guests', 'total_price', 'status', 'special_requests',
            'duration_days', 'created_at'
        ]
        read_only_fields = ['booking_id', 'guest', 'total_price', 'created_at']
    
    def validate_number_of_guests(self, value):
        """
        Custom validation for number of guests
        """
        if value <= 0:
            raise serializers.ValidationError("Number of guests must be greater than 0")
        return value
    
    def create(self, validated_data):
        """
        Create booking with auto-calculated total price
        """
        # calculate total price based on listing price and duration
        listing = validated_data['listing']
        duration = (validated_data['check_out_date'] - validated_data['check_in_date']).days
        validated_data['total_price'] = listing.price_per_night * duration
        validated_data['guest'] = self.context['request'].user
        
        return super().create(validated_data)