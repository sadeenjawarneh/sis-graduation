from django.contrib import admin

from .models import Proposal


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'status', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('title',)
