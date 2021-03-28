#coding=utf-8

import datetime
from django.db import models, transaction
from django.forms import ModelForm, Textarea, TextInput, HiddenInput
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.db.models.signals import post_save

from stdnum.iso7064 import mod_11_10 

from meds.models import *
from eskulap import models as em

from django.db.models import Q
from django.db.models import Count, Min, Sum, Max, Avg

from order.templatetags.mytagslib import * 
from project.common_models import AdminSetter

import settings

 


def validate_iso7064(value):
  from django.core.validators import ValidationError
  if not mod_11_10.is_valid(value) and value:
    raise ValidationError('Broj je neispravan, molimo provjerite!')



class Rabat(models.Model):
  iznos = models.IntegerField()

  def __unicode__(self): return '%s %' % self.iznos
 
class Valuta(models.Model):
  naziv = models.CharField(max_length=64)
  kratica = models.CharField(max_length=16)
  html = models.CharField(max_length=16)  
  jed_iznos = models.IntegerField()

class TecajnaLista(models.Model):
  date = models.DateField()

  def srednji_tecaj(self):
    return self.tecaji.get(tip='2').iznos

  def prodajni_tecaj(self):
    return self.tecaji.get(tip='3').iznos

class Tecaj(models.Model):
  TIP_TECAJA = (
        ('1', 'Kupovni'),
        ('2', 'Srednji'),
        ('3', 'Prodajni'),
  )
  tip = models.CharField(max_length=4, choices=TIP_TECAJA)
  valuta = models.ForeignKey(Valuta, related_name='tecaji')
  iznos = models.DecimalField(max_digits=8, decimal_places=6)
  lista = models.ForeignKey(TecajnaLista, related_name='tecaji')

def validate_iznos(value):
  from django.core.validators import ValidationError
  if not value > 0:
    raise ValidationError('Iznos mora biti pozitivan, molimo provjerite!')
  


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

def izracunaj_troskove(iznos):  
  if iznos > 20.50: return Decimal('6')
  elif iznos > 5.50: return Decimal('4')
  else: return Decimal('2')  

class Trziste(models.Model):
  naziv = models.CharField(max_length=64)

  koeficijent_pacijenti = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
  koeficijent_ljekarne = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
  koeficijent_lobo = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

  transport = models.BooleanField(default=1)

  def __unicode__(self): return self.naziv
  
  class Meta:
    verbose_name_plural = 'Trzista'

def artikal_drugo_trziste_calc_maloprodajna_cijena(nabavna_cijena, trziste, atc_id=None, atc_sifra=None):
    def_pdv = settings.TaxRate
    pdv = get_pdv(atc_id=atc_id, atc_sifra=atc_sifra)
    pdv_factor = (pdv + 100.0) / 100.0
    if pdv < (def_pdv * 0.99):
        pdv_factor *= 1.1
    return float(nabavna_cijena) * float(trziste.koeficijent_pacijenti) * pdv_factor

def artikal_drugo_trziste_calc_veleprodajna_cijena(nabavna_cijena, trziste):
    return float(nabavna_cijena) * float(trziste.koeficijent_ljekarne)


class ArtikalDrugoTrziste(models.Model, AdminSetter):
  ime = models.CharField(max_length=128, blank=True, db_index=True)
  cijena = models.DecimalField(max_digits=12, decimal_places=2)
  trziste = models.ForeignKey(Trziste, related_name='artikli')
  sifra = models.CharField(max_length=20, default="")
  kolicina_jed = models.CharField(max_length=20, default="")
  kolicina = models.CharField(max_length=10, default="")
  jedinice = models.CharField(max_length=10, default="")
  ATC = models.ForeignKey(AtcCode,  null=True)

  def calc_maloprodajna_cijena(self):
    return artikal_drugo_trziste_calc_maloprodajna_cijena(self.cijena, self.trziste, atc_id=self.ATC_id) if self.id is not None else 0.0

  def calc_veleprodajna_cijena(self):
    return artikal_drugo_trziste_calc_veleprodajna_cijena(self.cijena, self.trziste) if self.id is not None else 0.0

  def cijena_pacijenti(self):
    return "%.2f" % (self.calc_maloprodajna_cijena())
  def cijena_ljekarne(self):
    return "%.2f" % (self.calc_veleprodajna_cijena())
  def cijena_lobopharm(self):
    return "%.2f" % (self.cijena * self.trziste.koeficijent_lobo)


