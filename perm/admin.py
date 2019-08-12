from django.contrib import admin
from .models import Perm
from .models import Signature

# class PermAdmin(admin.ModelAdmin):
#     list_display = ('nom', 'description', 'note', 'remarque')

# admin.site.register(Perm, PermAdmin)

# class SignatureAdmin(admin.ModelAdmin):
#     list_display = ('nom', 'perm', 'date', 'login')

# admin.site.register(Signature, SignatureAdmin)
