from django.contrib import admin
from depo.models import *

class DepoAdmin(admin.ModelAdmin):
  list_display=('id', 'naziv',)

class LijekAdmin(admin.ModelAdmin):
  list_display=('id', 'naziv', 'cijena',)
  # list_display=('id', 'naziv', 'cijena', 'ukupni_ulaz', 'ukupna_zarada', 'mjesecna_potrosnja', 'mjesecna_zarada', 'depo', 'stanje', 'min_stanje', 'ima_za_dana', 'preporucena_zaliha', 'ima_prosjecno', 'prosjecno_previse',)

class ZahtjevAdmin(admin.ModelAdmin):
  list_display=('id', 'lijek', 'user', 'status', 'created', 'modified',)

class PosiljkaAdmin(admin.ModelAdmin):
  list_display=('id', 'datum', 'zaduzio', 'lijekovi',)

class PosiljkaLijekAdmin(admin.ModelAdmin):
  list_display=('id', 'lijek', 'kolicina',)

admin.site.register(Depo, DepoAdmin)
admin.site.register(Lijek, LijekAdmin)
admin.site.register(Zahtjev, ZahtjevAdmin)
admin.site.register(Posiljka, PosiljkaAdmin)
admin.site.register(PosiljkaLijek, PosiljkaLijekAdmin)
admin.site.register(PosiljkaLijekKutija)
admin.site.register(LijekKutijaEvents)

