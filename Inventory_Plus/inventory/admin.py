from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Product, Category, Supplier, StockMovement
from accounts.models import User

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number')}),
    )

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'unit_price', 'quantity_in_stock', 'get_stock_status')
    list_filter = ('category', 'is_perishable', 'created_at')
    search_fields = ('name', 'sku', 'description')
    filter_horizontal = ('suppliers',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_stock_status(self, obj):
        return obj.get_stock_status()
    get_stock_status.short_description = 'Stock Status'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'city', 'country')
    list_filter = ('city', 'country')
    search_fields = ('name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'performed_by', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name', 'reason')
    readonly_fields = ('created_at',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(StockMovement, StockMovementAdmin)

admin.site.site_header = 'Inventory Plus Administration'
admin.site.site_title = 'Inventory Plus'
admin.site.index_title = 'Welcome to Inventory Plus Administration'