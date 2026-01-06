# Simple session cart
from decimal import Decimal
from django.conf import settings
from .models import Product

SESSION_KEY = 'cart'

class SessionCart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(SESSION_KEY)
        if not cart:
            cart = self.session[SESSION_KEY] = {}
        self.cart = cart

    def add(self, product_id, quantity=1):
        pid = str(product_id)
        if pid in self.cart:
            self.cart[pid] += quantity
        else:
            self.cart[pid] = quantity
        self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[SESSION_KEY] = {}
        self.session.modified = True
        self.cart = self.session[SESSION_KEY]

    def save(self):
        self.session[SESSION_KEY] = self.cart
        self.session.modified = True

    def items(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            quantity = self.cart.get(str(product.id), 0)
            yield {
                'product': product,
                'quantity': quantity,
                'line_total': product.price * quantity
            }

    def total(self):
        total = 0
        for item in self.items():
            total += item['line_total']
        return total
