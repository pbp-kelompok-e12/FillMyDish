from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse

from saved_recipe.models import SavedRecipe

from .models import MealPlan, MealPlanItem

@login_required(login_url='/login/')
def show_mealplan(request):
    plans = MealPlan.objects.filter(user=request.user).order_by('-created_at')
    context = {'plans': plans}
    return render(request, 'mealplan.html', context)

@login_required(login_url='/login/')
def create_mealplan(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            return render(
                request,
                'mealplan_create.html', 
                {'error': 'Plan title is required.',
                'title': title,
                'description': description,
                },
            )

        request.session.pop('mealplan_edit_draft', None)
        request.session['mealplan_draft'] = {
            'title': title,
            'description': description,
            'recipe_ids': [],
        }
        return redirect('saved_recipe')
    return render(request, 'mealplan_create.html')

@login_required(login_url='/login/')
@require_POST
def toggle_draft_recipe(request, recipe_id):
    if 'mealplan_draft' in request.session:
        draft_key = 'mealplan_draft'
    elif 'mealplan_edit_draft' in request.session:
        draft_key = 'mealplan_edit_draft'
    else:
        return JsonResponse({'message': 'There is no meal plan in progress.'},status=400,)

    draft = request.session[draft_key]
    recipe = get_object_or_404(SavedRecipe, pk=recipe_id, user=request.user,)
    recipe_ids = draft.get('recipe_ids', [])

    if recipe_id in recipe_ids:
        recipe_ids.remove(recipe_id)
        added = False
    else:
        recipe_ids.append(recipe_id)
        added = True

    draft['recipe_ids'] = recipe_ids
    request.session[draft_key] = draft

    return JsonResponse({'success': True, 'added': added, 'message': ('Recipe added to plan.' if added else 'Recipe removed from plan.'),})

@login_required(login_url='/login/')
@require_POST
def save_mealplan_draft(request):
    draft = request.session.get("mealplan_draft")

    if not draft:
        return JsonResponse({"message": "There is no meal plan to save."}, status=400,)

    title = draft.get("title", "").strip()
    description = draft.get("description", "").strip()
    recipe_ids = draft.get("recipe_ids", [])

    if not title:
        return JsonResponse({"message": "Plan title is required."}, status=400,)
    if not recipe_ids:
        return JsonResponse({"message": "Add at least one recipe before saving the plan."}, status=400,)

    recipes = SavedRecipe.objects.filter(user=request.user, pk__in=recipe_ids,)
    recipes_by_id = {recipe.pk: recipe for recipe in recipes}

    if len(recipes_by_id) != len (recipe_ids):
        return JsonResponse({"message": "One or more selected recipes are no longer available."}, status=400,)

    with transaction.atomic():
        plan = MealPlan.objects.create(user=request.user, title=title, description=description,)

        MealPlanItem.objects.bulk_create([
            MealPlanItem(
                meal_plan=plan,
                recipe=recipes_by_id[recipe_id],
                order=order,
            )
            for order, recipe_id in enumerate(recipe_ids)
            ])

    request.session.pop("mealplan_draft", None)

    return JsonResponse({
        "success": True,
        "redirect_url": reverse(
            "mealplan:mealplan_detail",
            args=[plan.pk],
        ),
    })

@login_required(login_url='/login/')
@require_POST
def cancel_mealplan_draft(request):
    request.session.pop("mealplan_draft", None)
    return redirect("mealplan:show_mealplan")

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
    return JsonResponse({"message": "Item deleted successfully"}, status=200)

@login_required(login_url='/login/')
@require_POST
def delete_mealplan(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    plan.delete()
    return JsonResponse({"message": "Plan deleted successfully"}, status=200)

@login_required(login_url='/login/')
def edit_mealplan_recipes(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user,)
    edit_draft = request.session.get('mealplan_edit_draft')

    if not edit_draft or edit_draft.get('plan_id') != plan.id:
        edit_draft = {
            'plan_id': plan.id,
            'title': plan.title,
            'description': plan.description or '',
            'recipe_ids': list(plan.items.order_by('order').values_list('recipe_id', flat=True,)),
        }
    else:
        edit_draft.setdefault(
            'recipe_ids',
            list(plan.items.order_by('order').values_list('recipe_id', flat=True,)),
        )

    request.session['mealplan_edit_draft'] = edit_draft
    plan.title = edit_draft['title']
    plan.description = edit_draft['description']

    recipe_ids = edit_draft.get('recipe_ids', [])
    recipes = SavedRecipe.objects.filter(
        user=request.user,
        id__in=recipe_ids,
    )
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    items = [
        {'recipe': recipes_by_id[recipe_id]}
        for recipe_id in recipe_ids
        if recipe_id in recipes_by_id
    ]

    return render(
        request,
        'mealplan_detail.html',
        {
            'plan': plan,
            'items': items,
            'edit_mode': True,
        },
    )

@login_required(login_url='/login/')
def update_mealplan(request, plan_id):
    plan = get_object_or_404(
        MealPlan,
        id=plan_id,
        user=request.user,
    )

    if request.method == 'POST':
        edit_draft = request.session.get('mealplan_edit_draft')

        if request.POST.get('action') == 'cancel':
            if edit_draft and edit_draft.get('plan_id') == plan.id:
                request.session.pop('mealplan_edit_draft', None)

            return redirect(
                'mealplan:mealplan_detail',
                plan_id=plan.id,
            )

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if not title:
            return render(
                request,
                'mealplan_edit.html',
                {
                    'plan': plan,
                    'error': 'Plan title is required.',
                    'title': title,
                    'description': description,
                },
                status=400,
            )

        if not edit_draft or edit_draft.get('plan_id') != plan.id:
            edit_draft = {
                'plan_id': plan.id,
                'recipe_ids': list(
                    plan.items.order_by('order').values_list(
                        'recipe_id',
                        flat=True,
                    )
                ),
            }

        edit_draft['title'] = title
        edit_draft['description'] = description
        request.session['mealplan_edit_draft'] = edit_draft

        return redirect(
            'mealplan:edit_mealplan_recipes',
            plan_id=plan.id,
        )

    request.session.pop('mealplan_draft', None)
    request.session['mealplan_edit_draft'] = {
        'plan_id': plan.id,
        'title': plan.title,
        'description': plan.description or '',
        'recipe_ids': list(
            plan.items.order_by('order').values_list(
                'recipe_id',
                flat=True,
            )
        ),
    }

    return render(
        request,
        'mealplan_edit.html',
        {'plan': plan},
    )

@login_required(login_url='/login/')
@require_POST
def save_mealplan_recipe_changes(request, plan_id):
    plan = get_object_or_404(
        MealPlan,
        id=plan_id,
        user=request.user,
    )

    edit_draft = request.session.get('mealplan_edit_draft')

    if not edit_draft or edit_draft.get('plan_id') != plan.id:
        edit_draft = {
            'title': plan.title,
            'description': plan.description or '',
            'recipe_ids': list(
                plan.items.order_by('order').values_list(
                    'recipe_id',
                    flat=True,
                )
            ),
        }

    if request.POST.get('action') == 'cancel':
        request.session.pop('mealplan_edit_draft', None)
        return redirect(
            'mealplan:mealplan_detail',
            plan_id=plan.id,
        )

    recipe_ids = list(dict.fromkeys(edit_draft.get('recipe_ids', [])))

    deleted_item_ids = request.POST.getlist('items_to_delete')
    deleted_recipe_ids = set(
        plan.items.filter(
            id__in=deleted_item_ids,
        ).values_list('recipe_id', flat=True)
    )
    recipe_ids = [
        recipe_id
        for recipe_id in recipe_ids
        if recipe_id not in deleted_recipe_ids
    ]

    recipes = SavedRecipe.objects.filter(
        user=request.user,
        id__in=recipe_ids,
    )
    available_recipe_ids = set(
        recipes.values_list('id', flat=True)
    )

    if len(available_recipe_ids) != len(recipe_ids):
        return redirect(
            'mealplan:edit_mealplan_recipes',
            plan_id=plan.id,
        )

    with transaction.atomic():
        plan.title = edit_draft['title']
        plan.description = edit_draft['description']
        plan.save(update_fields=['title', 'description'])

        plan.items.exclude(recipe_id__in=recipe_ids).delete()

        existing_items = {
            item.recipe_id: item
            for item in plan.items.all()
        }

        for order, recipe_id in enumerate(recipe_ids):
            item = existing_items.get(recipe_id)

            if item:
                if item.order != order:
                    item.order = order
                    item.save(update_fields=['order'])
            else:
                MealPlanItem.objects.create(
                    meal_plan=plan,
                    recipe_id=recipe_id,
                    order=order,
                )

    request.session.pop('mealplan_edit_draft', None)

    return redirect(
        'mealplan:mealplan_detail',
        plan_id=plan.id,
    )