class Klijent(models.Model):
  TIP_OBVEZNIKA = (
        ('1', 'R-1'),
        ('2', 'R-2'),
       ('3', 'Nije obveznik'),
  )
  TIP_KLIJENTA = {1: 'Fizička osoba', 2: 'Pravna osoba', '3': 'Ljekarna'}
  
  tip_klijenta = models.IntegerField() 
  titula = models.CharField(max_length=32, null=True, blank=True)
  ime = models.CharField(max_length=64, null=True, blank=True)
  prezime = models.CharField(max_length=64, null=True, blank=True)
  naziv = models.CharField(max_length=64, null=True, blank=True) 
  oib = models.CharField(max_length=64, null=True, blank=True, validators=[validate_iso7064,])
  tip_poreznog_obveznika = models.CharField(max_length=4, choices=TIP_OBVEZNIKA, null=True, blank=True) 
  adresa = models.CharField(max_length=192, null=True, blank=True)
  postanski_broj = models.CharField(max_length=16, null=True, blank=True)
  grad = models.CharField(max_length=64, null=True, blank=True)
  zemlja = models.CharField(max_length=128, null=True, blank=True)

  
  telefon = models.CharField(max_length=64, null=True, blank=True, verbose_name="Fiksni telefon")
  mobitel = models.CharField(max_length=64, null=True, blank=True, verbose_name="Mobilni telefon")
  fax = models.CharField(max_length=32, null=True, blank=True)
  email = models.CharField(max_length=64, null=True, blank=True)
  web = models.URLField(verify_exists=False, null=True, blank=True)

  rabat = models.ForeignKey(Rabat, related_name='tvrtke', null=True, blank=True)

  opaska = models.CharField(max_length=128, null=True, blank=True)
 
  def __unicode__(self): return "%s %s" % (self.ime, self.prezime)

  def get_full_name(self):
    if self.ime: return "%s %s" % (self.ime, self.prezime)
    else: return self.naziv
 
  def get_absolute_url(self):
    return reverse('client.view', args=[self.id])
  
  def get_tip_obveznika(self):
    return self.TIP_OBVEZNIKA[int(self.tip_poreznog_obveznika)][1]
  
  def is_company(self):
    return self.tip_klijenta-1 

  def zadnje_narudzbe(self):
    return self.narudzbe.all().order_by('-id')[:20]


  def get_report_name(self):
      # ako je dummy ime, potrazi nekog slucajnog klijenta i daj njegovo ime za report
      if self.ime == "." and self.prezime == "Depo":
          from django.db.models import Q
          q = Q(tip_klijenta=1) & ~Q(ime__iexact=".") & ~Q(ime__iexact="")
          klijent = Klijent.objects.filter(q).order_by("?")[0]
          return klijent.get_report_name()
      res = ""
      if self.tip_klijenta == 1:
          res = self.get_full_name()
      else:
          res = self.naziv
      return res


  class Meta:
    verbose_name_plural = 'Klijenti'
    ordering = ['prezime', 'ime', 'naziv',]
    unique_together = ('ime', 'prezime', 'adresa', 'grad',)


class TvrtkaForm(ModelForm):
  
  class Meta:
    model = Klijent
    exclude = ('ime', 'prezime', 'titula',)  
    widgets = {
            'opaska': Textarea(attrs={'cols': 20, 'rows': 10}),
            'tip_klijenta': HiddenInput(attrs={'value': 2}),
        }

class KlijentForm(ModelForm):
  
  
  
  
  class Meta:
    model = Klijent
    exclude = ('naziv', 'tip_poreznog_obveznika', 'web', 'fax', 'oib', 'titula', 'rabat', )  
    widgets = {
            'opaska': Textarea(attrs={'cols': 20, 'rows': 10}),
            'tip_klijenta': HiddenInput(attrs={'value': 1}),
           
        }

  def __init__(self, *args, **kwargs):
        super(KlijentForm, self).__init__(*args, **kwargs)
        self.fields['ime'].widget.attrs['autofocus'] = ""
	self.fields['grad'].initial = "Zagreb"
	self.fields['zemlja'].initial = "Hrvatska"
	self.fields['postanski_broj'].initial = "10000"

