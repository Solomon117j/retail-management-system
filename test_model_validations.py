#!/usr/bin/env python
"""
Test script for model validations and field constraints
"""
import os
import sys
import django
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Brand, Category, Product
from e_commerce.models import CustomerAccount, OnlineOrder, SavedPaymentMethod
from content_management.models import BlogPost, Tutorial, SocialMediaIntegration
from procurement.models import Supplier, SupplierProduct
from api.models import APIKey, APIRequestLog, Webhook

def test_brand_model():
    """Test Brand model validations"""
    print("🧪 Testing Brand Model...")

    # Test valid brand creation
    try:
        brand = Brand(
            name="Test Brand",
            description="Test description",
            primary_color="#FF5733",
            secondary_color="#33FF57",
            brand_voice="Friendly and professional",
            aesthetic_description="Modern and clean",
            brand_story="Our brand story"
        )
        brand.full_clean()  # This will validate all fields
        print("✅ Brand model validation passed")
    except ValidationError as e:
        print(f"❌ Brand model validation failed: {e}")

    # Test invalid color format
    try:
        brand = Brand(
            name="Test Brand",
            primary_color="invalid-color"
        )
        brand.full_clean()
        print("❌ Should have failed for invalid color format")
    except ValidationError:
        print("✅ Correctly rejected invalid color format")

def test_customer_account_model():
    """Test CustomerAccount model validations"""
    print("\n🧪 Testing CustomerAccount Model...")

    # Test valid customer creation
    try:
        customer = CustomerAccount(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            preferred_language="en",
            marketing_opt_in=True,
            sms_notifications=False,
            push_notifications=True
        )
        customer.full_clean()
        print("✅ CustomerAccount model validation passed")
    except ValidationError as e:
        print(f"❌ CustomerAccount model validation failed: {e}")

    # Test invalid email
    try:
        customer = CustomerAccount(
            first_name="John",
            last_name="Doe",
            email="invalid-email"
        )
        customer.full_clean()
        print("❌ Should have failed for invalid email")
    except ValidationError:
        print("✅ Correctly rejected invalid email")

def test_online_order_model():
    """Test OnlineOrder model validations"""
    print("\n🧪 Testing OnlineOrder Model...")

    # Test guest checkout
    try:
        order = OnlineOrder(
            shipping_address="123 Test St, Test City",
            shipping_method="standard",
            status="pending",
            total_amount=Decimal('99.99'),
            payment_method="credit_card",
            guest_email="guest@example.com",
            guest_first_name="Guest",
            guest_last_name="User",
            guest_phone="+1234567890"
        )
        order.full_clean()
        print("✅ OnlineOrder guest checkout validation passed")
    except ValidationError as e:
        print(f"❌ OnlineOrder validation failed: {e}")

def test_saved_payment_method_model():
    """Test SavedPaymentMethod model validations"""
    print("\n🧪 Testing SavedPaymentMethod Model...")

    # Create a test customer first
    customer = CustomerAccount.objects.create(
        first_name="Test",
        last_name="User",
        email="test@example.com"
    )

    try:
        payment = SavedPaymentMethod(
            customer=customer,
            payment_type="credit_card",
            card_last_four="1234",
            card_brand="Visa",
            expiry_month=12,
            expiry_year=2025,
            is_default=True
        )
        payment.full_clean()
        print("✅ SavedPaymentMethod validation passed")
    except ValidationError as e:
        print(f"❌ SavedPaymentMethod validation failed: {e}")
    finally:
        customer.delete()

def test_blog_post_model():
    """Test BlogPost model validations"""
    print("\n🧪 Testing BlogPost Model...")

    try:
        post = BlogPost(
            title="Test Blog Post",
            slug="test-blog-post",
            author="Test Author",
            content="This is a test blog post content.",
            is_published=True
        )
        post.full_clean()
        print("✅ BlogPost validation passed")
    except ValidationError as e:
        print(f"❌ BlogPost validation failed: {e}")

def test_supplier_model():
    """Test Supplier model validations"""
    print("\n🧪 Testing Supplier Model...")

    try:
        supplier = Supplier(
            name="Test Supplier",
            email="supplier@example.com",
            phone="+1234567890",
            on_time_delivery_rate=Decimal('95.50'),
            quality_rating=Decimal('4.5'),
            compliance_score=Decimal('98.00'),
            tenant_id="tenant_001"
        )
        supplier.full_clean()
        print("✅ Supplier validation passed")
    except ValidationError as e:
        print(f"❌ Supplier validation failed: {e}")

def test_api_key_model():
    """Test APIKey model validations"""
    print("\n🧪 Testing APIKey Model...")

    try:
        api_key = APIKey(
            name="Test API Key",
            key="test_api_key_12345",
            rate_limit=1000
        )
        api_key.full_clean()
        print("✅ APIKey validation passed")
    except ValidationError as e:
        print(f"❌ APIKey validation failed: {e}")

def test_relationships():
    """Test model relationships"""
    print("\n🧪 Testing Model Relationships...")

    # Test Brand -> Product relationship
    try:
        brand = Brand.objects.create(name="Test Brand")
        category = Category.objects.create(name="Test Category")

        product = Product(
            name="Test Product",
            category=category,
            brand=brand,
            unit_price=Decimal('29.99'),
            cost_price=Decimal('19.99')
        )
        product.full_clean()
        print("✅ Brand-Product relationship validation passed")

        # Clean up
        product.delete()
        category.delete()
        brand.delete()

    except ValidationError as e:
        print(f"❌ Relationship validation failed: {e}")

def main():
    """Run all model validation tests"""
    print("🚀 Starting Model Validation Tests\n")

    test_brand_model()
    test_customer_account_model()
    test_online_order_model()
    test_saved_payment_method_model()
    test_blog_post_model()
    test_supplier_model()
    test_api_key_model()
    test_relationships()

    print("\n✅ Model validation testing completed!")

if __name__ == "__main__":
    main()
