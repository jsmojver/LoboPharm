#coding=utf-8



from order.models import *
from depo.models import *
from fiskalizacija.models import *
from meds.models import Artikal

from django.template import RequestContext
from django.shortcuts import render_to_response, render, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings

from sysapp.views import ClientAlert
from decimal import Decimal

from django.views.generic import ListView
from django.db.models import Count, Min, Sum, Max, Avg
from django.contrib.auth.models import User

import time, datetime
from random import randint


import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from cgi import escape

from django.core.mail import EmailMessage


from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, Table
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def mod11ini(value):
    
    length = len(value)
    sum = 0
    for i in xrange(0, length):
        sum += int(value[length - i - 1]) * (i + 2)
    res = sum % 11
    if res > 1:
        res = 11 - res
    else:
        res = 0
    return str(res)

class MojeDanasnjeNarudzbe(ListView):
    
    def get_queryset(self):
        return Narudzba.objects.filter(narucio=self.request.user, created__gte=datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)) 
    
    def get_context_data(self, **kwargs):
        context = super(MojeDanasnjeNarudzbe, self).get_context_data(**kwargs)
        
        
        context['uplate'] = self.get_queryset().filter(uplate__vrsta=0).aggregate(Sum('uplate__iznos'))['uplate__iznos__sum']
        context['ukupno'] = self.get_queryset().count()

        return context

class MyDepoToday(ListView):
    
    def get_queryset(self):
        return NarucenArtikal.objects.filter(narudzba__narucio=self.request.user, trziste=8, created__gte=datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)) 

    def get_context_data(self, **kwargs):
        context = super(MyDepoToday, self).get_context_data(**kwargs)
        context['kutija'] = sum([int(i.kolicina) for i in self.get_queryset()])
        context['ukupno'] = sum([i.get_total() for i in self.get_queryset()])

        indict = self.get_queryset().values('kolicina', 'ime')
        result = {}
        for i in indict:
          if i['ime'] not in result: 
            result[i['ime']] = int(i['kolicina'])
          else:
            result[i['ime']] += int(i['kolicina'])
        context['obracun'] = result 

        return context

def narudzba_get_sifra(request, narudzba_id):
  narudzba = get_object_or_404(Narudzba, sifra=narudzba_id) 
  return render(request, 'order/narudzba_detail.html', {'narudzba': narudzba}) 

def uplate_obracun(request): 
  
  uplate = ''
  if request.method == 'POST':
    blagajnik = User.objects.get(id=int(request.POST['blagajnik']))
    dan = request.POST['dan']
    mjesec = request.POST['mjesec']
    godina = request.POST['godina']
    if not (dan.isdigit() and mjesec.isdigit() and godina.isdigit()): return render(request, 'order/uplate_obracun.html', {'djelatnici': User.objects.filter(groups__name='Izdavanje')}) 
    
    try: uplate = Uplata.objects.filter(djelatnik=blagajnik, created__year=godina, created__month=mjesec, created__day=dan, vrsta=0)
    except: uplate = []
 
    interval = uplate.aggregate(Min('created'), Max('created'))

    kune_uplate = uplate.filter(valuta=4, vrsta=0, tip__in=[1, 2, 4, 6, 7, 8, 9]).aggregate(Sum('iznos'))['iznos__sum']
    euri_uplate = uplate.filter(valuta=1, vrsta=0, tip__in=[1, 2, 4, 6, 7, 8, 9]).aggregate(Sum('iznos'))['iznos__sum']
  
    if kune_uplate is None: kune_uplate = 0
    if euri_uplate is None: euri_uplate = 0

    

  try:
    p = "\x1b\x40" 
    p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
    p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
    p += strftime("%A, %d. %B %Y.  %H:%M:%S").decode('utf-8').encode('cp852') + '\n' 
    p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\n\x1b\x45\x01- O B R A Č U N   B L A G A J N E-\x1b\x45\x00\n\n')
    p += TXT_NORMAL + TXT_ALIGN_CT
    p += 'Djelatnik: %s\n' % blagajnik.get_full_name().encode('cp852')
    p += to852('Uplaćeno: %s kn\n') % kune_uplate
    p += to852('Uplaćeno: %s eur\n') % euri_uplate
    p += '\nPromet:\n\n'

    for i in range(42): p += '\xcd' 
    p += '\x1b\x21\x01' 
    for i in uplate:
      p+= '{:<20}'.format(i.get_tip()[:20]) + '{:>20}'.format('%s' % i.created) + '{:>15}'.format('%s %s' % (i.iznos, i.valuta.kratica)) + '\n'   
    p += '\x1b\x21\x00' 
    for i in range(42): p += '\xcd' 

    p += TXT_ALIGN_CT + '\n  Sigurnosni kod potvrde: %s  \n\x1c\x70\x02\x00\n\n\n\n\n\n' %  randint(1000000000, 9999999999) + PAPER_FULL_CUT
    printpos = 'javascript:print_plugin.escpos("%s");' % p.encode('hex')

    return render(request, 'order/uplate_obracun.html', {'object_list': uplate, 'djelatnici': User.objects.filter(groups__name='Izdavanje'), 'kune_uplate': kune_uplate, 'euri_uplate': euri_uplate, 'blagajnik': blagajnik, 'interval': interval, 'printpos': printpos})
  except NameError:
    return render(request, 'order/uplate_obracun.html', {'djelatnici': User.objects.filter(groups__name='Izdavanje')})

def danasnje_stanje_blagajne(request): 
  
  today = datetime.datetime.today()

  try: uplate = Uplata.objects.filter(djelatnik=request.user, created__year=today.year, created__month=today.month, created__day=today.day, vrsta=0)
  except: uplate = []
 
  interval = uplate.aggregate(Min('created'), Max('created'))

  kune_uplate = uplate.filter(valuta=4, vrsta=0, tip__in=[1, 2, 4, 6, 7, 8, 9]).aggregate(Sum('iznos'))['iznos__sum']
  euri_uplate = uplate.filter(valuta=1, vrsta=0, tip__in=[1, 2, 4, 6, 7, 8, 9]).aggregate(Sum('iznos'))['iznos__sum']

  if kune_uplate is None: kune_uplate = 0
  if euri_uplate is None: euri_uplate = 0

  try:
    p = "\x1b\x40" 
    p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
    p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
    p += strftime("%A, %d. %B %Y.  %H:%M:%S").decode('utf-8').encode('cp852') + '\n' 
    p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\n\x1b\x45\x01- O B R A Č U N   B L A G A J N E-\x1b\x45\x00\n\n')
    p += TXT_NORMAL + TXT_ALIGN_CT
    p += 'Djelatnik: %s\n' % request.user.get_full_name().encode('cp852')
    p += to852('Uplaćeno: %s kn\n') % kune_uplate
    p += to852('Uplaćeno: %s eur\n') % euri_uplate
    p += '\nPromet:\n\n'
    
    for i in uplate:
      p+= '{:<20}'.format(i.get_tip()[:20]) + '{:>20}'.format('%s' % i.created) + '{:>15}'.format('%s %s' % (i.iznos, i.valuta.kratica)) + '\n'

    p += TXT_ALIGN_CT + '\n  Sigurnosni kod potvrde: %s  \n\x1c\x70\x02\x00\n\n\n\n\n\n' %  randint(1000000000, 9999999999) + PAPER_FULL_CUT
    return HttpResponse('javascript:print_plugin.escpos("%s");' % p.encode('hex'))
   
  except:
    return HttpResponse('')