class OrderPosiljka(models.Model):
  STATUS = (
        (0, 'Zaključana'),
        (1, 'Aktivna'),               
  )  
  datum = models.DateTimeField(auto_now_add=True)
  status = models.IntegerField(default=1)
  indeks_zadnje_narudzbe = models.IntegerField(default=1)
  
  class Meta:
    verbose_name_plural = 'Pošiljke'
    
  def sifra(self):
    return '%s/%s' % (self.datum.year, self.id)  
    
class Narudzba(models.Model):
  STATUS_NARUDZBE = (
        (0, 'Zaključana'),
        (1, 'Zaprimljen zahtjev'),
        (2, 'Plaćeno po ponudi'),
        (3, 'Neuspješno izvršeno'),
        (4, 'Sve stiglo na skladište'),
        (5, 'Djelomično stiglo na skladište'),
        (6, 'Sve naplaćeno i isporučeno'),
        (7, 'Stornirano'),
        (8, 'Djelomično naplaćeno i isporučeno'),
        (9, 'Naručeno od dobavljača'),
        (10, 'VIP status'),
  )
  broj = models.IntegerField(default=1)
  posiljka = models.ForeignKey(OrderPosiljka, related_name='narudzbe')
  klijent = models.ForeignKey(Klijent, related_name='narudzbe')

  narucio = models.ForeignKey(User, related_name='narudzbe', blank=True, null=True)
  slati_postom = models.BooleanField(default=0) 
  sms_obavijest = models.BooleanField(default=0) 
  ispisana_potvrda = models.BooleanField(default=0) 
  depo = models.BooleanField(default=0) 

  sifra = models.BigIntegerField()
  status = models.IntegerField(default=1)   
  created = models.DateTimeField(auto_now_add=True)     
  modified = models.DateTimeField(auto_now=True) 
  zabiljezba = models.CharField(max_length=512, blank=True, null=True) 

  konto_name = models.CharField(max_length=25)
  

  class Meta:
    verbose_name_plural = 'Narudžbe'    
    ordering = ['-broj']

  def get_status(self):
    return self.STATUS_NARUDZBE[self.status][1]

  def get_total(self):
    zbroj = 0
    for i in self.artikli.filter(status__in=[0,1,4]):
      if i.valuta == 1: zbroj += eur2hrk(i.jedinicna_cijena*int(i.kolicina)) 
      elif i.valuta == 4: zbroj += i.jedinicna_cijena*int(i.kolicina)
    return zbroj
 
  def get_total_za_izdati(self):
    return sum([i.jedinicna_cijena * int(i.kolicina) for i in self.artikli.filter(status=1, za_izdavanje=1)])
  
  def ukupna_cijena(self):
    cijena = sum([i.jedinicna_cijena * int(i.kolicina) for i in self.artikli.all()])
    if self.artikli.filter(shipping=1).count():
      cijena += izracunaj_troskove(self.osnovica_za_troskove()) 
    return cijena
  
  def ukupna_cijena_bez_troskova_euri(self):
    cijena = sum([i.jedinicna_cijena * int(i.kolicina) for i in self.artikli.filter(valuta=1)])
    return cijena
  
  def ukupna_cijena_bez_troskova_kune(self):
    cijena = sum([i.jedinicna_cijena * int(i.kolicina) for i in self.artikli.filter(valuta=4)])
    return cijena

  def osnovica_za_troskove(self):
    return sum([i.jedinicna_cijena * int(i.kolicina) for i in self.artikli.filter(shipping=1)])
  
  def ukupna_cijena_kn(self):
    cijena = 0
    for i in self.artikli.all():
      if i.valuta == 4: cijena += i.jedinicna_cijena * int(i.kolicina)
      else: cijena += eur2hrk(i.jedinicna_cijena*int(i.kolicina))
    if self.artikli.filter(shipping=1).count():
      cijena += eur2hrk(izracunaj_troskove(cijena))
    return cijena

  def troskovi(self):
    return izracunaj_troskove(self.get_total())
  
  def get_barcode(self):
    return '12%s' % self.sifra
  
  def troskovi_su_placeni(self):
    if self.uplate.filter(tip='4').count(): return 1
    else: return 0
 
  def get_polog(self):
    polog = sum([i.to_euro() for i in self.uplate.filter(tip=1)])
    if not polog: return 0
    else: return polog

  def get_polog_kn(self):
    polog_kune = sum([i.iznos for i in self.uplate.filter(tip__in=[1,10], valuta=4)])
    polog_euri = sum([i.iznos for i in self.uplate.filter(tip__in=[1,10], valuta=1)])
    return eur2hrk(polog_euri) + Decimal(polog_kune)
  
  def get_polog_eur(self):
    polog_kune = sum([i.iznos for i in self.uplate.filter(tip__in=[1,10], valuta=4)])
    polog_euri = sum([i.iznos for i in self.uplate.filter(tip__in=[1,10], valuta=1)])
    return Decimal(polog_euri) + hrk2eur(polog_kune)
    
  def za_platiti_kn(self):
    return self.fetch_zaduzenja() - self.fetch_uplate()
  
  def za_platiti_eur(self):
    return self.fetch_zaduzenja_eur() - self.fetch_uplate_eur()

  def za_platiti(self):
    return self.ukupna_cijena() - self.fetch_uplate()

  def fetch_uplate(self):
    return sum([i.to_kn() for i in self.uplate.filter(vrsta=0)])
  def fetch_zaduzenja(self):
    return sum([i.to_kn() for i in self.uplate.filter(vrsta=1)])
  
  def fetch_uplate_eur(self):
    return sum([i.to_euro() for i in self.uplate.filter(vrsta=0)])
  def fetch_zaduzenja_eur(self):
    return sum([i.to_euro() for i in self.uplate.filter(vrsta=1)])

  def grand_total(self):
    total = sum([i.to_euro() for i in self.uplate.filter(vrsta=0)]) - sum([i.to_euro() for i in self.uplate.filter(vrsta=1)])
    return total
  
  def grand_total_kn(self):
    total = sum([i.to_kn() for i in self.uplate.filter(vrsta=0)]) - sum([i.to_kn() for i in self.uplate.filter(vrsta=1)])
    return total

  def usluge_transporta(self):
    return izracunaj_troskove(self.osnovica_za_troskove())
  
  def usluge_transporta_kn(self):
    return eur2hrk(izracunaj_troskove(self.osnovica_za_troskove()))

  def vazeci_fiskalni_racun(self): 
    return self.racuni.filter(storno=0, stornira_racun__isnull=True).count() 
  
  def postoje_uplate_za_narudzbu(self): 
    return self.uplate.filter(vrsta=0).count()
  
  def bilanca_uplata(self): 
    kune = self.uplate.filter(valuta=4, vrsta=0).aggregate(Sum('iznos'))['iznos__sum']
    euri = self.uplate.filter(valuta=1, vrsta=0).aggregate(Sum('iznos'))['iznos__sum']
    if kune == None: kune = 0
    if euri == None: euri = 0
    return kune + euri

  def generiraj_poziv_na_broj(self):
    datefield = "%02d%02d%04d" % (self.created.day, self.created.month, self.created.year)
    kontrolna = mod11ini("%s%s" % (self.sifra, datefield))
    return "%s-%s-%s" % (self.sifra, datefield, kontrolna)

  def get_report_total_price(self):
    return sum([i.get_report_total_price() for i in self.artikli.all()])

  def get_pdv_code(self):
    defpdv = get_pdv()
    pdv = defpdv
    for i in self.artikli.all():
      npdv = get_pdv(atc_sifra=i.atc_sifra)
      if npdv < pdv:
        pdv = npdv
    if pdv < defpdv:
      return '-%d' % (int(pdv),)
    else:
      return ''

  def __init__(self, *args, **kwargs):
    super(Narudzba, self).__init__(*args, **kwargs) 
    if self.sifra == None: 
      from random import randint
      self.sifra = randint(10**9,10**10-1)
      if Narudzba.objects.filter(sifra=self.sifra).count():
        raise ValueError('Već postoji taj kod narudžbe u bazi podataka')
      self.posiljka, created = OrderPosiljka.objects.get_or_create(status=1) 
      if created: self.broj = 1 
      else: 
        self.broj = self.posiljka.indeks_zadnje_narudzbe + 1
        self.posiljka.indeks_zadnje_narudzbe += 1
        self.posiljka.save()


