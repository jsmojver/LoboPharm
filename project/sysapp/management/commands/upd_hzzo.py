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
            make_option('-d', '--dry_run', dest='dry_run',
                        action='store_true',
                        help='Display updates without db commit',
                        default=False),
            make_option('-r', '--reset_pdv', dest='reset_pdv',
                        action='store_true',
                        help='Reset pdv for all items before update',
                        default=False),
            make_option('-a', '--add_atc', dest='add_atc',
                        action='store_true',
                        help='Add missing atc codes',
                        default=False),
            )

    def handle(self, *args, **options):
        global cmd_write
        # self.stdout.write('Options %s, args %s' % (options, args))
        if len(args) < 1:
            self.stdout.write('Missing excel_file argument.\n')
            return
        cmd_write = lambda s: self.stdout.write(s.encode('utf-8'))
        xparse(args[0], options['cfg_file'], options['dry_run'], options['reset_pdv'], options['add_atc'])
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

def xparse(ex_file, cfg_file=None, dry_run=False, reset_pdv=False, add_atc=False):
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
    if dry_run:
        if reset_pdv:
            cmd_write('PDV for all items will be reset.')
    pdvs = {}
    for n,r in enumerate(sh.rows[start_row - 1:],start_row):
        if not sh.row_dimensions[n].hidden:
            v = extract_values(r)
            atc_sifra = atc_naziv_to_sifra(v['ATC_naziv'])
            pdv = v['pdv']
            pdvs[atc_sifra] = pdv
            # create or update object in ListaHZZO
            n = 0
            try:
                n = ListaHZZO.objects.filter(ATC_naziv=v['ATC_naziv']).count()
            except:
                pass
            if 0 == n:
                if dry_run:
                    cmd_write('New item %s, %s\n' % (v['zasticeno_ime_lijeka'], v['ATC_naziv']))
                    try:
                        atc = AtcCode.objects.get(sifra=atc_sifra)
                    except:
                        cmd_write('Unknown ATC code %s. Contact your administrator.\n' % (atc_sifra,))
                else:
                    atc = None
                    try:
                        atc = AtcCode.objects.get(sifra=atc_sifra)
                    except:
                        if add_atc:
                            atc = add_new_atc(atc_sifra, v['genericko_ime'])
                    if None != atc:
                        lhz = ListaHZZO(ATC=atc, **v)
                        # lhz.ATC = atc
                        lhz.save()
                    else:
                        cmd_write('Unknown ATC code %s. Contact your administrator.\n' % (atc_sifra,))
    if not dry_run:
        if reset_pdv:
            ListaHZZO.objects.all().update(pdv=None)
    for sifra in pdvs:
        if dry_run:
            rs = ListaHZZO.objects.filter(ATC__sifra=sifra)
            for r in rs:
                cmd_write('Update %s to pdv %f %%\n' % (r.genericko_ime, pdvs[sifra]))
        else:
            ListaHZZO.objects.filter(ATC__sifra=sifra).update(pdv=pdvs[sifra])
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

def add_new_atc(sifra, opis):
    parent = find_parent(sifra)
    atc = AtcCode(sifra=sifra, opis=opis, parent=parent)
    atc.save()

def find_parent(sifra):
    parent = None
    while len(sifra) > 0:
        sifra = sifra[:-1]
        try:
            parent = AtcCode.objects.get(sifra=sifra)
            break
        except:
            pass
    return parent
