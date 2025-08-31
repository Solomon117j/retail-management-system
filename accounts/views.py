import logging
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django import forms
from django.views import View
from .models import User
from django.contrib import messages
from e_commerce.models import CustomerAccount
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
# from django.db import DatabaseError


logger = logging.getLogger(__name__)

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'registration/customer_registration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_customer = True
            user.is_employee = False
            user.save()
            
            # Create a CustomerAccount for the user
            try:
                CustomerAccount.objects.create(
                    user=user,
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                    email=user.email,
                    # Other fields will use their default values
                )
            except Exception as e:
                logger.error(f"Error creating CustomerAccount for user {user.id}: {e}")
                # If there's an error creating the CustomerAccount, delete the user
                user.delete()
                messages.error(request, "There was an error creating your account. Please try again.")
                return render(request, 'registration/customer_registration.html', {'form': form})
            
            login(request, user)
            return redirect('e_commerce:customer_account_list')
        return render(request, 'registration/customer_registration.html', {'form': form})

class CustomerLoginView(LoginView):
    template_name = 'registration/customer_login.html'

    def form_valid(self, form):
        user = form.get_user()
        try:
            customer_account = CustomerAccount.objects.get(user=user)
            logger.info(f"Customer login - User ID: {user.id}, Username: {user.username}")
            logger.info(f"User is_customer: {user.is_customer}, is_employee: {user.is_employee}")
        except CustomerAccount.DoesNotExist:
            logger.error(f"Customer account does not exist for User ID: {user.id}, Username: {user.username}")
            messages.error(self.request, "Customer account does not exist. Please contact support.")
            return redirect('accounts:customer_login')
        logger.info(f"User is_customer: {user.is_customer}, is_employee: {user.is_employee}")
        # Handle authentication manually to avoid calling parent method twice
        login(self.request, user)
        logger.info("Login successful, redirecting to customer account list")
        return redirect('e_commerce:customer_account_list')



@method_decorator(csrf_protect, name='dispatch')
class StaffLoginView(LoginView):
    template_name = 'registration/staff_login.html'

    def dispatch(self, request, *args, **kwargs):
        # Log request method and CSRF token for all requests
        logger.info(f"StaffLoginView dispatch - Method: {request.method}")
        if request.method == "POST":
            csrf_token = request.META.get('CSRF_COOKIE')
            post_token = request.POST.get('csrfmiddlewaretoken')
            logger.info(f"CSRF Token Debug - Cookie: {csrf_token}")
            logger.info(f"CSRF Token Debug - POST: {post_token}")
            logger.info(f"CSRF Token Match: {csrf_token == post_token}")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        logger.info(f"Staff login form valid for user: {user.username}")
        
        # Check if user is staff and active
        if not user.is_active:
            messages.error(self.request, "This account is inactive.")
            return redirect('accounts:staff_login')
            
        if not user.is_staff:
            messages.error(self.request, "Staff access required.")
            return redirect('accounts:staff_login')
        
        # Check if user has a staff account (if you have a separate Staff model)
        if hasattr(user, 'employee_profile'):
            # If you have a Staff profile model, check its existence
            staff_account = user.employee_profile  # Correctly access the employee profile
            logger.info(f"User has employee profile: {staff_account}")
            
        login(self.request, user)
        logger.info(f"Staff login successful for user: {user.username}")
        return redirect('dashboards:dashboard')  # Ensure this URL name is correct

    def form_invalid(self, form):
        logger.info(f"Staff login form invalid: {form.errors}")
        return super().form_invalid(form)
class GenericLoginView(View):
    """Presents a choice between customer and staff login."""
    
    def get(self, request):
        return render(request, 'registration/login_choice.html')