class Uplata(models.Model): 
  TIP_UPLATE = (
        ('1', 'Polog'),
        ('2', 'Uplata za lijek'),
        ('3', 'Uplata poštom ili na račun'),
        ('4', 'Usluge transporta'),
        ('5', 'Fiskalni račun'),
        ('6', 'Poštarina'),
        ('7', 'Usluge posredovanja'),
        ('8', 'Povrat novca'),
        ('9', 'Ispravak greške pri uplati'),
        ('10', 'Uplaćeno prije uvođenja sustava'),
  )
  VRSTA = {0: 'Uplata', 1: 'Zaduženje', 2: 'Isplata'}

  narudzba = models.ForeignKey(Narudzba, related_name='uplate')
  valuta = models.ForeignKey(Valuta, related_name='uplate')
  djelatnik = models.ForeignKey(User, related_name='uplate')
  klijent = models.ForeignKey(Klijent, related_name='uplate')

  
  
  

  iznos = models.DecimalField(max_digits=12, decimal_places=2)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  tip = models.CharField(max_length=4, choices=TIP_UPLATE, default='2')
  vrsta = models.IntegerField(null=True, default=0) 
  tecaj = models.DecimalField(max_digits=8, decimal_places=6) 
  napomena = models.CharField(max_length=4096, null=True, blank=True)
  

  

  def get_tip(self):
    return self.TIP_UPLATE[int(self.tip)-1][1]
  
  def get_vrsta(self):
    return self.VRSTA[self.vrsta]

  def get_vrsta_predznak(self):
    if self.vrsta: return '-'
    else: return ''

  def timestamp(self):
    if self.created != self.modified: return '<div class="modified">%s</div>' % self.modified
    else: return self.created

  def to_euro(self):
    if self.valuta_id == 4: 
      return hrk2eur(self.iznos) 
    else: return self.iznos

  def to_kn(self):
    if self.valuta_id == 1:
      return eur2hrk(self.iznos)
    else: return self.iznos

