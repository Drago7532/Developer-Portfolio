from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    VENDOR = 'vendor'
    BUYER = 'buyer'
    ROLE_CHOICES = [
        (VENDOR, 'Vendor'),
        (BUYER, 'Buyer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BUYER)

    def is_vendor(self):
        return self.role == self.VENDOR

    def is_buyer(self):
        return self.role == self.BUYER

class Store(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'name')

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to='products/',
        blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.quantity * self.price

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Review {self.rating} for {self.product.name}"

class Tweet():
    CONSUMER_KEY = 'srfJmlecIUZgScq9i0pRWyrN1'
    CONSUMER_SECRET = 'jHxorf0V8SaBxCXlulM7HgrTNIWHS3fxiqDZG4ndHTPOYBESmO'
