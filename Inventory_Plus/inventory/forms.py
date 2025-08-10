from django import forms
from .models import Product, Category, Supplier, StockMovement
from django.core.exceptions import ValidationError
from datetime import date

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'suppliers', 'description', 
                 'unit_price', 'quantity_in_stock', 'reorder_level', 
                 'is_perishable', 'expiry_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'suppliers': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
       
        self.fields['suppliers'].required = False
        
       
        self.fields['suppliers'].help_text = 'Select suppliers (optional)'
        
        
        for field in self.fields:
            if field != 'suppliers' and field != 'is_perishable':
                self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        is_perishable = cleaned_data.get('is_perishable')
        expiry_date = cleaned_data.get('expiry_date')
        
        if is_perishable and not expiry_date:
            raise ValidationError('Expiry date is required for perishable items.')
        
        if expiry_date and expiry_date < date.today():
            raise ValidationError('Expiry date cannot be in the past.')
        
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'logo', 'email', 'phone_number', 'website', 
                 'address', 'city', 'country']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'logo':
                self.fields[field].widget.attrs['class'] = 'form-control'

class StockUpdateForm(forms.Form):
    MOVEMENT_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]
    
    movement_type = forms.ChoiceField(choices=MOVEMENT_CHOICES)
    quantity = forms.IntegerField(min_value=1)
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ImportForm(forms.Form):
    csv_file = forms.FileField(
        label='Select CSV file',
        help_text='Please upload a CSV file with products data'
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('File must be CSV format.')
        return file