from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('', views.review_list, name='list'),
    path('add/', views.review_add, name='add'),
    path('<int:pk>/edit/', views.review_edit, name='edit'),
    path('<int:pk>/delete/', views.review_delete, name='delete'),
]