# coding:utf-8

from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from meds.models import Artikal, Stoff, Stoffname, Stoffinteraktion, ArtikalSearch, Dobavljac, SastavLijeka, Fertigarzneimittel, AtcCode
from order.models import ArtikalDrugoTrziste
import simplejson

from django.forms import ModelForm

from django.views.generic import ListView




def ArtikalDrugoTrzisteSearch(request): 
  if request.method == 'POST':
    q = request.POST['q']
    return HttpResponseRedirect(reverse('meds.search.drugotrziste.query', kwargs={'query': q}))

class ArtikalDrugoTrzisteListView(ListView):
  def get_queryset(self):
    query = self.kwargs['query']
    if query.isdigit():        
      return ArtikalDrugoTrziste.objects.filter(id=query)
    else:
      return ArtikalDrugoTrziste.objects.filter(ime__istartswith=query)

  
  def get_context_data(self, **kwargs):
    context = super(ArtikalDrugoTrzisteListView, self).get_context_data(**kwargs)
    context['query'] = self.kwargs['query']
    return context





def NaprednoPretrazivanje(request):
    if request.method == 'GET' and 'submitted' in request.GET: 
        form = ArtikalSearch(request.GET)

        if form.is_valid(): 
            from django.db.models import Q
            pzn = form.cleaned_data['pzn']
            djelatna_tvar_1 = form.cleaned_data['djelatna_tvar_1']
            djelatna_tvar_2 = form.cleaned_data['djelatna_tvar_2']
            djelatna_tvar_3 = form.cleaned_data['djelatna_tvar_3']
            dobavljac = form.cleaned_data['dobavljac']
            atc = form.cleaned_data['atc']
            ean = form.cleaned_data['ean']

            q = Q()
            if pzn:
              q &= Q(ZoNr=pzn)
            if atc:
              q &= Q(ATC=atc)
            if ean:
              q &= Q(ean__kod=ean)
            if dobavljac:
              q &= Q(dobavljac=dobavljac)

            model_results = Artikal.objects.filter(q)

            if djelatna_tvar_1:
                model_results = model_results.filter(abda_artikal__sastav__stoff=djelatna_tvar_1, abda_artikal__sastav__stofftyp=1)
            if djelatna_tvar_2:
                model_results = model_results.filter(abda_artikal__sastav__stoff=djelatna_tvar_2, abda_artikal__sastav__stofftyp=1)
            if djelatna_tvar_3:
                model_results = model_results.filter(abda_artikal__sastav__stoff=djelatna_tvar_3, abda_artikal__sastav__stofftyp=1)

            paginator = Paginator(model_results, 30)

            try: page = request.GET[u'page']
            except: page=1

            try:
              page_obj = paginator.page(page)
            except PageNotAnInteger:
              page_obj = paginator.page(1)        
            except EmptyPage:
              page_obj = paginator.page(paginator.num_pages)            
 
            url = reverse('meds.search.advanced') + '?submitted=1&dobavljac=%s&djelatna_tvar_1=%s&djelatna_tvar_2=%s&djelatna_tvar_3=%s&pzn=%s&atc=%s&ean=%s' % (dobavljac, djelatna_tvar_1, djelatna_tvar_2, djelatna_tvar_3, pzn, atc, ean)

            return render(request, 'meds/meds_search_advanced.html', {'stranica': page_obj, 'page_obj': page_obj, 'paginator': paginator, 'form': form, 'adresa': url})
     

    else:
        form = ArtikalSearch() 

    return render(request, 'meds/meds_search_advancedform.html', {
        'form': form,
    })




    
   
class SearchAbdaMedsListView(ListView):
  def get_queryset(self):
    query = self.kwargs['query']
    return Fertigarzneimittel.objects.filter(Q(suchbegriff__istartswith=query)).select_related('sastav', 'anbieter')

  def get_context_data(self, **kwargs):
    
    context = super(SearchAbdaMedsListView, self).get_context_data(**kwargs)
    context['query'] = self.kwargs['query']
    context['lastSearchUrl'] = self.request.get_full_path() 
    return context

def searchAbdaMeds(request):
  
  if request.method == 'POST':
    q = request.POST['q']
    return HttpResponseRedirect(reverse('meds.abda.search.q', kwargs={'query': q}))

def searchAbdaStoffMeds(request):
  
  if request.method == 'POST':
    q = request.POST['q']
    return HttpResponseRedirect(reverse('meds.abda.stoff.search.q', kwargs={'query': q}))

class SearchAbdaStoffMedsListView(ListView):
  def get_queryset(self):
    query = self.kwargs['query']
    return SastavLijeka.objects.filter(stoff=query).select_related('lijek', 'lijek__anbieter', 'stoff').order_by('lijek__suchbegriff')
  
  def get_context_data(self, **kwargs):
    
    context = super(SearchAbdaStoffMedsListView, self).get_context_data(**kwargs)
    context['query'] = self.kwargs['query']
    context['lastSearchUrl'] = self.request.get_full_path() 
    return context



class SearchMedsListView(ListView):
  def get_queryset(self):
    sortfield=self.kwargs['sortfield']
    order = self.kwargs['order']
    query = self.kwargs['query']
    if 'desc' in order: sortfield = '-%s' % sortfield
    return Artikal.objects.filter(Q(name__istartswith=query)|Q(slug__istartswith=query)).order_by(sortfield, 'dobavljac', 'Sortname2')

  def get_context_data(self, **kwargs):
    
    context = super(SearchMedsListView, self).get_context_data(**kwargs)
    
    context['sortfield'] = self.kwargs['sortfield']
    context['order'] = self.kwargs['order']
    context['query'] = self.kwargs['query']
    context['toggleorder'] = 'asc' if 'desc' in context['order'] else 'desc'
    context['lastSearchUrl'] = self.request.get_full_path() 
    return context

