from django.contrib import admin

from .models import Problem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "time_limit", "memory_limit", "created_at")
    list_filter = ("difficulty",)
    search_fields = ("title", "description")
