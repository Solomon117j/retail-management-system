# store_management/urls.py (app level)
from django.urls import path
from . import views

app_name = 'store_management'

urlpatterns = [
    # Store URLs
    path('', views.StoreListView.as_view(), name='store_list'),
    path('<int:pk>/', views.StoreDetailView.as_view(), name='store_detail'),
    path('add/', views.StoreCreateView.as_view(), name='store_create'),
    path('<int:pk>/edit/', views.StoreUpdateView.as_view(), name='store_update'),
    path('<int:pk>/delete/', views.StoreDeleteView.as_view(), name='store_delete'),
    
    # Department URLs (remove 'stores/' prefix)
    path('<int:store_id>/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('<int:store_id>/departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view() , name='department_detail'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view() , name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # Manager URLs
    path('managers/<int:pk>/subordinates/', views.ManagerSubordinatesView.as_view(), name='manager_subordinates'),
]