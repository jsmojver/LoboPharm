#coding:utf-8

from fiskalizacija.flib import *
from fiskalizacija.models import *

from django.shortcuts import render_to_response, render, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.conf import settings
from django.views.generic import ListView
from django.db.models import Count, Min, Sum, Max, Avg

from django.contrib.auth.models import User

from reportlab.pdfgen import *
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

import time

class FiskalizacijaObracunView(ListView):
  template_name = 'fiskalizacija/obracun.html'
  model = User

  def post(self, request, *args, **kwargs):
    return super(FiskalizacijaObracunView, self).get(request, *args, **kwargs)
  
  def get_queryset(self):
    t=time.localtime()

    try: 
      self.godina = self.request.POST['godina']
      assert(self.godina.isdigit())
    except: self.godina = t.tm_year 
    try: 
      self.mjesec = self.request.POST['mjesec']
      assert(self.mjesec.isdigit())
    except: self.mjesec = t.tm_mon
    try: 
      self.dan = self.request.POST['dan']
      assert(self.dan.isdigit())
    except: self.dan = t.tm_mday
 
    object_list = self.model.objects.filter(racuni__created__year=self.godina, racuni__created__month=self.mjesec, racuni__created__day=self.dan, racuni__storno=0, racuni__stornira_racun__isnull=True).annotate(broj=Count('racuni'),iznos=Sum('racuni__iznos'))
        
    return object_list 

  def get_context_data(self, **kwargs):
    context = super(FiskalizacijaObracunView, self).get_context_data(**kwargs)
    t = time.localtime()
    context['dan'] = self.dan 
    context['mjesec'] = self.mjesec 
    context['godina'] = self.godina
    return context

def pp_submit(request, ppreqid):
  try: pp = PoslovniProstorPoruka.objects.get(id=ppreqid)
  except: return HttpResponse('javascript:info_warning("Greška", "Artikal nije pronađen!");')    

  pp.fiskaliziraj()
  #try:
  odg = pp.posalji()
  odg = pp.fiskalizacija.odgovor
  pp.http_status = odg[0]
  pp.poruka_odgovor = odg[1]
  pp.save()
  #except:
  #  pass

  return HttpResponseRedirect(reverse('fiskalizacija.pp.view', args=[pp.id]))

def dostavi_naknadno_racun(request, racun_id):
  try: r = Racun.objects.get(id=racun_id)
  except: return HttpResponse('info_warning("Greška", "Račun ne postoji!");')    

  if r.jir: return HttpResponse('info_warning("Greška", "Račun je već fiskaliziran!");')
  greska = ''
  start_time = time.time()

  if r.zastitni_kod and not r.jir:
    r.naknadno_dostavljen = True
    try:
      r.posalji()
    except Exception, e:
      greska = e
      exec_time = time.time() - start_time
      RacunLog(racun=r, tip=3, poruka_zahtjev=e, trajanje=exec_time).save()
      return HttpResponse('{"racun_id": "%s", "exec_time": "%s", "greska": "%s", "status": "failed"}' % (r.id, exec_time, greska))

  exec_time = time.time() - start_time
  if r.jir: return HttpResponse('{"racun_id": "%s", "exec_time": "%s", "greska": "%s", "status": "success", "jir": "%s"}' % (r.id, exec_time, greska, r.jir))
  else:  return HttpResponse('{"racun_id": "%s", "status": "unknown"}' % (r.id))