class UplataForm(ModelForm):
  
  class Meta:
    model = Uplata
    exclude = ('narudzba', 'djelatnik', 'klijent', 'created', 'modified', 'vrsta', 'tecaj',)  


class NarucenArtikal(models.Model): 
  STATUS = (
        ('0', 'Naručen'),        
        ('1', 'Na skladištu'),
        ('2', 'Storniran'),
        ('3', 'Stigao u Njemačku'),
        ('4', 'Naplaćen'),        
        ('5', 'Izdan'),        
        ('6', ''),        
        ('7', 'Upućen na povrat'),
        ('8', 'Proknjižen povrat'),
        ('9', 'Naručeno od dobavljača'),
  )
  narudzba = models.ForeignKey(Narudzba, related_name='artikli')
  Sortname1 = models.CharField(max_length=96, null=True, blank=True) 
  trziste = models.ForeignKey(Trziste, null=True, blank=True, related_name='naruceni_artikli') 
  ZoNr = models.BigIntegerField(null=True, blank=True)
  ime = models.CharField(max_length=96)
  kolicina = models.CharField(max_length=8) 
  jedinice = models.CharField(max_length=8, null=True, blank=True)
  pakiranje = models.CharField(max_length=8, null=True, blank=True)
  std_kolicina = models.CharField(max_length=25, null=True, blank=True)
  kratica_dobavljaca = models.CharField(max_length=10, null=True, blank=True)
  jedinicna_cijena = models.DecimalField(max_digits=12, decimal_places=2)
  valuta = models.IntegerField(default=1, null=True, blank=True)
  tip = models.IntegerField(default=0, null=True, blank=True) 
  shipping = models.IntegerField(default=1, null=True, blank=True) 
  created = models.DateTimeField(auto_now_add=True)     
  modified = models.DateTimeField(auto_now=True)     
  status = models.IntegerField(default=0, db_index=True) 
  placeno = models.BooleanField(default=0)
  
  za_izdavanje = models.BooleanField(default=1) 
  
  atc_sifra = models.CharField(max_length=7, null=True)  

  def toggle_izdavanje(self):
    if self.za_izdavanje: self.za_izdavanje = 0
    else: self.za_izdavanje = 1
    self.save()
 
  def get_status(self):
    return self.STATUS[self.status][1]

  def jedinicna_cijena_kn(self):
    if self.valuta == 1: return eur2hrk(self.jedinicna_cijena)
    else: return self.jedinicna_cijena
  
  def jedinicna_cijena_eur(self):
    if self.valuta == 4: return hrk2eur(self.jedinicna_cijena)
    else: return self.jedinicna_cijena
  
  def get_total(self):
    return int(self.kolicina)*self.jedinicna_cijena

  @property
  def get_total_property(self):
    return int(self.kolicina)*self.jedinicna_cijena
  
  def get_total_kn(self):
    # if self.valuta == 1: return eur2hrk(self.get_total())
    # elif self.valuta == 4: return self.get_total()
    return int(self.kolicina) * self.jedinicna_cijena_kn()

  def get_total_eur(self):
    # if self.valuta == 4: return hrk2eur(self.get_total())
    # elif self.valuta == 1: return self.get_total()
    return int(self.kolicina) * self.jedinicna_cijena_eur()

  def narucio(self):
    return self.log_order.get(event=0).user.get_full_name() 

  def valuta_text(self):
    return Valuta.objects.get(id=self.valuta).kratica

  def get_report_price(self):
    res = 0
    # prvo provjeri je li lijek u tablici za njemacko trziste
    if self.ZoNr is not None:
        try:
            item = Artikal.objects.get(ZoNr=self.ZoNr)
            res = item.ApoEk / Decimal(100.0)
        except:
            pass
    else:
        # ako nije, potrazi ga u depo
        from project.depo.models import Lijek
        try:
            item = Lijek.objects.get(naziv__iexact=self.ime)
            res = item.nabavna_cijena_eur
        except:
            # ako nije ni u depo, potrazi ga u ljekovima s ostalih trzista
            try:
                item = ArtikalDrugoTrziste.objects.get(ime__iexact=self.ime)
                res = item.cijena
            except:
                pass

    # nabavna cijena + marza (20%) + PDV (25%)
    pdv = get_pdv(atc_sifra=self.atc_sifra)
    return Decimal(round(res * Decimal(1.2 * (1. + pdv / 100.)), 2))

  def get_report_total_price(self):
    return self.get_report_price() * Decimal(self.kolicina)

  class Meta:
    verbose_name_plural = 'Naručeni artikli'  

