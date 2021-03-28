#coding=utf-8


import barcode

from sysapp.constants import *
from sysapp.escpos import *

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader, Context, RequestContext
from django.template.loader import render_to_string
from trml2pdf import trml2pdf

import cStringIO as StringIO
import ho.pisa as pisa

from sysapp.models import * 
from depo.views import ticks


import serial
import simplejson

from meds.models import get_pdv

from order.models import Narudzba, NarucenArtikal, Klijent, Valuta
from django.contrib.auth.models import User

from fiskalizacija.models import *
from django.views.generic import CreateView, ListView

from django.db.models import Count, Min, Sum, Max, Avg

from constants import *
from time import strftime
import locale, math, datetime
from datetime import date


def to852(instring):
  return instring.decode('utf-8').encode('cp852')

def ClientAlert(notify):
  return HttpResponse('javascript:alert("%s");' % notify)

def eansvg(request, broj):
  return HttpResponse(barcode.get_barcode('ean', broj).render())

def eanpng(request, broj):
  from barcode.writer import ImageWriter
  a = ImageWriter()
  a.dpi = 130
  image = barcode.get_barcode('ean', broj, writer=a).render()
  response = HttpResponse(mimetype="image/png")
  image.save(response, "PNG")
  return response

def moveright(ulaz):
  return '{:>23}'.format(ulaz)

def moveright_narrow(ulaz):  
  return '{:>46}'.format(ulaz)
  
def order_print_shipping_label(request, order_id):
  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  primatelj = moveright(narudzba.klijent.get_full_name().encode('cp852'))
  adresa = moveright(narudzba.klijent.adresa.encode('cp852'))
  mjesto = narudzba.klijent.postanski_broj + ' ' + narudzba.klijent.grad
  mjesto = moveright(mjesto.encode('cp852'))
  zemlja = moveright(to852(narudzba.klijent.zemlja))
  barkod = '12%s' % narudzba.sifra
  width = 2

  msg = ''

  if len(narudzba.klijent.adresa) > 22 or len('%s %s' % (narudzba.klijent.ime, narudzba.klijent.prezime)) > 22 or len(narudzba.klijent.grad) > 15:
    primatelj = moveright_narrow(primatelj)
    adresa = moveright_narrow(adresa)
    mjesto = moveright_narrow(mjesto)
    zemlja = moveright_narrow(zemlja)
    width = 1

  commands = ['N', 
          'q800',
          'Q400,19',
          'I8,2,001',
          'A15,160,0,4,%s,2,N,"%s"' % (width, primatelj),
          'A15,210,0,4,%s,2,N,"%s"' % (width, adresa),
          'A15,260,0,4,%s,2,N,"%s"' % (width, mjesto),
          'A15,310,0,4,%s,2,N,"%s"' % (width, zemlja),


          'I8,1,001',
          'A130,10,0,4,1,1,N,"%s"' % "Kurfürsten-Apotheke".decode('utf-8').encode('cp850'),
          'A130,35,0,3,1,1,N,"%s"' % "Kurfürstenstraße 5, 45138 Essen, BRD".decode('utf-8').encode('cp850'),
          'A130,70,0,3,1,1,N,"%s"' % "Rückgabe an: MPT, Dolac 9, 10000 Zagreb, HR".decode('utf-8').encode('cp850'),
          'A500,95,0,3,1,1,N,"(adresa za povrat)"',
          'LO120,60,645,3', 
          'LO765,60,3,300', 
          'LO40,365,725,3', 
          
          'A40,130,0,3,1,1,N,"%s"' % "Empfänger:".decode('utf-8').encode('cp850'),
          'LO40,150,3,215', 
          'LO40,150,150,3', 

          'GG20,10,"logo1"',
          'B40,320,0,E30,2,2,35,N,"%s"' % barkod,
          'P1,1',]
  for i in commands:
    msg += ("%s\n" % i)
  return HttpResponse(msg.encode('hex')) 

def order_print_barcode(request, order_id):
  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  p = "\x1b\x40\n" 
  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n ** %s **  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('Bestellnummer') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 

