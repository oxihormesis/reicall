from django.contrib import admin

from .models import Campaign, LeadSources, Lead, Call

# Register our models with the basic ModelAdmin
admin.site.register(Campaign, admin.ModelAdmin)
admin.site.register(LeadSources, admin.ModelAdmin)
admin.site.register(Lead, admin.ModelAdmin)
admin.site.register(Call, admin.ModelAdmin)
