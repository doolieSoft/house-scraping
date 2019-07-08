from django.db import models
from django.utils.safestring import mark_safe


# Create your models here.
class Annonce(models.Model):
    id = models.BigIntegerField(primary_key=True)
    price = models.CharField(max_length=20)
    old_price = models.CharField(max_length=20)
    localisation = models.CharField(max_length=50)
    type_house = models.CharField(max_length=50)
    surface = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    lien = models.URLField()
    update_date_time = models.DateTimeField(auto_now=True)
    mark_as_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.type_house + " | " + self.localisation

    # def image_tag(self):
    #     return mark_safe('<img src="%s" width="130" />' % self.image.url)

    def lien_tag(self):
        return mark_safe('<a href="{}">{}</a>'.format(self.lien, self.lien))
