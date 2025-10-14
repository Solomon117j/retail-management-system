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
    path('export/', views.store_export, name='store_export'),

    # Department URLs (store_id is UUID)
    path('<uuid:store_id>/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('<uuid:store_id>/departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<uuid:pk>/', views.DepartmentDetailView.as_view() , name='department_detail'),
    path('departments/<uuid:pk>/edit/', views.DepartmentUpdateView.as_view() , name='department_edit'),
    path('departments/<uuid:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    path('departments/export/', views.department_export, name='department_export'),
]
