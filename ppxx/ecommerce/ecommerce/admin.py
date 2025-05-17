from django.contrib import admin
from .models import *

@admin.register(CodeCenter)
class CodeCenterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('code', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'availability', 'created_at', 'updated_at', 'get_many_pictures')  # Remplacez par get_many_pictures
    search_fields = ('name', 'description')
    list_filter = ('availability',)

    def get_many_pictures(self, obj):
        """
        Retourne une liste des descriptions ou IDs des images associées.
        """
        return ", ".join([str(picture.description) for picture in obj.many_pictures.all()])

    get_many_pictures.short_description = "Images associées"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'description')
    
    
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'status', 'is_active')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('start_date', 'end_date')  # Si tu veux rendre ces champs en lecture seule
    list_per_page = 10  # Limite de résultats par page

    # Action de filtrage par date d'expiration
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ici, tu peux ajouter des filtres personnalisés si besoin
        return queryset

    def is_active(self, obj):
        return obj.status == 'active'
    is_active.boolean = True  # Affichage d'un icône True/False dans l'admin

    # Si tu veux personnaliser l'affichage du statut
    def status_display(self, obj):
        return dict(Subscription.STATUS_CHOICES).get(obj.status, 'Inconnu')
    status_display.short_description = 'Statut'

admin.site.register(Subscription, SubscriptionAdmin)



class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('date_joined',)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)