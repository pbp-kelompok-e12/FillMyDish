from django.contrib import admin
from .models import Review
# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user','message','is_visible','created_at')
    list_filter = ('is_visible', 'created_at')
    search_fields = ('user__username','message')
