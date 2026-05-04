from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not username or not email or not password1:
            messages.error(request, 'Заполните все обязательные поля.')
        elif password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Этот email уже зарегистрирован.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name, last_name=last_name
            )
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Добро пожаловать, {first_name or username}!')
            return redirect('index')
    return render(request, 'users/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'index')
            messages.success(request, f'Добро пожаловать, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('profile')
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def wishlist_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'users/wishlist.html', {'wishlist': profile.wishlist.all()})
