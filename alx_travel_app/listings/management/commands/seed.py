import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    """
    Management command to seed the database with sample data
    """
    help = 'Seed the database with sample listings, bookings, and reviews'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=50,
            help='Number of bookings to create (default: 50)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=30,
            help='Number of reviews to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('Clearing existing data...')
            )
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            # Keep users, just clear travel-related data
        
        self.stdout.write(
            self.style.SUCCESS('Starting database seeding...')
        )
        
        # Create sample users if they don't exist
        users = self.create_sample_users()
        
        # Create sample listings
        listings = self.create_sample_listings(users, options['listings'])
        
        # Create sample bookings
        bookings = self.create_sample_bookings(users, listings, options['bookings'])
        
        # Create sample reviews
        self.create_sample_reviews(users, listings, bookings, options['reviews'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(listings)} listings\n'
                f'- {len(bookings)} bookings\n'
                f'- {options["reviews"]} reviews'
            )
        )
    
    def create_sample_users(self):
        """Create sample users if they don't exist"""
        sample_users_data = [
            {'username': 'john_host', 'first_name': 'John', 'last_name': 'Smith', 'email': 'john@example.com'},
            {'username': 'jane_host', 'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane@example.com'},
            {'username': 'mike_traveler', 'first_name': 'Mike', 'last_name': 'Johnson', 'email': 'mike@example.com'},
            {'username': 'sarah_explorer', 'first_name': 'Sarah', 'last_name': 'Wilson', 'email': 'sarah@example.com'},
            {'username': 'david_guest', 'first_name': 'David', 'last_name': 'Brown', 'email': 'david@example.com'},
            {'username': 'lisa_traveler', 'first_name': 'Lisa', 'last_name': 'Davis', 'email': 'lisa@example.com'},
            {'username': 'alex_host', 'first_name': 'Alex', 'last_name': 'Miller', 'email': 'alex@example.com'},
            {'username': 'emma_guest', 'first_name': 'Emma', 'last_name': 'Garcia', 'email': 'emma@example.com'},
        ]
        
        users = []
        for user_data in sample_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'password': 'pbkdf2_sha256$390000$dummy$hash'  # Dummy password hash
                }
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {user.username}')
        
        return users
    
    def create_sample_listings(self, users, count):
        """Create sample listings"""
        sample_listings = [
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'Beautiful apartment in the heart of the city with modern amenities.',
                'location': 'New York, NY',
                'price_per_night': Decimal('150.00'),
                'property_type': 'apartment',
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 1,
            },
            {
                'title': 'Beachfront Villa',
                'description': 'Stunning villa with ocean views and private beach access.',
                'location': 'Miami, FL',
                'price_per_night': Decimal('350.00'),
                'property_type': 'villa',
                'max_guests': 8,
                'bedrooms': 4,
                'bathrooms': 3,
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Peaceful cabin surrounded by nature, perfect for a getaway.',
                'location': 'Aspen, CO',
                'price_per_night': Decimal('200.00'),
                'property_type': 'cabin',
                'max_guests': 6,
                'bedrooms': 3,
                'bathrooms': 2,
            },
            {
                'title': 'Luxury Hotel Suite',
                'description': 'Five-star hotel suite with concierge service and spa access.',
                'location': 'Las Vegas, NV',
                'price_per_night': Decimal('400.00'),
                'property_type': 'hotel',
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
            },
            {
                'title': 'Historic Townhouse',
                'description': 'Charming historic home in a quiet neighborhood.',
                'location': 'Boston, MA',
                'price_per_night': Decimal('180.00'),
                'property_type': 'house',
                'max_guests': 6,
                'bedrooms': 3,
                'bathrooms': 2,
            },
        ]
        
        # Additional generated listings
        cities = [
            'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ',
            'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX',
            'San Jose, CA', 'Austin, TX', 'Jacksonville, FL', 'Fort Worth, TX',
            'Columbus, OH', 'Charlotte, NC', 'San Francisco, CA', 'Indianapolis, IN'
        ]
        
        property_types = ['apartment', 'house', 'hotel', 'villa', 'cabin']
        
        listings = []
        hosts = users[:4]  # First 4 users as hosts
        
        # Create predefined listings
        for i, listing_data in enumerate(sample_listings[:count]):
            listing_data['host'] = hosts[i % len(hosts)]
            listing_data['has_wifi'] = random.choice([True, False])
            listing_data['has_parking'] = random.choice([True, False])
            listing_data['has_kitchen'] = random.choice([True, False])
            listing_data['has_pool'] = random.choice([True, False])
            listing_data['allows_pets'] = random.choice([True, False])
            
            listing = Listing.objects.create(**listing_data)
            listings.append(listing)
            self.stdout.write(f'Created listing: {listing.title}')
        
        # Create additional random listings if needed
        for i in range(len(sample_listings), count):
            listing_data = {
                'title': f'Amazing {random.choice(property_types).title()} #{i+1}',
                'description': f'A wonderful place to stay with great amenities and comfortable accommodations.',
                'location': random.choice(cities),
                'price_per_night': Decimal(str(random.randint(50, 500))),
                'property_type': random.choice(property_types),
                'max_guests': random.randint(1, 10),
                'bedrooms': random.randint(1, 5),
                'bathrooms': random.randint(1, 4),
                'host': random.choice(hosts),
                'has_wifi': random.choice([True, False]),
                'has_parking': random.choice([True, False]),
                'has_kitchen': random.choice([True, False]),
                'has_pool': random.choice([True, False]),
                'allows_pets': random.choice([True, False]),
            }
            
            listing = Listing.objects.create(**listing_data)
            listings.append(listing)
            self.stdout.write(f'Created listing: {listing.title}')
        
        return listings
    
    def create_sample_bookings(self, users, listings, count):
        """Create sample bookings"""
        bookings = []
        guests = users[4:]  # Last 4 users as guests
        
        for i in range(count):
            listing = random.choice(listings)
            guest = random.choice(guests)
            
            # Generate random booking dates
            start_date = date.today() + timedelta(days=random.randint(1, 180))
            duration = random.randint(1, 14)
            end_date = start_date + timedelta(days=duration)
            
            booking_data = {
                'listing': listing,
                'guest': guest,
                'check_in_date': start_date,
                'check_out_date': end_date,
                'number_of_guests': random.randint(1, min(listing.max_guests, 4)),
                'total_price': listing.price_per_night * duration,
                'status': random.choice(['pending', 'confirmed', 'completed']),
                'special_requests': random.choice([
                    'Late check-in requested',
                    'Extra towels needed',
                    'Quiet room please',
                    'Ground floor preferred',
                    ''
                ])
            }
            
            try:
                booking = Booking.objects.create(**booking_data)
                bookings.append(booking)
                self.stdout.write(f'Created booking: {booking.booking_id}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Skipped booking creation: {str(e)}')
                )
        
        return bookings
    
    def create_sample_reviews(self, users, listings, bookings, count):
        """Create sample reviews"""
        completed_bookings = [b for b in bookings if b.status == 'completed']
        review_comments = [
            'Amazing place! Highly recommended.',
            'Great location and very clean.',
            'Perfect for our family vacation.',
            'Host was very responsive and helpful.',
            'Beautiful property with stunning views.',
            'Everything was as described. Will book again!',
            'Comfortable stay with all necessary amenities.',
            'Excellent value for money.',
            'The place exceeded our expectations.',
            'Good location but could use some updates.',
        ]
        
        created_reviews = 0
        
        for i in range(count):
            if completed_bookings:
                # Create review from a completed booking
                booking = random.choice(completed_bookings)
                reviewer = booking.guest
                listing = booking.listing
                completed_bookings.remove(booking)  # Ensure one review per booking
            else:
                # Create review from any user/listing combination
                reviewer = random.choice(users[4:])  # Guests only
                listing = random.choice(listings)
            
            # Check if review already exists
            if Review.objects.filter(listing=listing, reviewer=reviewer).exists():
                continue
            
            review_data = {
                'listing': listing,
                'reviewer': reviewer,
                'rating': random.randint(3, 5),  # Mostly positive reviews
                'comment': random.choice(review_comments),
                'booking': booking if 'booking' in locals() else None
            }
            
            try:
                review = Review.objects.create(**review_data)
                created_reviews += 1
                self.stdout.write(f'Created review: {review.review_id}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Skipped review creation: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_reviews} reviews')
        )