class LogArtikla(models.Model): 
  artikal = models.ForeignKey(NarucenArtikal, related_name='log_order')
  user = models.ForeignKey(User, related_name='log_order')
  event = models.IntegerField()
  opis = models.CharField(max_length=128)
  datetime = models.DateTimeField(auto_now_add=True)
  
class OrderZahtjevIzdavanje(models.Model):
  STATUS = (
        ('0', 'Upućen zahtjev za izdavanje'),        
        ('1', 'Artikal otpremljen iz skladišta'), 
        ('2', 'Artikal dostavljen prodaji'), 
        ('3', 'Artikal isporučen kupcu'),
        ('4', 'Odbijen zahtjev za izdavanje'),        
        ('5', 'Zahtjev zaključan'),
  )  
  narucen_artikal = models.ForeignKey(NarucenArtikal, related_name='order_zahtjevi_izdavanje', blank=True, null=True)
  user = models.ForeignKey(User, related_name='order_zahtjevi_izdavanje')  
  status = models.IntegerField(choices=STATUS)     
  created = models.DateTimeField(auto_now_add=True)      
  modified = models.DateTimeField(auto_now=True)      
  fetched = models.BooleanField(default=0)          
  zabiljezba = models.CharField(max_length=1024, blank=True, null=True) 
  


class KosaricaDbManager(models.Manager):
  def interakcije(self, stoff_id_list, obj_list): 
    from django.db import *
    cursor = connection.cursor()
    query = str(tuple(map(str,stoff_id_list)))
    for i in stoff_id_list:    
      cursor.execute("""
        SELECT * FROM `abda_Stoffinteraktion` WHERE  `StoffNr` IN %s
        AND InteraktionNr IN 
        (SELECT DISTINCT InteraktionNr
        FROM  `abda_Stoffinteraktion` 
        WHERE  `StoffNr` IN %s
        GROUP BY  `InteraktionNr`
        HAVING COUNT(InteraktionNr) >1)
        ORDER BY InteraktionNr DESC
        LIMIT 0, 50
        """
      % (query,query))
      
    dic={}
    for x,y,z,a,b in [row for row in cursor.fetchall()]:
      dic.setdefault(z, []).append(str(b))      
      

    for key in dic:
      if not ('1' in dic[key] and '0' in dic[key]): dic[key]='0' 
      else: dic[key]='1'
        

    pic = dic
                  
    cursor.close()    
    return pic      