def obracun_moj_promet(request):
  try: moji_artikli = NarucenArtikal.objects.filter(log_order__user=request.user, log_order__event=5, status=5, modified__startswith=datetime.date.today()).order_by('trziste')
  except: return
  
  p = "\x1b\x40" 
  p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
  p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
  p += strftime("%A, %d. %B %Y.  %H:%M:%S").decode('utf-8').encode('cp852') + '\n' 
  p += TXT_ALIGN_CT + TXT_2HEIGHT + to852('\n\x1b\x45\x01- D N E V N I  P R O M E T -\x1b\x45\x00\n\n')
  p += TXT_NORMAL + TXT_ALIGN_CT
  p += 'Djelatnik: %s\n' % to852(request.user.get_full_name().encode('utf-8'))
  p += '\n\n'
  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<29}'.format('Artikal') + '{:>3}'.format('Kol') + '{:>11}'.format('Vrijeme') + '{:>14}'.format('Trziste') + '\x1b\x45\x00\n'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 
  
  for i in moji_artikli.all():
    p += '{:<29}'.format(i.ime[:27]) + '{:>3}'.format(i.kolicina) + '{:>11}'.format('%s' % i.modified.time()) + '{:>14}'.format(to852(i.trziste.naziv.encode('utf-8')))
    p += '\n'
  
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 
  p += TXT_ALIGN_CT + '\n  Sigurnosni kod potvrde: %s  \n\x1c\x70\x02\x00\n\n\n\n\n\n' %  randint(1000000000, 9999999999) + PAPER_FULL_CUT
  
  printpos = 'javascript:print_plugin.escpos("%s");' % p.encode('hex')
  
  return HttpResponse(printpos)

def trazi_korisnika(request):
    
    from django.db.models import Q
    rezultat = ''

    if request.method == 'POST':
      q = request.POST['ime_pacijenta'] 
      if q: 
        qset = (Q(ime__icontains=q) | Q(prezime__icontains=q))
        rezultat = Klijent.objects.filter(qset)
        if not rezultat.count() or rezultat.count() > 200:
          # search for start
          name_parts = q.split()
          if len(name_parts) > 0:
              qset = Q(ime__istartswith=name_parts[0])
          if len(name_parts) > 1:
              qset |= Q(prezime__istartswith=name_parts[1])
          rezultat = Klijent.objects.filter(qset)
          if not rezultat.count():          
            return HttpResponse('javascript:$(target).find("form").effect("shake", { times:2 }, 120);') 
            #return HttpResponse('javascript:info_warning("Upozorenje", "Previše rezultata, molimo suzite pretragu!");') 
          elif rezultat.count() > 200:
            return HttpResponse('javascript:info_warning("Upozorenje", "Previše rezultata, molimo suzite pretragu!");') 
                
    return render(request, 'order/order_trazi_korisnika.html', {'object_list': rezultat})

def odaberi_korisnika(request, pk):
  
  request.user.kosarica.klijent = get_object_or_404(Klijent, id=pk)
  request.user.kosarica.save()
  return HttpResponseRedirect(reverse('order.kosarica.view'))

def kosarica_remove(request, kosarica_artikal_id):    
  try: request.user.kosarica.artikli.get(id=kosarica_artikal_id).delete()
  except: return HttpResponse('javascript:info_warning("Greška", "Artikal nije pronađen!");')    
  return HttpResponseRedirect(reverse('order.kosarica.view'))
  
def kosarica_add(request): 
  if request.method == 'POST':
    lijek_id = int(request.POST['lijekId']) 
    kolicina = int(request.POST['kolicina'])
       
    if not kolicina>0: return HttpResponse('javascript:info_warning("Upozorenje", "Količina mora biti pozitivna!");')
   
    artikal = Artikal.objects.get(id=lijek_id)
        
    try: KosaricaArtikal.objects.create(artikal_id=lijek_id, kosarica_id=request.user.kosarica.id, kolicina=kolicina, naziv=artikal.name, cijena=artikal.cijena_s_marzom(), troskovi=artikal.manipulativni(), trziste=Trziste.objects.get(naziv='Njemačka'), shipping=0) 
    except: pass
    
    try: KosaricaArtikal.objects.filter(artikal__id=lijek_id, kosarica__id=request.user.kosarica.id).update(kolicina=kolicina)
    except: pass
    
    return HttpResponseRedirect(reverse('order.kosarica.view'))

def kosarica_add_alternate(request): 
  if request.method == 'POST':
    lijek_id = int(request.POST['lijekId']) 
    kolicina = int(request.POST['kolicina'])
  
    if not kolicina>0: return ClientAlert("Količina bi trebala biti pozitivna!")
    artikal = ArtikalDrugoTrziste.objects.get(id=lijek_id)
    atc_sifra = artikal.ATC.sifra if None != artikal.ATC else None

    tip_klijenta = request.user.kosarica.klijent.tip_klijenta
    
    if tip_klijenta == 1: 
      cijenaZaKorisnika = artikal.cijena_pacijenti()    
    elif tip_klijenta == '2': cijenaZaKorisnika = artikal.cijena_ljekarne()
    else: cijenaZaKorisnika = artikal.cijena_pacijenti()

    try: KosaricaArtikal.objects.create(kosarica_id=request.user.kosarica.id, kolicina=kolicina, naziv=artikal.ime, cijena=cijenaZaKorisnika, trziste=artikal.trziste, shipping=artikal.trziste.transport, atc_sifra=atc_sifra)
    except: pass
  
    return HttpResponseRedirect(reverse('order.kosarica.view'))

