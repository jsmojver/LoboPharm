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
        'sheet_name' : 'Preisliste',
        'start_row' : 7,
        'trziste' : 'Austrija',
        'key' : 'ime',
        'columns' : {
            'ime' : 'B',
            'cijena' : 'F',
            'sifra' : '',
            'kolicina_jed' : '',
            'kolicina' : '',
            'jedinica' : ''
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
    get_filter_dict = create_get_filter_dict(trziste, cfg['key'], cfg['columns'])
    extract_dict = make_extract_dict(cfg['key'], cfg['columns'])
    # print extract_dict
    extract_values = get_extract_values(extract_dict)

    wb = load_workbook(ex_file)
    sh = wb[cfg['sheet_name']]
    start_row = cfg['start_row']
    for n,r in enumerate(sh.rows[start_row - 1:],start_row):
        v = extract_values(r)
        fd = get_filter_dict(r)
        print fd
        print v
        # this line works just in Django 1.7
        # ArtikalDrugoTrziste.objects.update_or_create(**fd, defaults=v)
        cnt = ArtikalDrugoTrziste.objects.filter(**fd).update(**v)
        if 0 == cnt:
            rs = ArtikalDrugoTrziste.objects.filter(**fd)
            if 0 == rs.count():
                upd = dict(v)
                upd.update(fd)
                a = ArtikalDrugoTrziste(**upd)
                a.save()
    pass

def create_get_filter_dict(trziste, name, cfg):
    column = cfg[name]
    column_ix = column_index_from_string(column) - 1
    def f(row):
        return { 'trziste' : trziste, 
                name : row[column_ix].value }
    return f

def get_extract_values(extract_dict):
    def f(row):
        res = {}
        for n in extract_dict:
            res[n] = extract_dict[n](row)
        return res
    return f

def str_to_dec(s):
    d = Decimal(0)
    try:
        d = Decimal(s)
    except:
        pass
    return d

default_fun_dict = {
        'cijena' : str_to_dec
        }

def make_extract_dict(key, cfg, fun_dict=default_fun_dict):
    res = {}
    for n in cfg:
        if n != key:
            col_name = cfg[n]
            if None != col_name and '' != col_name:
                try:
                    ix = column_index_from_string(col_name) - 1
                    res[n] = make_getter(ix, fun_dict.get(n, unicode))
                except:
                    pass
    return res
    
def make_getter(ix, conv_fun):
    def f(r):
        v = r[ix].value
        if None != v:
            return conv_fun(v)
        else:
            return None
    return f    

