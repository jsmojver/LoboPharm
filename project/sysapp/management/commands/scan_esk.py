import json
import jsmin
import re
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from order.models import Narudzba, NarucenArtikal
from meds.models import ListaHZZO, AtcCode
from eskulap import models as em

# eskulap statuses
SE_NONE = 0
SE_FISKALIZIRANA = 1
SE_IZDANA = 2

# idema statuses
SI_NONE = 0
SI_NARUCENA = 1
SI_ZAKLJUCENA = 2

def dummy_write(*args, **kwargs):
    pass

cmd_write = dummy_write

class Command(BaseCommand):
    args = ''
    help = 'imports data from eskulap'
    option_list = BaseCommand.option_list + (
            make_option('-p', '--print', dest='print',
                        help='print imported data',
                        action='store_true',
                        default=False),
            )

    def handle(self, *args, **options):
        global cmd_write
        # self.stdout.write('Options %s, args %s' % (options, args))
        if options['print']:
            cmd_write = self.stdout.write
        scan(cmd_write)
        cmd_write = dummy_write

def scan(cmd_write):

    handle_fiskalizirane(cmd_write)
    handle_izdane(cmd_write)

def HandleEskulapNaplatu(narudzbaid):
    # narudzba = Narudzba.objects.get(pk=narudzbaid)
    narudzba = Narudzba.objects.get(broj=narudzbaid)
    if 1 == narudzba.status:
        narudzba.status = 2
        narudzba.save()
        for na in narudzba.artikli.all():
            na.status = 4
            na.save()

def handle_fiskalizirane(cmd_write):
    try:
        ponude = em.PonudeZ.objects.filter(statuseskulap=SE_FISKALIZIRANA).all()
    except Exception, ex:
        cmd_write('Unable to access eskulap data.\n%s\n' % (ex,))
        return
    cmd_write('%d ponuda found.\n' % (ponude.count()))
    # handle each ponuda
    for p in ponude:
        cmd_write('Ponuda %d za %s.\n' % (p.narudzbaid, p.kupac))
        # update data in our tables
        HandleEskulapNaplatu(p.narudzbaid)
        # update eskulap interface data
        # in new Django
        #p.statusidema = SI_NARUCENA
        #p.save(update_fields=['statusidema'])
        # will be set after 'Narucen od dobavljaca'
        #em.PonudeZ.objects.filter(id=p.id).update(statusidema=SI_NARUCENA)

def HandleEskulapIsporuku(narudzbaid):
    # narudzba = Narudzba.objects.get(pk=narudzbaid)
    narudzba = Narudzba.objects.get(broj=narudzbaid)
    narudzba.status = 6
    narudzba.save()
    for na in narudzba.artikli.all():
        na.status = 5
        na.save()

def handle_izdane(cmd_write):
    try:
        ponude = em.PonudeZ.objects.exclude(statusidema=SI_ZAKLJUCENA).filter(statuseskulap=SE_IZDANA).all()
    except Exception, ex:
        cmd_write('Unable to access eskulap data.\n%s\n' % (ex,))
        return
    cmd_write('%d ponuda found.\n' % (ponude.count()))
    # handle each ponuda
    for p in ponude:
        cmd_write('Ponuda %d za %s.\n' % (p.narudzbaid, p.kupac))
        # update data in our tables
        HandleEskulapIsporuku(p.narudzbaid)
        # update eskulap interface data
        # in new Django
        #p.statusidema = SI_ZAKLJUCENA
        #p.save(update_fields=['statusidema'])
        em.PonudeZ.objects.filter(id=p.id).update(statusidema=SI_ZAKLJUCENA)
