# coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings

from order.models import validate_iso7064
from order.models import *

from flib import *
import time, uuid, locale
from sysapp.constants import *
from sysapp.escpos import *

import time

import logging
logger = logging.getLogger(__name__)

# Create your models here.
 
# Todo: foreign key koji pridružuje narudžbi / artiklu s depoa
#       foreign key -> kupac? ili to preko narudžbe/artikla s depoa? možda bolje tako, ne unosi se kupac za baš svaki račun 

################### MODEL VALIDATORS #########################

def validate_jir(value):
  import re 
  if not re.match(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', value):
    raise ValidationError('JIR je neispravan, molimo provjerite!')

def validate_zki(value):
  import re 
  if not re.match(r'[a-f0-9]{32}', value):
    raise ValidationError('ZKI je neispravan, molimo provjerite!')
##############################################################

class RadnoMjesto(models.Model):
  ip = models.IPAddressField()
  oznaka = models.CharField(max_length=64)
  djelatnik = models.ForeignKey(User, related_name='radnomjesto', null=True, blank=True)

class Racun(models.Model):
  id = models.IntegerField(primary_key=True) # Mora se eksplicitno navesti, inače ne radi ručno postavljanje ID-a u M2Nr i nastanu problemi
  djelatnik = models.ForeignKey(User, related_name='racuni', null=True, blank=True)
  narudzba = models.ForeignKey(Narudzba, related_name='racuni', null=True, blank=True)
  iznos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  datum_vrijeme_racun = models.CharField(max_length=32, blank=True, null=True) # Datum i vrijeme IZDAVANJA, vrijeme SLANJA se ionako bilježi u porukama itd 
  datum_vrijeme_zastitni = models.CharField(max_length=32, blank=True, null=True) # Datum i vrijeme IZDAVANJA
  http_status = models.CharField(max_length=64, blank=True, null=True)
  naplatni_uredjaj = models.CharField(max_length=32, blank=True, null=True)
  naknadno_dostavljen = models.BooleanField(default=0)
  fiskaliziran = models.BooleanField(default=0)
  problem = models.BooleanField(default=0)
  storno = models.BooleanField(default=0)  
  stornira_racun = models.OneToOneField('self', blank=True, null=True)
  uuid = models.CharField(max_length=64, blank=True, null=True)
  jir = models.CharField(max_length=64, blank=True, null=True, validators=[validate_jir,])
  zastitni_kod = models.CharField(max_length=64, blank=True, null=True, validators=[validate_zki,])
  nacin_placanja = models.CharField(max_length=2, blank=True, null=True)
  oib_operatera = models.CharField(max_length=32, blank=True, null=True, validators=[validate_iso7064,])
  oznaka_operatera = models.CharField(max_length=64, blank=True, null=True)
  oib_obveznika = models.CharField(max_length=32, blank=True, null=True, validators=[validate_iso7064,])
  oznaka_poslovnog_prostora = models.CharField(max_length=32, blank=True, null=True)
  poruka_zahtjev = models.CharField(max_length=8192, blank=True, null=True)
  poruka_odgovor = models.CharField(max_length=8192, blank=True, null=True)  
  
#  poruka_potpis = models.CharField(max_length=8192, blank=True, null=True)
  created = models.DateTimeField(auto_now_add=True)     # kad je dodan u narudžbu
  modified = models.DateTimeField(auto_now=True)   # kad je dodan u narudžbu
  napomena = models.CharField(max_length=2048, blank=True, null=True)
  
  def get_absolute_url(self):
    return reverse('fiskalizacija.racun.detalji', args=[self.id])

  class Meta:
    get_latest_by = 'id'
    ordering = ['-id']
#  -> onda možeš dohvaćati po Racun.objects.filter(storno=False).latest()
# todo - dodati polja datetime (pravi datetime), uredno_dostavljen flag za filtriranje itd. postaviti index na nešto

  def fiskaliziraj(self):
    if hasattr(self, 'fiskalizacija'): return

    self.fiskalizacija = Fiskalizacija() # objekt iz biblioteke za fiskalizaciju flib
     
   # <test> #
    self.oib_obveznika = settings.OIB_OBVEZNIKA 
    self.oib_operatera = self.djelatnik.userprofile.oib
    self.oznaka_poslovnog_prostora = settings.POSLOVNI_PROSTOR 
    self.naplatni_uredjaj = self.djelatnik.userprofile.oznaka_naplatnog_uredjaja 
    self.nacin_placanja = 'G' # TODO: dodati podršku za ostale načine plaćanja
   # </test> #
    
    self.fiskalizacija.racun.Oib = self.oib_obveznika
    self.fiskalizacija.racun.USustPdv = 'true'
    self.fiskalizacija.racun.DatVrijeme = self.datum_vrijeme_racun
    
    self.fiskalizacija.racun.OznSlijed = 'P'
    self.fiskalizacija.racun.BrRac.BrOznRac = self.id
    self.fiskalizacija.racun.BrRac.OznPosPr = self.oznaka_poslovnog_prostora
    self.fiskalizacija.racun.BrRac.OznNapUr = self.naplatni_uredjaj

    for i in self.porezi.all():    
      self.fiskalizacija.porez = self.fiskalizacija.client2.factory.create('tns:Porez')
      self.fiskalizacija.porez.Stopa = i.stopa
      self.fiskalizacija.porez.Osnovica = i.osnovica
      self.fiskalizacija.porez.Iznos = i.iznos
      self.fiskalizacija.racun.Pdv.Porez.append(self.fiskalizacija.porez)

    self.fiskalizacija.racun.IznosUkupno = '%.2f' % self.iznos
    self.fiskalizacija.racun.NacinPlac = self.nacin_placanja
    self.fiskalizacija.racun.OibOper = self.oib_operatera

    if self.naknadno_dostavljen: self.fiskalizacija.racun.NakDost = 'true'
    else: self.fiskalizacija.racun.NakDost = 'false'

    self.fiskalizacija.izracunaj_zastitni_kod(self.datum_vrijeme_zastitni) # Pazi, ovo se pri svakom slanju računa
    self.zastitni_kod = self.fiskalizacija.racun.ZastKod
    
    # self.poruka_zahtjev = self.fiskalizacija.generiraj_poruku()
    self.save()
  
  def __init__(self, *args, **kwargs):
    super(Racun, self).__init__(*args, **kwargs) 
    if not self.fiskaliziran:
      t = time.localtime()                # Vidi jel vrijeme lokalno ili UTC !!!
      self.uuid = str(uuid.uuid4())	  # TODO: Ovo nije dobro, ne treba se pamtiti kao sveto pismo nego to pisati u racunlog a uuid svaki put drugi!
				          # moze u bazu racun zadnji uuid koji je prosao, inace u racunlog trpati uuid!!
      try: self.id = Racun.objects.latest().id + 1
      except: self.id = settings.POCETNI_BROJ_RACUNA 
      self.fiskaliziran = 1    
      self.datum_vrijeme_racun = '%02d.%02d.%02dT%02d:%02d:%02d' % (t.tm_mday, t.tm_mon, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec)
      self.datum_vrijeme_zastitni = '%02d.%02d.%02d %02d:%02d:%02d' % (t.tm_mday, t.tm_mon, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec)                 
      # prije spremanja mora se provjeriti ima li sve kritične stavke!
      self.save()    

  def posalji(self):
    if not hasattr(self, 'fiskalizacija'): self.fiskaliziraj()
    # Tu dodati timing da mjeri koliko traje iduca linija i nek se zapise u racunlog
    self.uuid = str(uuid.uuid4()) # zapisat ćemo uuid tu i u racunlog, ako sve prođe okej i ne pukne do kraja zapisat će se i u bazu kao self.save() i tako ostati - OK
    self.fiskalizacija.zaglavlje.IdPoruke = self.uuid
    t=time.localtime() 				# dohvati trenutno vrijeme slanja
    self.fiskalizacija.zaglavlje.DatumVrijeme = '%02d.%02d.%02dT%02d:%02d:%02d' % (t.tm_mday, t.tm_mon, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec)

    if abs(time.mktime(t)-time.mktime(time.strptime(self.datum_vrijeme_zastitni, '%d.%m.%Y %H:%M:%S'))) < 5: # <5 sec razlike od izdavanja do slanja, pošalji ih ISTE
      self.fiskalizacija.zaglavlje.DatumVrijeme = self.datum_vrijeme_racun # ako je < 5 sec, izvadi vrijeme iz ZKI pa to pošalji

    if not self.oznaka_operatera: self.oznaka_operatera = self.djelatnik.userprofile.oznaka_operatera
    self.save()


    start_time = time.time()
    self.fiskalizacija.odgovor = self.fiskalizacija.posalji()
    exec_time = '%.3f' % float(time.time() - start_time)
    rl = RacunLog(tip=1, racun=self, uuid=self.uuid, trajanje=exec_time, poruka_zahtjev=self.fiskalizacija.generiraj_poruku(), vrijeme_slanja=self.fiskalizacija.zaglavlje.DatumVrijeme)
    rl.save()

    try: 
      response = self.fiskalizacija.odgovor[1]
      try: self.jir = response.Jir      
      except AttributeError: pass

      if not self.oznaka_operatera: self.oznaka_operatera = self.djelatnik.userprofile.oznaka_operatera
      rl.http_status=self.fiskalizacija.odgovor[0]
      rl.poruka_odgovor=str(self.fiskalizacija.potpisPlugin.poruka_odgovor) + '\n\n' + str(response)
      rl.signature_valid = self.fiskalizacija.potpisPlugin.valid_signature
      rl.digest = response.Signature.SignedInfo.Reference[0].DigestValue
      rl.signature = response.Signature.SignatureValue
      rl.save()
    except: pass
    self.save()
 
  def oznaka_racuna(self):
    return '%s-%s-%s' % (self.id, self.oznaka_poslovnog_prostora, self.naplatni_uredjaj)

  def render(self):
    p = "\x1b\x40" # init string, s tim pocinjemo
    p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x22\x01\x01'  # Ispisi logo u memoriji (32,34) - hex \x20\x22 (da ide brze)
    p += '\x1b\x74\x12\n' + TXT_ALIGN_CT + TXT_NORMAL # Centralno poravnanje
    p += TXT_ALIGN_CT + TXT_BOLD_ON + TXT_2HEIGHT + to852('- R A Č U N -') + TXT_NORMAL + TXT_ALIGN_CT + '\n\nbroj ' + TXT_UNDERL_ON + str(self.oznaka_racuna()) + TXT_NORMAL

    p += ('\n\nDatum i vrijeme: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n' % self.datum_vrijeme_zastitni).decode('utf-8').encode('cp852')
    p += to852('ZKI: %s\n\n' % self.zastitni_kod)

    p += '\x1b\x21\x01' # Promijeni font u B
    p += '\x1b\x45\x01' + '{:<31}'.format('Naziv proizvoda') + '{:>5}'.format('Kol') + '{:>10}'.format('Cijena') + '{:>10}'.format('Iznos') + '\x1b\x45\x00\n'
    p += '\x1b\x21\x00' # Promijeni font u A
    for i in range(42): p += '\xcd' # Dvostruka linija
    p += '\n\x1b\x21\x01' # Promijeni font u B
   
    for i in self.stavke.all():
      p += '{:<31}'.format(i.naziv[:31]) + '{:>5}'.format(i.kolicina) + '{:>10}'.format(i.cijena) + '{:>10}'.format(i.iznos)  + '\n'
    
    p += '\x1b\x21\x00'
    for i in range(42): p += '\xcd' # Dvostruka linija
    p += '\n' + TXT_2WIDTH + TXT_ALIGN_RT +'UKUPNO: %s KN  \n\n' % self.iznos + TXT_ALIGN_CT + TXT_NORMAL
    djelatnik = self.djelatnik.get_full_name()
    
    p += TXT_ALIGN_CT + '\x1b\x45\x01\x1b\x2d\x01              Obračun poreza              \x1b\x2d\x00\x1b\x45\x00\n\n'.decode('utf-8').encode('cp852')
    p += '\x1b\x21\x01' # Promijeni font u B
    p += '\x1b\x45\x01' + '{:<15}'.format('Vrsta poreza') + '{:<10}'.format('Stopa') + '{:>15}'.format('Osnovica') + '{:>16}'.format('Iznos') + '\x1b\x45\x00\n'
    for i in self.porezi.all():
      p += '{:<15}'.format('PDV') + '{:<10}'.format(i.stopa) + '{:>15}'.format(i.osnovica) + '{:>16}'.format(i.iznos)  + '\n'   
    p += '\x1b\x21\x00' # Vrati font u A

    try:
      validate_jir(str(self.jir))
      p += '\nJIR: ' + TXT_BOLD_ON + to852(self.jir) + TXT_BOLD_OFF
    except ValidationError:
      p += to852('\nJIR: Nije moguće dohvatiti JIR\nRazlog: Internet veza u prekidu')

    #p += '\n\x1d\x68\x50\x1d\x48\x00\x1d\x6b\x02'
    #p += '14%s\x00' % self.id
    p += to852('\n\n Račun izdao: %s') % to852(self.oznaka_operatera)
    p += to852('\nNačin plaćanja: Novčanice \n\n')
    p += TXT_ALIGN_CT + '** Hvala na povjerenju! **'
    p += '\n\n\n\n\n\n' + PAPER_FULL_CUT

    return p

  def convert_zki_time(self):
    """ Dohvaća vrijeme u ZKI formatu (bez T) i pretvara ga u format sa T """
    return '%sT%s' % (self.datum_vrijeme_zastitni[:10], self.datum_vrijeme_zastitni[11:])

  def izracunaj_zki(self):
    return zkicalc([self.oib_obveznika, self.datum_vrijeme_racun, self.id, self.oznaka_poslovnog_prostora, self.naplatni_uredjaj, self.iznos])

  def suma_stavki(self):
    return sum([i.iznos for i in self.stavke.all()])
  
class RacunStavka(models.Model):
  racun = models.ForeignKey(Racun, related_name='stavke', null=True, blank=True)
  iznos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  kolicina = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  cijena = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  naziv = models.CharField(max_length=256, blank=True, null=True)

class RacunLog(models.Model):
  TIP_PORUKE = {1: 'Odlazna', 2: 'Naknadna dostava', 3: 'Greška'}

  vrijeme = models.DateTimeField(auto_now_add=True, blank=True)
  racun = models.ForeignKey(Racun, related_name='log', null=True, blank=True)
  uuid = models.CharField(max_length=64, blank=True, null=True)           # -> Zaglavlje koje se mijenja!
  vrijeme_slanja = models.CharField(max_length=64, blank=True, null=True) # -> Zaglavlje
  http_status = models.CharField(max_length=16, blank=True, null=True)
  tip = models.IntegerField(default=1)
  poruka_zahtjev = models.CharField(max_length=8192, blank=True, null=True)
  poruka_odgovor = models.CharField(max_length=10192, blank=True, null=True)
  digest = models.CharField(max_length=128, blank=True, null=True)
  signature = models.CharField(max_length=1024, blank=True, null=True)
  keyinfo = models.CharField(max_length=2048, blank=True, null=True)
  trajanje = models.CharField(max_length=32, blank=True, null=True)
  signature_valid = models.BooleanField(default=0)

  def tip_hr(self):
    return self.TIP_PORUKE[self.tip]
  
class RacunPorez(models.Model):
  racun = models.ForeignKey(Racun, related_name='porezi', null=True, blank=True) # Ne bi li ovo trebalo biti vezano na stavke? svaka može imati drugu poreznu stopu? NE, dvije stavke mogu imati istu, a ovo je suma sumarum za račun po kategorijama poreza
  stopa = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  osnovica = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  iznos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  # A naziv poreza? Zasad je samo PDV, ok.

  def naziv(self): # TODO: ovo je Privremeno!
    return 'PDV'

  def ukupno(self):
    return self.osnovica + self.iznos

class PoslovniProstorPoruka(models.Model): # TODO: Rijesi unique UUID i za poslovni prostor!

  oib_tvrtke = models.CharField(max_length=32, blank=True, null=True, validators=[validate_iso7064,])
  oib_odgovornog = models.CharField(max_length=32, blank=True, null=True, validators=[validate_iso7064,])
  oznaka_poslovnog_prostora = models.CharField(max_length=64, blank=True, null=True)
  radno_vrijeme = models.CharField(max_length=1024, blank=True, null=True)
  datum_pocetka_primjene = models.CharField(max_length=64, blank=True, null=True)
  ulica = models.CharField(max_length=64, blank=True, null=True)
  kucni_broj = models.CharField(max_length=64, blank=True, null=True)
  broj_poste = models.CharField(max_length=64, blank=True, null=True)
  naselje = models.CharField(max_length=64, blank=True, null=True)
  opcina = models.CharField(max_length=64, blank=True, null=True)
  datum_vrijeme = models.CharField(max_length=64, blank=True, null=True)
  uuid = models.CharField(max_length=64, blank=True, null=True)
  http_status = models.CharField(max_length=64, blank=True, null=True)
  fiskaliziran = models.BooleanField(default=0)
  poruka_zahtjev = models.CharField(max_length=8192, blank=True, null=True)
  poruka_odgovor = models.CharField(max_length=10192, blank=True, null=True)
 
  signature_valid = models.BooleanField(default=0)

  class Meta:
    ordering = ['-id']

  def get_absolute_url(self):
    return reverse('fiskalizacija.pp.view', args=[self.id])
  
  def fiskaliziraj(self):
    self.fiskalizacija = Fiskalizacija()
    
    t = time.localtime()
    self.uuid = str(uuid.uuid4()) # TODO: ovo mora biti JEDINSTVENO pri svakom slanju
    self.fiskaliziran = 1
    self.datum_vrijeme = '%02d.%02d.%02dT%02d:%02d:%02d' % (t.tm_mday, t.tm_mon, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec)
    
    self.pp = self.fiskalizacija.client2.factory.create('tns:PoslovniProstor')
    self.pp.Oib = self.oib_tvrtke
    self.pp.OznPoslProstora = self.oznaka_poslovnog_prostora
    self.pp.RadnoVrijeme = self.radno_vrijeme
    self.pp.DatumPocetkaPrimjene = self.datum_pocetka_primjene
    self.pp.SpecNamj = self.oib_odgovornog
    adresa = self.fiskalizacija.client2.factory.create('tns:Adresa')
    adresni_podatak = self.fiskalizacija.client2.factory.create('tns:AdresniPodatakType')

    self.fiskalizacija.zaglavlje.DatumVrijeme = self.datum_vrijeme
    self.fiskalizacija.zaglavlje.IdPoruke = self.uuid

    adresa.Ulica = self.ulica
    adresa.KucniBroj = self.kucni_broj
    adresa.BrojPoste = self.broj_poste
    adresa.Naselje = self.naselje
    adresa.Opcina = self.opcina

    self.pp.AdresniPodatak = adresni_podatak
    adresni_podatak.Adresa = adresa

    self.pp.__delattr__('OznakaZatvaranja')

  def posalji(self):
    self.fiskalizacija.odgovor = self.fiskalizacija.client2.service.poslovniProstor(self.fiskalizacija.zaglavlje, self.pp)
    self.poruka_zahtjev =  self.fiskalizacija.client2.last_sent().str()
    self.poruka_odgovor = str(self.fiskalizacija.odgovor)
    self.signature_valid = self.fiskalizacija.potpisPlugin.valid_signature
    self.save()
    # except: pass # TODO: pametniji error handling

  def test(self):
    self.oib_tvrtke = '12746672508'
    self.oznaka_poslovnog_prostora = 'Poslovnica1'
    self.radno_vrijeme = 'Pon-Pet: 08:00-19:00, Sub:08:00-14:00'
    self.datum_pocetka_primjene = '01.04.2012'
    self.oib_odgovornog = '12746672508'
    self.ulica = 'Trg Testiranja'
    self.kucni_broj = '1'
    self.broj_poste = '10000'
    self.naselje = 'Zagreb'
    self.opcina = 'Zagreb'

  def __init__(self, *args, **kwargs):
    super(PoslovniProstorPoruka, self).__init__(*args, **kwargs)

class PoslovniProstorPorukaForm(ModelForm):
  """
  Automatski generira formu za poslovni prostor
  """
  class Meta:
    model = PoslovniProstorPoruka
    exclude = ('datum_vrijeme', 'uuid', 'poruka_zahtjev', 'poruka_odgovor', 'http_status', 'signature_valid',)  
    widgets = {
            'radno_vrijeme': Textarea(attrs={'cols': 20, 'rows': 10}),
            'fiskaliziran': HiddenInput(attrs={'value': 1}),
        }

class RacunForm(ModelForm):
  """
  Automatski generira formu za izdavanje računa (stare narudžbe)
  """
  class Meta:
    model = Racun
#    exclude = ('narudzba', 'datum_vrijeme_zastitni', 'datum_vrijeme_racun', 'http_status', 'naknadno_dostavljen', 'problem', 'storno', 'djelatnik', 'uuid', 'poruka_zahtjev', 'poruka_odgovor', 'jir', 'zastitni_kod', 'id',)  
    fields = ('napomena', 'iznos',)
    widgets = {
            'napomena': Textarea(attrs={'cols': 20, 'rows': 10}),
            'fiskaliziran': HiddenInput(attrs={'value': 1}),
        }
