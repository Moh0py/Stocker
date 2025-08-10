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
    """Send expiry alert email"""
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
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    response.write('\ufeff')
    
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
        try:
            decoded_file = csv_file.read().decode('utf-8')
        except UnicodeDecodeError:
            csv_file.seek(0)
            try:
                decoded_file = csv_file.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                csv_file.seek(0)
                decoded_file = csv_file.read().decode('latin-1')
        
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        header_mapping = {
            'Name': 'name',
            'name': 'name',
            'Product Name': 'name',
            'product_name': 'name',
            
            'SKU': 'sku',
            'sku': 'sku',
            'Product Code': 'sku',
            'Code': 'sku',
            
            'Category': 'category',
            'category': 'category',
            'Product Category': 'category',
            
            'Description': 'description',
            'description': 'description',
            'Product Description': 'description',
            
            'Unit Price': 'unit_price',
            'unit_price': 'unit_price',
            'Price': 'unit_price',
            'price': 'unit_price',
            'Cost': 'unit_price',
            
            'Stock': 'quantity_in_stock',
            'stock': 'quantity_in_stock',
            'quantity_in_stock': 'quantity_in_stock',
            'Quantity': 'quantity_in_stock',
            'quantity': 'quantity_in_stock',
            'Qty': 'quantity_in_stock',
            
            'Reorder Level': 'reorder_level',
            'reorder_level': 'reorder_level',
            'reorder': 'reorder_level',
            'Reorder': 'reorder_level',
            'Min Stock': 'reorder_level',
            
            'Suppliers': 'suppliers',
            'suppliers': 'suppliers',
            'Supplier': 'suppliers',
            'supplier': 'suppliers',
            'Vendor': 'suppliers',
            'vendors': 'suppliers',
        }
        
        errors = []
        success_count = 0
        
        for row_num, row in enumerate(reader, start=2):  
            try:
                mapped_row = {}
                for key, value in row.items():
                    if key:  
                        mapped_key = header_mapping.get(key.strip(), key.lower().strip())
                        mapped_row[mapped_key] = value.strip() if value else ''
                
                if not mapped_row.get('name'):
                    errors.append(f"Row {row_num}: Product name is required")
                    continue
                
                if not mapped_row.get('sku'):
                    errors.append(f"Row {row_num}: Product SKU is required")
                    continue
                
                name = mapped_row['name']
                sku = mapped_row['sku']
                
                if Product.objects.filter(sku=sku).exists():
                    errors.append(f"Row {row_num}: Product with SKU '{sku}' already exists")
                    continue
                
                category = None
                if mapped_row.get('category'):
                    category_name = mapped_row['category']
                    category, created = Category.objects.get_or_create(name=category_name)
                    if created:
                        print(f"Created new category: {category_name}")
                
                try:
                    unit_price = float(mapped_row.get('unit_price', 0) or 0)
                    if unit_price < 0:
                        unit_price = 0
                        errors.append(f"Row {row_num}: Price cannot be negative, set to 0")
                except (ValueError, TypeError):
                    unit_price = 0.0
                    errors.append(f"Row {row_num}: Invalid price format, defaulting to 0")
                
                try:
                    quantity_in_stock = int(float(mapped_row.get('quantity_in_stock', 0) or 0))
                    if quantity_in_stock < 0:
                        quantity_in_stock = 0
                        errors.append(f"Row {row_num}: Stock quantity cannot be negative, set to 0")
                except (ValueError, TypeError):
                    quantity_in_stock = 0
                    errors.append(f"Row {row_num}: Invalid stock quantity, defaulting to 0")
                
                try:
                    reorder_level = int(float(mapped_row.get('reorder_level', 10) or 10))
                    if reorder_level < 0:
                        reorder_level = 10
                        errors.append(f"Row {row_num}: Reorder level cannot be negative, set to 10")
                except (ValueError, TypeError):
                    reorder_level = 10
                    errors.append(f"Row {row_num}: Invalid reorder level, defaulting to 10")
                
                product = Product(
                    name=name,
                    sku=sku,
                    category=category,
                    description=mapped_row.get('description', ''),
                    unit_price=unit_price,
                    quantity_in_stock=quantity_in_stock,
                    reorder_level=reorder_level,
                    created_by=user
                )
                product.save()
                
                suppliers_data = mapped_row.get('suppliers', '')
                if suppliers_data and suppliers_data != 'nan' and suppliers_data.lower() != 'null':
                    try:
                        supplier_names = [s.strip() for s in str(suppliers_data).split(',') if s.strip()]
                        for supplier_name in supplier_names:
                            if supplier_name and supplier_name != 'nan':
                                supplier, created = Supplier.objects.get_or_create(
                                    name=supplier_name,
                                    defaults={
                                        'email': f'{supplier_name.lower().replace(" ", "").replace(".", "")}@example.com',
                                        'phone_number': '000-000-0000',
                                        'address': 'Unknown',
                                        'city': 'Unknown',
                                        'country': 'Unknown'
                                    }
                                )
                                product.suppliers.add(supplier)
                                if created:
                                    print(f"Created new supplier: {supplier_name}")
                    except Exception as supplier_error:
                        errors.append(f"Row {row_num}: Error processing suppliers: {str(supplier_error)}")
                
                success_count += 1
                
            except Exception as row_error:
                errors.append(f"Row {row_num}: Unexpected error - {str(row_error)}")
                continue
        
        
        result = {
            'success': success_count > 0,
            'count': success_count,
            'errors': errors,
            'total_processed': success_count + len([e for e in errors if 'Row' in e])
        }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'File reading error: {str(e)}',
            'count': 0,
            'errors': []
        }

def validate_csv_file(csv_file):
    try:
        if not csv_file.name.endswith('.csv'):
            return {'valid': False, 'error': 'File must be a CSV file'}
        
        if csv_file.size > 5 * 1024 * 1024:
            return {'valid': False, 'error': 'File size too large (maximum 5MB)'}
        
        csv_file.seek(0)
        try:
            decoded_file = csv_file.read().decode('utf-8')
        except UnicodeDecodeError:
            csv_file.seek(0)
            decoded_file = csv_file.read().decode('utf-8-sig')
        
        csv_file.seek(0)  
        
        lines = decoded_file.split('\n')
        if len(lines) < 2:
            return {'valid': False, 'error': 'File is empty or does not contain enough data'}
        
        headers = [h.strip() for h in lines[0].split(',')]
        required_headers = ['name', 'Name', 'Product Name', 'product_name']
        
        has_name = any(header in headers for header in required_headers)
        if not has_name:
            return {'valid': False, 'error': 'File must contain a name column (Name or Product Name)'}
        
        return {'valid': True, 'headers': headers, 'row_count': len(lines) - 1}
        
    except Exception as e:
        return {'valid': False, 'error': f'Error validating file: {str(e)}'}