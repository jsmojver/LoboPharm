from django.views.generic import ListView, DetailView, TemplateView
from django.conf.urls.defaults import patterns, include, url

from meds.models import *
from order.models import *
from meds.views import * 
 
urlpatterns = patterns('meds.views',
    url(r'^autocomplete$', 'ajax_autocomplete_ime', name='ajax_autocomplete_ime'),
    url(r'^autocomplete/stoffname$', 'ajax_autocomplete_stoffname', name='ajax_autocomplete_stoffname'),
    url(r'^autocomplete/hersteller$', 'ajax_autocomplete_hersteller', name='ajax_autocomplete_hersteller'),
    url(r'^autocomplete/atc$', 'ajax_autocomplete_atc', name='ajax_autocomplete_atc'),
    url(r'^autocomplete/drugatrzista$', 'ajax_autocomplete_drugatrzista', name='ajax_autocomplete_drugatrzista'),

    url(r'^autocomplete/abda$', 'ajax_autocomplete_abda', name='ajax_autocomplete_abda'),
    url(r'^autocomplete/sastojak$', 'ajax_autocomplete_sastojak', name='ajax_autocomplete_sastojak'),
   
    url(r'^search/drugotrziste/submit$', 'ArtikalDrugoTrzisteSearch', name='meds.search.drugotrziste.submit'), 
    url(r'^search/drugotrziste/form$', TemplateView.as_view(template_name="meds/artikal_drugo_trziste_searchform.html"), name='meds.search.drugotrziste.form'),
    url(r'^search/drugotrziste/query/(?P<query>[\w\ ]+)$', ArtikalDrugoTrzisteListView.as_view(model=ArtikalDrugoTrziste, paginate_by=25, template_name="meds/artikal_drugo_trziste_results.html"), name='meds.search.drugotrziste.query'), 
    
    url(r'^search/(?P<query>.*)/(?P<order>\w+)/(?P<sortfield>\w+)$', SearchMedsListView.as_view(model=Artikal, paginate_by=25), name='meds.search.q'), 
    url(r'^search/begins/(?P<upit>.*)/$', 'search', {'tip': 1}),
    url(r'^search/similar/(?P<upit>\d+)/$', 'search', {'tip': 2}),

    url(r'^search/alternative/(?P<upit>\d+)/$', 'search', {'tip': 3}),

    url(r'^order/search$', 'view_order'),

    url(r'^alternative/(?P<upit>\w+)/$', 'alternative', name='meds.alternative'),
    url(r'^similar/(?P<upit>\w+)/$', 'similar', name='meds.similar'),
    url(r'^search/submit$', 'searchMeds', name='searchMeds'),

    url(r'^search$', TemplateView.as_view(template_name="meds/meds_search_form.html"), name='meds.search.form'),
    url(r'^search/advanced$', 'NaprednoPretrazivanje', name='meds.search.advanced'),

    url(r'^view/(?P<pk>\d+)$', DetailView.as_view(model=Artikal), name='meds.view'),
    url(r'^view/pzn/(\d+)$', 'meds_pzn_view', name='meds.pzn.view'),
    
    url(r'^view/sastav/(?P<pk>\d+)$', DetailView.as_view(model=Artikal, template_name="meds/meds_view_sastav.html"), name='meds.view.sastav'),
    url(r'^view/interakcije/(\d+)$', 'interakcije', name='meds.view.interakcije'),
    url(r'^view/upute/(?P<pk>\d+)$', DetailView.as_view(model=Artikal, template_name="meds/meds_view_upute.html"), name='meds.view.upute'),
    
    url(r'^interaction/detail/(?P<pk>\d+)$', DetailView.as_view(model=Interaktion), name='meds.interaction.detail'),


    

    url(r'^abda/search$', TemplateView.as_view(template_name="meds/abda_search_form.html"), name='meds.abda.search.form'),
    url(r'^abda/search/submit$', 'searchAbdaMeds', name='searchAbdaMeds'),
    url(r'^abda/search/(?P<query>.*)$', SearchAbdaMedsListView.as_view(model=Fertigarzneimittel, paginate_by=20, template_name="meds/abda_search_list.html"), name='meds.abda.search.q'), 

    url(r'^abda/sastojak/search$', TemplateView.as_view(template_name="meds/abda_stoff_search_form.html"), name='meds.abda.stoff.search.form'),
    url(r'^abda/sastojak/search/submit$', 'searchAbdaStoffMeds', name='searchAbdaStoffMeds'),
    url(r'^abda/sastojak/search/(?P<query>.*)$', SearchAbdaStoffMedsListView.as_view(model=SastavLijeka, paginate_by=20, template_name="meds/abda_stoff_search_list.html"), name='meds.abda.stoff.search.q'), 

)