def print_receipt(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- P O T V R D A -\x1b\x45\x00\n')
  p += TXT_NORMAL + TXT_ALIGN_CT
  p += to852('o uplaćenoj akontaciji\n\n')


  
  p += to852('Klijent: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))
  p += ('Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<50}'.format('Artikl') + '{:>5}'.format('Kol') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  for i in narudzba.artikli.all():
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''
    
    p+= '{:<50}'.format('%s %s' % (i.ime[:40], kolicina)) + '{:>5}'.format(i.kolicina) + '\n'
 
  if narudzba.uplate.filter(tip='4').count():
    dobava = sum([i.to_kn() for i in narudzba.uplate.filter(tip='4')])
    p += '{:<50}'.format('Usluga dobave') + '{:>5}'.format('1') + '\n' 
  
  if narudzba.uplate.filter(tip='6').count():
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<50}'.format('Usluga postarine') + '{:>5}'.format('1') + '\n' 
    
  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n\n' 

  p += 'Akontacija: \x1b\x45\x01%s %s\x1b\x45\x00\n'.decode('utf-8').encode('cp852') % (narudzba.get_polog_kn(), 'KN')

  p += TXT_ALIGN_CT

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n ** %s **  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('Hvala na posjeti!') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 


def ispis_papirica_za_narudzbu(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  narudzba.ispisana_potvrda = 1
  narudzba.save()

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- F A X   P O T V R D A -\x1b\x45\x00\n\n\n') 

  p += to852('Klijent: \n\x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))

  p += TXT_NORMAL + '\n'
  
  
  try: p += ('Adresa: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n' % narudzba.klijent.adresa).encode('cp852')
  except: pass
  try: p += ('\x1b\x45\x01\x1b\x2d\x01%s %s %s\x1b\x2d\x00\x1b\x45\x00 \n' % (narudzba.klijent.postanski_broj, narudzba.klijent.grad, narudzba.klijent.zemlja)).encode('cp852')
  except: p+= ('Nedostaje grad/zemlja/post.broj\n')
  if narudzba.klijent.telefon:
    try: p += ('Tel: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n' % (narudzba.klijent.telefon)).decode('utf-8').encode('cp852')
    except: pass
  if narudzba.klijent.mobitel:
    try: p += ('Mob: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n' % (narudzba.klijent.mobitel)).decode('utf-8').encode('cp852')
    except: pass

  p += ('Šifra narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n' % narudzba.sifra).decode('utf-8').encode('cp852')
  p += to852('Naručila: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.narucio.get_full_name().encode('utf-8'))
  p += ('Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')
  
  p += '\x1b\x21\x00' 
  p += '\x1b\x45\x01' + '{:<20}'.format('Artikl') + '{:<6}'.format('Kol') + '\x1b\x45\x00\n'
  for i in range(42): p += '\xcd'
  p += '\n' + TXT_BOLD_ON

  for i in narudzba.artikli.all():
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
      kolicina2 = stkol + ' ' + i.jedinice
    else: 
      kolicina = ''
      kolicina2 = ''
 
    if len(i.ime) > 41: i.ime = i.ime[:41] + '\n' + i.ime[41:]
    p += to852(i.ime) + '\n'
  
    if i.pakiranje is None:
      i.pakiranje = ''

    p += '{:<17}'.format('[%s %s' % (i.jedinicna_cijena, i.valuta_text())) + '{:^8}'.format('x %s' % i.kolicina) + '{:>17}'.format(' = %s %s]' % (i.get_total(), i.valuta_text())) + '\n'
    if i.kratica_dobavljaca:
      p += '{:<21}'.format('[Trziste: %s ' % to852(i.trziste.naziv.encode('utf-8'))) + '{:>21}'.format(' Dobavljac: %s]' % to852(i.kratica_dobavljaca)) + '\n'
    else:
      p += '{:<41}'.format('[Trziste: %s ' % to852(i.trziste.naziv.encode('utf-8'))) + ']\n'
    if i.ZoNr: p += '{:<41}'.format('PZN: %s, Kol: %s (%s)\n' % (i.ZoNr, kolicina2, i.pakiranje.rstrip()))
    else: pass 
    p += '\n'
  
  p += '\x1b\x21\x00' + TXT_BOLD_OFF
  for i in range(42): p += '\xcd' 

  p += '\n' + TXT_2WIDTH + TXT_ALIGN_RT
  if narudzba.uplate.filter(tip='4').count():
    dobava = sum([i.iznos for i in narudzba.uplate.filter(tip='4')])
    p += 'Transport: %s %s\n'.decode('utf-8').encode('cp852') % (dobava, EUR)
  else: dobava = 0

  p += 'Ukupno: %s %s\n'.decode('utf-8').encode('cp852') % (narudzba.ukupna_cijena_bez_troskova_euri() + dobava, EUR)

  p += TXT_ALIGN_CT + TXT_NORMAL

  try: p += '\n\nAkontacija: \x1b\x45\x01%s %s\x1b\x45\x00\n'.decode('utf-8').encode('cp852') % (narudzba.uplate.filter(tip='1', valuta=4, vrsta=0).aggregate(Sum('iznos'))['iznos__sum'], 'KN')
  except: pass
  try: p += 'Akontacija: \x1b\x45\x01%s %s\x1b\x45\x00\n'.decode('utf-8').encode('cp852') % (narudzba.uplate.filter(tip='1', valuta=1, vrsta=0).aggregate(Sum('iznos'))['iznos__sum'], 'EUR')
  except: pass

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += '\n\n\n\n\n\n' + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 

def print_receipt_2(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- R A Č U N -\x1b\x45\x00\n\n')
  p += TXT_NORMAL + TXT_ALIGN_CT


  
  p += to852('Klijent: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))
  p += ('Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<30}'.format('Artikl') + '{:>5}'.format('Kol') + '{:>10}'.format('Cijena') + '{:>10}'.format('Ukupno') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  for i in narudzba.artikli.all():
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''

    p += '{:<30}'.format('%s %s' % (i.ime[:23], kolicina)) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.jedinicna_cijena_kn()) + '{:>10}'.format(i.get_total_kn()) + '\n'
 
  if narudzba.uplate.filter(tip='4').count():
    dobava = sum([i.to_kn() for i in narudzba.uplate.filter(tip='4')])
    p += '{:<30}'.format('Usluga dobave') + '{:>5}'.format('1') + '{:>10}'.format(dobava) + '{:>10}'.format(dobava) + '\n' 
  
  if narudzba.uplate.filter(tip='6').count():
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<30}'.format('Usluga postarine') + '{:>5}'.format('1') + '{:>10}'.format(postarina) + '{:>10}'.format(postarina) + '\n' 
    
  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n' + TXT_2WIDTH + TXT_ALIGN_RT
  p += 'Ukupno: %.2f KN \n\n' % abs(narudzba.fetch_zaduzenja())
  p += TXT_ALIGN_CT + TXT_NORMAL

  if narudzba.artikli.filter(placeno=0):
    p += 'Akontacija: \x1b\x45\x01%s %s\x1b\x45\x00\n'.decode('utf-8').encode('cp852') % (narudzba.get_polog_kn(), 'KN')
    p += 'Preostalo za platiti: \x1b\x45\x01%s %s\x1b\x45\x00\n\n'.decode('utf-8').encode('cp852') % (narudzba.za_platiti_kn(), 'KN')
  else:
    p += to852('Račun je podmiren!\n\n')

  p += TXT_ALIGN_CT

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n ** %s **  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('Hvala na posjeti!') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 


def print_racun_za_pristigle(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- R A Č U N -\x1b\x45\x00\n\n')
  p += TXT_NORMAL + TXT_ALIGN_CT


  
  p += to852('Klijent: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))
  p += ('Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<30}'.format('Artikl') + '{:>5}'.format('Kol') + '{:>10}'.format('Cijena') + '{:>10}'.format('Ukupno') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  ukupan_iznos = 0
  naknadni_racun = 0
  lista_naknadnih = []

  datumi_uplata = list(set([i.date() for i in LogArtikla.objects.filter(event=4, artikal__in=narudzba.artikli.all().values_list('id', flat=True)).values_list('datetime', flat=True)]))
  if len(datumi_uplata)>1: 
    naknadni_racun = 1
    lista_naknadnih = LogArtikla.objects.filter(event=4, datetime__startswith=sorted(datumi_uplata)[-1], artikal__in=narudzba.artikli.all().values_list('id', flat=True)).values_list('artikal', flat=True)

  for i in narudzba.artikli.filter(status__in=[4, 5]):
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''

    if naknadni_racun and i.id not in lista_naknadnih:
      pass
    else:
      total_cijena = int(i.kolicina) * i.jedinicna_cijena_kn()
      p += '{:<30}'.format('%s %s' % (i.ime[:23], kolicina)) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.jedinicna_cijena_kn()) + '{:>10}'.format(total_cijena) + '\n'
      ukupan_iznos += total_cijena

  if narudzba.uplate.filter(tip='4').count() and not naknadni_racun:
    dobava = sum([i.to_kn() for i in narudzba.uplate.filter(tip='4')])
    p += '{:<30}'.format('Usluga dobave') + '{:>5}'.format('1') + '{:>10}'.format(dobava) + '{:>10}'.format(dobava) + '\n' 
    ukupan_iznos += dobava
  
  if narudzba.uplate.filter(tip='6').count() and not naknadni_racun:
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<30}'.format('Usluga postarine') + '{:>5}'.format('1') + '{:>10}'.format(postarina) + '{:>10}'.format(postarina) + '\n' 
    ukupan_iznos += postarina  
     
  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n' + TXT_2WIDTH + TXT_ALIGN_RT
  p += 'Ukupno: %.2f KN \n\n' % ukupan_iznos
  p += TXT_ALIGN_CT + TXT_NORMAL

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n ** %s **  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('Hvala na posjeti!') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 


def ispis_njemackog_racuna_broj(request, racun_broj):

  
  
  
  try: racun = NarudzbaRacun.objects.get(broj=racun_broj)
  except: return
  
  ukupno = Decimal(0)

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 

  p += '\x1b\x74\x12\x1b\x45\x01' + TXT_ALIGN_CT + TXT_NORMAL 
  p += to852("U korist i na račun") + "\x1b\x45\x00\n\n"

  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- R E C H N U N G -\x1b\x45\x00\n')
  p += TXT_NORMAL + TXT_ALIGN_CT

  p += 'Nr. %s' % racun.broj_racuna() + '\n\n'


  
  p += to852('Auftraggeber: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % racun.narudzba.klijent.get_full_name().encode('utf-8'))

  p += ('Datum: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % racun.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<30}'.format('Artikel') + '{:>5}'.format('Menge') + '{:>10}'.format('Preis') + '{:>10}'.format('Total') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  for i in racun.stavke.all():
    if i.valuta == 1: i.jedinicna_cijena = hrk2eur(i.jedinicna_cijena)
    ukupno += Decimal(i.kolicina) * i.jedinicna_cijena 
    p += '{:<30}'.format('%s' % i.naziv) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.jedinicna_cijena) + '{:>10}'.format(Decimal(i.kolicina) * i.jedinicna_cijena) + '\n'

  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n' + TXT_ALIGN_RT

  import project.settings
  pdv_factor = 1.0 / (1.0 + project.settings.TaxRate / 100.0)
  ukupno_bez_mwst = ukupno * Decimal(pdv_factor)
  ukupno_bez_mwst = ukupno_bez_mwst.quantize(Decimal(10) ** -2)

  p += '{:>16}'.format('Zwischensumme:  ') + '{:>12}'.format('%.2f KN  ' % eur2hrk(ukupno_bez_mwst)) + '{:>12}'.format('%.2f EUR ' % ukupno_bez_mwst) + '\n'
  p += '{:>16}'.format('PDV/MwSt 25%:  ') + '{:>12}'.format('%.2f KN  ' % (eur2hrk(ukupno) - eur2hrk(ukupno_bez_mwst))) + '{:>12}'.format('%.2f EUR ' % (ukupno - ukupno_bez_mwst)) + '\n\n'
  p += TXT_BOLD_ON + '{:>16}'.format('Gesamtbetrag:  ') + '{:>12}'.format('%.2f KN  ' % eur2hrk(ukupno)) + '{:>12}'.format('%.2f EUR ' % ukupno) + '\n\n' + TXT_BOLD_OFF

  p += TXT_ALIGN_CT + TXT_NORMAL

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % racun.narudzba.sifra
  p += TXT_ALIGN_CT + '\n %s  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('** Hvala na posjeti! ** \n ** Vielen Dank fur Ihren Besuch! **') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 

class PoreznaStopaAccu(object):
    def __init__(self, stopa, osnovica=0.0):
        self.stopa = stopa
        self.osnovica = osnovica

    def porez(self):
        return self.stopa * self.osnovica / 100.

    def ukupno(self):
        return self.osnovica + self.porez()

    def add_to_osnovica(self, value):
        self.osnovica += value

    def add_to_ukupno(self, value):
        self.add_to_osnovica(value * self.inverz_stopa())

    def inverz_stopa(self):
        return 100. / (100. + self.stopa)


def do_encode_racun_njemacki(user, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return None
  
  if not narudzba.narudzba_racuni.count():
    racun = NarudzbaRacun(kreirao=user, narudzba=narudzba)
    try: racun.broj = NarudzbaRacun.objects.latest('broj').broj + 1
    except: racun.broj = 1
    racun.save()
  else: racun = False 

  pdvs = {}
  
  ukupno = Decimal(0)

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 

  p += '\x1b\x74\x12\x1b\x45\x01' + TXT_ALIGN_CT + TXT_NORMAL 
  p += to852("U korist i na račun") + "\x1b\x45\x00\n\n"

  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- R E C H N U N G -\x1b\x45\x00\n')
  p += TXT_NORMAL + TXT_ALIGN_CT

  if narudzba.narudzba_racuni.count():
    p += 'Nr. %s' % narudzba.narudzba_racuni.latest('id').broj_racuna() + '\n\n'  
  else:
    p += '\n'


  
  p += to852('Auftraggeber: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))

  if racun: p += ('Datum: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % racun.created).decode('utf-8').encode('cp852')
  else:
    try:
      r = narudzba.narudzba_racuni.latest('created')
      p += ('Datum: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % r.created).decode('utf-8').encode('cp852')
    except: pass

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<30}'.format('Artikel') + '{:>5}'.format('Menge') + '{:>10}'.format('Preis') + '{:>10}'.format('Total') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  for i in narudzba.artikli.all():
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''

    ukupno += Decimal(i.kolicina) * i.jedinicna_cijena_eur()

    p += '{:<30}'.format('%s %s' % (i.ime[:23], kolicina)) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.jedinicna_cijena_eur()) + '{:>10}'.format(Decimal(i.kolicina) * i.jedinicna_cijena_eur()) + '\n'

    if racun:
      NarudzbaRacunStavka(racun=racun, naziv=i.ime, jedinicna_cijena=i.jedinicna_cijena_eur(), kolicina=int(i.kolicina), iznos=Decimal(i.kolicina)*i.jedinicna_cijena_eur()).save()

    pdv = get_pdv(atc_sifra=i.atc_sifra)
    if not pdv in pdvs:
      pdvs[pdv] = PoreznaStopaAccu(pdv)
    uk = float(Decimal(i.kolicina) * i.jedinicna_cijena_eur())
    pdvs[pdv].add_to_ukupno(uk)

 
  if narudzba.uplate.filter(tip='6').count():
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<30}'.format('Postgebuehr') + '{:>5}'.format('1') + '{:>10}'.format(hrk2eur(postarina)) + '{:>10}'.format(hrk2eur(postarina)) + '\n'
    ukupno += hrk2eur(postarina)

    if racun:
      NarudzbaRacunStavka(racun=racun, naziv='Postgebuhr', jedinicna_cijena=hrk2eur(postarina), kolicina=1, iznos=hrk2eur(postarina)).save()

    pdv = get_pdv()
    if not pdv in pdvs:
      pdvs[pdv] = PoreznaStopaAccu(pdv)
    pdvs[pdv].add_to_ukupno(float(hrk2eur(postarina)))

    
  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n' + TXT_ALIGN_RT

  # print pdvs
  for pdv in sorted(pdvs.keys()):
      p += '{:>16}'.format('Zwischensumme:  ') + '{:>12}'.format('%.2f KN  ' % (eur2hrk(pdvs[pdv].osnovica),)) + '{:>12}'.format('%.2f EUR ' % (pdvs[pdv].osnovica,)) + '\n'
      p += '{:<8}'.format('PDV/MwSt') + '{:>8}'.format('%.1f%%: ' % (pdv,)) + '{:>12}'.format('%.2f KN  ' % (eur2hrk(pdvs[pdv].porez()),)) + '{:>12}'.format('%.2f EUR ' % (pdvs[pdv].porez(),)) + '\n\n'

  p += TXT_BOLD_ON + '{:>16}'.format('Gesamtbetrag:  ') + '{:>12}'.format('%.2f KN  ' % (eur2hrk(ukupno),)) + '{:>12}'.format('%.2f EUR ' % (ukupno,)) + '\n\n' + TXT_BOLD_OFF

# import project.settings
# pdv_factor = 1.0 / (1.0 + project.settings.TaxRate / 100.0)
# ukupno_bez_mwst = ukupno * Decimal(pdv_factor)
# ukupno_bez_mwst = ukupno_bez_mwst.quantize(Decimal(10) ** -2)

# p += '{:>16}'.format('Zwischensumme:  ') + '{:>12}'.format('%.2f KN  ' % eur2hrk(ukupno_bez_mwst)) + '{:>12}'.format('%.2f EUR ' % ukupno_bez_mwst) + '\n'
# p += '{:>16}'.format('PDV/MwSt 25%:  ') + '{:>12}'.format('%.2f KN  ' % (eur2hrk(ukupno) - eur2hrk(ukupno_bez_mwst))) + '{:>12}'.format('%.2f EUR ' % (ukupno - ukupno_bez_mwst)) + '\n\n'
# p += TXT_BOLD_ON + '{:>16}'.format('Gesamtbetrag:  ') + '{:>12}'.format('%.2f KN  ' % eur2hrk(ukupno)) + '{:>12}'.format('%.2f EUR ' % ukupno) + '\n\n' + TXT_BOLD_OFF

  p += TXT_ALIGN_CT + TXT_NORMAL

  if narudzba.artikli.filter(placeno=0):
    p += 'Anzahlung: \x1b\x45\x01%s KN (%s EUR)\x1b\x45\x00\n'.decode('utf-8').encode('cp852') % (narudzba.get_polog_kn(), narudzba.get_polog_eur())
    p += 'Restzahlung: \x1b\x45\x01%s KN (%s EUR)\x1b\x45\x00\n\n'.decode('utf-8').encode('cp852') % (narudzba.za_platiti_kn(), narudzba.za_platiti_eur())
  else:
    p += to852('Račun je podmiren\nRechnung bezahlt!\n\n')

  p += TXT_ALIGN_CT

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n %s  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('** Hvala na posjeti! ** \n ** Vielen Dank fur Ihren Besuch! **') + PAPER_FULL_CUT

  return p

def print_racun_njemacki(request, order_id):
    p = do_encode_racun_njemacki(request.user, order_id)
    if None != p:
        return HttpResponse(p.encode('hex'))
    return


def print_potvrda_o_uplati_njemacki(request, order_id): 

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return
  
  ukupno = Decimal(0)

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- E I N Z A H L U N G S B E L E G -\x1b\x45\x00\n')
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- Potvrda o primljenim sredstvima -\x1b\x45\x00\n')
  p += TXT_NORMAL + TXT_ALIGN_CT
  p += '\n\n'


  
  p += to852('Auftraggeber: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))
  p += ('Datum der Bestellung: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<30}'.format('Artikel') + '{:>5}'.format('Menge') + '{:>10}'.format('Preis') + '{:>10}'.format('Total') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  for i in narudzba.artikli.all():
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''

    ukupno += Decimal(i.kolicina) * i.jedinicna_cijena_eur()

    p += '{:<30}'.format('%s %s' % (i.ime[:23], kolicina)) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.jedinicna_cijena_eur()) + '{:>10}'.format(Decimal(i.kolicina) * i.jedinicna_cijena_eur()) + '\n'

  if narudzba.uplate.filter(tip='6').count():
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<30}'.format('Postgebuehr') + '{:>5}'.format('1') + '{:>10}'.format(hrk2eur(postarina)) + '{:>10}'.format(hrk2eur(postarina)) + '\n'
    ukupno += hrk2eur(postarina)

  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n' + TXT_ALIGN_RT

  import project.settings
  pdv_factor = 1.0 / (1.0 + project.settings.TaxRate / 100.0)
  ukupno_bez_mwst = ukupno * Decimal(pdv_factor)
  ukupno_bez_mwst = ukupno_bez_mwst.quantize(Decimal(10) ** -2)

  
  
  

  p += '{:>16}'.format('Zwischensumme:  ') + '{:>12}'.format('%.2f KN  ' % eur2hrk(ukupno_bez_mwst)) + '{:>12}'.format('%.2f EUR ' % ukupno_bez_mwst) + '\n'
  p += '{:>16}'.format('PDV/MwSt 25%:  ') + '{:>12}'.format('%.2f KN  ' % (eur2hrk(ukupno) - eur2hrk(ukupno_bez_mwst))) + '{:>12}'.format('%.2f EUR ' % (ukupno - ukupno_bez_mwst)) + '\n\n'
  p += TXT_BOLD_ON + '{:>16}'.format('Gesamtbetrag:  ') + '{:>12}'.format('%.2f KN  ' % eur2hrk(ukupno)) + '{:>12}'.format('%.2f EUR ' % ukupno) + '\n\n' + TXT_BOLD_OFF

  p += TXT_ALIGN_CT + TXT_NORMAL

  
  
  
  
  

  p += TXT_ALIGN_CT

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n %s  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('** Hvala na posjeti! ** \n ** Vielen Dank fur Ihren Besuch! **') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 



def print_potvrda_njemacki(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- B E S T A T I G U N G  -\x1b\x45\x00\n')
  p += TXT_NORMAL + TXT_ALIGN_CT
  p += to852('der Bestellung\n\n')


  
  p += to852('Auftraggeber: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))
  p += ('Datum der Bestellung: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<50}'.format('Artikel') + '{:>5}'.format('Menge') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  for i in narudzba.artikli.all():
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''
    
    p+= '{:<50}'.format('%s %s' % (i.ime[:40], kolicina)) + '{:>5}'.format(i.kolicina) + '\n'
 
  if narudzba.uplate.filter(tip='6').count():
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<50}'.format('Postgebuehr') + '{:>5}'.format('1') + '\n'
    
  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n\n' 

  p += 'Anzahlung: \x1b\x45\x01%s KN %s EUR\x1b\x45\x00\n'.decode('utf-8').encode('cp852') % (narudzba.get_polog_kn(), narudzba.get_polog_eur())

  p += TXT_ALIGN_CT

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n ** %s **  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('Vielen dank fur Ihren Besuch!') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 


def print_racun_za_pristigle(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\x1b\x45\x01- R A Č U N -\x1b\x45\x00\n\n')
  p += TXT_NORMAL + TXT_ALIGN_CT


  
  p += to852('Klijent: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % narudzba.klijent.get_full_name().encode('utf-8'))
  p += ('Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % narudzba.created).decode('utf-8').encode('cp852')

  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<30}'.format('Artikl') + '{:>5}'.format('Kol') + '{:>10}'.format('Cijena') + '{:>10}'.format('Ukupno') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 

  ukupan_iznos = 0
  naknadni_racun = 0
  lista_naknadnih = []

  datumi_uplata = list(set([i.date() for i in LogArtikla.objects.filter(event=4, artikal__in=narudzba.artikli.all().values_list('id', flat=True)).values_list('datetime', flat=True)]))
  if len(datumi_uplata)>1: 
    naknadni_racun = 1
    lista_naknadnih = LogArtikla.objects.filter(event=4, datetime__startswith=sorted(datumi_uplata)[-1], artikal__in=narudzba.artikli.all().values_list('id', flat=True)).values_list('artikal', flat=True)

  for i in narudzba.artikli.filter(status__in=[4, 5]):
    if i.std_kolicina is not None: 
      try: stkol = '%.0f' % float(i.std_kolicina)
      except: stkol = i.std_kolicina
      kolicina = '{:<6}'.format('%s %s' % (stkol, i.jedinice))
    else: kolicina = ''

    if naknadni_racun and i.id not in lista_naknadnih:
      pass
    else:
      total_cijena = int(i.kolicina) * i.jedinicna_cijena_kn()
      p += '{:<30}'.format('%s %s' % (i.ime[:23], kolicina)) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.jedinicna_cijena_kn()) + '{:>10}'.format(total_cijena) + '\n'
      ukupan_iznos += total_cijena

  if narudzba.uplate.filter(tip='4').count() and not naknadni_racun:
    dobava = sum([i.to_kn() for i in narudzba.uplate.filter(tip='4')])
    p += '{:<30}'.format('Usluga dobave') + '{:>5}'.format('1') + '{:>10}'.format(dobava) + '{:>10}'.format(dobava) + '\n' 
    ukupan_iznos += dobava
  
  if narudzba.uplate.filter(tip='6').count() and not naknadni_racun:
    postarina = sum([i.to_kn() for i in narudzba.uplate.filter(tip='6')])
    p += '{:<30}'.format('Usluga postarine') + '{:>5}'.format('1') + '{:>10}'.format(postarina) + '{:>10}'.format(postarina) + '\n' 
    ukupan_iznos += postarina  
     
  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += '\n' + TXT_2WIDTH + TXT_ALIGN_RT
  p += 'Ukupno: %.2f KN \n\n' % ukupan_iznos
  p += TXT_ALIGN_CT + TXT_NORMAL

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '12%s\x00\x0a' % narudzba.sifra
  p += TXT_ALIGN_CT + '\n ** %s **  \n\x1c\x70\x02\x00\n\n\n\n\n\n' % to852('Hvala na posjeti!') + PAPER_FULL_CUT

  return HttpResponse(p.encode('hex')) 



def print_racun(request, racun_id):
  try: racun = Racun.objects.get(id=racun_id)
  except: return
    
  return HttpResponse(racun.render().encode('hex'))



def print_racun(request, racun_id):
  try: racun = Racun.objects.get(id=racun_id)
  except: return
    
  return HttpResponse(racun.render().encode('hex'))

def dnevni_obracun(request):
  t=time.localtime()                         
  racuni = Racun.objects.filter(djelatnik=request.user, created__year=t.tm_year, created__month=t.tm_mon, created__day=t.tm_mday, storno=0, stornira_racun__isnull=True)
  
  broj = racuni.count()
  iznos = racuni.aggregate(Sum('iznos'))

  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x22\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += strftime("%A, %d. %B %Y.  %H:%M:%S").decode('utf-8').encode('cp852') + '\n' 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\n\x1b\x45\x01- O B R A Č U N -\x1b\x45\x00\n\n')
  p += TXT_NORMAL + TXT_ALIGN_CT
  p += 'Djelatnik: %s\n' % request.user.get_full_name().encode('cp852')
  p += to852('Broj izdanih računa: %s\n') % broj
  p += to852('Ukupan iznos novca u kasi: %s kn\n') % iznos['iznos__sum']
  p += TXT_ALIGN_CT + '\n  Hvala!  \n\x1c\x70\x02\x00\n\n\n\n\n\n' + PAPER_FULL_CUT
  
  return HttpResponse(p.encode('hex')) 

def print_receipt_html(request, order_id):

  try: narudzba = Narudzba.objects.get(id=order_id)
  except: return

  lijekovi = []
  for i in narudzba.artikli.all():
    lijekovi.append((i.ime, i.kolicina, i.jedinicna_cijena))

  narucitelj = narudzba.klijent.ime + ' ' + narudzba.klijent.prezime
  p = Potvrda()
  p.narucitelj = narucitelj.encode('utf-8')
  p.datum = narudzba.created
  p.lijekovi = lijekovi
  p.sluzbenik = request.user.get_full_name().encode('utf-8')
  p.barcode = '12%s' % narudzba.sifra

  x = p.render_html()
  return HttpResponse(x)

def barcode_submit(request, barcode): 
  
  def calculate_check_digit(c): return (10-(sum(map(int, c[1::2]))*3 + sum(map(int, c[:12:2])))%10)%10 
  if len(barcode)!=13 or calculate_check_digit(barcode[:12]) != int(barcode[12]): return HttpResponse('javascript:alert("Neispravan barkod!");') 
  
  try: narudzba = Narudzba.objects.get(sifra=barcode[2:12])  
  except: return HttpResponse('javascript:alert("Nema takve narudžbe!");')
   
  
  return HttpResponse('show_order(%s);' % narudzba.id)

def barcode_test(request, barcode): 
  
  return HttpResponse('alert("barcode submitted" + %s);' % barcode)

def pdf_render_to_response(template, context, objekt=None):
  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'inline; filename=ispis.pdf'
  tpl = loader.get_template(template)
  tc = {'item': objekt}
  tc.update(context)

  pdf = trml2pdf.parseString(tpl.render(Context(tc)).encode('utf-8'))
  response.write(pdf)
  return response

def test_pdf(request):
  return pdf_render_to_response('rml/test.rml', request)

def order_to_pdf(request, order_id):
  try: narudzbe = Narudzba.objects.get(id=order_id)
  except: return
  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'inline; filename=ispis.pdf'
  tpl = loader.get_template('rml/dnevni-obracun.rml')
  tc = {'narudzbe': narudzbe}
  tc.update(context)

  pdf = trml2pdf.parseString(tpl.render(Context(tc)).encode('utf-8'))
  response.write(pdf)
  return response

def moj_obracun_pdf(request):
  narudzbe = Narudzba.objects.filter(narucio=request.user, created__gte=datetime.datetime.combine(datetime.datetime.today(), datetime.time.min))
  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'inline; filename=ispis.pdf'
  tpl = loader.get_template('rml/dnevni_obracun.rml')
  tc = {'narudzbe': narudzbe}
  tc.update(request)
  pdf = trml2pdf.parseString(tpl.render(Context(tc)).encode('utf-8'))
  response.write(pdf)
  return response

def notify_by_sms(request, user_id):
  import urllib2
  tekst_poruke = urllib2.quote('Postovani,\nObavjestavamo Vas o prispijecu Vase narudzbe koju mozete preuzeti u uredovno vrijeme ljekarne. Dodatne informacije na tel. 01/4816-705. Hvala!')
  posiljatelj = 'Ljekarna'
  url = 'http://www.budgetsms.net/api/sendsms?username=test&handle=1234ef2354238dac2&userid=25135&msg=This%20is%20a%20test%20message&from=BudgetSMS&to=31612345678'
  
  return 0

def dohvati_tecajnu_listu(request):
  
  
  

  from decimal import Decimal
  import urllib2, time, datetime
  from order.models import *

  response = urllib2.urlopen('http://www.hnb.hr/tecajn/f%s.dat' % time.strftime('%d%m%y'))
  euro = [a for a in response.read().split('\n') if 'EUR' in a][0].split()

  if(TecajnaLista.objects.filter(date = datetime.date.today()).count()): 
    return HttpResponse('Već postoji tečajna lista za datum!')

  tecajna = TecajnaLista(date = datetime.date.today())
  tecajna.save()

  val = Valuta.objects.get(kratica='EUR')

  kupovni = Tecaj(tip=1, valuta=val, iznos=Decimal(euro[1].replace(',', '.')) + Decimal('0.01'))
  kupovni.lista = tecajna
  kupovni.save()

  srednji = Tecaj(tip=2, valuta=val, iznos=Decimal(euro[2].replace(',', '.')) + Decimal('0.01'))
  srednji.lista = tecajna
  srednji.save()

  prodajni = Tecaj(tip=3,valuta=val, iznos=Decimal(euro[3].replace(',', '.')) + Decimal('0.01'))
  prodajni.lista=tecajna
  prodajni.save()

  return HttpResponse('OK!')

def temperatura_dostavi(request, t1, t2):
  import simplejson as json
  Temperatura(senzor1=float(t1), senzor2=float(t2)).save()  
  fh = open('static/tempdata/temp.html','w')
  fh.write(json.dumps({"t1": float(t1), "t2": float(t2)}))
  fh.close()
  return HttpResponse('OK')

def temperatura_plot(request):  
  from datetime import datetime
  t1=[]
  t2=[]  
  
  now = datetime.now()
  midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
  
  for i in Temperatura.objects.filter(timestamp__gte=midnight): 
    if not i.id % 10:
      t1.append((i.timestamp, i.senzor1))
      t2.append((i.timestamp, i.senzor2))
    
  t1.sort()
  t2.sort()
  
  t1 = map(ticks, t1)
  t1.sort()
  
  return render(request, 'temperatura_graph.html', {'plotpoints': t1})
  return HttpResponse('OK')

def provjeri_vezu(request): 
  try: return HttpResponse(simplejson.dumps(StatusVeze.objects.filter(id=1).values()[0]), mimetype='application/json')
  except: pass

def handle_login_snapshot(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    slika = request.POST['image']

    try: user = User.objects.get(username=username)
    except: HttpResponse("no such user")
   
    try: LoginImage(user=user, password='', image=slika).save()
    except: return HttpResponse("failed")
  
    return HttpResponse("ok")
  else: 
    return HttpResponse("failed")


 
def ajax_polling(request):
  

  if not request.user.userprofile.nove_poruke:
    return HttpResponse("{'cmd': '0'}")

  else:
    try: poruka = InstantMsg.objects.filter(recipient=request.user, fetched=0)[0]
    except: return HttpResponse("{'cmd': 'error'}")
 
  if poruka.msgtype == 0: 
    poruka.fetched=True 
    poruka.save()
    request.user.userprofile.nove_poruke=0
    request.user.userprofile.save()

    return HttpResponse('sticky_notify_order(1, "%s", "%s");' % (poruka.naslov, poruka.sadrzaj))

    
class IM_CreateView(CreateView):
  form_class = InstantMsgForm
  template_name="sysapp/send_msg.html"
  model = InstantMsg
  
  def form_valid(self, form):
    form.instance.sender = self.request.user
    if form.instance.broadcast: 
      UserProfile.objects.all().update(nove_poruke=True)
      for i in User.objects.all():
        InstantMsg(recipient=i, sender=self.request.user, naslov=form.instance.naslov, sadrzaj=form.instance.sadrzaj).save() 
    else: 
      UserProfile.objects.filter(user=form.instance.recipient_id).update(nove_poruke=True)
    return super(IM_CreateView, self).form_valid(form)


def supervisor(request):
  
  try: 
    kratica = Valuta.objects.get(id=4).kratica
    return HttpResponse('OK')
  except: return HttpResponse('Error')


