import os
import sys
import django
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techshop.settings')
django.setup()

from store.models import Product

# A dictionary mapping product names or brands to image URLs
IMAGE_URLS = {
    'iPhone 15 Pro Max 256GB Titanium': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?q=80&w=1000&auto=format&fit=crop',
    'Samsung Galaxy S24 Ultra 512GB': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=1000&auto=format&fit=crop',
    'Xiaomi 13T Pro 12/512GB Black': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1000&auto=format&fit=crop',
    'Apple MacBook Air 15" M2 8/256GB': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1000&auto=format&fit=crop',
    'ASUS ROG Zephyrus G14 (2024)': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=1000&auto=format&fit=crop',
    'Lenovo IdeaPad Slim 3 15IRU8': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?q=80&w=1000&auto=format&fit=crop',
    'Apple AirPods Pro (2nd Gen) USB-C': 'https://images.unsplash.com/photo-1588423771073-b8903fbb85b5?q=80&w=1000&auto=format&fit=crop',
    'Sony WH-1000XM5 Black': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?q=80&w=1000&auto=format&fit=crop',
    'Apple Watch Series 9 45mm': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?q=80&w=1000&auto=format&fit=crop',
    'Samsung Galaxy Watch 6 Classic': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?q=80&w=1000&auto=format&fit=crop',
    'iPad Pro 11" M2 (2022) 128GB': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop',
}

def download_images():
    products = Product.objects.all()
    for p in products:
        if p.name in IMAGE_URLS:
            print(f"Downloading image for {p.name}...")
            url = IMAGE_URLS[p.name]
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    filename = f"{slugify(p.name)}.jpg"
                    p.image.save(filename, ContentFile(response.content), save=True)
                    print(f"Successfully saved image for {p.name}")
                else:
                    print(f"Failed to download image for {p.name}: Status {response.status_code}")
            except Exception as e:
                print(f"Error downloading image for {p.name}: {e}")

if __name__ == '__main__':
    download_images()