class Kosarica(models.Model):
  djelatnik = models.OneToOneField(User, related_name='kosarica') 
  klijent = models.ForeignKey(Klijent, related_name='kosarica', null=True, blank=True) 
  ukupna_cijena = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  broj_artikala = models.IntegerField(null=True, blank=True)
  ip_adresa = models.IPAddressField(null=True, blank=True)
  objects = KosaricaDbManager()

  def isprazni(self):
    for i in self.artikli.all():
      i.delete()

  def zbroji(self):
    return sum([i.kolicina for i in self.artikli.all()])

  def cijena(self):



    kuna = sum([i.cijena * i.kolicina for i in self.artikli.filter(valuta=Valuta.objects.get(kratica='HRK').id)])
    eura = sum([i.cijena * i.kolicina for i in self.artikli.filter(valuta=Valuta.objects.get(kratica='EUR').id)])
    kuna = kuna + eur2hrk(eura)
    return kuna 
  
  def zbroji_troskove(self):
    return sum(self.artikli.values_list('troskovi', flat=True))



  
  def provjeri_interakcije_old2(self):
    lista_djelatnih_tvari = [i for s in [x.artikal.lista_djelatnih_tvari() for x in self.artikli.all()] for i in s] 
    return Kosarica.objects.interakcije(lista_djelatnih_tvari, self.artikli.all())    
  
  def provjeri_interakcije_old(self):
    return Kosarica.objects.interakcije(self.artikli.values_list('artikal__M2Nr', flat=True), self.artikli.all())      
  
  def provjeri_interakcije(self):   
    from meds.models import Stoffinteraktion
    artikli = self.artikli.filter(artikal__isnull=False)
    lista_djelatnih_tvari = [i for s in [x.artikal.lista_djelatnih_tvari() for x in artikli] for i in s] 
    interakcije = Stoffinteraktion.objects.filter(stoff__in=lista_djelatnih_tvari)
    
    rjecnik = dict([(j, x.artikal.name) for x in artikli for j in x.artikal.lista_djelatnih_tvari()])
    for i in interakcije: i.name = rjecnik[i.stoff_id]
    
    return [(i,j) for i in interakcije for j in interakcije if i.interaktion_id==j.interaktion_id and i.lokalisation!=j.lokalisation and i.stoff_id<j.stoff_id]
    
  def __unicode__(self): return self.djelatnik.get_full_name()

def create_user_cart(sender, instance, created, **kwargs):
    if created:
       profile, created = Kosarica.objects.get_or_create(djelatnik=instance)

post_save.connect(create_user_cart, sender=User)

User.cart = property(lambda u: u.get_cart() )

class KosaricaArtikal(models.Model):
  kosarica = models.ForeignKey(Kosarica, related_name='artikli', null=True, blank=True)
  kolicina = models.IntegerField(null=True, blank=True)
  cijena = models.DecimalField(max_digits=12, decimal_places=2)
  valuta = models.IntegerField(default=1, null=True, blank=True)
  tip = models.IntegerField(default=0, null=True, blank=True) 
  shipping = models.IntegerField(default=1, null=True, blank=True) 
  troskovi = models.IntegerField(blank=True, null=True)
  naziv = models.CharField(max_length=96, blank=True, null=True)
  trziste = models.ForeignKey(Trziste, related_name='artikli_u_kosarici', null=True, blank=True)
  artikal = models.ForeignKey('meds.Artikal', related_name='kosarica_artikal', null=True, blank=True) 
              
  atc_sifra = models.CharField(max_length=7, null=True)  


  def ukupna_cijena(self):
    return self.kolicina * self.cijena 

  def valuta_text(self):
    return Valuta.objects.get(id=self.valuta).kratica
  