def searchMeds(request):
  
  if request.method == 'POST':
    q = request.POST['q']
    return HttpResponseRedirect(reverse('meds.search.q', kwargs={'query': q, 'order': 'asc', 'sortfield': 'Sortname1'}))
    
def alternative(request, upit):
  
  view = ListView.as_view(template_name = 'meds/artikal_alternative_list.html', paginate_by=25, queryset=Artikal.objects.filter(ATCCode=upit))
  return view(request)
  
def similar(request, upit):
  
  view = ListView.as_view(template_name = 'meds/artikal_similar_list.html', paginate_by=25, queryset=Artikal.objects.filter(ATCCode__istartswith=upit[:-2]))
  return view(request)

def interakcije(request, lijekId):
  
  try: lijek = Artikal.objects.get(id=lijekId)
  except: raise Http404

  lista_djelatnih_tvari = lijek.lista_djelatnih_tvari()
  interakcije = Stoffinteraktion.objects.filter(stoff__in=lista_djelatnih_tvari).order_by('interaktion__klinischebedeutung')

  return render(request, 'meds/meds_view_interakcije.html', {'artikal': lijek, 'interakcije': interakcije})
  

def ajax_autocomplete_ime(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:       
        model_results = Artikal.objects.filter(Q(name__istartswith=value)|Q(slug__istartswith=value)).values_list('name', flat=True)
        if model_results.count() > 500: results = []
        else: 
           model_results = dict.fromkeys(model_results).keys() 
           results = [ {'label': x, 'value': x } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def ajax_autocomplete_drugatrzista(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:       
        model_results = ArtikalDrugoTrziste.objects.filter(ime__istartswith=value).values_list('ime', 'id')
        if model_results.count() > 500: results = []
        else: 
           
           results = [ {'label': x[0], 'value': x[0], 'id': x[1] } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def ajax_autocomplete_stoffname(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:
        model_results = Stoffname.objects.filter(suchbegriff__istartswith=value, vorzugsbezeichnungfl=1).values_list('name', 'stoff_id')
        if model_results.count() > 500: results = []
        else: 
           model_results = dict.fromkeys(model_results).keys() 
           results = [ {'label': x[0], 'value': x[0], 'id': x[1] } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def ajax_autocomplete_sastojak(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:
        model_results = Stoffname.objects.filter(suchbegriff__istartswith=value, vorzugsbezeichnungfl=1).values_list('name', 'stoff_id')
        if model_results.count() > 500: results = []
        else: 
           model_results = dict.fromkeys(model_results).keys() 
           results = [ {'label': x[0], 'value': x[0], 'id': x[1] } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def ajax_autocomplete_abda(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:
        model_results = Fertigarzneimittel.objects.filter(suchbegriff__istartswith=value).values_list('produktname', 'id', 'suchbegriff')
        if model_results.count() > 500: results = []
        else: 
           model_results = dict.fromkeys(model_results).keys() 
           results = [ {'label': x[0], 'value': x[0], 'id': x[2] } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def ajax_autocomplete_hersteller(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:
        model_results = Dobavljac.objects.filter(naziv__istartswith=value).values_list('naziv', 'id')
        if model_results.count() > 500: results = []
        else: 
           model_results = dict.fromkeys(model_results).keys() 
           results = [ {'label': x[0], 'value': x[0], 'id': x[1] } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def ajax_autocomplete_atc(request): 
  results = []
  if request.method == 'GET':
    if request.GET.has_key(u'term'):
      value = request.GET[u'term']      
      if len(value)>2:
        model_results = AtcCode.objects.filter(sifra__istartswith=value).values_list('sifra', 'opis', 'id')
        if model_results.count() > 500: results = []
        else: 
           model_results = dict.fromkeys(model_results).keys() 
           results = [ {'label': '%s %s' % (x[0], x[1]), 'value': '%s %s' % (x[0], x[1]), 'id': x[2] } for x in model_results ]
 
  json = simplejson.dumps(results)
  return HttpResponse(json, mimetype='application/json')


def search(request, tip, upit):
  if request.method == 'GET':
    
    if tip == 1:  
      model_results = Artikal.objects.filter(name__istartswith=upit)
      if model_results.count() > 500:
        return HttpResponse('Previše rezultata, molimo suzite pretragu!')

    
    elif tip == 2:
      try: a = Artikal.objects.get(id=upit)
      except: raise Http404
      try: model_results = Artikal.objects.filter(ATCCode__istartswith=a.ATCCode[:-2])
      except: raise Http404
    
    
    elif tip == 3:
      try: a = Artikal.objects.get(id=upit)
      except: raise Http404
      try: model_results = Artikal.objects.filter(ATCCode=a.ATCCode)
      except: raise Http404
    
    
    elif tip == 4:
      try: a = Artikal.objects.get(id=upit)
      except: raise Http404
      try: model_results = Artikal.objects.filter(ATCCode=a.ATCCode)
      except: raise Http404
    
    else: raise Http404

    paginator = Paginator(model_results, 30) 

    try: page = request.GET[u'page']
    except: page=1

    try:
      page_obj = paginator.page(page)
    except PageNotAnInteger:
      page_obj = paginator.page(1)        
    except EmptyPage:
      page_obj = paginator.page(paginator.num_pages)            

    return render(request, 'meds/meds_search.html', {'stranica': page_obj, 'paginator': paginator, 'lijek_id': upit})


def view_order(request):
  return render(request, 'meds/meds_view_order.html')

def meds_pzn_view(request, pzn):
  artikal = get_object_or_404(Artikal, ZoNr=pzn)
  return render(request, 'meds/artikal_detail.html', {'artikal': artikal}) 

