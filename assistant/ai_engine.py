from store.models import Product, Category
from django.db.models import Q
from fuzzywuzzy import fuzz, process
import random
import re

class TechShopAssistant:
    """Enhanced AI assistant with fuzzy matching, context awareness, and improved logic."""

    GREETINGS = ['привет', 'здравствуй', 'hello', 'hi', 'добрый день', 'добрый вечер', 'доброе утро', 'салют', 'хайо']
    FAREWELLS = ['пока', 'до свидания', 'спасибо', 'благодарю', 'bye', 'exit']
    HELP_KEYWORDS = ['помоги', 'помощь', 'что умеешь', 'что ты можешь', 'help', 'команды', 'умеешь']

    GREET_RESPONSES = [
        "Привет! 👋 Я интеллектуальный ассистент TechShop. Помогу вам выбрать идеальную технику, расскажу о товарах и подберу варианты под ваш бюджет. Что ищете?",
        "Здравствуйте! 🤖 Я ваш личный помощник по электронике. Спросите меня о конкретных товарах, подборе по цене или попросите показать новинки!",
        "Привет! Рад видеть вас в TechShop! Чем могу помочь? 😊",
    ]

    HELP_RESPONSE = """Я умею многое! Вот примеры того, как я могу вам помочь:

🔍 **Поиск товаров** — "покажи айфон 15", "есть ли макбуки?"
💰 **Подбор по бюджету** — "смартфоны до 400000 тенге", "покажи что-нибудь до 100000"
⭐ **Лучшие предложения** — "какие у вас топ товары?", "что посоветуешь?"
🏷️ **Акции** — "есть ли скидки?", "покажи распродажу"
📋 **Категории** — "какие есть категории?", "покажи наушники"
❓ **Наличие** — "есть ли в наличии samsung s24?"

Просто напишите мне, что вы хотите найти!"""

    def process_message(self, message, session_history=None):
        """Process user message using fuzzy matching and return an intelligent response."""
        msg = message.lower().strip()
        
        # 1. Greetings & basic intents
        if any(fuzz.partial_ratio(g, msg) > 85 for g in self.GREETINGS) and len(msg.split()) <= 3:
            return random.choice(self.GREET_RESPONSES)

        if any(fuzz.partial_ratio(f, msg) > 85 for f in self.FAREWELLS) and len(msg.split()) <= 3:
            return "Всегда пожалуйста! 👋 Если появятся вопросы — обращайтесь. Хорошего дня!"

        if any(fuzz.partial_ratio(h, msg) > 85 for h in self.HELP_KEYWORDS):
            return self.HELP_RESPONSE

        # 2. Extract budget and search by it
        budget = self._extract_budget(msg)
        
        # 3. Fuzzy search for categories
        category = self._detect_category(msg)

        if budget and category:
            return self._recommend_by_budget_and_category(budget, category)
        elif budget:
            return self._recommend_by_budget(budget)
        elif category:
            # If user just mentions a category but also words like "top", "best"
            if any(w in msg for w in ['топ', 'лучш', 'рекоменд']):
                return self._get_featured(category)
            return self._search_by_category(category)

        # 4. Specific product fuzzy search
        product_response = self._fuzzy_search_products(msg)
        if product_response:
            return product_response

        # 5. Sales/discounts
        if any(fuzz.partial_ratio(w, msg) > 80 for w in ['скидка', 'акция', 'распродажа', 'выгодно']):
            return self._get_sales()

        # 6. Top/recommended
        if any(fuzz.partial_ratio(w, msg) > 80 for w in ['топ', 'лучший', 'рекомендация', 'популярный', 'хит']):
            return self._get_featured()

        # 7. New arrivals
        if any(fuzz.partial_ratio(w, msg) > 80 for w in ['новинка', 'новый', 'поступление']):
            return self._get_new_products()

        # 8. Categories list
        if any(fuzz.partial_ratio(w, msg) > 80 for w in ['категория', 'раздел', 'виды', 'ассортимент', 'каталог']):
            return self._list_categories()

        # Default fallback
        return self._default_response(message)

    def _extract_budget(self, msg):
        """Extract budget amount from message intelligently."""
        patterns = [
            r'до\s*(\d+[\d\s]*)\s*(тенге|тг|₸|руб|рублей)?',
            r'бюджет\s*(\d+[\d\s]*)',
            r'в пределах\s*(\d+[\d\s]*)',
            r'не дороже\s*(\d+[\d\s]*)',
            r'(\d+[\d\s]*)\s*(тенге|тг|₸)',
        ]
        for pattern in patterns:
            match = re.search(pattern, msg)
            if match:
                try:
                    # Clean up spaces
                    val = match.group(1).replace(' ', '')
                    return int(val)
                except ValueError:
                    pass
        return None

    def _detect_category(self, msg):
        """Use fuzzy matching to detect if user is asking for a specific category."""
        categories = Category.objects.all()
        cat_names = [cat.name.lower() for cat in categories]
        
        # We use token_set_ratio to handle things like "покажи мне смартфоны"
        best_match = process.extractOne(msg, cat_names, scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] > 70:
            # Find the actual category object
            for cat in categories:
                if cat.name.lower() == best_match[0]:
                    return cat
                    
        # Hardcoded synonyms
        synonyms = {
            'телефон': 'Смартфоны',
            'мобильник': 'Смартфоны',
            'сотка': 'Смартфоны',
            'комп': 'Ноутбуки',
            'ноут': 'Ноутбуки',
            'макбук': 'Ноутбуки',
            'уши': 'Наушники',
            'гарнитура': 'Наушники',
            'айпад': 'Планшеты'
        }
        
        for syn, actual_cat in synonyms.items():
            if fuzz.token_set_ratio(syn, msg) > 80:
                return Category.objects.filter(name=actual_cat).first()
                
        return None

    def _recommend_by_budget_and_category(self, budget, category):
        products = Product.objects.filter(category=category, price__lte=budget, stock__gt=0).order_by('-rating')[:5]
        if not products.exists():
            return f"К сожалению, я не нашёл товары в категории **{category.name}** до {budget:,} ₸. Попробуйте немного увеличить бюджет или посмотреть другие категории."

        lines = [f"🎯 Нашёл отличные **{category.name.lower()}** до {budget:,} ₸:\n"]
        for p in products:
            lines.append(f"• [{p.name}](/product/{p.slug}/) — **{p.price:,} ₸**" + (f" (★ {p.rating})" if p.rating > 0 else ""))
        return "\n".join(lines)

    def _recommend_by_budget(self, budget):
        products = Product.objects.filter(price__lte=budget, stock__gt=0).order_by('-rating')[:5]
        if not products.exists():
            return f"К сожалению, не нашёл подходящих товаров до {budget:,} ₸."

        lines = [f"🎯 Вот лучшие товары под ваш бюджет (до {budget:,} ₸):\n"]
        for p in products:
            lines.append(f"• [{p.name}](/product/{p.slug}/) — **{p.price:,} ₸**")
        lines.append(f"\n👉 [Посмотреть все](/catalog/?max_price={budget})")
        return "\n".join(lines)

    def _search_by_category(self, category):
        products = Product.objects.filter(category=category, stock__gt=0).order_by('-rating')[:5]
        if products.exists():
            lines = [f"📦 Вот популярные товары в категории **{category.name}**:\n"]
            for p in products:
                lines.append(f"• [{p.name}](/product/{p.slug}/) — **{p.price:,} ₸**")
            lines.append(f"\n👉 [Перейти в каталог](/catalog/?category={category.slug})")
            return "\n".join(lines)
        return f"В категории **{category.name}** пока нет товаров в наличии."

    def _fuzzy_search_products(self, msg):
        """Intelligently search products matching user input."""
        # Clean common words from query
        stop_words = ['покажи', 'найди', 'есть', 'ли', 'хочу', 'купить', 'мне', 'нужен', 'нужна']
        cleaned_words = [w for w in msg.split() if w not in stop_words]
        cleaned_msg = " ".join(cleaned_words)
        
        if not cleaned_msg:
            return None

        products = list(Product.objects.filter(stock__gt=0))
        
        # Create a list of tuples (product, score)
        scored_products = []
        for p in products:
            # Score based on name, brand, and description
            name_score = fuzz.token_set_ratio(cleaned_msg, p.name.lower())
            brand_score = fuzz.token_set_ratio(cleaned_msg, p.brand.lower()) * 0.8
            
            score = max(name_score, brand_score)
            if score > 60:  # Threshold for relevance
                scored_products.append((p, score))
                
        # Sort by score descending, then by rating
        scored_products.sort(key=lambda x: (x[1], x[0].rating), reverse=True)
        top_matches = [item[0] for item in scored_products[:5]]

        if top_matches:
            lines = [f"🔍 Вот что я нашёл по вашему запросу:\n"]
            for p in top_matches:
                lines.append(f"• [{p.name}](/product/{p.slug}/) — **{p.price:,} ₸**")
            return "\n".join(lines)
            
        return None

    def _get_sales(self):
        products = Product.objects.filter(old_price__isnull=False, stock__gt=0).order_by('-old_price')[:5]
        if not products.exists():
            return "Сейчас акций нет, но мы регулярно обновляем скидки! Следите за новостями. 🔥"
        lines = ["🏷️ **Горячие скидки:**\n"]
        for p in products:
            lines.append(f"• [{p.name}](/product/{p.slug}/) — ~~{p.old_price:,}~~ **{p.price:,} ₸** (-{p.discount_percent}%)")
        return "\n".join(lines)

    def _get_featured(self, category=None):
        query = Product.objects.filter(is_featured=True, stock__gt=0)
        if category:
            query = query.filter(category=category)
            
        products = query.order_by('-rating')[:5]
        if not products.exists():
            return "В данный момент нет рекомендаций, но вы можете посмотреть наш каталог: /catalog/"
        
        cat_text = f" в категории {category.name}" if category else ""
        lines = [f"⭐ **Топ наших рекомендаций{cat_text}:**\n"]
        for p in products:
            lines.append(f"• [{p.name}](/product/{p.slug}/) — **{p.price:,} ₸**")
        return "\n".join(lines)

    def _get_new_products(self):
        products = Product.objects.filter(is_new=True, stock__gt=0).order_by('-created_at')[:5]
        if not products.exists():
            return "Новинки появятся совсем скоро! Следите за обновлениями 🆕"
        lines = ["🆕 **Свежие поступления:**\n"]
        for p in products:
            lines.append(f"• [{p.name}](/product/{p.slug}/) — **{p.price:,} ₸**")
        return "\n".join(lines)

    def _list_categories(self):
        categories = Category.objects.all()
        if not categories.exists():
            return "Категории загружаются. Зайдите в каталог: /catalog/"
        lines = ["📋 **Мы предлагаем следующие категории товаров:**\n"]
        for cat in categories:
            count = cat.products.filter(stock__gt=0).count()
            lines.append(f"• [{cat.name}](/catalog/?category={cat.slug}) — {count} товаров")
        return "\n".join(lines)

    def _default_response(self, message):
        responses = [
            f"Кажется, я не совсем понял запрос «{message}». Попробуйте сформулировать иначе, например: «ноутбуки до 500000» или «покажи новинки».",
            f"Хмм, по запросу «{message}» ничего не нашлось. Уточните, что именно вы ищете (название, категорию или бюджет)? 🤖",
            "Я всё еще учусь! Пожалуйста, уточните ваш запрос. Напишите «что ты умеешь», чтобы узнать мои возможности. 💡",
        ]
        return random.choice(responses)
