from django.urls import path
from mealplan.views import (
    show_mealplan,
    create_mealplan,
    mealplan_detail,
    delete_mealplan,
    toggle_draft_recipe,
    save_mealplan_draft,
    cancel_mealplan_draft,
    update_mealplan,
    edit_mealplan_recipes,
    delete_item,
)

app_name = 'mealplan'

urlpatterns = [
    path('plan/', show_mealplan, name='show_mealplan'),
    path('plan/create/', create_mealplan, name='create_mealplan'),
    path('plan/<int:plan_id>/', mealplan_detail, name='mealplan_detail'),
    path('plan/<int:plan_id>/delete/', delete_mealplan, name='delete_mealplan'),
    path('plan/draft/recipe/<int:recipe_id>/toggle', toggle_draft_recipe, name='toggle_draft_recipe',),
    path('plan/draft/save/', save_mealplan_draft, name='save_mealplan_draft'),
    path('plan/draft/cancel', cancel_mealplan_draft, name='cancel_mealplan_draft',),
    path('plan/<int:plan_id>/edit/', update_mealplan, name='update_mealplan'),
    path('plan/<int:plan_id>/edit-recipes/', edit_mealplan_recipes, name='edit_mealplan_recipes'),
    path('plan/item/<int:item_id>/delete/', delete_item, name='delete_item'),
]