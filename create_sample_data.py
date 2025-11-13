#!/usr/bin/env python3
"""
Script to create sample plants with placeholder images for testing.
"""

import sys
import os
sys.path.insert(0, '.venv/lib/python3.11/site-packages')

from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models import Plant, PlantImage
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample plants and images for testing."""

    with app.app_context():
        try:
            # Sample plant data
            plants_data = [
                {
                    'name': 'Monstera Deliciosa',
                    'location': 'Living Room',
                    'images': ['monstera_1.jpg', 'monstera_2.jpg']
                },
                {
                    'name': 'Snake Plant',
                    'location': 'Bedroom',
                    'images': ['snake_plant_1.jpg']
                },
                {
                    'name': 'Peace Lily',
                    'location': 'Bathroom',
                    'images': ['peace_lily_1.jpg', 'peace_lily_2.jpg', 'peace_lily_3.jpg']
                },
                {
                    'name': 'Spider Plant',
                    'location': 'Kitchen',
                    'images': ['spider_plant_1.jpg']
                }
            ]

            # Create plants and images
            for plant_data in plants_data:
                # Check if plant already exists
                existing_plant = Plant.query.filter_by(name=plant_data['name']).first()
                if existing_plant:
                    print(f"Plant '{plant_data['name']}' already exists, skipping...")
                    continue

                # Create plant
                plant = Plant(
                    name=plant_data['name'],
                    location=plant_data['location']
                )
                db.session.add(plant)
                db.session.flush()  # Get the plant ID

                print(f"Created plant: {plant.name} (ID: {plant.id})")

                # Create placeholder images
                for i, image_filename in enumerate(plant_data['images']):
                    image_path = f'static/images/{image_filename}'

                    # Create a simple colored placeholder image
                    create_placeholder_image(image_path, plant_data['name'], i+1)

                    # Create PlantImage record
                    captured_at = datetime.now() - timedelta(days=random.randint(0, 30))
                    plant_image = PlantImage(
                        plant_id=plant.id,
                        image_path=image_path,
                        captured_at=captured_at
                    )
                    db.session.add(plant_image)

                    print(f"  - Created image: {image_filename}")

            db.session.commit()
            print("\n✅ Sample data created successfully!")

        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            db.session.rollback()

def create_placeholder_image(filepath, plant_name, image_num):
    """Create a simple colored placeholder image."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create a 400x300 image
        img = Image.new('RGB', (400, 300), color=get_random_color())
        draw = ImageDraw.Draw(img)

        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()

        # Add text
        text = f"{plant_name}\nImage {image_num}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (400 - text_width) // 2
        y = (300 - text_height) // 2

        draw.text((x, y), text, fill='white', font=font)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Save image
        img.save(filepath)
        print(f"Created placeholder image: {filepath}")

    except ImportError:
        # Fallback if PIL is not available - create a simple text file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath.replace('.jpg', '.txt'), 'w') as f:
            f.write(f"Placeholder for {plant_name} - Image {image_num}")
        print(f"Created text placeholder: {filepath.replace('.jpg', '.txt')}")

def get_random_color():
    """Get a random pleasant color."""
    colors = [
        (34, 139, 34),   # Forest Green
        (0, 128, 0),     # Green
        (46, 139, 87),   # Sea Green
        (60, 179, 113),  # Medium Sea Green
        (107, 142, 35),  # Olive Drab
        (34, 139, 34),   # Forest Green
    ]
    return random.choice(colors)

if __name__ == '__main__':
    create_sample_data()