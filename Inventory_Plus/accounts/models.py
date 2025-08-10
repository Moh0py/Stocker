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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="images/avatars/", default="images/avatars/avatar.webp")
    department = models.CharField(max_length=100, blank=True, verbose_name='sections')
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name='emoplye number')
    
    def __str__(self) -> str:
        return f"Profile {self.user.username}"
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        unique_together = ['user', 'product']  