document.addEventListener('DOMContentLoaded', function() {
    // Initialize Animate On Scroll
    AOS.init({
        duration: 800,
        once: true,
        offset: 50
    });

    // Mobile Menu Toggle
    const burgerBtn = document.getElementById('burgerBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (burgerBtn && mobileMenu) {
        burgerBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            document.body.style.overflow = this.classList.contains('active') ? 'hidden' : '';
        });
    }

    // Scroll to Top Button
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Add to Cart AJAX
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn:not(.no-ajax)');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href') || this.dataset.url;
            if (!url) return;

            // Simple animation
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = 'fa fa-spinner fa-spin';
            }

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Update badges
                    document.querySelectorAll('.cart-badge').forEach(badge => {
                        badge.textContent = data.cart_count;
                        badge.style.display = 'flex';
                    });
                    
                    // Reset icon
                    if (icon) {
                        icon.className = 'fa fa-check';
                        setTimeout(() => { icon.className = 'fa fa-shopping-cart'; }, 2000);
                    }
                    
                    showToast(data.message || 'Товар добавлен в корзину');
                }
            })
            .catch(err => {
                console.error(err);
                if (icon) icon.className = 'fa fa-shopping-cart';
            });
        });
    });

    // Wishlist AJAX
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href') || this.dataset.url;
            if (!url) return;

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.in_wishlist) {
                        this.classList.add('active');
                        this.querySelector('i').className = 'fa fa-heart';
                    } else {
                        this.classList.remove('active');
                        this.querySelector('i').className = 'far fa-heart';
                    }
                } else {
                    window.location.href = '/users/login/'; // Redirect if not logged in
                }
            });
        });
    });
});

// Simple Toast Notification System
function showToast(message, type = 'success') {
    const container = document.querySelector('.messages-container') || createMessagesContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-info-circle';
    
    alert.innerHTML = `
        <i class="fa ${iconClass}"></i>
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()"><i class="fa fa-times"></i></button>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
    return container;
}
