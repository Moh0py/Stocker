from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Product, Category, Supplier, StockMovement
from .forms import ProductForm, CategoryForm, SupplierForm, StockUpdateForm, ImportForm
from .utils import send_low_stock_alert, send_expiry_alert, export_to_csv, import_from_csv
import csv
from datetime import datetime, timedelta


# Helper functions for permission checks
def is_admin(user):
    """Check if user is admin (using user_type field)"""
    return user.is_authenticated and hasattr(user, 'is_admin_user') and user.is_admin_user()

def is_admin_or_staff(user):
    """Check if user is admin, staff, or superuser"""
    if not user.is_authenticated:
        return False
    return (hasattr(user, 'is_admin_user') and user.is_admin_user()) or user.is_staff or user.is_superuser


# Mixins for permission checks
class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user is admin"""
    def test_func(self):
        return is_admin_or_staff(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to perform this action.')
        return redirect('inventory:dashboard')


# Dashboard View
@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    low_stock_products = Product.objects.filter(quantity_in_stock__lte=F('reorder_level')).count()
    
    recent_movements = StockMovement.objects.select_related('product', 'performed_by')[:10]
    low_stock_items = Product.objects.filter(quantity_in_stock__lte=F('reorder_level'))[:5]
    
    # Show expiring products only to admins
    if is_admin_or_staff(request.user):
        expiring_products = Product.objects.filter(
            is_perishable=True,
            expiry_date__lte=datetime.now().date() + timedelta(days=7)
        )[:5]
    else:
        expiring_products = None
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock_products': low_stock_products,
        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items,
        'expiring_products': expiring_products,
    }
    return render(request, 'inventory/dashboard.html', context)


# Product Views - Employees can view, add, update (but not delete)
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('suppliers')
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        supplier = self.request.GET.get('supplier')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if supplier:
            queryset = queryset.filter(suppliers__id=supplier)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['suppliers'] = Supplier.objects.all()
        return context



class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = self.object.stock_movements.all()[:10]
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("Form errors:", form.errors)
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def update_stock(request, pk):
    """Employees and admins can update stock"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            movement_type = form.cleaned_data['movement_type']
            quantity = form.cleaned_data['quantity']
            
            if movement_type == 'in':
                product.quantity_in_stock += quantity
            elif movement_type == 'out':
                if product.quantity_in_stock >= quantity:
                    product.quantity_in_stock -= quantity
                else:
                    messages.error(request, 'Insufficient stock!')
                    return redirect('inventory:update_stock', pk=pk)
            else:
                product.quantity_in_stock = quantity
            
            product.save()
            
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                reason=form.cleaned_data['reason'],
                performed_by=request.user
            )
            
            if product.is_low_stock():
                send_low_stock_alert(product)
            
            messages.success(request, 'Stock updated successfully!')
            return redirect('inventory:product_detail', pk=pk)
    else:
        form = StockUpdateForm()
    
    return render(request, 'stock/stock_update.html', {'form': form, 'product': product})



class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10


class CategoryCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        return context


class SupplierCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Supplier created successfully!')
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Supplier updated successfully!')
        return super().form_valid(form)


class SupplierDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Supplier deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Report Views - Available to all logged-in users
@login_required
def inventory_report(request):
    products = Product.objects.select_related('category').prefetch_related('suppliers')
    total_value = sum(p.get_total_value() for p in products)
    low_stock_count = products.filter(quantity_in_stock__lte=F('reorder_level')).count()
    out_of_stock_count = products.filter(quantity_in_stock=0).count()
    
    categories_data = Category.objects.annotate(
        product_count=Count('products'),
        total_value=Sum(F('products__quantity_in_stock') * F('products__unit_price'))
    )
    
    context = {
        'products': products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'categories_data': categories_data,
        'report_date': datetime.now(),
    }
    
    if request.GET.get('export') == 'csv':
        return export_to_csv(products, 'inventory_report')
    
    return render(request, 'reports/inventory_report.html', context)


@login_required
def supplier_report(request):
    suppliers = Supplier.objects.annotate(
        product_count=Count('products'),
        total_products_value=Sum(
            F('products__quantity_in_stock') * F('products__unit_price')
        )
    )
    
    context = {
        'suppliers': suppliers,
        'report_date': datetime.now(),
    }
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="supplier_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Supplier Name', 'Email', 'Phone', 'Product Count', 'Total Value'])
        
        for supplier in suppliers:
            writer.writerow([
                supplier.name,
                supplier.email,
                supplier.phone_number,
                supplier.product_count,
                supplier.total_products_value or 0
            ])
        
        return response
    
    return render(request, 'reports/supplier_report.html', context)


# Import/Export - Only admins
@login_required
@user_passes_test(is_admin_or_staff)
def import_products(request):
    """Only admins can import products"""
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            result = import_from_csv(csv_file, request.user)
            if result['success']:
                messages.success(request, f"Successfully imported {result['count']} products!")
            else:
                messages.error(request, f"Error importing products: {result['error']}")
            return redirect('inventory:product_list')
    else:
        form = ImportForm()
    
    return render(request, 'products/import.html', {'form': form})


@login_required
def export_products(request):
    """Everyone can export products"""
    products = Product.objects.select_related('category').prefetch_related('suppliers')
    return export_to_csv(products, 'products_export')