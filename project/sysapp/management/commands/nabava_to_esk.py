import json
import jsmin
import re
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from order.models import Narudzba, NarucenArtikal
from nabava.models import Nabava, NabavaItem
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
        send_nabavu(cmd_write, args[0])
        cmd_write = dummy_write

def send_nabavu(cmd_write, nabava_id):

    handle_nabavu(cmd_write, int(nabava_id))

def HandleEskulapNaplatu(narudzbaid):
    # narudzba = Narudzba.objects.get(pk=narudzbaid)
    narudzba = Narudzba.objects.get(broj=narudzbaid)
    narudzba.status = 2
    narudzba.save()
    for na in narudzba.artikli.all():
        na.status = 4
        na.save()

def handle_nabavu(cmd_write, nabava_id):
    try:
        nabava = Nabava.objects.get(id=nabava_id)
        for n in nabava.itemi.order_by('artikal__narudzba__id').values('artikal__narudzba__id').distinct():
#        for n in NabavaItem.objects.filter(nabava__id=nabava.id).values('artikal__narudzba__id'):
            cmd_write('Set narucena za narudzbu %d.\n' % (n['artikal__narudzba__id'],))
#            em.PonudeZ.objects.filter(narudzbaid=n['artikal__narudzba__id']).update(statusidema=SI_NARUCENA)
    except Exception, ex:
        cmd_write('Unable to send data to eskulap.\n%s\n' % (ex,))
        return