class NarudzbaRacun(models.Model):
  narudzba = models.ForeignKey(Narudzba, related_name='narudzba_racuni', null=True, blank=True)
  kreirao = models.ForeignKey(User, related_name='narudzba_racuni', null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)      
  modified = models.DateTimeField(auto_now=True)      
  storniran = models.BooleanField(default=0)          
  stornira_racun = models.ForeignKey('NarudzbaRacun', related_name='stornira', null=True, blank=True)
  zabiljezba = models.CharField(max_length=1024, blank=True, null=True) 
  broj = models.IntegerField(default=1, null=True, blank=True, db_index=True)
  mjesec = models.IntegerField(default=8, null=True, blank=True)
  godina = models.IntegerField(default=13, null=True, blank=True)

  def broj_racuna(self):
    return '%s%02d-%04d' % (str(self.created.year)[2:], self.created.month, self.broj)

class NarudzbaRacunStavka(models.Model):
  racun = models.ForeignKey(NarudzbaRacun, related_name='stavke', null=True, blank=True)
  naziv = models.CharField(max_length=96, blank=True, null=True)
  jedinicna_cijena = models.DecimalField(max_digits=12, decimal_places=2)
  valuta = models.IntegerField(default=1, null=True, blank=True)
  kolicina = models.IntegerField(null=True, blank=True)
  iznos = models.DecimalField(max_digits=12, decimal_places=2)

def GetEskulapPonuda(narudzba):
    ponuda = None
    rs = em.PonudeZ.objects.filter(narudzbaid=narudzba.broj)
    if rs.count() != 0:
        ponuda = rs[0]
    return ponuda

def IsSentToEskulap(narudzba):
    return 0 != em.PonudeZ.objects.filter(narudzbaid=narudzba.id).count()

def CreatePonuda(narudzba):
    ponuda = em.PonudeZ(\
            narudzbaid = narudzba.broj,
            datum = datetime.datetime.now(),
            kupacid = narudzba.klijent.id,
            kupac = narudzba.klijent.get_full_name(),
            adresa = narudzba.klijent.adresa,
            statuseskulap = 0,
            statusidema = 0)
    return ponuda

def GetKolicinaUPakiranju(nar_art):
    res = ''
    try:
        if 'Njemacka' == nar_art.trziste.naziv:
            res = nar_art.pakiranje
        else:
            ar = ArtikalDrugoTrziste.objects.get(ime=art_ime, trziste=trziste)
            res = ar.kolicina
    except:
        pass
    return res

def GetOrCreateEskulapArtikal(nar_art):
    pakiranje = GetKolicinaUPakiranju(nar_art)
    es_art, created = em.Artikal.objects.get_or_create(\
            naziv = nar_art.ime,
            pakiranje = pakiranje,
            trziste = nar_art.trziste.naziv)
    if created:
        es_art.mj = nar_art.jedinice
    return es_art, created

def CreateStavku(nar_art, es_art, rbr):
    cijena = nar_art.jedinicna_cijena_kn()
    pdv = get_pdv(atc_sifra=nar_art.atc_sifra)
    stavka = em.PonudeS(\
            rbr = rbr,
            artikalid = es_art.id, 
            trziste = nar_art.trziste.naziv,
            kolicina = nar_art.kolicina,
            mpcijena = cijena,
            pdv = pdv)
    return stavka

def HandleMailOrder(narudzba):
    if 1 == narudzba.status:
        narudzba.artikli.all().update(status=4)
        narudzba.status = 2
        narudzba.save()

@transaction.commit_on_success
def SendToEskulap(narudzba):
    if 'Konto 2' == narudzba.konto_name:
        HandleMailOrder(narudzba)
        return narudzba.broj
    ponuda = GetEskulapPonuda(narudzba)
    if None != ponuda:
        return ponuda.narudzbaid
    ponuda = CreatePonuda(narudzba)
    ponuda.save()
    for rbr, artikal in enumerate(narudzba.artikli.all(), 1):
        es_art, created = GetOrCreateEskulapArtikal(artikal)
        if created:
            es_art.save()
        stavka = CreateStavku(artikal, es_art, rbr)
        ponuda.stavke.add(stavka)
        stavka.save()
    ponuda.save()
    return ponuda.narudzbaid

def IsSentToEskulap(narudzba):
    ponuda = GetEskulapPonuda(narudzba)
    if None != ponuda:
        return True
    elif 'Konto 2' == narudzba.konto_name and 1 != narudzba.status:
        return True
    else:
        return False

