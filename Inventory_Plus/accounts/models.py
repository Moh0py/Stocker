from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def is_employee_user(self):
        return self.user_type == 'employee'
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'