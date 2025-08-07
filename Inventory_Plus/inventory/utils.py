from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import Product, Category, Supplier
import io

def send_low_stock_alert(product):
    subject = f'Low Stock Alert: {product.name}'
    message = f'''
    Dear Manager,
    
    The following product is running low on stock:
    
    Product: {product.name}
    SKU: {product.sku}
    Current Stock: {product.quantity_in_stock}
    Reorder Level: {product.reorder_level}
    
    Please consider reordering this product soon.
    
    Best regards,
    Inventory Plus System
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.MANAGER_EMAIL],
        fail_silently=True,
    )

def send_expiry_alert(product):
    subject = f'Expiry Alert: {product.name}'
    message = f'''
    Dear Manager,
    
    The following perishable product is approaching its expiry date:
    
    Product: {product.name}
    SKU: {product.sku}
    Expiry Date: {product.expiry_date}
    Current Stock: {product.quantity_in_stock}
    
    Please take necessary action.
    
    Best regards,
    Inventory Plus System
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.MANAGER_EMAIL],
        fail_silently=True,
    )

def export_to_csv(queryset, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if filename.startswith('product'):
        writer.writerow(['Name', 'SKU', 'Category', 'Suppliers', 'Unit Price', 'Stock', 'Reorder Level', 'Status'])
        for product in queryset:
            suppliers = ', '.join([s.name for s in product.suppliers.all()])
            writer.writerow([
                product.name,
                product.sku,
                product.category.name if product.category else '',
                suppliers,
                product.unit_price,
                product.quantity_in_stock,
                product.reorder_level,
                product.get_stock_status()
            ])
    else:
        writer.writerow(['Name', 'SKU', 'Category', 'Unit Price', 'Stock', 'Total Value'])
        for product in queryset:
            writer.writerow([
                product.name,
                product.sku,
                product.category.name if product.category else '',
                product.unit_price,
                product.quantity_in_stock,
                product.get_total_value()
            ])
    
    return response

def import_from_csv(csv_file, user):
    try:
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        count = 0
        for row in reader:
            category = None
            if row.get('category'):
                category, _ = Category.objects.get_or_create(name=row['category'])
            
            product = Product(
                name=row['name'],
                sku=row['sku'],
                category=category,
                description=row.get('description', ''),
                unit_price=float(row.get('unit_price', 0)),
                quantity_in_stock=int(row.get('quantity_in_stock', 0)),
                reorder_level=int(row.get('reorder_level', 10)),
                created_by=user
            )
            product.save()
            
            if row.get('suppliers'):
                supplier_names = row['suppliers'].split(',')
                for supplier_name in supplier_names:
                    supplier, _ = Supplier.objects.get_or_create(
                        name=supplier_name.strip(),
                        defaults={
                            'email': f'{supplier_name.strip().lower().replace(" ", "")}@example.com',
                            'phone_number': '000-000-0000',
                            'address': 'Unknown',
                            'city': 'Unknown',
                            'country': 'Unknown'
                        }
                    )
                    product.suppliers.add(supplier)
            
            count += 1
        
        return {'success': True, 'count': count}
    except Exception as e:
        return {'success': False, 'error': str(e)}