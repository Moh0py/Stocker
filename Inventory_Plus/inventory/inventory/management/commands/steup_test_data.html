from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventory.models import Category, Supplier, Product
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates demo data for the inventory system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo users...')
        
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@inventoryplus.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        
        employee_user, created = User.objects.get_or_create(
            username='employee',
            defaults={
                'email': 'employee@inventoryplus.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'employee',
            }
        )
        if created:
            employee_user.set_password('emp123')
            employee_user.save()
            self.stdout.write(self.style.SUCCESS('Employee user created'))
        
        self.stdout.write('Creating categories...')
        categories = [
            Category.objects.get_or_create(name='Electronics', description='Electronic devices and accessories')[0],
            Category.objects.get_or_create(name='Office Supplies', description='Stationery and office equipment')[0],
            Category.objects.get_or_create(name='Furniture', description='Office and home furniture')[0],
            Category.objects.get_or_create(name='Food & Beverages', description='Perishable food items and drinks')[0],
            Category.objects.get_or_create(name='Cleaning Supplies', description='Cleaning products and equipment')[0],
        ]
        
        self.stdout.write('Creating suppliers...')
        suppliers = [
            Supplier.objects.get_or_create(
                email='techworld@example.com',
                defaults={
                    'name': 'TechWorld Inc',
                    'phone_number': '555-0101',
                    'website': 'https://techworld.com',
                    'address': '123 Tech Street',
                    'city': 'San Francisco',
                    'country': 'USA',
                }
            )[0],
            Supplier.objects.get_or_create(
                email='officeplus@example.com',
                defaults={
                    'name': 'Office Plus',
                    'phone_number': '555-0102',
                    'website': 'https://officeplus.com',
                    'address': '456 Business Ave',
                    'city': 'New York',
                    'country': 'USA',
                }
            )[0],
            Supplier.objects.get_or_create(
                email='furniturepro@example.com',
                defaults={
                    'name': 'Furniture Pro',
                    'phone_number': '555-0103',
                    'address': '789 Furniture Blvd',
                    'city': 'Chicago',
                    'country': 'USA',
                }
            )[0],
            Supplier.objects.get_or_create(
                email='foodsupply@example.com',
                defaults={
                    'name': 'Food Supply Co',
                    'phone_number': '555-0104',
                    'address': '321 Food Court',
                    'city': 'Los Angeles',
                    'country': 'USA',
                }
            )[0],
        ]
        
        self.stdout.write('Creating products...')
        products_data = [
            ('Laptop Dell XPS 15', 'LAP001', categories[0], [suppliers[0]], 1299.99, 15, 5, False, None),
            ('Wireless Mouse', 'MOU001', categories[0], [suppliers[0]], 29.99, 50, 10, False, None),
            ('Office Chair', 'CHA001', categories[2], [suppliers[2]], 299.99, 8, 3, False, None),
            ('Printer Paper A4', 'PAP001', categories[1], [suppliers[1]], 24.99, 100, 20, False, None),
            ('Coffee Beans 1kg', 'COF001', categories[3], [suppliers[3]], 15.99, 25, 10, True, date.today() + timedelta(days=30)),
            ('Hand Sanitizer', 'SAN001', categories[4], [suppliers[1]], 4.99, 5, 15, False, None),
            ('USB-C Cable', 'CAB001', categories[0], [suppliers[0]], 12.99, 75, 20, False, None),
            ('Standing Desk', 'DSK001', categories[2], [suppliers[2]], 599.99, 3, 2, False, None),
            ('Milk 1L', 'MLK001', categories[3], [suppliers[3]], 3.99, 10, 15, True, date.today() + timedelta(days=5)),
            ('Notebook Pack', 'NOT001', categories[1], [suppliers[1]], 9.99, 40, 15, False, None),
        ]
        
        for name, sku, category, supplier_list, price, stock, reorder, perishable, expiry in products_data:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': category,
                    'unit_price': price,
                    'quantity_in_stock': stock,
                    'reorder_level': reorder,
                    'is_perishable': perishable,
                    'expiry_date': expiry,
                    'created_by': admin_user,
                    'description': f'High quality {name.lower()} for your business needs.',
                }
            )
            if created:
                product.suppliers.set(supplier_list)
                self.stdout.write(self.style.SUCCESS(f'Product {name} created'))
        
        self.stdout.write(self.style.SUCCESS('Demo data setup complete!'))