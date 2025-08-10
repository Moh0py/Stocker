from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import Profile, User



class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('inventory:dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        messages.success(self.request, 'Account created successfully! Please login.')
        return response


class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


def sign_up(request: HttpRequest):
    if request.method == "POST":
        try:
            with transaction.atomic():
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password"],
                    email=request.POST.get("email", ""),
                    first_name=request.POST.get("first_name", ""),
                    last_name=request.POST.get("last_name", "")
                )
                
                profile = Profile.objects.create(
                    user=new_user,
                    about=request.POST.get("about", ""),
                    department=request.POST.get("department", ""),
                    employee_id=request.POST.get("employee_id", ""),
                    avatar=request.FILES.get("avatar", Profile._meta.get_field('avatar').default)
                )

            messages.success(request, "User registered successfully")
            return redirect("accounts:login")
        
        except IntegrityError as e:
            messages.error(request, "Username already exists, please choose another one")
        except Exception as e:
            messages.error(request, "Could not register user, please try again")
            print(f"Error in sign_up: {e}")
    
    return render(request, "accounts/signup.html")


@login_required
def update_user_profile(request: HttpRequest):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                user = request.user
                user.first_name = request.POST.get("first_name", user.first_name)
                user.last_name = request.POST.get("last_name", user.last_name)
                user.email = request.POST.get("email", user.email)
                user.save()

                profile.about = request.POST.get("about", "")
                profile.department = request.POST.get("department", profile.department)
                profile.employee_id = request.POST.get("employee_id", profile.employee_id)
                
                if "avatar" in request.FILES:
                    profile.avatar = request.FILES["avatar"]
                
                profile.save()

            messages.success(request, "Profile updated successfully")
            return redirect("accounts:profile", user_name=user.username)
            
        except Exception as e:
            messages.error(request, "Could not update profile")
            print(f"Error updating profile: {e}")

    return render(request, "accounts/update_profile.html", {"profile": profile})


def sign_in(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("inventory:dashboard")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            next_url = request.GET.get("next", "inventory:dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "accounts/signin.html")


@login_required
def log_out(request: HttpRequest):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("accounts:login")


def user_profile_view(request:HttpRequest, user_name):

    try:
        user = User.objects.get(username=user_name)
        if not Profile.objects.filter(user=user).first():
            new_profile = Profile(user=user)
            new_profile.save()
        
    except Exception as e:
        print(e)
        return render(request,'404.html')
    

    return render(request, 'accounts/profile.html', {"user" : user})

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    products_count = Product.objects.filter(created_by=request.user).count() if hasattr(Product, 'created_by') else 0
    suppliers_count = Supplier.objects.count()
    movements_count = StockMovement.objects.filter(performed_by=request.user).count()
    recent_movements = StockMovement.objects.filter(performed_by=request.user).select_related('product')[:5]

    return render(request, 'accounts/profile.html', {
        "user": request.user,
        "profile": profile,
        "products_count": products_count,
        "suppliers_count": suppliers_count,
        "movements_count": movements_count,
        "recent_movements": recent_movements
    })