import json
import jsmin
import re
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from meds.models import ListaHZZO, AtcCode
from openpyxl import load_workbook, Workbook
from openpyxl.cell import column_index_from_string
from optparse import make_option

cmd_write = None

class Command(BaseCommand):
    args = 'excel_file ...>'
    help = 'Exports arc codes to excel file.'
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
        export(args[0], options['cfg_file'])
        cmd_write = None

default_cfg = {
        'sheet_name' : 'AtcCodes',
        'start_row' : 2,
        'columns' : {
            'sifra' : 'A',
            'opis' : 'B'
            },
        'header' : {
            'A' : 'ATC kode',
            'B' : 'opis'
            }
        }

def export(ex_file, cfg_file=None):
    cfg = {}
    cfg.update(default_cfg)
    if None != cfg_file:
        f = open(cfg_file)
        b = f.read()
        cfg.update(json.loads(jsmin.jsmin(b)))

    setter_dict = make_setter_dict(cfg['columns'])
    create_row_values = get_create_row_values(setter_dict)

    wb = Workbook()
    sh = wb.active
    sh.title = cfg['sheet_name']

    sh.append(cfg['header'])
    for db_values in AtcCode.objects.all().values():
        values = create_row_values(db_values)
        sh.append(values)

    wb.save(ex_file)
    pass

def get_create_row_values(setter_dict):
    def f(values):
        res = {}
        for n in setter_dict:
            res[n] = setter_dict[n](values)
        return res
    return f

default_fun_dict = {
        }

def make_setter_dict(cfg, fun_dict=default_fun_dict):
    res = {}
    for n in cfg:
        col_name = cfg[n]
        if None != col_name and '' != col_name:
            try:
                res[col_name] = make_setter(n, fun_dict.get(n, lambda x: x))
            except:
                pass
    return res
    
def make_setter(n, conv_fun):
    def f(values):
        return conv_fun(values[n])
    return f    

