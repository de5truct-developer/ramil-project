import os
import django
import sys
import random
from PIL import Image, ImageDraw, ImageFont

# Set up Django
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techshop.settings')
django.setup()

from store.models import Category, Product
from django.core.files import File
from django.utils.text import slugify

def create_placeholder_image(text, filename, size=(600, 600), bg_color=(240, 240, 245), text_color=(108, 99, 255)):
    """Generate a placeholder image for products."""
    img = Image.new('RGB', size, color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
        
    # Get text box
    bbox = d.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    d.text(position, text, fill=text_color, font=font)
    
    path = os.path.join(base_dir, 'media', 'products', filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path

def seed_data():
    print("Clearing old data...")
    Product.objects.all().delete()
    Category.objects.all().delete()

    print("Creating categories...")
    cats = [
        {'name': 'Смартфоны', 'icon': 'fa-mobile-alt', 'order': 1},
        {'name': 'Ноутбуки', 'icon': 'fa-laptop', 'order': 2},
        {'name': 'Наушники', 'icon': 'fa-headphones', 'order': 3},
        {'name': 'Умные часы', 'icon': 'fa-clock', 'order': 4},
        {'name': 'Планшеты', 'icon': 'fa-tablet-alt', 'order': 5},
    ]
    
    cat_objs = {}
    for c in cats:
        cat_objs[c['name']] = Category.objects.create(**c)

    print("Creating products...")
    
    products_data = [
        # Смартфоны
        {
            'cat': 'Смартфоны', 'name': 'iPhone 15 Pro Max 256GB Titanium', 'brand': 'Apple',
            'price': 650000, 'old_price': 700000, 'stock': 15, 'is_featured': True, 'rating': 4.9, 'reviews_count': 12,
            'desc': 'Флагманский смартфон Apple с титановым корпусом и процессором A17 Pro. Камера 48 Мп, поддержка USB-C.',
            'specs': {'Экран': '6.7" OLED', 'Процессор': 'Apple A17 Pro', 'Память': '256 ГБ', 'Камера': '48+12+12 Мп'}
        },
        {
            'cat': 'Смартфоны', 'name': 'Samsung Galaxy S24 Ultra 512GB', 'brand': 'Samsung',
            'price': 680000, 'old_price': None, 'stock': 10, 'is_new': True, 'rating': 4.8, 'reviews_count': 8,
            'desc': 'Мощный смартфон с ИИ функциями Galaxy AI. Стилус S Pen в комплекте.',
            'specs': {'Экран': '6.8" AMOLED', 'Процессор': 'Snapdragon 8 Gen 3', 'Память': '512 ГБ', 'Камера': '200+50+12+10 Мп'}
        },
        {
            'cat': 'Смартфоны', 'name': 'Xiaomi 13T Pro 12/512GB Black', 'brand': 'Xiaomi',
            'price': 320000, 'old_price': 350000, 'stock': 20, 'is_featured': False, 'rating': 4.6, 'reviews_count': 25,
            'desc': 'Отличный смартфон с камерами Leica и быстрой зарядкой 120 Вт.',
            'specs': {'Экран': '6.67" AMOLED 144Hz', 'Процессор': 'MediaTek Dimensity 9200+', 'Память': '512 ГБ', 'Зарядка': '120 Вт'}
        },
        
        # Ноутбуки
        {
            'cat': 'Ноутбуки', 'name': 'Apple MacBook Air 15" M2 8/256GB', 'brand': 'Apple',
            'price': 650000, 'old_price': 690000, 'stock': 5, 'is_featured': True, 'rating': 4.9, 'reviews_count': 40,
            'desc': 'Тонкий и легкий ноутбук с большим экраном 15 дюймов и мощным чипом M2.',
            'specs': {'Экран': '15.3" Liquid Retina', 'Процессор': 'Apple M2', 'ОЗУ': '8 ГБ', 'SSD': '256 ГБ'}
        },
        {
            'cat': 'Ноутбуки', 'name': 'ASUS ROG Zephyrus G14 (2024)', 'brand': 'ASUS',
            'price': 850000, 'old_price': None, 'stock': 3, 'is_new': True, 'rating': 4.7, 'reviews_count': 5,
            'desc': 'Компактный игровой ноутбук с OLED экраном и видеокартой RTX 4070.',
            'specs': {'Экран': '14" OLED 120Hz', 'Процессор': 'Ryzen 9 8945HS', 'Видеокарта': 'RTX 4070', 'ОЗУ': '32 ГБ'}
        },
        {
            'cat': 'Ноутбуки', 'name': 'Lenovo IdeaPad Slim 3 15IRU8', 'brand': 'Lenovo',
            'price': 250000, 'old_price': 280000, 'stock': 30, 'is_featured': False, 'rating': 4.5, 'reviews_count': 15,
            'desc': 'Надежный ноутбук для учебы и офисной работы по доступной цене.',
            'specs': {'Экран': '15.6" IPS', 'Процессор': 'Intel Core i5-1335U', 'ОЗУ': '16 ГБ', 'SSD': '512 ГБ'}
        },

        # Наушники
        {
            'cat': 'Наушники', 'name': 'Apple AirPods Pro (2nd Gen) USB-C', 'brand': 'Apple',
            'price': 125000, 'old_price': 140000, 'stock': 50, 'is_featured': True, 'rating': 4.8, 'reviews_count': 120,
            'desc': 'Внутриканальные наушники с лучшим активным шумоподавлением и разъемом Type-C.',
            'specs': {'Тип': 'TWS', 'Шумоподавление': 'Активное (ANC)', 'Время работы': 'до 30 часов с кейсом'}
        },
        {
            'cat': 'Наушники', 'name': 'Sony WH-1000XM5 Black', 'brand': 'Sony',
            'price': 180000, 'old_price': 200000, 'stock': 15, 'is_featured': True, 'rating': 4.9, 'reviews_count': 45,
            'desc': 'Полноразмерные наушники с эталонным качеством звука и шумоподавлением.',
            'specs': {'Тип': 'Полноразмерные', 'Шумоподавление': 'Активное (ANC)', 'Подключение': 'Bluetooth / Кабель'}
        },

        # Часы
        {
            'cat': 'Умные часы', 'name': 'Apple Watch Series 9 45mm', 'brand': 'Apple',
            'price': 220000, 'old_price': None, 'stock': 20, 'is_new': True, 'rating': 4.7, 'reviews_count': 30,
            'desc': 'Новые умные часы с двойным тапом и более ярким экраном.',
            'specs': {'Экран': 'OLED до 2000 нит', 'Процессор': 'S9 SiP', 'Влагозащита': 'WR50'}
        },
        {
            'cat': 'Умные часы', 'name': 'Samsung Galaxy Watch 6 Classic', 'brand': 'Samsung',
            'price': 160000, 'old_price': 180000, 'stock': 12, 'is_featured': False, 'rating': 4.6, 'reviews_count': 18,
            'desc': 'Классический дизайн с вращающимся безелем.',
            'specs': {'Экран': 'Super AMOLED', 'Размер': '47mm', 'ОС': 'Wear OS'}
        },

        # Планшеты
        {
            'cat': 'Планшеты', 'name': 'iPad Pro 11" M2 (2022) 128GB', 'brand': 'Apple',
            'price': 450000, 'old_price': None, 'stock': 8, 'is_featured': True, 'rating': 4.9, 'reviews_count': 22,
            'desc': 'Мощный планшет для профессионалов на базе процессора M2.',
            'specs': {'Экран': '11" Liquid Retina', 'Процессор': 'Apple M2', 'Память': '128 ГБ'}
        },
    ]

    for p_data in products_data:
        cat_name = p_data.pop('cat')
        cat = cat_objs[cat_name]
        
        # Generate placeholder image
        img_name = f"{slugify(p_data['name'])}.jpg"
        img_path = create_placeholder_image(p_data['brand'], img_name)
        
        p = Product(
            category=cat,
            name=p_data['name'],
            brand=p_data['brand'],
            price=p_data['price'],
            old_price=p_data['old_price'],
            stock=p_data['stock'],
            is_featured=p_data.get('is_featured', False),
            is_new=p_data.get('is_new', False),
            rating=p_data['rating'],
            reviews_count=p_data['reviews_count'],
            description=p_data['desc'],
            specifications=p_data['specs']
        )
        
        with open(img_path, 'rb') as f:
            p.image.save(img_name, File(f), save=False)
            
        p.save()
        print(f"Created: {p.name}")

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
