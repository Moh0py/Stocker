from django.urls import path
from .views import CustomLoginView, SignUpView, CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]