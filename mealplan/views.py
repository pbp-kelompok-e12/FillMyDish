from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import MealPlan, MealPlanItem

from django.http import JsonResponse

@login_required(login_url='/login/')
def show_mealplan(request):
    plans = MealPlan.objects.filter(user=request.user).order_by('-created_at')
    context = {'plans': plans}
    return render(request, 'mealplan.html', context)

def create_mealplan(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            return render(request, 'mealplan_create.html', 
                          {'error': 'Plan title is required.',
                           'title': title,
                           'description': description,
                           })
        plan = MealPlan.objects.create(user=request.user, title=title, description=description)
        request.session['mealplan_pending_plan_id'] = plan.id
        return redirect('saved_recipe')
    return render(request, 'mealplan_create.html')

def mealplan_detail(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    items = plan.items.all()
    context = {
        'plan': plan,
        'items': items,
    }
    return render(request, 'mealplan_detail.html', context)

@require_POST
def delete_item(request, item_id):
    item = get_object_or_404(MealPlanItem, id=item_id, meal_plan__user=request.user)
    plan_id = item.meal_plan.id
    item.delete()
    return JsonResponse({"message": "Item deleted successfully"}, status=200)

@require_POST
def delete_mealplan(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    plan.delete()
    return JsonResponse({"message": "Plan deleted successfully"}, status=200)

@require_POST
def update_mealplan(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    form = MealPlan(request.POST)