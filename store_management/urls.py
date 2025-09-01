# store_management/urls.py (app level)
from django.urls import path
from . import views

app_name = 'store_management'

urlpatterns = [
    # Store URLs (UUID primary keys)
    path('', views.StoreListView.as_view(), name='store_list'),
    path('<uuid:pk>/', views.StoreDetailView.as_view(), name='store_detail'),
    path('add/', views.StoreCreateView.as_view(), name='store_create'),
    path('<uuid:pk>/edit/', views.StoreUpdateView.as_view(), name='store_update'),
    path('<uuid:pk>/delete/', views.StoreDeleteView.as_view(), name='store_delete'),
    
    # Department URLs (store_id is UUID)
    path('<uuid:store_id>/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('<uuid:store_id>/departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<uuid:pk>/', views.DepartmentDetailView.as_view() , name='department_detail'),
    path('departments/<uuid:pk>/edit/', views.DepartmentUpdateView.as_view() , name='department_edit'),
    path('departments/<uuid:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Employee URLs (UUID primary keys)
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<uuid:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),

    # Manager URLs (Employee PK is UUID)
    path('managers/<uuid:pk>/subordinates/', views.ManagerSubordinatesView.as_view(), name='manager_subordinates'),
]