from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import MealPlan, MealPlanItem

@login_required(login_url='/login/')
def show_mealplan(request):
    plans = MealPlan.objects.filter(user=request.user).order_by('-created_at')
    context = {'plans': plans}
    return render(request, 'mealplan.html', context)

@login_required(login_url='/login/')
def create_mealplan(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        if title:
            MealPlan.objects.create(
                user=request.user,
                title=title,
                description=description
            )
        return redirect('mealplan:show_mealplan')
    return render(request, 'mealplan_create.html')

@login_required(login_url='/login/')
def mealplan_detail(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    items = plan.items.all()
    context = {
        'plan': plan,
        'items': items,
    }
    return render(request, 'mealplan_detail.html', context)

@login_required(login_url='/login/')
@require_POST
def delete_item(request, item_id):
    item = get_object_or_404(MealPlanItem, id=item_id, meal_plan__user=request.user)
    plan_id = item.meal_plan.id
    item.delete()
    return redirect('mealplan:mealplan_detail', plan_id=plan_id)

@login_required(login_url='/login/')
@require_POST
def delete_mealplan(request, plan_id):
    plan = get_object_or_404(MealPlan, id = plan_id, user=request.user)
    plan.delete()
    return redirect('mealplan:show_plans')