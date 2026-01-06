from django.contrib import admin
from .models import User, Store, Product, Order, OrderItem, Review
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
