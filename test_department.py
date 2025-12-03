from django.contrib.auth import get_user_model
from store_management.models import Department, Store
from store_management.views import DepartmentCreateStandaloneView
from django.test import RequestFactory
from django import forms

User = get_user_model()

# Test 1: User without store
print("Test 1: User without store")
user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'testpass'})
if created:
    user.set_password('testpass')
    user.save()

factory = RequestFactory()
request = factory.post('/stores/departments/create/', {'department_name': 'Test Dept', 'description': 'Test'})
request.user = user

view = DepartmentCreateStandaloneView()
view.request = request

form = view.get_form()
print('Form is valid:', form.is_valid())
if not form.is_valid():
    print('Form errors:', form.errors)
else:
    response = view.form_valid(form)
    print('Form valid, response status:', response.status_code)

# Test 2: User with store
print("\nTest 2: User with store")
store = Store.objects.create(name='Test Store', address='123 Test St', city='Test City', region='Test Region', phone='1234567890', opening_date='2023-01-01')
user_with_store, created = User.objects.get_or_create(username='testuser2', defaults={'password': 'testpass'})
if created:
    user_with_store.set_password('testpass')
    user_with_store.save()
user_with_store.store = store
user_with_store.save()

request2 = factory.post('/stores/departments/create/', {'department_name': 'Test Dept 2', 'description': 'Test 2'})
request2.user = user_with_store

view2 = DepartmentCreateStandaloneView()
view2.request = request2

form2 = view2.get_form()
print('Form is valid:', form2.is_valid())
if not form2.is_valid():
    print('Form errors:', form2.errors)
else:
    response2 = view2.form_valid(form2)
    print('Form valid, response status:', response2.status_code)
    # Check if department was created
    dept = Department.objects.filter(department_name='Test Dept 2').first()
    if dept:
        print('Department created successfully')
    else:
        print('Department not created')
