from django.urls import path
from . import views

app_name = 'store_management'

urlpatterns = [
    # Store URLs
    path('', views.StoreListView.as_view(), name='store_list'),  # /stores/
    path('<int:pk>/', views.StoreDetailView.as_view(), name='store_detail'),
    path('add/', views.StoreCreateView.as_view(), name='store_create'),
    path('<int:pk>/edit/', views.StoreUpdateView.as_view(), name='store_update'),
    path('<int:pk>/delete/', views.StoreDeleteView.as_view(), name='store_delete'),
    
    # Department URLs - Fixed patterns
    path('<int:store_id>/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('<int:store_id>/departments/add/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(),  name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
]