from django.contrib import admin

from .models import Annonce


# Register your models here.
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('id_annonce',
                    'last_update_time',
                    'localisation',
                    'price',
                    'old_price',
                    'type_house',
                    'surface',
                    'description',
                    'lien_tag',
                    'mark_as_deleted')
    ordering = ('-last_update_time',)


admin.site.register(Annonce, AnnonceAdmin)