def kosarica_add_iz_stare_narudzbe(request, pk):
  try: narucen_artikal = NarucenArtikal.objects.get(id=pk)
  except: return

  if narucen_artikal.ZoNr:
    artikal = Artikal.objects.get(ZoNr=narucen_artikal.ZoNr)
    KosaricaArtikal.objects.create(artikal_id=artikal.id, kosarica_id=request.user.kosarica.id, kolicina=narucen_artikal.kolicina, naziv=artikal.name, cijena=artikal.cijena_s_marzom(), troskovi=artikal.manipulativni(), trziste=Trziste.objects.get(naziv='Njemačka'), shipping=1)
  else:
    KosaricaArtikal.objects.create(kosarica_id=request.user.kosarica.id, kolicina=narucen_artikal.kolicina, naziv=narucen_artikal.ime, cijena=narucen_artikal.jedinicna_cijena, trziste=narucen_artikal.trziste, shipping=narucen_artikal.shipping, valuta=narucen_artikal.valuta, atc_sifra=narucen_artikal.atc_sifra)

  return HttpResponse('javascript:info_notify("OK", "Artikl dodan u košaricu!");')



def kosarica_submit(request): 
  kosarica = request.user.kosarica
  if not kosarica.artikli.count(): return HttpResponse('javascript:info_warning("Upozorenje", "Košarica ne može biti prazna!");')
  narudzba = Narudzba(klijent=request.user.kosarica.klijent, status=1, narucio=request.user)
  narudzba.save()

  if kosarica.artikli.filter(trziste=8).count() == kosarica.artikli.all().count():
    narudzba.depo = 1
    narudzba.save()
  
  for i in kosarica.artikli.all():
    if i.artikal: 
      artikal = i.artikal
      nartikal = NarucenArtikal(narudzba=narudzba, ZoNr=artikal.ZoNr, Sortname1=artikal.Sortname1, ime=artikal.name, kolicina=i.kolicina, jedinice=artikal.jedinice, std_kolicina=artikal.std_kolicina, kratica_dobavljaca=artikal.kratica_dobavljaca, jedinicna_cijena=i.cijena, trziste=i.trziste, valuta=i.valuta, shipping=i.shipping, pakiranje=artikal.kolicina, atc_sifra=artikal.ATC.sifra)
      nartikal.save()
    else:
      nartikal=NarucenArtikal(narudzba=narudzba, ime=i.naziv, jedinicna_cijena=i.cijena, kolicina=i.kolicina, trziste=i.trziste, valuta=i.valuta, shipping=i.shipping, atc_sifra=i.atc_sifra)
      nartikal.save()    
    LogArtikla(artikal=nartikal, user=request.user, event=0, opis='Artikal je naručen').save()
  
    
    try: Uplata(narudzba=narudzba, valuta_id=i.valuta, djelatnik=request.user, klijent=narudzba.klijent, iznos=i.cijena*i.kolicina, tip=2, vrsta=1, tecaj=TecajnaLista.objects.latest('date').prodajni_tecaj(), napomena=nartikal.ime).save()
    except: pass

  
  if narudzba.artikli.filter(shipping=1).count(): 
    try: Uplata(narudzba=narudzba, valuta_id=1, djelatnik=request.user, klijent=narudzba.klijent, iznos=narudzba.usluge_transporta(), tip=4, vrsta=1, tecaj=TecajnaLista.objects.latest('date').prodajni_tecaj()).save()
    except: pass

  
  
  
  
  
  kosarica.isprazni()
  return HttpResponseRedirect(reverse('order.view', args=[narudzba.id]))
    
def kosarica_empty(request):
  try: request.user.kosarica.artikli.all().delete()
  except: pass
  return HttpResponseRedirect(reverse('order.kosarica.view'))

def kosarica_naslovna(request):
  return render(request, "order/naslovna_kosarica.html")

def kosarica_price_adjust(request, kosaricaartikal_id, novacijena):
  artikal = get_object_or_404(KosaricaArtikal, pk=kosaricaartikal_id)
  artikal.cijena=novacijena
  artikal.save()
  return HttpResponse('')

def kosarica_qty_adjust(request, kosaricaartikal_id, novakolicina):
  artikal = get_object_or_404(KosaricaArtikal, pk=kosaricaartikal_id)
  artikal.kolicina=novakolicina
  artikal.save()
  return HttpResponse('')

def order_set_konto(request, order_id, konto_name):
    order = get_object_or_404(Narudzba, pk=order_id)
    if 1 != order.status or IsSentToEskulap(order):
        return HttpResponse('javascript:info_warning("Upozorenje", "Nije moguće promijeniti konto!");')
    order.konto_name = konto_name
    order.save()
    return HttpResponseRedirect(reverse('order.view', args=[order_id]))

def order_vip_status(request, order_id):
    order = get_object_or_404(Narudzba, pk=order_id)
    if 'Konto 1' != order.konto_name:
        return HttpResponse('javascript:info_warning("Upozorenje", "Neispravan konto!");')
    if not IsSentToEskulap(order):
        return HttpResponse('javascript:info_warning("Upozorenje", "Nije napravljena ponuda!");')
    if 1 != order.status:
        return HttpResponse('javascript:info_warning("Upozorenje", "Nije moguće postaviti VIP status!");')
    order.status = 10
    order.save()
    return HttpResponseRedirect(reverse('order.view', args=[order_id]))

def order_narudzba_storniraj(request, order_id):
  order = get_object_or_404(Narudzba, pk=order_id)
  order.status = 7
  order.save()
  order.artikli.all().delete()
  return HttpResponseRedirect(reverse('order.posiljka.active.view'))
  
def order_izdavanje(request, narudzba_id):
  narudzba = get_object_or_404(Narudzba, pk=narudzba_id)  
  artikli = narudzba.artikli.filter(status=1)
  if not artikli.count():
    return HttpResponse('javascript:info_warning("Upozorenje", "Nema artikala koje je moguće izdati!");')
  return render(request, "order/izdavanje_form.html", {'narudzba': narudzba, 'artikli': artikli})      
  

def order_izdavanje_zahtjev(request, artikal_id):
  artikal = get_object_or_404(NarucenArtikal, pk=artikal_id)  
  OrderIzdavanjeZahtjev(narucen_artikal=artikal, user=request.user, status=0).save()
  return HttpResponse('javascript:info_notify("Obavijest", "Zahtjev upućen!");')      

