from django.contrib import admin

from .models import Annonce


# Register your models here.
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'update_date_time',
                    'localisation',
                    'price',
                    'old_price',
                    'type',
                    'surface',
                    'description',
                    'lien_tag',
                    'mark_as_deleted')
    ordering = ('-update_date_time',)


admin.site.register(Annonce, AnnonceAdmin)
