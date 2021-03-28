# coding=utf-8



from depo.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.db.models import Sum, Count, Avg

from django.views.generic import CreateView, ListView

from order.models import *

class DepoListView(ListView):  
  def get_queryset(self):
    sortfield=self.kwargs['sortfield']
    order = self.kwargs['order']
    if 'desc' in order: sortfield = '-%s' % sortfield
    return Lijek.objects.select_related().all().order_by(sortfield)    
    
    
  def get_context_data(self, **kwargs):
    
    context = super(DepoListView, self).get_context_data(**kwargs)
    
    context['sortfield'] = self.kwargs['sortfield']
    context['order'] = self.kwargs['order']
    context['toggleorder'] = 'asc' if 'desc' in context['order'] else 'desc'
    return context

class DepoKutijeListView(ListView): 
    def get_queryset(self):
        return PosiljkaLijekKutija.objects.filter(lijek__id=self.kwargs['pk'])

class DepoKutijeEventsListView(ListView): 
    def get_queryset(self):
        return LijekKutijaEvents.objects.filter(kutija__id=self.kwargs['pk'])

class DepoZahtjevCreateView(CreateView):
  form_class = ZahtjevForm
  template_name="depo/zahtjev_izdavanje.html"
  model = Zahtjev
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    try: KosaricaArtikal.objects.create(kosarica_id=self.request.user.kosarica.id, kolicina=form.instance.kolicina, naziv=form.instance.lijek.naziv, cijena=form.instance.lijek.cijena, trziste=Trziste.objects.get(naziv='Depo'), shipping=Lijek.objects.get(id=form.instance.lijek.id).depo.transport, valuta=Valuta.objects.get(kratica='HRK').id) 
    except: pass



    return HttpResponseRedirect(reverse('order.kosarica.view'))

class DepoStavkeListView(ListView):
  
  def get_queryset(self):
    return Zahtjev.objects.filter(user=self.request.user)

class DepoStanjeListView(ListView):
  
  template_name="depo/stanje_kutija_list.html"
  def get_queryset(self):
    return PosiljkaLijekKutija.objects.filter(depo_lijek=self.kwargs['pk'], status__in=[0,1,2,3]).order_by('status', 'modified')

class DepoInventuraKutijaListView(ListView):
  template_name="depo/inventura_detail.html"
  def get_queryset(self):
    return InventuraKutija.objects.filter(inventura=self.kwargs['pk']).order_by('-nedostaje', '-modified')



def posiljka_lijek_add(request):
  try: posiljka = Posiljka.objects.filter(locked=0).latest('id')
  except: 
    posiljka = Posiljka(zaduzio=request.user)
    posiljka.save()
  if request.method == 'POST':
    form = PosiljkaLijekForm(request.POST)
    if form.is_valid():
      form.save()
      

      
      
      
      
  return render(request, 'depo/posiljka_lijek_add.html', {'posiljka': posiljka})

def posiljka_lijek_delete(request, lijek):
  lijek = get_object_or_404(PosiljkaLijek, pk=lijek)
  posiljka = lijek.posiljka
  if posiljka.locked == 1: return  
  lijek.delete()      
  return render(request, 'depo/posiljka_lijek_add.html', {'posiljka': posiljka})

def posiljka_zakljucaj(request):
  try: posiljka = Posiljka.objects.filter(locked=0).latest('id')
  except: return HttpResponse('Nema takve pošiljke!')
  
  if posiljka.lijekovi.count(): 
    posiljka.locked = 1

    
      
    for i in posiljka.lijekovi.all(): 
      i.lijek.stanje = i.lijek.stanje + i.kolicina
      i.lijek.save()

    posiljka.save()    
    return HttpResponseRedirect(reverse('depo.posiljka.detail', args=[posiljka.id]))
  else:
    return render(request, 'depo/posiljka_lijek_add.html', {'posiljka': posiljka})


def zahtjev_status_ukloni(request, zahtjev_id, status):
  try: Zahtjev.objects.filter(id=zahtjev_id).update(status=status)
  except: return HttpResponse('')
  return HttpResponseRedirect(reverse('depo.stavke.nerijesene'))
  
def kosarica_list(request): 
  from order.templatetags.mytagslib import eur2hrk  
  
  
    
  
  kosarica = Lijek.objects.filter(kutije_depo_lijekova__user=3, kutije_depo_lijekova__status=2).annotate(broj_kutija=Count('kutije_depo_lijekova'))
  if not len(kosarica): return HttpResponseRedirect(reverse('depo.zahtjev.izdavanje')) 

  ukupno = sum([i.broj_kutija*i.cijena for i in kosarica])
  ukupno_hrk= eur2hrk(sum([i.broj_kutija*i.cijena for i in kosarica]))
  
  for i in kosarica:    
    i.user = request.user.get_full_name()    
    i.ukupno = i.broj_kutija * i.cijena
    i.ukupno_hrk = eur2hrk(i.ukupno)
                                          
  return render(request, 'depo/kosarica_list.html', {'object_list': kosarica, 'ukupno': ukupno, 'ukupno_hrk': ukupno_hrk})