def order_izdavanje_izdaj(request, narudzba_id):
  narudzba = get_object_or_404(Narudzba, pk=narudzba_id)  
  for i in narudzba.artikli.filter(status=1):
    i.status = 4
    i.placeno = 1
    i.save()
    LogArtikla(artikal=i, user=request.user, event=5, opis='Artikal je izdan kupcu').save()
  return HttpResponse('javascript:info_notify("Izdano", "Narudžba %s uspješno izdana!");' % narudzba.sifra)      

def order_narudzba_naplati_sve(request, narudzba_id):
   
  narudzba = get_object_or_404(Narudzba, pk=narudzba_id)  
  for i in narudzba.artikli.all():
    tmp = order_artikal_naplati(request, i.id)
  return HttpResponseRedirect(reverse('order.view', args=[narudzba.id,]))

def order_narudzba_izdaj_sve(request, narudzba_id):
   
  narudzba = get_object_or_404(Narudzba, pk=narudzba_id)  
  for i in narudzba.artikli.all():
    tmp = order_artikal_izdaj(request, i.id)
  return HttpResponseRedirect(reverse('order.view', args=[narudzba.id,]))



def order_artikal_zaprimi(request, narucenartikal_id, redirect_to):
  artikal = get_object_or_404(NarucenArtikal, pk=narucenartikal_id)
  if artikal.status == 0: 
    artikal.status = 1  
    artikal.save()
    LogArtikla(artikal=artikal, user=request.user, event=1, opis='Artikal zaprimljen u skladište').save()
    
    
    if not NarucenArtikal.objects.filter(status=0, narudzba = artikal.narudzba).count():
      artikal.narudzba.status = 4 
    else:
      artikal.narudzba.status = 5 
    artikal.narudzba.save()
    if redirect_to == '0':
      return HttpResponseRedirect(reverse('order.incoming.view'))
    else: 
      return HttpResponseRedirect(reverse('order.view', args=[artikal.narudzba.id]))

def order_artikal_naplati(request, artikal_id):
  
  artikal = get_object_or_404(NarucenArtikal, pk=artikal_id)
  LogArtikla(artikal=artikal, user=request.user, event=4, opis='Artikal je naplaćen').save()
  artikal.status=4
  artikal.placeno=1
  artikal.save()
  return HttpResponseRedirect(reverse('order.view', args=[artikal.narudzba.id,]))

def order_artikal_storniraj(request, artikal_id):
  
  artikal = get_object_or_404(NarucenArtikal, pk=artikal_id)
  if artikal.status == '0':
    LogArtikla(artikal=artikal, user=request.user, event=2, opis='Artikal je storniran').save() 
    artikal.status=2
    artikal.save()

  return HttpResponseRedirect(reverse('order.view', args=[artikal.narudzba.id,]))

def order_artikal_izdaj(request, artikal_id):
  
  artikal = get_object_or_404(NarucenArtikal, pk=artikal_id)
  
  

  if artikal.trziste_id == 8:
    try: 
      depolijek = Lijek.objects.get(naziv=artikal.ime)
      kolicina = int(artikal.kolicina)
      
      
      depolijek.save()  
      Zahtjev(lijek=depolijek, kolicina=kolicina, user=request.user, status=0).save()
     
     
    except:
      return HttpResponse('javascript:info_warning("Upozorenje", "Ne mogu pronaći lijek s takvim nazivom na depou. Upomoć!")')
  else:
    Zahtjev(lijek_id=400, kolicina=1, user=request.user, status=0, zabiljezba='Izdavanje narudžbe', narucenartikal=artikal, narudzba=artikal.narudzba).save()

  LogArtikla(artikal=artikal, user=request.user, event=5, opis='Artikal je izdan kupcu').save()
  artikal.status=5
  artikal.save()
  
  
  if not artikal.narudzba.artikli.all().exclude(placeno=1).count():   
    artikal.narudzba.status = 6
    artikal.narudzba.save()
 
  return HttpResponseRedirect(reverse('order.view', args=[artikal.narudzba.id,]))



def order_uplata_add(request):
  
  if request.method == 'POST':
    tip = request.POST['tip_uplate'] 
    iznos = str(request.POST['iznos']).replace(',', '.')
    iznos = Decimal(iznos)

    valuta = request.POST['valuta']
    napomena = request.POST['biljeska']
    vrsta = request.POST['vrsta']
    try: narudzba = Narudzba.objects.get(id=request.POST['narudzba'])
    except: return
       
    
   
    uplata = Uplata(narudzba=narudzba, djelatnik=request.user, klijent=narudzba.klijent, iznos=iznos, tip=tip, vrsta=vrsta, valuta_id=valuta, napomena=napomena, tecaj=TecajnaLista.objects.latest('date').prodajni_tecaj()).save()
    if tip=='6':
      narudzba.slati_postom = 1
      narudzba.save()
    try: pass
    except: return HttpResponse('javascript:info_warning("Upozorenje", "Greška!");')
    
    return HttpResponseRedirect(reverse('order.view', args=[narudzba.id]))

def order_uplata_delete(request, narudzba_id, uplata_id):
  try: 
    narudzba = Narudzba.objects.get(id=narudzba_id)
    uplata = Uplata.objects.get(id=uplata_id)
  except: return HttpResponse('')
 
  if uplata.vrsta == 1 and uplata.tip != '2':
    uplata.delete()
    if uplata.tip=='6':
      narudzba.slati_postom = 0
      narudzba.save()

  return HttpResponseRedirect(reverse('order.view', args=[narudzba.id]))

