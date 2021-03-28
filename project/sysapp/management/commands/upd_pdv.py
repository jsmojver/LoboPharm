import json
import jsmin
import re
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
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
        'sheet_name' : 'Sheet1',
        'start_row' : 4,
        'columns' : {
            'pdv' : 'A',
            'ATC_naziv' : 'C',
            'genericko_ime' : 'V',
            'ddd_jed_mj' : 'X',
            'proizvodac' : 'O',
            'zasticeno_ime_lijeka' : 'D',
            'oblik_lijeka' : '',
            'cijena_u_kn_za_jed_oblika' : 'R',
            'cijena_u_kn_za_orig_pakir' : 'F',
            'napomena' : '',
            'grupa' : '',
            'podgrupa' : ''
            }
        }

def xparse(ex_file, cfg_file=None):
    cfg = {}
    cfg.update(default_cfg)
    if None != cfg_file:
        f = open(cfg_file)
        b = f.read()
        cfg.update(json.loads(jsmin.jsmin(b)))
    get_atc_sifra = create_get_atc_sifra(cfg)
    extract_dict = make_extract_dict(cfg['columns'])
    # print extract_dict
    extract_values = get_extract_values(extract_dict)
    wb = load_workbook(ex_file)
    sh = wb[cfg['sheet_name']]
    start_row = cfg['start_row']
    pdvs = {}
    for n,r in enumerate(sh.rows[start_row - 1:],start_row):
        if not sh.row_dimensions[n].hidden:
            v = extract_values(r)
            atc_sifra = atc_naziv_to_sifra(v['ATC_naziv'])
            pdv = v['pdv']
            pdvs[atc_sifra] = pdv
    for sifra in pdvs:
        ListaHZZO.objects.filter(ATC__sifra=sifra).update(pdv=pdvs[sifra])
        # rs = ListaHZZO.objects.filter(ATC__sifra=sifra)
        # for r in rs:
        #     cmd_write('Update %s to pdv %f %%\n' % (r.genericko_ime, pdvs[sifra]))
    pass

def create_get_atc_sifra(cfg):
    column = cfg['columns']['ATC_naziv']
    column_ix = column_index_from_string(column) - 1
    def f(row):
        return row[column_ix].value[:7]
    return f

def get_create_hzzo_item(cfg):
    pdx_ix = column_index_from_string(cfg['columns']['pdv']) - 1

def atc_naziv_to_sifra(naziv):
    return naziv[:7]

def get_extract_values(extract_dict):
    def f(row):
        res = {}
        for n in extract_dict:
            res[n] = extract_dict[n](row)
        return res
    return f

re_pdv = re.compile(r'[Tt](?P<pdv>\d+)')

def str_to_pdv(s):
    res = None
    m = re_pdv.search(s)
    if m != None:
        res = Decimal(m.group('pdv'))
    return res

def str_to_ATC_naziv(s):
    return s[:7] + u' ' + s[7:10]

default_fun_dict = {
        'pdv' : str_to_pdv,
        'ATC_naziv' : str_to_ATC_naziv
        }

def make_extract_dict(cfg, fun_dict=default_fun_dict):
    res = {}
    for n in cfg:
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

