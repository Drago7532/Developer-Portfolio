from itertools import product

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from .models import Store, Product, Order, OrderItem, Review
from .forms import UserRegisterForm, StoreForm, ProductForm, ReviewForm
from .cart import SessionCart
from mariadb import connect, ProgrammingError, OperationalError
from shop.utils.twitter_client import get_twitter_client
from django.contrib.sites.models import Site

# Create your views here.

# Registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully")
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'shop/register.html', {'form': form})

# Login / logout can use Django built-in views or custom; we use built-in urls

# Helpers
def vendor_check(user):
    return user.is_authenticated and user.is_vendor()

def buyer_check(user):
    return user.is_authenticated and user.is_buyer()

# Vendor: Store CRUD
@login_required
@user_passes_test(vendor_check)
def stores_list(request):
    stores = request.user.stores.all()
    return render(request, 'shop/vendor/stores_list.html', {'stores': stores})

def tweet_new_store(store):
    client = get_twitter_client()

    tweet_text = (
        f"New Store Added!\n\n"
        f"{store.name}\n"
        f"{store.description}\n"
    )

    client.update_status(tweet_text)

@ login_required
@user_passes_test(vendor_check)
def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            tweet_new_store(store)
            messages.success(request, "Store created")
            return redirect('stores_list')
    else:
        form = StoreForm()
    return render(request, 'shop/vendor/store_form.html', {'form': form})

@login_required
@user_passes_test(vendor_check)
def store_edit(request, pk):
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, "Store updated")
            return redirect('stores_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'shop/vendor/store_form.html', {'form': form})

@login_required
@user_passes_test(vendor_check)
def store_delete(request, pk):
    store =  get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == 'POST':
        store.delete()
        messages.success(request, "Store removed")
        return redirect('stores_list')
    return render(request, 'shop/vendor/store_confirm_delete.html', {'store': store})

import tweepy
import os

def tweet_new_product(product, request=None):
    """If the product has an image, include a direct
     link to the image in the tweet"""
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_KEY_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    # Stop gracefully if keys are missing
    if not all([consumer_key, consumer_secret, access_token, access_secret]):
        print("Twitter API keys missing. Skipping tweet.")
        return

    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )

    tweet_text = (
        f"New product added!\n"
        f"Store: {product.store.name}\n"
        f"Product: {product.name}\n"
        f"{product.description[:200]}"
    )

    # Add image URL if it exists
    if product.image:
        if request:
            image_url = request.build_absolute_uri(product.image.url)
        else:
            current_site = Site.objects.get_current()
            image_url = f"https://{current_site.domain}{product.image.url}"
        tweet_text += f"\nImage: {image_url}"

    client.create_tweet(text=tweet_text)


# Vendor: Product CRUD within a store
@login_required
@user_passes_test(vendor_check)
def product_create(request, store_pk):
    store = get_object_or_404(Store, pk=store_pk, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            tweet_new_product(product, request=request)
            messages.success(request, "Product added")
            return redirect('store_products', store_pk=store.pk)
    else:
        form = ProductForm()
    return render(request, 'shop/vendor/product_form.html', {'form': form, 'store': store})

@login_required
@user_passes_test(vendor_check)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, store__owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated")
            return redirect('store_products', store_pk=product.store.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/vendor/product_form.html', {'form': form, 'store': product.store})

@login_required
@user_passes_test(vendor_check)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, store__owner=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted")
        return redirect('stores_list')
    return render(request, 'shop/vendor/product_confirm_delete.html', {'product': product})

@login_required
@user_passes_test(vendor_check)
def store_products(request, store_pk):
    store = get_object_or_404(Store, pk=store_pk, owner=request.user)
    products = store.products.all()
    return render(request, 'shop/vendor/products_list.html', {'store': store, 'products': products})

# Buyer: browse products & add to cart
def product_list(request):
    products = Product.objects.select_related('store').all()
    return render(request, 'shop/products/list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    review_form = ReviewForm()
    return render(request, 'shop/products/detail.html', {
        'product': product,
        'review_form': review_form
    })


@login_required
@user_passes_test(buyer_check)
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = SessionCart(request)
    cart.add(product.id, quantity=1)
    messages.success(request, f"Added {product.name} to cart")
    return redirect('cart_detail')

@login_required
@user_passes_test(buyer_check)
def cart_detail(request):
    cart = SessionCart(request)
    items = list(cart.items())
    total = cart.total()
    return render(request, 'shop/cart/detail.html', {'items': items, 'total': total})

@login_required
@user_passes_test(buyer_check)
def cart_remove(request, pk):
    cart = SessionCart(request)
    cart.remove(pk)
    messages.success(request, "Item removed from cart")
    return redirect('cart_detail')

# Checkout: create Order + OrderItems, send invoice email, clear cart
from django.db import transaction

@login_required
@user_passes_test(buyer_check)
def checkout(request):
    cart = SessionCart(request)
    items = list(cart.items())
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect('product_list')

    with transaction.atomic():
        total = cart.total()
        order = Order.objects.create(buyer=request.user, total=total)
        for it in items:
            product = it['product']
            quantity = it['quantity']
            if product.stock < quantity:
                # handle insufficient stock
                messages.error(request, f"Not enough stock for {product.name}")
                transaction.set_rollback(True)
                return redirect('cart_detail')
            # reduce stock
            product.stock -= quantity
            product.save()
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)

        # send invoice email
        subject = f"Invoice for Order #{order.id}"
        message = render_to_string('shop/emails/invoice.html', {'order':order, 'items':order.items.all(), 'user': request.user})
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email], html_message=message)
        order.email_sent = True
        order.save()

        cart.clear()
        messages.success(request, "Checkout complete. Invoice sent to your email")
        return redirect('order_detail',pk=order.pk)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    # ensure buyer or vendor with items in order can view
    if request.user != order.buyer and not (request.user.is_vendor() and order.items.filter(product__store__owner=request.user).exists()):
        messages.error(request, "Permission denied")
        return redirect('home')
    return render(request, 'shop/orders/detail.html', {'order': order})

# Reviews
@login_required
@user_passes_test(buyer_check)
def add_review(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.method =='POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.buyer = request.user
            # check verification: has buyer purchased product?
            purchased = OrderItem.objects.filter(order__buyer=request.user, product=product).exists()
            review.verified = purchased
            review.save()
            messages.success(request, "Review submitted")
    return redirect('product_detail', pk=product_pk)
