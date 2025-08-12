from django.urls import path
from . import views
from .views import CustomLoginView, SignUpView, CustomLogoutView 

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/update/', views.update_user_profile, name="update_user_profile"),  
    path('profile/<str:user_name>/', views.user_profile_view, name="user_profile_view"),  
]