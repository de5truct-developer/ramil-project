from django.contrib import admin
from .models import Category, Product, Review, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'subtotal']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'is_featured', 'is_new', 'rating']
    list_filter = ['category', 'is_featured', 'is_new', 'brand']
    search_fields = ['name', 'brand', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_featured', 'is_new']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']


def make_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')


def make_shipped(modeladmin, request, queryset):
    queryset.update(status='shipped')


def make_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')


def make_cancelled(modeladmin, request, queryset):
    queryset.update(status='cancelled')


make_confirmed.short_description = 'Отметить как "Подтверждён"'
make_shipped.short_description = 'Отметить как "Отправлен"'
make_delivered.short_description = 'Отметить как "Доставлен"'
make_cancelled.short_description = 'Отметить как "Отменён"'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'last_name', 'email', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'email', 'first_name', 'last_name']
    list_editable = ['status']
    inlines = [OrderItemInline]
    actions = [make_confirmed, make_shipped, make_delivered, make_cancelled]
    readonly_fields = ['order_number', 'total_price', 'created_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'count', 'total', 'created_at']
