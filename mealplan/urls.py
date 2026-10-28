from django.urls import path
from mealplan.views import show_mealplan, create_mealplan, mealplan_detail, delete_mealplan, delete_item

app_name = 'mealplan'

urlpatterns = [
    path('plan/', show_mealplan, name='show_mealplan'),
    path('plan/create/', create_mealplan, name='create_mealplan'),
    path('plan/<int:plan_id>/', mealplan_detail, name='mealplan_detail'),
    path('plan/<int:plan_id>/delete/', delete_mealplan, name='delete_mealplan'),
    path('plan/item/<int:item_id>/delete/', delete_item, name='delete_item'),
]