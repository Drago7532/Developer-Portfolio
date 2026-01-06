from django.urls import path, reverse_lazy, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),

    # auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='shop/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    #vendor urls
    path('vendor/stores/', views.stores_list, name='stores_list'),
    path('vendor/stores/create/', views.store_create, name='store_create'),
    path('vendor/stores/<int:pk>/edit/', views.store_edit, name='store_edit'),
    path('vendor/stores/<int:pk>/delete/', views.store_delete, name='store_delete'),

    path('vendor/stores/<int:store_pk>/products/', views.store_products, name='store_products'),
    path('vendor/stores/<int:store_pk>/products/add/', views.product_create, name='product_create'),
    path('vendor/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('vendor/products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    #cart/checkout
    path('cart/', views.cart_detail, name='cart_detail'),
    path('card/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),

    # orders
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # reviews
    path('product/<int:product_pk>/review/', views.add_review, name='add_review'),

    # password reset (built-in)
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='shop/auth/password_reset_form.html',
        email_template_name='shop/auth/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='shop/auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='shop/auth/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='shop/auth/password_reset_complete.html'), name='password_reset_complete'),

    # API URL
    path('api/', include('shop.api.urls')),

]