from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Review

# Create your views here.
def review_list(request):
    reviews = Review.objects.filter(is_visible=True).select_related('user')
    return render(request, 'review_list.html', {'reviews': reviews})

@login_required
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

@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review:list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review_form.html', {'form':form})

@login_required
@require_POST
def review_delete(request,pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    review.delete()
    return redirect("review:list")

