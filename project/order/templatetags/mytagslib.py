#coding: utf-8

from django import template
from django.template.defaultfilters import stringfilter
from math import fabs

register = template.Library()

@register.filter(name='addpoint')
def addpoint(value):
    """adds decimal point and returns string"""
    value = str(value)
    return '{0}.{1}'.format(value[:-2],value[-2:])

@register.filter(name='eur2hrk')
def eur2hrk(value):
    from order.models import TecajnaLista
    from decimal import Decimal
    """converts eur to hrk"""   
    lista = TecajnaLista.objects.latest('date')    
    value = Decimal(value)
    
    zaokruzi = Decimal(value*lista.prodajni_tecaj()).quantize(Decimal(10)**(-2)) # Zaokruzi na 2 decimale
    if int(zaokruzi*100) % 4:
      zaokruzi += (4 - int(zaokruzi*100)%4) * Decimal('0.01') # Naštimaj da je sve lijepo djeljivo s 4 pa će i PDV savršeno štimati

    return zaokruzi

@register.filter(name='hrk2eur')
def hrk2eur(value):
    from order.models import TecajnaLista
    from decimal import Decimal
    """converts eur to hrk"""   
    lista = TecajnaLista.objects.latest('date')    
    value = Decimal(value)
    return Decimal(value/lista.prodajni_tecaj()).quantize(Decimal(10)**(-2)) # Zaokruzi na 2 decimale

@register.filter(name='abs')
def abs(value):
    """ return absolute value """   
    return fabs(value) 

    
@register.filter(name='translate')
def translate(value):
    """ Prevedi najčešće kratice u templateima """   
    if str(value) == 'True': return 'Da'
    elif str(value) == 'False': return 'Ne'
    elif str(value) == 'None': return '0'
    else: return value


#--------------------------------------------------------------------------------------------------


@register.filter(name='format_float')
def format_float(value, precision):
    res = "0"
    try:
        if precision is not None:
            precison_str = "%%.%df" % precision
            res = (precison_str % value).replace(".", ",")
        else:
            res = ("%g" % value).replace(".", ",")
    except:
        pass

    # group digits
    a = res.split(",")
    dec = a[0]
    frac = a[1] if len(a) > 1 else ""

    if len(dec) > 0 and dec[0] == "-":
        neg = True
        dec = dec[1:]
    else:
        neg = False

    if len(dec) > 3:
        g = []
        while len(dec) > 0:
            g.append(dec[-3:])
            dec = dec[:len(dec)-3] if len(dec) > 3 else ""
        dec = ".".join(reversed(g))

    res = "%s,%s" % (dec, frac) if len(frac) != 0 else dec
    if neg:
        res = "-%s" % (res)

    return res


#--------------------------------------------------------------------------------------------------
