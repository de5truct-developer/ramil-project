from store.models import Cart, Category


def cart_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first()
        if cart:
            count = cart.count
    except Exception:
        pass
    return {'cart_count': count}


def categories_list(request):
    categories = Category.objects.all()
    return {'all_categories': categories}