def kosarica_lock(request):
  PosiljkaLijekKutija.objects.filter(user=request.user, status=2).update(status=4, locked=1) 
  return HttpResponseRedirect(reverse('depo.zahtjev.izdavanje'))
  

def obracun_dnevni(request):
  from datetime import datetime
  from order.templatetags.mytagslib import eur2hrk  

  now = datetime.now()
  midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
  
  korisnici = User.objects.all()
  for i in korisnici:
    i.broj_kutija = PosiljkaLijekKutija.objects.filter(user=i, status=4, locked=1, modified__gte=midnight).count()
    i.inkasirano = PosiljkaLijekKutija.objects.filter(user=i, status=4, locked=1, modified__gte=midnight).aggregate(Sum('cijena'))
    try: i.inkasirano_hrk = eur2hrk(i.inkasirano['cijena__sum'])
    except: i.inkasirano_hrk = 0

  return render(request, 'depo/obracun_dnevni.html', {'korisnici': korisnici})    
 
def generiraj_epl2_za_30x18(request, barkod, ime_lijeka):
  
  
  ime_lijeka = ime_lijeka[:23].decode('utf-8').encode('cp852') 
  str = ''
  commands = ['N', 
     'q240',
     'Q144,22,-40', 
     'A8,5,0,1,1,1,R,"%s"' % '{:^22}'.format(ime_lijeka), 
      'B12,30,0,E30,2,2,70,B,"%s"' % barkod,
      'I8,2,001',
      
     'P1,1',]
  for i in commands:
    str += '%s\n' % i
  return HttpResponse(str)

def debug_ispis_naljepnica(request, posiljkalijek_id): 
  import simplejson as json
  pl = PosiljkaLijekKutija.objects.filter(lijek=posiljkalijek_id, printed=0) 
  return HttpResponse(json.dumps(dict([(i.id, '{:^22}'.format(i.lijek.lijek.naziv)) for i in pl])))   

def naljepnica_je_ispisana(request, posiljkalijekkutija):
  plk = get_object_or_404(PosiljkaLijekKutija, pk=posiljkalijekkutija)
  plk.printed = 1
  plk.save()
  return HttpResponse('OK')

def sve_naljepnice_su_ispisane(request, posiljkalijek):
  plk = get_object_or_404(PosiljkaLijek, pk=posiljkalijek)
  for i in plk.kutije_depo_lijekova.all():
    i.printed = 1
    i.save()
  return HttpResponse('OK')




def inventura_skeniraj(request, barcode):
  from django.db import IntegrityError
 
  try: kutija = PosiljkaLijekKutija.objects.get(id=barcode, status=0, inventura=0)
  except: return HttpResponse(u'info_notify("Greška", "Kutija se ne vodi na skladištu ili je već unesena!");')
  
  kutija.inventura = 1
  try: inv = Inventura.objects.get(status=0) 
  except: 
    inv = Inventura(user=request.user) 
    inv.save()
  
  try: InventuraKutija(inventura=inv, kutija=kutija, status=kutija.status).save()
  except IntegrityError:
    return HttpResponse(u'info_notify("Greška", "Kutija već unesena!");')  
  kutija.save()
  
  
  return HttpResponse(u"info_notify('%s', '%s <br />Skeniran u inventuri'); load_and_focus_tab('%s', 1);" % (kutija.lijek.lijek.naziv, kutija.id, reverse('depo.inventura.skenirano'))) 

def inventura_zatvori(request):
  try:
    inv = Inventura.objects.get(status=0) 
    for i in PosiljkaLijekKutija.objects.filter(status=0, inventura=0): 
      InventuraKutija(inventura=inv, kutija=i, status=i.status, nedostaje=1).save()    
    inv.status=1
    inv.save()
    return HttpResponse(u"info_notify('Inventura %s', 'Uspješno zatvorena'); load_and_focus_tab('%s', 1);" % (inv.id, reverse('depo.inventura.skenirano')))
  except: return HttpResponse(u'')      

