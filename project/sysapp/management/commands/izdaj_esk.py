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

    handle_narucene_narudzbe(cmd_write)

def handle_narucene_narudzbe(cmd_write):
    try:
        em.PonudeZ.objects.filter(statuseskulap=SE_FISKALIZIRANA, statusideme=SI_NARUCENA).update(statuseskulap=SE_IZDANA)
    except Exception, ex:
        cmd_write('Unable to access eskulap data.\n%s\n' % (ex,))
        return
