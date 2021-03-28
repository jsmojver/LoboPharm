from django.contrib import admin
from meds.models import Artikal

#class ArtikalAdmin(admin.ModelAdmin):
#  list_display=('id', 'name', 'ZoNr', 'slug', 'kolicina', 'jedinice', 'std_kolicina', 'apoek', 'apovk', 'kvaek', 'hervk', 'ATCCode',)

admin.site.register(Artikal)

