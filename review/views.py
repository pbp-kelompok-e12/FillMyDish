from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def review_list(request):
    return HttpResponse('Review list')

def review_add(request):
    return HttpResponse('Add review')

def review_edit(request, pk):
    return HttpResponse(f'Edit review {pk}')

def review_delete(request,pk):
    return HttpResponse(f'Delete review {pk}')