def order_fiskaliziraj_racun(request, narudzba_id):
  import time
  n = get_object_or_404(Narudzba, pk=narudzba_id) 
  if n.racuni.filter(storno=0, stornira_racun__isnull=True).count(): 
    return HttpResponse('{"racun_id": "%s", "greska": "Račun je već fiskaliziran"}' % n.racuni.filter(storno=0).latest().id)

  r = Racun(djelatnik=request.user, narudzba=n) 

  ukupan_iznos = 0

  if not r.stavke.count(): 
    
    

    for i in n.artikli.all():
      RacunStavka(cijena=i.jedinicna_cijena_kn(), iznos=Decimal(i.kolicina)*i.jedinicna_cijena_kn(), kolicina=i.kolicina, naziv=i.ime, racun=r).save()
      ukupan_iznos += Decimal(i.kolicina)*i.jedinicna_cijena_kn()
 
    if n.uplate.filter(tip='4').count():
      dobava = sum([i.to_kn() for i in n.uplate.filter(tip='4')])
      RacunStavka(cijena=dobava, iznos=dobava, kolicina=1, naziv='Usluga dobave', racun=r).save()
      ukupan_iznos += dobava
  
    if n.uplate.filter(tip='6').count(): 
      postarina = sum([i.to_kn() for i in n.uplate.filter(tip='6')])
      RacunStavka(cijena=postarina, iznos=postarina, kolicina=1, naziv='Usluga postarine', racun=r).save()
      ukupan_iznos += postarina
    
    if n.uplate.filter(tip='7').count(): 
      posredovanje = sum([i.to_kn() for i in n.uplate.filter(tip='7')])
      RacunStavka(cijena=posredovanje, iznos=posredovanje, kolicina=1, naziv='Usluga posredovanja', racun=r).save()
      ukupan_iznos += posredovanje

  porezna_osnovica = Decimal(ukupan_iznos) * Decimal('100.00') / (Decimal(settings.STOPA_PDV) + Decimal('100.00'))

  iznos_poreza = ukupan_iznos-porezna_osnovica
  if not r.porezi.count():
    RacunPorez(racun=r, stopa=Decimal(settings.STOPA_PDV), iznos=iznos_poreza, osnovica=porezna_osnovica).save()

  r.iznos = ukupan_iznos 

  
  

  greska = ''
  start_time = time.time()
  try: r.posalji()
  except Exception, e:
    greska = e
    RacunLog(racun=r, tip=3, poruka_zahtjev=e).save()
  exec_time = time.time() - start_time
  return HttpResponse('{"racun_id": "%s", "exec_time": "%s", "greska": "%s"}' % (r.id, exec_time, greska))      

def order_akontacija_racun(request, narudzba_id):
  import time
  n = get_object_or_404(Narudzba, pk=narudzba_id) 

  if n.racuni.filter(storno=0, stornira_racun__isnull=True).count(): 
    return HttpResponse('{"racun_id": "%s", "greska": "Akontacija je već fiskalizirana"}' % n.racuni.filter(storno=0).latest().id)

  if not n.get_polog_kn() > 0: 
    return HttpResponse('{"racun_id": "%s", "greska": "Nema evidentiranih pologa"}' % n.racuni.filter(storno=0).latest().id)

  r = Racun(djelatnik=request.user, narudzba=n) 

  ukupan_iznos = 0

  if not r.stavke.count(): 
    RacunStavka(cijena=n.get_polog_kn(), iznos=n.get_polog_kn(), kolicina=1, naziv='Akontacija za narudzbu', racun=r).save()  
    ukupan_iznos = n.get_polog_kn()

  porezna_osnovica = Decimal(ukupan_iznos) * Decimal('100.00') / (Decimal(settings.STOPA_PDV) + Decimal('100.00'))

  iznos_poreza = ukupan_iznos-porezna_osnovica
  if not r.porezi.count():
    RacunPorez(racun=r, stopa=Decimal(settings.STOPA_PDV), iznos=iznos_poreza, osnovica=porezna_osnovica).save()

  r.iznos = ukupan_iznos 

  greska = ''
  start_time = time.time()
  try: r.posalji()
  except Exception, e:
    greska = e
    RacunLog(racun=r, tip=3, poruka_zahtjev=e).save()
  exec_time = time.time() - start_time
  return HttpResponse('{"racun_id": "%s", "exec_time": "%s", "greska": "%s"}' % (r.id, exec_time, greska))      

def order_storniraj_racun(request, racun_id):
  

  import time
  racun = get_object_or_404(Racun, id=racun_id) 
  if racun.storno: 
    return HttpResponse('{"racun_id": "%s", "greska": "Račun je već storniran"}' % racun.id)

  if racun.narudzba: 
    storno = Racun(djelatnik=request.user, stornira_racun=racun, narudzba=racun.narudzba) 
  else:
    storno = Racun(djelatnik=request.user, stornira_racun=racun) 

  for i in racun.stavke.all(): 
    RacunStavka(cijena=i.cijena, iznos=-i.iznos, kolicina=-i.kolicina, naziv=i.naziv, racun=storno).save()   

  



   
  for i in racun.porezi.all():
    RacunPorez(racun=storno, stopa=i.stopa, iznos=-i.iznos, osnovica=-i.osnovica).save()

  storno.iznos = -racun.iznos 

  racun.storno = True
  racun.save()

  greska = ''
  start_time = time.time()
  try: storno.posalji()
  except Exception, e:
    greska = e
    RacunLog(racun=storno, tip=3, poruka_zahtjev=e).save()
  exec_time = time.time() - start_time
  return HttpResponse('{"racun_id": "%s", "exec_time": "%s", "greska": "%s"}' % (storno.id, exec_time, greska))      

def order_storniraj_njemacki_racun(request, racun_id):
  racun = get_object_or_404(NarudzbaRacun, id=racun_id)
  
  if racun.storniran: 
    return HttpResponse('{"racun_id": "%s", "greska": "Račun je već storniran"}' % racun.id)

  storno = NarudzbaRacun(kreirao=request.user, stornira_racun=racun, narudzba=racun.narudzba)

  try: storno.broj = NarudzbaRacun.objects.latest('broj').broj + 1
  except: storno.broj = 1
  storno.save()

  for i in racun.stavke.all():
    NarudzbaRacunStavka(jedinicna_cijena=i.jedinicna_cijena, iznos=-i.iznos, kolicina=-i.kolicina, naziv=i.naziv, racun=storno).save()

  racun.storniran = True
  racun.save()

  return HttpResponseRedirect(reverse('order.view', args=[racun.narudzba.id]))



