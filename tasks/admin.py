from django.contrib import admin
from .models import Task, Completion

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "difficulty", "active", "created_at")
    list_filter = ("active", "difficulty")
    search_fields = ("title", "user__username", "user__email")

@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "user", "date", "completed", "awarded_xp", "created_at")
    list_filter = ("completed", "date")
    search_fields = ("task__title", "user__username", "user__email")
