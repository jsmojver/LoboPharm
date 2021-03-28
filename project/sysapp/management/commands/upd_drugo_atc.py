import json
import jsmin
import re
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from order.models import ArtikalDrugoTrziste, Trziste
from meds.models import ListaHZZO, AtcCode
from openpyxl import load_workbook
from openpyxl.cell import column_index_from_string
from optparse import make_option

cmd_write = None

class Command(BaseCommand):
    args = 'excel_file ...>'
    help = 'Updates pdv for hzzo list'
    option_list = BaseCommand.option_list + (
            make_option('-c', '--cfg', dest='cfg_file',
                        help='parser configuration file',
                        default=None),
            )

    def handle(self, *args, **options):
        global cmd_write
        # self.stdout.write('Options %s, args %s' % (options, args))
        if len(args) < 1:
            self.stdout.write('Missing excel_file argument.\n')
            return
        cmd_write = self.stdout.write
        xparse(args[0], options['cfg_file'])
        cmd_write = None

default_cfg = {
        'sheet_name' : 'wirkstoffe',
        'start_row' : 2,
        'trziste' : 'Austrija',
        'key' : 'ime',
        'columns' : {
            'ime' : 'B',
            'atc_sifra' : 'D'
            }
        }

def xparse(ex_file, cfg_file=None):
    cfg = {}
    cfg.update(default_cfg)
    if None != cfg_file:
        f = open(cfg_file)
        b = f.read()
        cfg.update(json.loads(jsmin.jsmin(b)))

    try:
        trziste = Trziste.objects.get(naziv=cfg['trziste'])
    except:
        cmd_write('Nepoznato trziste, provjerite konfiguraciju.')
        return
    get_atc_sifra = create_get_atc_sifra(cfg['columns'])
    get_filter_dict = create_get_filter_dict(trziste, cfg['key'], cfg['columns'])

    wb = load_workbook(ex_file)
    sh = wb[cfg['sheet_name']]
    start_row = cfg['start_row']

    for n,r in enumerate(sh.rows[start_row - 1:],start_row):
        ATC = get_ATC(get_atc_sifra(r))
        fd = get_filter_dict(r)
        print ATC.sifra if ATC else None
        print fd
        ArtikalDrugoTrziste.objects.filter(**fd).update(ATC=ATC)
    pass

def create_get_atc_sifra(cfg):
    column = cfg['atc_sifra']
    column_ix = column_index_from_string(column) - 1
    def f(row):
        return row[column_ix].value
    return f

def create_get_filter_dict(trziste, name, cfg):
    column = cfg[name]
    column_ix = column_index_from_string(column) - 1
    def f(row):
        return { 'trziste' : trziste, 
                name : row[column_ix].value }
    return f

def get_ATC(sifra):
    ATC = None
    try:
        ATC = AtcCode.objects.get(sifra=sifra)
    except:
        pass
    return ATC