def moje_dnevno_pdf_izvjesce(request):
  
    narudzbe = MojeDanasnjeNarudzbe()
    narudzbe.request = request



    depo = Narudzba.objects.filter(narucio=request.user, created__gte=datetime.datetime.combine(datetime.datetime.today(), datetime.time.min), depo=1).exclude(status=7) 
    danasnji_tecaj = TecajnaLista.objects.latest('date').prodajni_tecaj()

    query = narudzbe.get_queryset().filter(depo=0).exclude(status=7) 
    uplate = query.filter(uplate__vrsta=0).aggregate(Sum('uplate__iznos'))['uplate__iznos__sum']
    kutija = query.aggregate(Sum('artikli__kolicina'))['artikli__kolicina__sum']
    artikala = query.aggregate(Count('artikli'))['artikli__count']

    uplate_depo = depo.filter(uplate__vrsta=0).aggregate(Sum('uplate__iznos'))['uplate__iznos__sum'] 
    kutija_depo = depo.aggregate(Sum('artikli__kolicina'))['artikli__kolicina__sum']
    artikala_depo = depo.aggregate(Count('artikli'))['artikli__count']

    moj_depo = MyDepoToday()
    moj_depo.request = request
    depo_query = moj_depo.get_queryset()

    indict = depo_query.values('kolicina', 'ime')
    result = {}
    for i in indict:
      if i['ime'] not in result:
        result[i['ime']] = int(i['kolicina'])
      else:
        result[i['ime']] += int(i['kolicina'])

    t=time.localtime()                         
    racuni = Racun.objects.filter(djelatnik=request.user, created__year=t.tm_year, created__month=t.tm_mon, created__day=t.tm_mday, storno=0, stornira_racun__isnull=True)
  
    broj_racuna = racuni.count()
    iznos_racuna = racuni.aggregate(Sum('iznos'))['iznos__sum']






    template = get_template('rml/test2.rml')
    context = Context({'pagesize': 'A4', 'narudzbe': query, 'djelatnik': request.user, 'uplaceno': uplate, 'kutija': kutija, 'artikala': artikala, 'datum': datetime.datetime.today(), 'uplate_depo': uplate_depo, 'kutija_depo': kutija_depo, 'artikala_depo': artikala_depo, 'depo': depo, 'depo_obracun': result, 'racuni': racuni, 'broj_racuna': broj_racuna, 'iznos_racuna': iznos_racuna, 'tecaj': danasnji_tecaj})
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), result, encoding='UTF-8')
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def pdf_danasnji_fiskalni_racuni(request):
    t=time.localtime()                         
    racuni = Racun.objects.filter(created__year=t.tm_year, created__month=t.tm_mon, created__day=t.tm_mday)
  
    broj_racuna = racuni.count()
    iznos_racuna = racuni.aggregate(Sum('iznos'))['iznos__sum']

    template = get_template('rml/danasnji_fiskalni_racuni.rml')
    context = Context({'pagesize': 'A4', 'racuni': racuni, 'broj': broj_racuna, 'iznos': iznos_racuna, 'djelatnik': request.user, 'datum': datetime.datetime.today()})
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), result, encoding='UTF-8')
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def pdf_ispis_danasnjih_narudzbi(request):
  
    query = Narudzba.objects.filter(created__gte=datetime.datetime.combine(datetime.datetime.today(), datetime.time.min), depo=0).exclude(status=6) 
    danasnji_tecaj = TecajnaLista.objects.latest('date').prodajni_tecaj()

    kutija = query.aggregate(Sum('artikli__kolicina'))['artikli__kolicina__sum']
    artikala = query.aggregate(Count('artikli'))['artikli__count']

    template = get_template('rml/ispis_danasnjih_narudzbi.rml')
    context = Context({'pagesize': 'A4', 'narudzbe': query, 'djelatnik': request.user, 'kutija': kutija, 'artikala': artikala, 'datum': datetime.datetime.today(), 'tecaj': danasnji_tecaj})
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), result, encoding='UTF-8')
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def pdf_slanje_danasnjih_narudzbi(request):
  
    query = Narudzba.objects.filter(created__gte=datetime.datetime.combine(datetime.datetime.today(), datetime.time.min), depo=0).exclude(status=6) 
    danasnji_tecaj = TecajnaLista.objects.latest('date').prodajni_tecaj()

    kutija = query.aggregate(Sum('artikli__kolicina'))['artikli__kolicina__sum']
    artikala = query.aggregate(Count('artikli'))['artikli__count']

    template = get_template('rml/ispis_danasnjih_narudzbi.rml')
    context = Context({'pagesize': 'A4', 'narudzbe': query, 'djelatnik': request.user, 'kutija': kutija, 'artikala': artikala, 'datum': datetime.datetime.today(), 'tecaj': danasnji_tecaj})
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.CreatePDF(html.encode('utf-8'), result, encoding='UTF-8')
    email = EmailMessage('Narudžba, %s' % datetime.date.today().isoformat(), 'Primjer - dostavljam narudžbu kao attachment', 'brainpool1971@yahoo.de', ['brainpool1971@yahoo.de'])
    if not pdf.err:
      email.attach('narudzbe-%s.pdf' % datetime.date.today().isoformat(), result.getvalue(), 'application/pdf')
      email.send()
    else: 
      return HttpResponse('FAIL')
    return HttpResponse('OK')


def pdf_dnevni_obracun_blagajne(request):
    import project.settings

    today = datetime.datetime.today()

    try: uplate = Uplata.objects.filter(djelatnik=request.user, created__year=today.year, created__month=today.month, created__day=today.day, vrsta=0)
    except: uplate = []
 
    interval = uplate.aggregate(Min('created'), Max('created'))
 
    kune_uplate = uplate.filter(valuta=4, vrsta=0, tip__in=[1, 2, 4, 6, 7, 8, 9]).aggregate(Sum('iznos'))['iznos__sum']
    euri_uplate = uplate.filter(valuta=1, vrsta=0, tip__in=[1, 2, 4, 6, 7, 8, 9]).aggregate(Sum('iznos'))['iznos__sum']

    template = get_template('rml/ispis_danasnje_blagajne.rml')
    context = Context({'pagesize': 'A4', 'uplate': uplate, 'djelatnik': request.user, 'datum': datetime.datetime.today(), 'uplate': uplate, 'interval': interval, 'kune': kune_uplate, 'euri': euri_uplate})
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), result, encoding='UTF-8')
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def generiraj_pdf417(narudzba_id):
  from elaphe.pdf417 import Pdf417
  narudzba = get_object_or_404(Narudzba, pk=narudzba_id)

  lista = ['HRVHUB30', 'HRK', '', '', '', '', 'KURFURSTEN APOTHEKE', 'KURFURSTENSTRASSE 5', '45138 ESSEN, BRD', project.settings.BankAccountNumber, 'HR01', '', 'CMDT', '']

  lista[2] = str(int(abs(narudzba.grand_total_kn()) * 100)).zfill(15)

  lista[3] = narudzba.klijent.get_full_name()
  lista[4] = narudzba.klijent.adresa
  lista[5] = narudzba.klijent.postanski_broj + ' ' + narudzba.klijent.grad
  lista[11] = str(narudzba.generiraj_poziv_na_broj())
  lista[13] = 'Narudzba ' + str(narudzba.sifra)

  f='\n'.join([i for i in lista])
  f += '\n'
  f = f.encode('utf-8')

  x = open('/tmp/log', 'w') 
  x.write(f)
  x.close()

  if len(f) % 6:
    f = f[:-1] 
    for i in range(5 - (len(f) % 6)): f+= ' '
    f += '\n'

  kod = "^924"

  g = [f[i:i+6] for i in range(0, len(f), 6)]
  h = [[ord(c) for c in i] for i in g] 
  for j in h:
    tmp = []
    s = sum([j[i] * 256**(5-i) for i in range(6)])
    for i in range(5):
      tmp.append(s%900)
      s = s / 900
    tmp = tmp[::-1]
    for i in range(5):
      kod += "^%03d" % tmp[i]
  
  x = open('/tmp/log2', 'w') 
  x.write(kod)
  x.close()

  try: pdf417 = Pdf417().render(kod, options=dict(compact=False, columns=9, eclevel=4), margin=1, scale=2)
  except:
    try: pdf417 = Pdf417().render(kod, options=dict(compact=False, columns=9, rows=36, eclevel=4), margin=1, scale=2)
    except: 
      try: pdf417 = Pdf417().render(kod, options=dict(compact=False, columns=9, rows=40, eclevel=4), margin=1, scale=2)
      except: pass 
  pdf417.save('/tmp/pdf417-' + str(narudzba.sifra) + '.png')
  return 1

