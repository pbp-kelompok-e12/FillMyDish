from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from FillMyDish.models import Profile
from .forms import ReviewForm
from .models import Review

# Create your views here.
def review_list(request):
    context = {
        "form":ReviewForm(),
    }

    return render(request, "review_list.html", context)

def get_reviews_json(request):
    reviews = Review.objects.filter(is_visible=True).select_related('user')

    data = []

    for review in reviews:
        profile = getattr(review.user, "profile", None)
        profile_image = profile.profile_image.url if profile and profile.profile_image else ""
        profile_username = profile.username if profile and profile.username else review.user.username
        data.append({
            "pk":str(review.pk),
            "fields":{
                "user":review.user.username,
                "profile_username": profile_username,
                "profile_image": profile_image,
                "profile_url": reverse("user_profile", kwargs={"username": review.user.username}),
                "is_owner": review.user_id == request.user.id,
                "message":review.message,
                "created_at":review.created_at,
                "updated_at":review.updated_at,
            },
        })
    return JsonResponse(data, safe=False)

@require_POST
def create_review_ajax(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message":"Silakan login terlebih dahulu"}, status=401)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit = False)
        review.user = request.user
        review.save()
        return JsonResponse(
            {"message":"Review berhasil ditambahkan.",
             "pk":str(review.pk)}, status = 201
        )
    return JsonResponse({"errors":form.errors.get_json_data()}, status=400)

@login_required(login_url="/login")
def review_add(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('review:list')
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form':form})

@login_required(login_url="/login")
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review berhasil diperbarui!")
            return redirect('review:list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'update_review.html', {'form':form})

@login_required(login_url="/login")
@require_POST
def delete_review(request,pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    
    if request.method == "POST":
        review.delete()
        messages.success(request, "Review berhasil dihapus!")

    return redirect("review:list")



