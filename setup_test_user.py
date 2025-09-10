#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

# Create test user
username = 'testuser'
email = 'test@example.com'
password = 'testpass123'

# Check if user already exists
if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists")
    user = User.objects.get(username=username)
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Test',
        last_name='User',
        school_name='Test School',
        school_type='high',
        grade_level='10th Grade',
        total_eco_tokens=100,
        level=2,
        experience_points=150
    )
    print(f"Created user: {username}")

# Create or update user profile
profile, created = UserProfile.objects.get_or_create(user=user)
if created:
    print(f"Created profile for {username}")
else:
    print(f"Profile already exists for {username}")

# Create superuser if it doesn't exist
if not User.objects.filter(is_superuser=True).exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("Created superuser: admin (password: admin123)")
else:
    print("Superuser already exists")

print("\nTest accounts created:")
print(f"Regular user: {username} (password: {password})")
print("Admin user: admin (password: admin123)")
print("\nYou can now test the quiz functionality!")
