#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from inventory.models import Product
from django.core.files import File

def get_available_images():
    """Get list of available image files in the product_images directory"""
    media_dir = Path('media/product_images')
    if not media_dir.exists():
        print("media/product_images directory not found!")
        return []

    images = []
    for file_path in media_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            images.append(file_path.name)

    print(f"Found {len(images)} image files: {images}")
    return images

def assign_images_to_products():
    """Assign images to products that don't have images"""
    available_images = get_available_images()
    if not available_images:
        print("No images available to assign!")
        return

    products = Product.objects.all()
    print(f"Total products: {products.count()}")

    # Get products without images
    products_without_images = products.filter(image__isnull=True) | products.filter(image='')
    print(f"Products without images: {products_without_images.count()}")

    # Create a mapping of product names to images
    image_mapping = {}
    for image in available_images:
        # Remove file extension to get base name
        base_name = Path(image).stem.lower()

        # Try to match with product names
        for product in products_without_images:
            product_name_lower = product.name.lower().replace(' ', '')

            # Check for partial matches
            if base_name in product_name_lower or product_name_lower in base_name:
                if product not in image_mapping:
                    image_mapping[product] = image
                    break

    # If we have more products than images, assign images in a round-robin fashion
    if len(products_without_images) > len(available_images):
        assigned_images = set(image_mapping.values())
        remaining_products = [p for p in products_without_images if p not in image_mapping]

        for i, product in enumerate(remaining_products):
            # Cycle through available images
            image = available_images[i % len(available_images)]
            image_mapping[product] = image

    # Assign images to products
    assigned_count = 0
    for product, image_filename in image_mapping.items():
        try:
            # Open the image file
            image_path = Path('media/product_images') / image_filename
            with open(image_path, 'rb') as f:
                # Create a Django File object
                django_file = File(f, name=image_filename)

                # Assign the image to the product
                product.image = django_file
                product.save()

                print(f"✓ Assigned {image_filename} to {product.name}")
                assigned_count += 1

        except Exception as e:
            print(f"✗ Failed to assign {image_filename} to {product.name}: {str(e)}")

    print(f"\nSummary:")
    print(f"Images assigned: {assigned_count}")
    print(f"Products with images now: {Product.objects.exclude(image__isnull=True).exclude(image='').count()}")
    print(f"Products still without images: {Product.objects.filter(image__isnull=True) | Product.objects.filter(image='').count()}")

if __name__ == '__main__':
    print("Assigning images to existing products...")
    assign_images_to_products()
    print("Done!")
