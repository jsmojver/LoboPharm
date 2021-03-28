from django.contrib import admin
from fiskalizacija.models import *

class RadnoMjestoAdmin(admin.ModelAdmin):
  list_display=('id', 'ip', 'oznaka', 'djelatnik',)

class RacunAdmin(admin.ModelAdmin):
  list_display=('id', 'djelatnik', 'iznos', 'datum_vrijeme_racun', 'naplatni_uredjaj', 'jir', 'zastitni_kod', 'uuid', 'storno', 'oib_operatera', )

admin.site.register(RadnoMjesto, RadnoMjestoAdmin)
admin.site.register(Racun, RacunAdmin)
admin.site.register(RacunLog)
admin.site.register(PoslovniProstorPoruka)

