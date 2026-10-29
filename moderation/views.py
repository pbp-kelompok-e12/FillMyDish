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

from moderation.models import SuspiciousRequest
# Create your views here.
@login_required(login_url="/login")
def show_logs(request):
    if not request.user.is_moderator:
        return redirect("main:show_main")
    return render(request, "logs.html")

@login_required(login_url="/login")
def logs_list(request):
    if not request.user.is_moderator:
        return redirect("main:show_main")
    logs = SuspiciousRequest.objects.all()
    return render(request, 'logs/_logs.html', {'logs': logs})

@login_required(login_url="/login")
def review(request, log_id):
    if not request.user.is_moderator:
        return redirect("main:show_main")
    log = get_object_or_404(SuspiciousRequest, pk=log_id)
    is_htmx = request.headers.get('HX-Request')

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in (SuspiciousRequest.Status.CLEARED, SuspiciousRequest.Status.FLAGGED):
            log.status = status
            log.save()
            reported_user = log.user
            if status == SuspiciousRequest.Status.FLAGGED:
                reported_user.is_banned = not reported_user.is_moderator
                reported_user.save()
            elif status == SuspiciousRequest.Status.CLEARED:
                reported_user.is_banned = False
                reported_user.save()
        if is_htmx:
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'reviewed'
            return response
        return redirect('moderation:logs')

    template = 'logs/_review.html' if is_htmx else 'logs/review.html'
    return render(request, template, {'log': log})