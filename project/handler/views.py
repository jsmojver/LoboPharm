# Create your views here.
# coding=utf-8

from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import simplejson, datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail

from depo.models import Lijek, Zahtjev
from depo.forms import *

from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, inlineformset_factory

from order.models import TecajnaLista, Tecaj, Valuta
from fiskalizacija.models import RadnoMjesto

from sysapp.models import InstantMsg, ObavijestiPost

import random

def home(request):
  return render_to_response('main.tpl')

def test(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      #todo-sanitize
      if len(value)>2:
        model_results = Lijek.objects.filter(naziv__istartswith=value)
        results = [ {'id': x.id, 'label': x.naziv, 'value': x.naziv } for x in model_results ]

  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


 
def logout_view(request):
  logout(request)
  return redirect('/accounts/login')

@login_required(login_url='/accounts/login/')
def main(request):
  from random import randint 
  try: lista = TecajnaLista.objects.latest('date')
  except: lista=''
  request.user.kosarica.ip_adresa = request.META['REMOTE_ADDR']
  try: 
    request.user.userprofile.ip = request.META['REMOTE_ADDR']
    request.user.userprofile.oznaka_naplatnog_uredjaja = RadnoMjesto.objects.get(ip=request.META['REMOTE_ADDR']).oznaka
    request.user.userprofile.save()
    InstantMsg.objects.filter(recipient=request.user).update(fetched=True)
  except: pass

  request.user.kosarica.save()

  if ObavijestiPost.objects.filter(created__gte=(datetime.date.today()-datetime.timedelta(days=1))).count():
    nove_obavijesti = True
  else:
    nove_obavijesti = False

  if request.META['REMOTE_ADDR'] == '10.41.1.1':
    return HttpResponseRedirect(reverse('light.order.incoming.view'))
  else:
    return render_to_response('index.html', {'ip_adresa': request.META['REMOTE_ADDR'], 'tecajna_lista': lista, 'randint': randint(100000,999999), 'nove_obavijesti': nove_obavijesti}, context_instance = RequestContext(request))

################################################### IZDAVANJE #################################################################

####### AJAX vezano uz polling, dodavanje redova u DOM i promjenu statusa zahtjeva javascriptom
  
def ajax_izdavanje_polling(request):
  """Vraca javascript za polling rutinu - """
  try: 
    zahtjev = Zahtjev.objects.filter(created__startswith=datetime.date.today(), fetched=False).latest('id') # Dohvati današnje zahtjeve koji još nisu preuzeti, TODO: tu provjeriti jel ih dohvatio user koji ih je uputio!!!
    zahtjev.fetched=True
    zahtjev.save()
    if zahtjev.narudzba:
      response = 'sticky_notify_order(1, "%s %s", "%s");' % (zahtjev.narudzba.klijent.prezime, zahtjev.narudzba.klijent.ime, request.user.get_full_name())
    else:
      response = 'sticky_notify_order(1, "%s", "x%s, %s");' % (zahtjev.lijek.naziv, zahtjev.kolicina, request.user.get_full_name())
    return HttpResponse(response)
  except:
    return HttpResponse('')


## Ovo prepisati, treba ići tako da ima url /ajax/preuzmi/ID koji radi sve provjere i izvrši radnju! Ovo je security hazard i pizdarija
def ajax_azuriraj_zahtjev(request, broj, status):
  try: zahtjev = Zahtjev.objects.get(id=broj)
  except: return

  # TODO: Dopusti samo povećavanje za 1, da se ne može vraćat u nepreuzeto itd..., TODO: provjera ovlasti, provjera svega živog i neživog po pitanju securitya
  zahtjev.status = status
  zahtjev.save()

  return HttpResponse(simplejson.dumps({'status': 1}), mimetype='application/json')

def ajax_izdavanje_lijeka(request): 
  """ Handla submitanje forme za izdavanje lijeka koju je poslao djelatnik prodaje """
  results = []
  if request.method == 'POST':
    form = ZahtjevForm(request.POST)
    if form.is_valid():
      lijek = form.cleaned_data['lijekId']
      kolicina = form.cleaned_data['kolicina']
      opaska = form.cleaned_data['opaska']
      user = request.user.id
      
      zahtjev = Zahtjev(lijek=Lijek.objects.get(id=lijek), status=0, kolicina=kolicina, user=User.objects.get(id=user), fetched=0, zabiljezba=opaska)
      zahtjev.save()      

      results = [{'status': 1}]      

    else:
      results = [{'status': 0}]

  return HttpResponse(simplejson.dumps(results), mimetype='application/json')

  
###############################################################################################################################
#  Objedini funkcije da npr u jsonu vraca kao jedno polje i html redak koji ce se dodavati, ili da javascript to obavi instead!
#  Stavi da se nakon prvog json vracenog zahtjeva za polling postavi flag "preuzet" u model i preskače ubuduće, da se to ne mora raditi posebnom funkcijom u callbacku

def ajax_izdavanje_prikaz(request):
  zahtjevi = Zahtjev.objects.filter(created__startswith=datetime.date.today()).order_by('-created') # tu mora ici filter za danasnji datum
  # paginator = Paginator(zahtjevi, 30) # Dodati paginator i parametar page ovoj funkciji da se mogu listati narudžbe ako ih je više od 30
  return render_to_response('ajax/izdavanje_prikaz.html', {'zahtjevi': zahtjevi})


def dodavanje_kosarica(request, posiljka):
  p = get_object_or_404(Posiljka, pk=posiljka)
  if request.method == 'POST':
    form = PosiljkaLijekForm(request.POST)
    if form.is_valid():
      pl = PosiljkaLijek()
      pl.lijek_id = form.cleaned_data['lijek'].id
      pl.posiljka_id = form.cleaned_data['posiljka'].id
      pl.kolicina = form.cleaned_data['kolicina']
      pl.save()
      return HttpResponse('OK')
    else:
      return HttpResponse('%s' % form.errors)
  else:
    return render_to_response('depo/posiljka_detail.html', {'posiljka': p}, context_instance=RequestContext(request))

def brisanje_kosarica(request, posiljka, lijek):
  p = get_object_or_404(Posiljka, pk=posiljka)
  l = p.lijekovi.filter(lijek=lijek)
  for i in l:
    i.delete()
  return HttpResponse('OK')

def azuriranje_kolicina_kosarica(request, lijek_id, kolicina):
  l = get_object_or_404(PosiljkaLijek, pk=lijek_id)
  if kolicina >= 0:
    l.kolicina = kolicina
    l.save()
  return HttpResponse('OK')

def ajax_dodavanje_paketa_test(request):
  PosiljkaFormSet = inlineformset_factory(Posiljka, PosiljkaLijek, extra=30)
  posiljka = Posiljka.objects.get(id=1)
  formset = PosiljkaFormSet(instance=posiljka)

  if request.method == 'POST':
    formset = PosiljkaFormSet(request.POST, request.FILES, instance=posiljka)
    if formset.is_valid():
      formset.save()
      return HttpResponse('Valiiiiiiiiiiiiid')
      # do something.
    else:
      return HttpResponse('jebiga, nije dobro')
  else:    
    return render_to_response('ajax/dodaj_paket.html', {'formset': formset, 'lijekovi': range(30), 'posiljka': posiljka, 'form': PosiljkaLijekForm()}, context_instance=RequestContext(request))

  