def order_check_konto(request, narudzba_id):
    narudzba = get_object_or_404(Narudzba, pk=narudzba_id) 
    if not narudzba.konto_name: 
        return HttpResponse('javascript:info_warning("Upozorenje", "Konto mora biti odabran!");')
    else:
        path = "order/virman/print/%s" % (narudzba_id,)
    if settings.VIRMAN_PDF:
        return HttpResponse('javascript:window.location.href="%s";' % (path,))
    else:
        return HttpResponseRedirect(reverse('order.virman.print', args=(narudzba_id,)))

def napravi_virman(request, narudzba_id):
    if settings.VIRMAN_PDF:
        return napravi_virman_pdf(request, narudzba_id)
    else:
        return napravi_virman_printer(request, narudzba_id)

def napravi_virman_pdf(request, narudzba_id):
    import project.settings

    narudzba = get_object_or_404(Narudzba, pk=narudzba_id) 
    es_ponuda_id = SendToEskulap(narudzba)

    pdv_code = narudzba.get_pdv_code()
    sifra_narudzbe = str(narudzba.sifra) + pdv_code

    hoffset = 0 
    voffset = 0 

      
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="hub3a.pdf"'

    pdfmetrics.registerFont(TTFont('FreeSans', "%s/templates/rml/FreeSans.ttf" % (project.settings.local.ProjectPath)))
   
    doc = canvas.Canvas(response, pagesize=A4)
    doc.setFont('FreeSans', 9)

    doc.drawString((8+hoffset)*mm, (286+voffset)*mm, narudzba.klijent.get_full_name())
    doc.drawString((8+hoffset)*mm, (282+voffset)*mm, narudzba.klijent.adresa)
    doc.drawString((8+hoffset)*mm, (278+voffset)*mm, "%s %s" % (narudzba.klijent.postanski_broj, narudzba.klijent.grad))
    
    doc.drawString((81+hoffset)*mm, (288+voffset)*mm, "HRK".decode('utf-8')) 
    

    total = "%.2f" % abs(narudzba.grand_total_kn())
    total = total.replace('.', ',')
 
    poziv_na_broj = narudzba.generiraj_poziv_na_broj() 

    doc.drawRightString((148+hoffset)*mm, (288+voffset)*mm, "=%s" % total) 
    
    doc.drawString((81+hoffset)*mm, (268+voffset)*mm, project.settings.BankAccountNumber.decode('utf-8'))

    doc.drawString((56+hoffset)*mm, (259+voffset)*mm, "HR01".decode('utf-8')) 
    doc.drawString((77+hoffset)*mm, (259+voffset)*mm, poziv_na_broj) 
    
    doc.drawString((8+hoffset)*mm, (258+voffset)*mm, "Kurfürsten Apotheke".decode('utf-8'))
    doc.drawString((8+hoffset)*mm, (254+voffset)*mm, "Kurfürstenstrasse 5".decode('utf-8'))
    doc.drawString((8+hoffset)*mm, (250+voffset)*mm, "45138 Essen, BRD".decode('utf-8'))

    doc.drawString((56+hoffset)*mm, (249+voffset)*mm, "CMDT".decode('utf-8')) 
    
    doc.drawString((88+hoffset)*mm, (249+voffset)*mm, "Uplata za narudžbu br. %s" % sifra_narudzbe) 
    doc.drawString((88+hoffset)*mm, (244+voffset)*mm, "Ponuda br. %d" % es_ponuda_id) 
    
    doc.setFont('FreeSans', 8)
    doc.drawString((161+hoffset)*mm, (267+voffset)*mm, project.settings.BankAccountNumber.decode('utf-8'))
    doc.drawString((161+hoffset)*mm, (258+voffset)*mm, "HR01 %s" % poziv_na_broj) 
    
    doc.drawString((161+hoffset)*mm, (288+voffset)*mm, "HRK =%s" % total) 
    
    doc.drawString((161+hoffset)*mm, (281+voffset)*mm, narudzba.klijent.get_full_name()) 

    doc.drawString((161+hoffset)*mm, (251+voffset)*mm, "Uplata za narudžbu".decode('utf-8')) 
    doc.drawString((161+hoffset)*mm, (247+voffset)*mm, "br. %s" % sifra_narudzbe) 
    
    doc.setFont('FreeSans', 9)
    doc.drawString((161+hoffset)*mm, (206+voffset)*mm, "Kurfürsten Apotheke".decode('utf-8'))
    doc.drawString((161+hoffset)*mm, (202+voffset)*mm, "Narudžba br. %s" % sifra_narudzbe)

    
    
    

    try: 
      generiraj_pdf417(narudzba.id)
      doc.drawImage('/tmp/pdf417-' + str(narudzba.sifra) + '.png', 20, 620, 160, 61) 
      os.remove('/tmp/pdf417-' + str(narudzba.sifra) + '.png')
    except: pass

    doc.showPage()
    doc.save()

    return response

def napravi_virman_printer(request, narudzba_id):
    import project.settings

    narudzba = get_object_or_404(Narudzba, pk=narudzba_id) 
    es_ponuda_id = SendToEskulap(narudzba)

    pdv_code = narudzba.get_pdv_code()
    sifra_narudzbe = str(narudzba.sifra) + pdv_code

    hoffset = 0 
    voffset = 0 


    try:
        p = "\x1b\x40" 
        p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
        p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
        p += TXT_NORMAL + TXT_ALIGN_CT + "\n\x1b\x45\x01- Ponuda br. %d-\x1b\x45\x00\n\n" % es_ponuda_id
        total = "%.2f" % abs(narudzba.grand_total_kn())
        total = total.replace('.', ',')
        p += 'HRK =%s\n' % total
        
        p += '\n\n\n\n\n\n' + PAPER_FULL_CUT

        return HttpResponse('javascript:print_plugin.escpos("%s");' % p.encode('hex'))
       
    except:
        return HttpResponse('')


