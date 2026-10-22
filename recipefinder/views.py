from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied   
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
import datetime
from django.views.decorators.http import require_POST
# Create your views here.
# @login_required(login_url="")
def find_recipe(request):
    return render(request, "find.html")

# @login_required(login_url="")
def input_ingredients(request):
    return render(request, "input.html")