def barcode_kutija(request, barcode): 
    
  kutija = get_object_or_404(PosiljkaLijekKutija, pk=barcode)  
  lijek = kutija.lijek.lijek
  
  
  
  
  
  
  if Zahtjev.objects.filter(lijek=lijek, status__in=[0, 1]).count(): postoji_zahtjev=1
  else: postoji_zahtjev=0
  
  
  if kutija.status == 0 and postoji_zahtjev: 
    try: 
      zahtjev = Zahtjev.objects.filter(lijek=lijek, status__in=[0, 1]).order_by('created')[0] 
      if zahtjev.kolicina > 1: 
        zahtjev.kolicina -= 1
        zahtjev.status = 1 
      else:
        zahtjev.status = 2 
      zahtjev.save()
      kutija.status = 1 
      kutija.user = request.user
      kutija.save()
      LijekKutijaEvents(kutija=kutija, user=request.user, vanredni = 0, vrsta = 1).save() 
      return HttpResponse(u"info_notify('%s', '%s <br />Izdan sa skladišta'); load_and_focus_tab('%s', 1);" % (lijek.naziv, kutija.id, reverse('depo.stavke.nerijesene')))
    except: pass

  
  elif kutija.status == 1: 
    try: 
      kutija.status = 2 
      kutija.user = request.user
      kutija.save()
      LijekKutijaEvents(kutija=kutija, user=request.user, vanredni = 0, vrsta = 2).save() 
      return HttpResponse(u'info_notify("%s", "%s <br />Preuzet u prodaji"); load_and_focus_tab("%s", 1);' % (lijek.naziv, kutija.id, reverse('depo.kosarica.list')))
    except: pass     

  
  elif kutija.status in [2, 4]: 
    try: 
      
      kutija.status = 3 
      kutija.user = request.user
      kutija.save()
      LijekKutijaEvents(kutija=kutija, user=request.user, vanredni = 1, vrsta = 3).save() 
      return HttpResponse(u'info_notify("%s", "%s <br />Povrat na skladište"); load_and_focus_tab("%s", 1);' % (lijek.naziv, kutija.id, reverse('depo.kosarica.list')))
    except: pass     

  
  elif kutija.status == 3: 
    try: 
      
      kutija.status = 0 
      kutija.user = request.user
      kutija.save()
      LijekKutijaEvents(kutija=kutija, user=request.user, vanredni = 1, vrsta = 0).save() 
      return HttpResponse(u'info_notify("%s", "%s <br />Povrat - preuzet na skladištu");' % (lijek.naziv, kutija.id))
    except: pass     
    
  
  try: return HttpResponse("load_and_focus_tab('%s', 1);" % reverse('depo.posiljka.kutija.events', args=[kutija.id]))
  except: return HttpResponse('')



def debug_ispis_kodiranih_naljepnica(request, posiljkalijek_id): 
  pl = PosiljkaLijek.objects.select_related('depo_kutije_lijekova').get(id=posiljkalijek_id)  
  escpos = "".join(['\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x0211%s\x00\x0a\n' % i for i in pl.kutije_depo_lijekova.values_list('id', flat=True)])
  escpos = '\x1b\x40\x1b\x61\x01\x1b\x61\x01\x1b\x61\x01%s\x1b\x61\x01\n\n%s\n\n\n\x1d\x56\x00' % (pl.lijek.naziv, escpos) 
  return HttpResponse(escpos.encode('hex'))     


def ticks((x,y)):
  return (int(x.strftime("%s")) * 1000, y)

def graph_lijek_alltime(request, pk):
  promet=[]
  
  for i in PosiljkaLijek.objects.filter(lijek__id=pk): 
    promet.append((i.posiljka.datum, i.kolicina))
   
  for i in Stavka.objects.filter(artikal__id=pk):
    promet.append((i.created, -i.kolicina)) 
    
  datumi = promet  
  datumi.sort()
  
  promet = map(ticks, promet)
  promet.sort()
  
  plotpoints=[]
  cumulative = 0
  
  for i in promet:                    
    plotpoints.append((i[0], cumulative))
    cumulative += i[1]
    
  
  objekt = Lijek.objects.get(id=pk)
  
  offset = objekt.stanje - cumulative
  
  plotpoints_offset = []
  for i in plotpoints:
    plotpoints_offset.append((i[0], i[1]+offset))
      
  return render(request, 'depo/lijek_graph.html', {'objekt': objekt, 'plotpoints': plotpoints_offset, 'datumi': datumi})
  
def racunaj_ukupni_ulaz(request):
  from django.db.models import Sum, Max, Min
  import datetime
  from decimal import Decimal
  
  test=[]
  for i in Lijek.objects.all():
    suma = i.depo_posiljka_lijekovi.all().aggregate(Sum('kolicina'))['kolicina__sum']
    if suma:
      i.ukupni_ulaz = suma
    else: i.ukupni_ulaz = 0
    
    test.append(suma)
    
    try: 
      i.ukupna_zarada = i.ukupni_ulaz * i.cijena
    except: i.ukupna_zarada = 0
    
    mindate = PosiljkaLijek.objects.filter(lijek__id=i.id).aggregate(Min('posiljka__datum'))['posiljka__datum__min']
    try: dana = float((datetime.datetime.now() - mindate).days)
    except: dana = 1
    i.broj_dana = dana
    
    try: i.mjesecna_potrosnja = 30 * i.ukupni_ulaz / dana
    except: i.mjesecna_potrosnja = 0
    i.mjesecna_zarada = Decimal(i.mjesecna_potrosnja) * i.cijena
    
    i.min_stanje = i.preporucena_zaliha()
    
    i.save()
    
    
  return HttpResponse('OK')
  

