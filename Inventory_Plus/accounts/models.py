from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def is_employee_user(self):
        return self.user_type == 'employee'