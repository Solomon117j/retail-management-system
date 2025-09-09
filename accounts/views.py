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
        logger.info(f"Customer login attempt - User ID: {user.id}, Username: {user.username}, Email: {user.email}")
        logger.info(f"User flags - is_customer: {user.is_customer}, is_employee: {user.is_employee}, is_staff: {user.is_staff}, is_active: {user.is_active}")

        # Check if user has customer flag set
        if not user.is_customer:
            logger.warning(f"User {user.username} attempted customer login but is_customer=False")
            messages.error(self.request, "This account is not configured as a customer account.")
            return redirect('accounts:customer_login')

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user {user.username} attempted login")
            messages.error(self.request, "This account is inactive.")
            return redirect('accounts:customer_login')

        try:
            customer_account = CustomerAccount.objects.get(user=user)
            logger.info(f"CustomerAccount found - ID: {customer_account.id}, Email: {customer_account.email}")
        except CustomerAccount.DoesNotExist:
            logger.error(f"CustomerAccount does not exist for User ID: {user.id}, Username: {user.username}")
            logger.error(f"Available CustomerAccount objects: {list(CustomerAccount.objects.values_list('user__username', flat=True))}")
            messages.error(self.request, "Customer account does not exist. Please contact support.")
            return redirect('accounts:customer_login')
        except Exception as e:
            logger.error(f"Unexpected error retrieving CustomerAccount for user {user.username}: {e}", exc_info=True)
            messages.error(self.request, "An unexpected error occurred during login. Please contact support.")
            return redirect('accounts:customer_login')

        # Handle authentication manually to avoid calling parent method twice
        login(self.request, user)
        logger.info(f"Customer login successful for user {user.username}, redirecting to customer account list")
        return redirect('e_commerce:customer_account_list')

    def form_invalid(self, form):
        logger.warning(f"Customer login form invalid - Errors: {form.errors}")
        for field, errors in form.errors.items():
            logger.warning(f"Field '{field}': {errors}")
        return super().form_invalid(form)



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
