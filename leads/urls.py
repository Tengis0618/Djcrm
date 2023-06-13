from django.urls import path
from . import views

urlpatterns = [
    path('', views.LeadListView.as_view(), name="leads"),
    path('categories/', views.CategoryListView.as_view(), name = 'category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name = 'category_detail'),
    path('create', views.LeadCreateView.as_view(), name="lead_create"),
    path('<str:pk>', views.LeadDetailView.as_view(), name="lead_detail"),
    path('<str:pk>/update', views.LeadUpdateView.as_view(), name="lead_update"),
    path('<str:pk>/delete', views.LeadDeleteView.as_view(), name="lead_delete"),
    path('<str:pk>/assign_agent/', views.AssignAgentView.as_view(), name="assign_agent"),
    path('<str:pk>/category/', views.LeadCategoryUpdateView.as_view(), name="lead_category_update"),
]