def izdaj_nevezan_racun(request):
  r = Racun(djelatnik=request.user, iznos=Decimal(settings.USLUGA_POSREDOVANJA), oib_obveznika=settings.OIB_OBVEZNIKA, oznaka_poslovnog_prostora=settings.POSLOVNI_PROSTOR, naplatni_uredjaj=request.user.userprofile.oznaka_naplatnog_uredjaja, nacin_placanja='G')

  if not r.stavke.count(): # Ovog u biti ne bi trebalo, TODO pogledaj zašto
    RacunStavka(cijena=settings.USLUGA_POSREDOVANJA, iznos=settings.USLUGA_POSREDOVANJA, kolicina=1, naziv='Usluge posredovanja', racun=r).save()  

  porezna_osnovica=r.iznos * Decimal('100.00') / (Decimal(settings.STOPA_PDV) + Decimal('100.00'))
  iznos_poreza = r.iznos-porezna_osnovica
  if not r.porezi.count():
    RacunPorez(racun=r, stopa=Decimal(settings.STOPA_PDV), iznos=iznos_poreza, osnovica=porezna_osnovica).save()

  greska = ''
  start_time = time.time()
  try:
    r.posalji()
  except Exception, e:
    greska = e
    RacunLog(racun=r, tip=3, poruka_zahtjev=e).save()
  exec_time = time.time() - start_time

  return HttpResponse('{"racun_id": "%s", "exec_time": "%s", "greska": "%s"}' % (r.id, exec_time, greska))
  # return HttpResponseRedirect(reverse('order.fiskaliziraj.racun_detalji', args=[r.id]))

def reportpdf(request):
    import project.settings
    query = Racun.objects.all()

    registerFont(TTFont('FreeSans', "%s/templates/rml/FreeSans.ttf" % (project.settings.local.ProjectPath)))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="popis-racuna.pdf"'

    elements = []

    doc = SimpleDocTemplate(response, rightMargin=0, leftMargin=6.5 , topMargin=0.3 , bottomMargin=0)
  
    data=[('Broj', 'Datum i vrijeme', 'Djelatnik', 'JIR', 'Zaštitni kod', 'Iznos', 'Naknadno')]
    suma = 0
    for i in query:
      data.append((i.oznaka_racuna(), i.datum_vrijeme_zastitni, i.djelatnik.get_full_name(), i.jir, i.zastitni_kod, i.iznos, i.naknadno_dostavljen))
      try: suma = suma + int(i.iznos)
      except: pass

    data.append(('', '', 'Ukupno: %s' % query.count(), '', '', suma, query.filter(naknadno_dostavljen=True).count()))

    table = Table(data)
    table.setStyle(TableStyle([
    ('FONT', (0, 0), (-1, -1), 'FreeSans'),
#    ('FONT', (0, 0), (-1, 0), 'FreeSans'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))
    elements.append(table)

    ####### Sveukupno #########

    doc.build(elements) 
    
    return response

def zki_kalkulator(request):
    """ Izračunaj proizvoljan zki ako netko zatraži """
    oib = settings.OIB_OBVEZNIKA 
    
    if request.method == 'POST':
      datumvrijeme = request.POST['datumvrijeme']
      broj = request.POST['broj']
      prostor = request.POST['prostor']
      uredjaj = request.POST['uredjaj']
      iznos = request.POST['iznos']

      zki = zkicalc([oib, datumvrijeme, broj, prostor, uredjaj, iznos])
 
 
      return render(request, 'fiskalizacija/zki_kalkulator.html', {'zki': zki, 'oib': oib, 'datumvrijeme': datumvrijeme, 'broj': broj, 'prostor': prostor, 'uredjaj': uredjaj, 'iznos': iznos})
                
    return render(request, 'fiskalizacija/zki_kalkulator.html', {'oib': oib})


def provjera_racuna(request):
    """ Provjerava sljednost računa - uspoređuje broj računa u bazi i aritmetičku razliku serijskih brojeva, vraća info box javascriptom 
        Provjerava postoje li nefiskalizirani računi
    """
    response = ''

    najnoviji = Racun.objects.filter()[:1].get()
    najstariji = Racun.objects.order_by('id')[0]

    delta = najnoviji.id - najstariji.id + 1
    ukupno = Racun.objects.all().count()
    if delta == ukupno: response += 'info_notify("OK", "Sljednost računa u skladu s brojčanim stanjem");'
    else: response += 'info_warning("Upozorenje", "Zovite upomoć, negdje nešto fali!");'

    if not Racun.objects.filter(jir__isnull=True).count(): response += 'info_notify("OK", "Svi računi ovjereni su JIR brojem");'
    else: response += 'info_warning("Upozorenje", "Svi računi nisu dostavljeni u PU");'

    return HttpResponse(response) 
     
