from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Review, Cart, CartItem, Order, OrderItem
import json


def get_or_create_cart(request):
    """Get or create cart for current user/session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge session cart if exists
        if not request.session.session_key:
            request.session.create()
        session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if session_cart:
            for item in session_cart.items.all():
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                if not created:
                    cart_item.quantity += item.quantity
                else:
                    cart_item.quantity = item.quantity
                cart_item.save()
            session_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def index(request):
    featured_products = Product.objects.filter(is_featured=True, stock__gt=0)[:8]
    new_products = Product.objects.filter(is_new=True, stock__gt=0)[:8]
    categories = Category.objects.all()
    sale_products = Product.objects.filter(old_price__isnull=False, stock__gt=0)[:6]
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
        'sale_products': sale_products,
    }
    return render(request, 'store/index.html', context)


def catalog(request):
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()

    # Filters
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')
    brand_filter = request.GET.get('brand', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if brand_filter:
        products = products.filter(brand=brand_filter)

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    valid_sorts = ['-created_at', 'price', '-price', '-rating', 'name']
    if sort_by not in valid_sorts:
        sort_by = '-created_at'
    products = products.order_by(sort_by)

    brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand='')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'brands': brands,
        'brand_filter': brand_filter,
        'min_price': min_price,
        'max_price': max_price,
        'total_count': products.count(),
    }
    return render(request, 'store/catalog.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related('user').all()
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        text = request.POST.get('text', '')
        if rating and text:
            review, created = Review.objects.get_or_create(
                product=product, user=request.user,
                defaults={'rating': rating, 'text': text}
            )
            if not created:
                review.rating = rating
                review.text = text
                review.save()
            # Update product rating
            all_reviews = product.reviews.all()
            if all_reviews.exists():
                product.rating = sum(r.rating for r in all_reviews) / all_reviews.count()
                product.reviews_count = all_reviews.count()
                product.save()
            messages.success(request, 'Ваш отзыв сохранён!')
            return redirect('product_detail', slug=slug)

    context = {
        'product': product,
        'reviews': reviews,
        'related': related,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.count, 'message': 'Товар добавлен в корзину'})
    messages.success(request, f'"{product.name}" добавлен в корзину!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    if item.cart == cart:
        item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.count, 'cart_total': float(cart.total)})
    return redirect('cart')


def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    if item.cart == cart:
        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            item.quantity = qty
            item.save()
        else:
            item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.count,
            'cart_total': float(cart.total),
            'item_subtotal': float(item.subtotal) if item.pk else 0
        })
    return redirect('cart')


def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('cart')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            notes=request.POST.get('notes', ''),
            total_price=cart.total,
        )
        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            item.product.stock -= item.quantity
            if item.product.stock < 0:
                item.product.stock = 0
            item.product.save(update_fields=['stock'])
        cart.items.all().delete()
        messages.success(request, f'Заказ #{order.order_number} успешно оформлен!')
        return redirect('order_success', order_number=order.order_number)

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        if hasattr(request.user, 'profile'):
            initial['phone'] = request.user.profile.phone
            initial['address'] = request.user.profile.address
            initial['city'] = request.user.profile.city

    return render(request, 'store/checkout.html', {'cart': cart, 'initial': initial})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile = request.user.profile
    if product in profile.wishlist.all():
        profile.wishlist.remove(product)
        in_wishlist = False
    else:
        profile.wishlist.add(product)
        in_wishlist = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'in_wishlist': in_wishlist})
    return redirect(request.META.get('HTTP_REFERER', '/'))
