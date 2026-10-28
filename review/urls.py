from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('', views.review_list, name='list'),
    path("json/", views.get_reviews_json, name="json"),
    path('create-ajax/', views.create_review_ajax, name='create_ajax'),
    path('<int:pk>/update/', views.review_edit, name='update'),
    path('<int:pk>/delete/', views.delete_review, name='delete'),
]