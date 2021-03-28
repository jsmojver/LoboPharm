#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import jsmin
import re
from decimal import Decimal

from optparse import OptionParser

from openpyxl import load_workbook
from openpyxl.cell import column_index_from_string

#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from meds.models import ListaHZZO

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
    print extract_dict
    extract_values = get_extract_values(extract_dict)
    wb = load_workbook(ex_file)
    sh = wb[cfg['sheet_name']]
    start_row = cfg['start_row']
    i = 0
    for n,r in enumerate(sh.rows[start_row - 1:],start_row):
        if sh.row_dimensions[n].hidden:
            v = extract_values(r)
            if v['ATC_naziv'].startswith('A02BA02'):
                print i, v['ATC_naziv']
                try:
                    lhz = ListaHZZO.objects.get(ATC_naziv=v['ATC_naziv'])
                    print 'ListaHZZO %d %s should be updated' % (lhz.id, lhz.zasticeno_ime_lijeka)
                except:
                    print 'New ListaHZZO objext should be created!'
                i += 1
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

if '__main__' == __name__:
    options = None
    args = None
    parser = OptionParser()
    parser.add_option('-c', '--cfg', dest='cfg_file',
                        help='parser configuration file',
                        default=None)
    options, args = parser.parse_args()
    xparse(args[0], cfg_file=options.cfg_file)
    pass

