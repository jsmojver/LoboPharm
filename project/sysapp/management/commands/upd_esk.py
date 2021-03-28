import json
import jsmin
import re
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from order.models import ArtikalDrugoTrziste
from meds.models import Artikal
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
    help = 'updates artikles in eskulap'
    option_list = BaseCommand.option_list + (
            make_option('-p', '--print', dest='print',
                        help='print updated',
                        action='store_true',
                        default=False),
            )

    def handle(self, *args, **options):
        global cmd_write
        # self.stdout.write('Options %s, args %s' % (options, args))
        if options['print']:
            cmd_write = self.stdout.write
        update(cmd_write)
        cmd_write = dummy_write

def update(cmd_write):

    update_artikli(cmd_write)

def GetArtikalData(art_ime, trziste):
    res = ''
    try:
        if 'Njemacka' == trziste:
            ar = Artikal.objects.get(name=art_ime)
            res = (ar.kolicina,)
        else:
            ar = ArtikalDrugoTrziste.objects.get(ime=art_ime, trziste__naziv=trziste)
            res = (ar.kolicina,)
    except:
        pass
    return res

def update_artikli(cmd_write):
    try:
        artikli = em.Artikal.objects.all()
    except Exception, ex:
        cmd_write('Unable to access eskulap data.\n%s\n' % (ex,))
        return
    cmd_write('%d artikals found.\n' % (artikli.count()))
    # handle each artikal
    for a in artikli:
        # update eskulap interface data
        d = GetArtikalData(a.naziv, a.trziste)
        # in new Django
        #a.pakiranje = d[0]
        #a.save(update_fields=['pakiranje'])
        # currently
        em.Artikal.objects.filter(id=a.id).update(pakiranje=d[0])
        cmd_write('Artikal %s pakiranje %s.\n' % (a.naziv, d[0]))