#--------------------------------------------------------------------------------------------------


def racuni_list(request):
    import datetime
    from project.util import str_to_date
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q

    q = Q()
    range_type = request.COOKIES.get("range_type", "")
    begin_date = str_to_date(request.COOKIES.get("begin_date"), datetime.date.today())
    end_date = str_to_date(request.COOKIES.get("end_date"), datetime.date.today())
    cookies = []

    if request.method == "POST":
        cmd = request.POST.get("cmd")
        if cmd == "daily_report_range":
            range_type = request.POST.get("range_type")
            begin_date = request.POST.get("begin_date")
            end_date = request.POST.get("end_date")
            cookies.append(("range_type", range_type))
            cookies.append(("begin_date", begin_date))
            cookies.append(("end_date", end_date))
            begin_date = str_to_date(begin_date)
            end_date = str_to_date(end_date)
        elif cmd == "download_monthly_report":
            return download_monthly_report(request, request.POST.get("monthly_report_year"), request.POST.get("monthly_report_month"))

    if range_type == "day":
        q &= Q(created__range=[begin_date, begin_date + datetime.timedelta(days=1)])
    elif range_type == "range":
        q &= Q(created__range=[begin_date, end_date + datetime.timedelta(days=1)])
    else:
        pass

    items_list = NarudzbaRacun.objects.filter(q).order_by('-broj')

    paginator = Paginator(items_list, 25)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    response = render_to_response("order/narudzbaracun_list.html",
        {
            "object_list": items,
            "page_obj": items,
            "paginator": paginator,
            "range_type": range_type,
            "begin_date": begin_date,
            "end_date": end_date,
            "report_months": [u"Siječanj", u"Veljača", u"Ožujak", u"Travanj", u"Svibanj", u"Lipanj", u"Srpanj", u"Kolovoz", u"Rujan", u"Listopad", u"Studeni", u"Prosinac"],
            "report_years": range(2013, datetime.datetime.now().year + 1),
            "now": datetime.datetime.now(),
        }, context_instance=RequestContext(request)
    )

    if len(cookies) > 0:
        for c in cookies:
            response.set_cookie(c[0], c[1])

    return response


#--------------------------------------------------------------------------------------------------


def download_daily_report(request):
    import datetime
    from project.util import str_to_date
    from django.db.models import Q
    import project.settings

    q = Q(storniran=False) & Q(stornira_racun=None)
    range_type = request.COOKIES.get("range_type", "")
    begin_date = str_to_date(request.COOKIES.get("begin_date"), datetime.date.today())
    end_date = str_to_date(request.COOKIES.get("end_date"), datetime.date.today())

    if range_type == "day":
        q &= Q(created__range=[begin_date, begin_date + datetime.timedelta(days=1)])
    elif range_type == "range":
        q &= Q(created__range=[begin_date, end_date + datetime.timedelta(days=1)])
    else:
        pass

    items = NarudzbaRacun.objects.filter(q).order_by('broj')

    class OrderItem:
        pass
    class ProductItem:
        pass

    order_items = []
    total_price = Decimal(0.0)

    for item in items:
        order = OrderItem()
        order.broj = item.broj
        order.client_name = item.narudzba.klijent.get_report_name()
        order.total_price = item.narudzba.get_report_total_price()
        order.products = []
        for p in item.narudzba.artikli.all():
            product = ProductItem()
            product.ime = p.ime
            product.kolicina = p.kolicina
            product.price = p.get_report_price()
            product.total_price = p.get_report_total_price()
            order.products.append(product)
        total_price += order.total_price

        order_items.append(order)

    html = render_to_string("order/narudzbaracun_report.html",
        {
            "items": order_items,
            "range_type": range_type,
            "begin_date": begin_date,
            "end_date": end_date,
            "total_price": total_price,
            "font_path": project.settings.local.FontPath,
        }, context_instance=RequestContext(request)
    )

    import cStringIO as StringIO
    out_stream = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), out_stream, encoding="UTF-8")
    data = out_stream.getvalue()
    #f = open("/tmp/bla.pdf", "wb")
    #f.write(data)
    #f.close()

    if pdf is not None:
        response = HttpResponse(data, mimetype="application/pdf")
        response["Content-Disposition"] = "attachment; filename=report_%s.pdf" % (begin_date.strftime("%Y-%m-%d"))
        return response
    else:
        return HttpResponse("")


#--------------------------------------------------------------------------------------------------


def download_monthly_report(request, year, month):
    from django.db.models import Q, Sum
    from calendar import monthrange
    from project.util import str_to_int
    import project.settings

    year = str_to_int(year)
    month = str_to_int(month)

    q = Q(storniran=False) & \
        Q(stornira_racun=None) & \
        Q(created__month=month) & \
        Q(created__year=year)

    days = []

    sum_total = 0.0
    for day in range(1, monthrange(year, month)[1] + 1):
        date_start = datetime.date(year, month, day)
        date_end = date_start + datetime.timedelta(days=1)
        sum_day = NarudzbaRacunStavka.objects.filter(racun__in=NarudzbaRacun.objects.filter(q & Q(created__gte=date_start, created__lt=date_end))).aggregate(sum=Sum("iznos"))["sum"]
        if sum_day is None:
            sum_day = 0.0
        sum_total += float(sum_day)
        days.append([date_start, sum_day])
        print date_start, sum_day

    html = render_to_string("order/narudzbaracun_monthly_report.html",
        {
            "year": year,
            "month": month,
            "days": days,
            "sum_total": sum_total,
            "font_path": project.settings.local.FontPath,
        }, context_instance=RequestContext(request)
    )

    import cStringIO as StringIO
    out_stream = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), out_stream, encoding="UTF-8")
    data = out_stream.getvalue()
    #f = open("/tmp/bla.pdf", "wb")
    #f.write(data)
    #f.close()

    if pdf is not None:
        response = HttpResponse(data, mimetype="application/pdf")
        response["Content-Disposition"] = "attachment; filename=report_%04d_%02d.pdf" % (year, month)
        return response
    else:
        return HttpResponse("")


#--------------------------------------------------------------------------------------------------
