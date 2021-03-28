#coding=utf-8


from django.db.models import F, Q
from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from django.views.generic import ListView, DetailView, UpdateView, CreateView, TemplateView


from depo.models import *
from depo.views import *

from order.models import *
from order.views import *
from meds.views import *
from meds.models import *
from fiskalizacija.models import *
from fiskalizacija.views import *
from sysapp.models import *
from sysapp.views import *
from nabava.models import *
from nabava.views import *

from datetime import datetime, timedelta
import settings


from django.contrib import admin
admin.autodiscover()
 
mjesec_dana = datetime.today()-timedelta(days=3650) 

urlpatterns = patterns('',
    
    url(r'^$', 'handler.views.main'),
    url(r'^autocomplete$', 'handler.views.test'),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    (r'^administrator/', include("project.admin.urls")),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html', }), 


    url(r'^meds/', include('meds.urls')),

    url(r'^client/search$', 'order.views.trazi_korisnika'),
    url(r'^client/view/(?P<pk>\d+)/$', DetailView.as_view(model=Klijent), name="client.view"), 
    url(r'^client/edit/(?P<pk>\d+)/$', UpdateView.as_view(form_class=KlijentForm, model=Klijent, template_name = 'order/klijent_edit.html'), name="client.edit"), 
    url(r'^client/create/$', CreateView.as_view(form_class=KlijentForm, model=Klijent, template_name = 'order/klijent_add.html'), name="client.create"), 
    url(r'^client/browse$', ListView.as_view(model=Klijent, paginate_by=25, queryset=Klijent.objects.filter(tip_klijenta=1)), name="client.browse"),
    url(r'^client/select/(?P<pk>\d+)/$', 'order.views.odaberi_korisnika', name="client.select"),

    url(r'^order/company/view/(?P<pk>\d+)/$', DetailView.as_view(model=Klijent), name="order.tvrtka.view"), 
    url(r'^order/company/edit/(?P<pk>\d+)/$', UpdateView.as_view(form_class=TvrtkaForm, model=Klijent, template_name = 'order/klijent_edit.html'), name="order.tvrtka.edit"), 
    url(r'^order/company/create/$', CreateView.as_view(form_class=TvrtkaForm, model=Klijent, template_name = 'order/klijent_add.html'), name="order.tvrtka.create"), 
    url(r'^order/company/browse$', ListView.as_view(model=Klijent, paginate_by=25, queryset=Klijent.objects.filter(tip_klijenta=2)), name="order.tvrtka.browse"),

    url(r'^order/print/(\d+)$', 'sysapp.views.print_receipt'),
    url(r'^order/print2/(\d+)$', 'sysapp.views.print_receipt_2'),
    url(r'^order/print/racun/njemacki/(\d+)$', 'sysapp.views.print_racun_njemacki'),
    url(r'^order/print/racun/njemacki/broj/(\d+)$', 'sysapp.views.ispis_njemackog_racuna_broj'),
    url(r'^order/print/potvrda/njemacki/(\d+)$', 'sysapp.views.print_potvrda_njemacki'),
    url(r'^order/print/potvrda/o/uplati/njemacki/(\d+)$', 'sysapp.views.print_potvrda_o_uplati_njemacki'),
    url(r'^order/print/racun/za/pristigle/(\d+)$', 'sysapp.views.print_racun_za_pristigle'),
    url(r'^order/print/papiric/(\d+)$', 'sysapp.views.ispis_papirica_za_narudzbu'),

    url(r'^order/print/barcode/(\d+)$', 'sysapp.views.order_print_barcode', name='order.print.barcode'),
    url(r'^order/print/html/(\d+)/$', 'sysapp.views.print_receipt_html'),
    url(r'^order/print/html2/(?P<pk>\d+)/$', DetailView.as_view(model=Narudzba, template_name="order/racun_njemacka.html"), name='order.racun.njemacki_preview'),
    
    url(r'^order/print/shipping/label/(\d+)/$', 'sysapp.views.order_print_shipping_label', name='order.print.shipping.label'),


    url(r'^order/batch/ispis/render$', TemplateView.as_view(template_name='order/batch_ispis_forma.html'), name='order.batch.ispis.render'),

    
    url(r'^order/view/(?P<pk>\d+)/$', DetailView.as_view(model=Narudzba), name='order.view'), 

    url(r'^order/view/sifra/(\d+)/$', 'order.views.narudzba_get_sifra', name='order.view.sifra'), 

    url(r'^order/kosarica/view$', ListView.as_view(model=Kosarica, paginate_by=25), name='order.kosarica.view'), 
    url(r'^order/kosarica/remove/(\d+)$', 'order.views.kosarica_remove', name='order.kosarica.remove'),
    url(r'^order/kosarica/add$', 'order.views.kosarica_add', name='order.kosarica.add'),
    url(r'^order/kosarica/add/alternate$', 'order.views.kosarica_add_alternate', name='order.kosarica.add.alternate'),
    url(r'^order/kosarica/empty$', 'order.views.kosarica_empty', name='order.kosarica.empty'), 
    url(r'^order/kosarica/submit$', 'order.views.kosarica_submit', name='order.kosarica.submit'),
    url(r'^order/kosarica/priceadjust/(\d+)/([\d\.]+)$', 'order.views.kosarica_price_adjust', name='order.kosarica.priceadjust'), 
    url(r'^order/kosarica/qtyadjust/(\d+)/(\d+)$', 'order.views.kosarica_qty_adjust', name='order.kosarica.qtyadjust'), 

   
    url(r'^order/kosarica/add/iz/stare/(\d+)$', 'order.views.kosarica_add_iz_stare_narudzbe', name='order.kosarica.add.iz.stare.narudzbe'),

    url(r'^order/kosarica/naslovna$', 'order.views.kosarica_naslovna', name='order.kosarica.naslovna'),

    

    url(r'^order/posiljka/active/view$', ListView.as_view(model=Narudzba, paginate_by=25, queryset=Narudzba.objects.select_related().filter(posiljka__status=1)), name='order.posiljka.active.view'),

    url(r'^nabava/all/view$', ListView.as_view(model=Nabava, paginate_by=25, queryset=Nabava.objects.all().order_by('-created')), name='nabava.all.view'),
    url(r'^nabava/all/naruci', 'nabava.views.naruci', name='nabava.all.naruci'),
    url(r'^nabava/one/list/(?P<nabava_id>\d+)/$', NabavaItemView.as_view(model=NabavaItem, paginate_by=25), name='nabava.one.list'),
    url(r'^nabava/item/list/(?P<nabava_id>\d+)/(?P<ime>.*)/(?P<trziste>.*)/(?P<std_kolicina>.*)/(?P<jedinice>.*)$', NabavaNarudzbaView.as_view(model=NabavaItem, paginate_by=25, template_name='nabava/nabavanarudzba_list.html'), name='nabava.item.list'),
    url(r'^nabava/one/export/(?P<nabava_id>\d+)/$', 'nabava.views.export_nabava', name='nabava.one.export'),

    url(r'^order/my/depo/list$', ListView.as_view(model=Narudzba, paginate_by=25, queryset=Narudzba.objects.filter(depo=1)), name='order.my.depo.list'),
    url(r'^order/my/depo/today$', MyDepoToday.as_view(model=NarucenArtikal, paginate_by=25, template_name="order/my_depo_today.html"), name='order.my.depo.today'),
    url(r'^order/my/depo/today/zbroji$', MyDepoToday.as_view(model=NarucenArtikal, paginate_by=25, template_name="order/my_depo_today_zbroji.html"), name='order.my.depo.today.zbroji'),

    url(r'^order/my/orders/list$', ListView.as_view(model=Narudzba, paginate_by=25, queryset=Narudzba.objects.filter(depo=0)), name='order.my.orders.list'),
    

    url(r'^order/my/list$', MojeDanasnjeNarudzbe.as_view(model=Narudzba, paginate_by=25, template_name="order/narudzba_my_list.html"), name='order.my.list'),

    url(r'^order/set/konto/(?P<order_id>\d+)/(?P<konto_name>.+)$', 'order.views.order_set_konto', name='order.set.konto'), 
    url(r'^order/vip/status/(?P<order_id>\d+)$', 'order.views.order_vip_status', name='order.vip.status'), 
    url(r'^order/narudzba/storniraj/(\d+)$', 'order.views.order_narudzba_storniraj', name='order.narudzba.storniraj'), 

    url(r'^order/narudzba/izdaj/sve/(\d+)$', 'order.views.order_narudzba_izdaj_sve', name='order.narudzba.izdaj.sve'), 
    url(r'^order/narudzba/naplati/sve/(\d+)$', 'order.views.order_narudzba_naplati_sve', name='order.narudzba.naplati.sve'), 

    url(r'^order/incoming/view$', ListView.as_view(model=NarucenArtikal, paginate_by=25, template_name="order/incoming_view_list.html", queryset=NarucenArtikal.objects.select_related('narudzba').filter(status=0).order_by('ime')), name='order.incoming.view'),
    url(r'^order/artikal/zaprimi/(\d+)/(\d+)$', 'order.views.order_artikal_zaprimi', name='order.artikal.zaprimi'),
    
    url(r'^order/izdavanje/(\d+)/$', 'order.views.order_izdavanje', name='order.izdavanje'),
    url(r'^order/izdavanje/zahtjev/(\d+)/$', 'order.views.order_izdavanje_zahtjev', name='order.izdavanje.zahtjev'), 
    url(r'^order/izdavanje/izdaj/(\d+)/$', 'order.views.order_izdavanje_izdaj', name='order.izdavanje.izdaj'),

    url(r'^order/artikal/izdaj/(\d+)/$', 'order.views.order_artikal_izdaj', name='order.artikal.izdaj'),
    url(r'^order/artikal/naplati/(\d+)/$', 'order.views.order_artikal_naplati', name='order.artikal.naplati'),

    url(r'^order/uplata/add$', 'order.views.order_uplata_add', name="order.uplata.add"), 
    url(r'^order/uplata/delete/(\d+)/(\d+)$', 'order.views.order_uplata_delete', name="order.uplata.delete"), 

    url(r'^order/virman/print/(\d+)$', 'order.views.napravi_virman', name="order.virman.print"), 
    url(r'^order/check/konto/(\d+)$', 'order.views.order_check_konto', name="order.check.konto"), 

    

    url(r'^light/order/incoming/view$', ListView.as_view(model=NarucenArtikal, paginate_by=100, template_name="order/narucenartikal_list_light.html", queryset=NarucenArtikal.objects.select_related('narudzba', 'trziste', 'narucio').filter(~Q(trziste=8), valuta=1).order_by('-created')), name='light.order.incoming.view'), 
    

    
    
    url(r'^sysapp/obavijesti$', ListView.as_view(model=ObavijestiPost, paginate_by=10, template_name="sysapp/obavijesti_list.html", queryset=ObavijestiPost.objects.all().order_by('-created')), name='sysapp.obavijesti'), 
    url(r'^sysapp/ticket/create/$', CreateView.as_view(form_class=TicketForm, model=Ticket, template_name = 'sysapp/ticket_create.html'), name="sysapp.ticket.create"), 
    url(r'^sysapp/ticket/list/$', ListView.as_view(model=Ticket, paginate_by=25, template_name = 'sysapp/ticket_list.html'), name="sysapp.ticket.list"), 

    

    url(r'^order/json/fiskaliziraj/racun/(\d+)/$', 'order.views.order_fiskaliziraj_racun', name='order.fiskaliziraj.racun'), 
    url(r'^order/json/akontacija/racun/(\d+)/$', 'order.views.order_akontacija_racun', name='order.akontacija.racun'), 
    url(r'^order/json/storniraj/racun/(\d+)/$', 'order.views.order_storniraj_racun', name='order.fiskaliziraj.storno'), 

    url(r'^order/fiskaliziraj/racun/view/(?P<pk>\d+)/$', DetailView.as_view(model=Racun, template_name="fiskalizacija/racun_detalji.html"), name='order.fiskaliziraj.racun_detalji'),
    url(r'^order/fiskaliziraj/racun/print/(\d+)$', 'sysapp.views.print_racun', name='sysapp.views.print_racun'),            

    url(r'^fiskalizacija/racun/list/$', ListView.as_view(model=Racun, paginate_by=25), name='fiskalizacija.racun.list'),
    url(r'^fiskalizacija/racun/view/(?P<pk>\d+)/$', DetailView.as_view(model=Racun, template_name="fiskalizacija/racun_detalji.html"), name='fiskalizacija.racun.detalji'),
    url(r'^fiskalizacija/racun/html/view/(?P<pk>\d+)/$', DetailView.as_view(model=Racun, template_name="fiskalizacija/racun_html.html"), name='fiskalizacija.racun.html'),
    url(r'^fiskalizacija/racun/dostavi/naknadno/(\d+)$', 'fiskalizacija.views.dostavi_naknadno_racun', name='fiskalizacija.racun.dostavi_naknadno'),
    url(r'^fiskalizacija/racun/log/view/(?P<pk>\d+)/$', DetailView.as_view(model=RacunLog), name="fiskalizacija.racunlog.view"), 

    url(r'^fiskalizacija/json/racun/detail/(?P<pk>\d+)/$', DetailView.as_view(model=Racun, template_name="fiskalizacija/racun_info_json.html"), name='fiskalizacija.json.racun_detail'),
    url(r'^fiskalizacija/json/neuspjesni/list/$', ListView.as_view(model=Racun, template_name="fiskalizacija/racun_neuspjesni_list_json.html", queryset=Racun.objects.filter(jir__isnull=True)), name="fiskalizacija.json.neuspjesni_list"),

     

    url(r'^fiskalizacija/poslovni/view/(?P<pk>\d+)/$', DetailView.as_view(model=PoslovniProstorPoruka), name="fiskalizacija.pp.view"), 
    url(r'^fiskalizacija/poslovni/list$', ListView.as_view(model=PoslovniProstorPoruka, paginate_by=25), name='fiskalizacija.pp.list'), 
    url(r'^fiskalizacija/poslovni/create/$', CreateView.as_view(form_class=PoslovniProstorPorukaForm, model=PoslovniProstorPoruka, template_name = 'fiskalizacija/poslovniprostorporuka_add.html'), name="fiskalizacija.pp.add"), 
    url(r'^fiskalizacija/poslovni/submit/(\d+)/$', 'fiskalizacija.views.pp_submit', name='fiskalizacija.pp.submit'),

    
    url(r'^fiskalizacija/racun/add/$', 'fiskalizacija.views.izdaj_nevezan_racun', name="fiskalizacija.racun.add"), 
    
    url(r'^fiskalizacija/report/pdf/$', 'fiskalizacija.views.reportpdf', name='fiskalizacija.report.pdf'),
    
    url(r'^fiskalizacija/zki/kalkulator/$', 'fiskalizacija.views.zki_kalkulator', name='fiskalizacija.zki.kalkulator'),
    url(r'^fiskalizacija/provjera/racuna/$', 'fiskalizacija.views.provjera_racuna', name='fiskalizacija.provjera.racuna'),

    url(r'^fiskalizacija/racun/nevezan$', TemplateView.as_view(template_name='fiskalizacija/izdaj_nevezan_racun.html'), name='fiskalizacija.racun.nevezan'), 

    url(r'^fiskalizacija/obracun$', 'sysapp.views.dnevni_obracun', name='fiskalizacija.obracun.dnevni'), 
    url(r'^fiskalizacija/obracunaj$', FiskalizacijaObracunView.as_view(), name='fiskalizacija.obracun'),

    url(r'^fiskalizacija/danasnji/pdf/$', 'order.views.pdf_danasnji_fiskalni_racuni', name='order.views.pdf_danasnji_fiskalni_racuni'),

    
       

    #url(r'^order/racuni/list$', ListView.as_view(model=NarudzbaRacun, queryset=NarudzbaRacun.objects.all().order_by('-broj'), paginate_by=25), name='order.racuni.list'),
    url(r'^order/racuni/list$', 'order.views.racuni_list', name='order.racuni.list'),
    url(r'^order/racuni/report/daily/download/$', 'order.views.download_daily_report'),
    url(r'^order/racuni/report/monthly/download/(?P<year>\d+)/(?P<month>\d+)/$', 'order.views.download_monthly_report'),

    url(r'^order/storniraj/njemacki/racun/(\d+)/$', 'order.views.order_storniraj_njemacki_racun', name='order.njemacki.racun.storniraj'), 

    
    
    
    url(r'^barcode/generate/(\d+)/$', 'sysapp.views.eansvg'),
    url(r'^barcode/generate/(\d+)/barcode.svg$', 'sysapp.views.eansvg'),
    url(r'^barcode/generate/png/(\d+)$', 'sysapp.views.eanpng'),
    
    url(r'^barcode/submit/11(\d+)\d/$', 'depo.views.barcode_kutija'), 
    url(r'^barcode/submit/13(\d+)\d/$', 'sysapp.views.barcode_test'), 
    
    url(r'^barcode/submit/(\d+)/$', 'sysapp.views.barcode_submit'), 

    
    url(r'^pdf/test/$', 'sysapp.views.test_pdf'),
    url(r'^pdf/order/view/(\d+)/$', 'sysapp.views.order_to_pdf'),

    url(r'^accounts/profile/$', 'handler.views.main'), 
    url(r'^accounts/logout/$', 'handler.views.logout_view'),

    url(r'^ajax/paket/dodaj$', 'handler.views.ajax_dodavanje_paketa_test'),
    
    url(r'^depo/posiljka/list$', ListView.as_view(model=Posiljka, queryset=Posiljka.objects.filter(datum__gt=mjesec_dana, locked=1).order_by('-datum'), paginate_by=25), name='depo.posiljka.list'), 
    url(r'^depo/posiljka/detail/(?P<pk>\d+)$', DetailView.as_view(model=Posiljka), name='depo.posiljka.detail'), 
    url(r'^depo/posiljka/detail/kutije/(?P<pk>\d+)$', DepoKutijeListView.as_view(model=PosiljkaLijekKutija, paginate_by=25), name='depo.posiljka.kutija.detail'), 
    url(r'^depo/posiljka/detail/kutije/events/(?P<pk>\d+)$', DepoKutijeEventsListView.as_view(model=LijekKutijaEvents, paginate_by=25), name='depo.posiljka.kutija.events'), 
    url(r'^depo/posiljka/kutija/barkod/epl2$', 'depo.views.generiraj_epl2_za_30x18', {'barkod': 1672367609, 'ime_lijeka': 'Minostad 50 mg 30 kps'}),
    
    url(r'^depo/posiljka/lijek/add$', 'depo.views.posiljka_lijek_add', name="depo.posiljka.lijek.add"), 
    url(r'^depo/posiljka/lijek/delete/(\d+)$', 'depo.views.posiljka_lijek_delete', name="depo.posiljka.lijek.delete"),
    url(r'^depo/posiljka/zakljucaj$', 'depo.views.posiljka_zakljucaj', name="depo.posiljka.zakljucaj"),    
    
                                                                      
    url(r'^depo/posiljka/kutija/kodiraj/(\d+)$', 'depo.views.debug_ispis_kodiranih_naljepnica', name='depo.posiljka.kutija.kodiraj'),
    url(r'^depo/posiljka/kutija/naljepnice/(\d+)$', 'depo.views.debug_ispis_naljepnica', name='depo.posiljka.kutija.kodiraj2'),
    url(r'^depo/posiljka/kutija/naljepnice/ispisana/(\d+)$', 'depo.views.naljepnica_je_ispisana'), 
    url(r'^depo/posiljka/kutija/naljepnice/svesuispisane/(\d+)$', 'depo.views.sve_naljepnice_su_ispisane'), 
    
    
    url(r'^depo/zahtjev/izdavanje/$', DepoZahtjevCreateView.as_view(), name='depo.zahtjev.izdavanje'),
    url(r'^depo/zahtjev/status/ukloni/(\d+)/(\d+)$', 'depo.views.zahtjev_status_ukloni', name='depo.zahtjev.status.ukloni'),
    
    url(r'^depo/stavke/pregled/$', DepoStavkeListView.as_view(model=Zahtjev, paginate_by=25), name='depo.stavke.pregled'),
    
    url(r'^depo/stanje/kutije/(?P<pk>\d+)$', DepoStanjeListView.as_view(paginate_by=25), name='depo.stanje.kutije'),
    url(r'^depo/stanje/ukupno$', ListView.as_view(model=PosiljkaLijekKutija, queryset=PosiljkaLijekKutija.objects.filter(status=0).order_by('-modified'), template_name='depo/stanje_ukupno.html', paginate_by=25), name='depo.stanje.ukupno'),    
    url(r'^depo/kosarica/list$', 'depo.views.kosarica_list', name='depo.kosarica.list'),
    url(r'^depo/kosarica/lock$', 'depo.views.kosarica_lock', name='depo.kosarica.lock'),
    
    
        
    url(r'^depo/inventura/skenirano$', ListView.as_view(model=PosiljkaLijekKutija, queryset=PosiljkaLijekKutija.objects.filter(status=0, inventura=1).order_by('-modified'), template_name='depo/inventura_skenirano.html', paginate_by=25), name='depo.inventura.skenirano'),
    url(r'^depo/inventura/list$', ListView.as_view(model=Inventura, paginate_by=25), name='depo.inventura.list'),
    url(r'^depo/inventura/detail/(?P<pk>\d+)$', DepoInventuraKutijaListView.as_view(model=InventuraKutija, paginate_by=25), name='depo.inventura.detail'),
    url(r'^depo/inventura/zatvori$', 'depo.views.inventura_zatvori', name='depo.inventura.zatvori'),    
    url(r'^barcode/submit/inventura/11(\d+)\d/$', 'depo.views.inventura_skeniraj', name='depo.inventura.skeniraj'),
      

    
    
    url(r'^depo/obracun/dnevni$', 'depo.views.obracun_dnevni', name='depo.obracun.dnevni'),        
    url(r'^order/uplate/obracun$', 'order.views.uplate_obracun', name="order.uplate.obracun"),
    url(r'^order/uplate/moj/obracun$', 'order.views.danasnje_stanje_blagajne', name="order.uplate.moj.obracun"),
    url(r'^order/obracun/moj/promet$', 'order.views.obracun_moj_promet', name="order.obracun.moj_promet"),
    
    url(r'^order/moj/obracun/pdf$', 'order.views.moje_dnevno_pdf_izvjesce', name="order.moje.dnevno.pdf.izvjesce"),
    url(r'^order/ispis/narudzbi/pdf$', 'order.views.pdf_ispis_danasnjih_narudzbi', name="order.ispis.danasnjih.narudzbi.pdf"),
    url(r'^order/ispis/blagajne/pdf$', 'order.views.pdf_dnevni_obracun_blagajne', name="order.dnevni.obracun.blagajne.pdf"),
    url(r'^order/slanje/narudzbi/pdf$', 'order.views.pdf_slanje_danasnjih_narudzbi', name="order.slanje.danasnjih.narudzbi.pdf"),

    
    
    url(r'^depo/stavke/nerijesene/$', ListView.as_view(model=Zahtjev, queryset=Zahtjev.objects.filter(status__in=[0,1]), template_name='depo/nerijesene_stavke.html', paginate_by=25), name='depo.stavke.nerijesene'),
    

    
            
    url(r'^ajax/paket/kosarica/(\d+)/$', 'handler.views.dodavanje_kosarica'),
    url(r'^ajax/paket/kosarica/izbrisi/(\d+)/(\d+)/$', 'handler.views.brisanje_kosarica'),
    url(r'^ajax/paket/kosarica/azuriraj/(\d+)/(\d+)/$', 'handler.views.azuriranje_kolicina_kosarica'),

    url(r'^ajax/izdavanje/prikaz$', 'handler.views.ajax_izdavanje_prikaz'),

    
    
    url(r'^ajax/lijekovi/list/$', ListView.as_view(model=Lijek, paginate_by=25), name='lijekovi.list'),        
    url(r'^depo/lijek/edit/(?P<pk>\d+)/$', UpdateView.as_view(form_class=LijekForm, model=Lijek, template_name = 'depo/lijek_edit.html'), name="depo.lijek.edit"), 
    url(r'^depo/lijek/add$', CreateView.as_view(form_class=LijekForm, model=Lijek, template_name = 'depo/lijek_add.html'), name="depo.lijek.add"), 
    url(r'^ajax/lijekovi/list/sort/(?P<order>\w+)/(?P<sortfield>\w+)/$', DepoListView.as_view(model=Lijek, paginate_by=25), name='lijekovi.list.sort'),        
    
    
    url(r'^ajax/lijekovi/naruciti/$', ListView.as_view(model=Lijek, paginate_by=25, template_name='depo/lijek_naruciti_list.html', queryset=Lijek.objects.filter(stanje__lt=F('min_stanje'))), name='depo.zalihe.nedostaje'),  

    
    url(r'^ajax/izdavanje/polling$', 'handler.views.ajax_izdavanje_polling'),
    url(r'^ajax/zahtjev/azuriraj/(\d+)/(\d+)$', 'handler.views.ajax_azuriraj_zahtjev'),   
    url(r'^ajax/forma/izdavanje$', 'handler.views.ajax_izdavanje_lijeka'),


    
    url(r'^ajax/izdavanje/olijeku/(?P<pk>\d+)/$', DetailView.as_view(model=Lijek)), 
  
    
    url(r'^hnb/tecajna$', 'sysapp.views.dohvati_tecajnu_listu'), 

    url(r'^graph/lijek/alltime/(?P<pk>\d+)/$', DetailView.as_view(model=Lijek, template_name="depo/lijek_graph.html")), 
    url(r'^graph/lijek/test/(?P<pk>\d+)/$', 'depo.views.graph_lijek_alltime'), 
    url(r'^dev/lijek/racunaj/$', 'depo.views.racunaj_ukupni_ulaz'), 

    url(r'^temperatura/dostavi/(?P<t1>-?\d+\.\d{2})/(?P<t2>-?\d+\.\d{2})$', 'sysapp.views.temperatura_dostavi'), 
    url(r'^temperatura/plot$', 'sysapp.views.temperatura_plot'), 
    
    url(r'^js/diocles/(\d+)$', TemplateView.as_view(template_name='diocles-dynamic.js'), name='js.diocles'), 
    url(r'^sysapp/provjeri/vezu/$', 'sysapp.views.provjeri_vezu', name='sysapp.provjeri.vezu'), 
    url(r'^sysapp/snapshot/submit$', 'sysapp.views.handle_login_snapshot', name='sysapp.snapshot.submit'), 

    url(r'^sysapp/message/send$', IM_CreateView.as_view(form_class=InstantMsgForm, model=InstantMsg, template_name='sysapp/send_msg.html'), name='sysapp.message.send'),
    url(r'^sysapp/ajax/polling$', 'sysapp.views.ajax_polling', name='sysapp.ajax.polling'), 
    url(r'^sysapp/supervisor$', 'sysapp.views.supervisor', name='sysapp.supervisor'), 
    
    url(r'^sysapp/barcode/scan$', TemplateView.as_view(template_name='barcode.html'), name='sysapp.barcode.scan'), 

)

if not settings.local.Deploy:
    import os
    urlpatterns += patterns('',
        (r'^img/(.*)$', 'django.views.static.serve', {'document_root': os.path.realpath(settings.local.ProjectPath + '/../static/img')}),
        (r'^inc/(.*)$', 'django.views.static.serve', {'document_root': os.path.realpath(settings.local.ProjectPath + '/../static/inc')}),
        (r'^data/(.*)$', 'django.views.static.serve', {'document_root': os.path.realpath(settings.local.ProjectPath + '/../data/')}),
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.realpath(settings.local.ProjectPath + '/../static')}),
    )
