from django.contrib import admin
from .models import GradingReport

@admin.register(GradingReport)
class GradingReportAdmin(admin.ModelAdmin):
    list_display  = ('team', 'phase', 'supervisor', 'chief_grade',
                      'examiner_one_grade', 'examiner_two_grade', 'final_grade', 'created_at')
    list_filter   = ('phase',)
    search_fields = ('team__name', 'supervisor__display_name')
    readonly_fields = ('final_grade', 'created_at')
