# coding=utf-8


from django.db import models
from django.forms import ModelForm
from django.db.models import Sum
from django.contrib.auth.models import User
from order.models import *
from django.core.urlresolvers import reverse
from project.common_models import AdminSetter


class Depo(models.Model):
  naziv = models.CharField(max_length=64)
  transport = models.BooleanField(default=1)
  def __unicode__(self): return self.naziv
  
  class Meta:
    verbose_name_plural = 'Depoi'



class Lijek(models.Model, AdminSetter):
  naziv = models.CharField(max_length=256)
  cijena = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
  depo = models.ForeignKey(Depo, related_name='lijekovi')
  stanje = models.PositiveIntegerField(null=True, blank=True)
  min_stanje = models.PositiveIntegerField(null=True, blank=True)
  
  ukupni_ulaz = models.IntegerField(blank=True, null=True)
  broj_dana = models.IntegerField(blank=True, null=True) 
  mjesecna_potrosnja = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  
  ukupna_zarada = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
  mjesecna_zarada = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
  nabavna_cijena_eur = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)

  
  def __unicode__(self): return self.naziv

  class Meta:
    verbose_name_plural = 'Lijekovi'
    ordering = ['naziv']   

  def ima_dovoljno(self):
    if self.stanje - self.min_stanje > 0: return 1
    else: return 0     
    
  def ima_za_dana(self): 
    try: return "%.2f" % (self.stanje*25/self.mjesecna_potrosnja)
    except: return 0
    
  def preporucena_zaliha(self): 
    return "%d" % (self.mjesecna_potrosnja / 3)
    
  def ima_prosjecno(self):
    try: return self.ukupni_ulaz / (self.broj_dana / 30)
    except: return 0
    
  def prosjecno_previse(self):
    return (self.ima_prosjecno() - self.min_stanje) * self.cijena

  def get_absolute_url(self):
    return reverse('lijekovi.list.sort', args=['asc','naziv'])
 
  def stanje_kutija(self):
    return PosiljkaLijekKutija.objects.filter(status=0, depo_lijek=self).count()
 
  def azuriraj_stanje(self):
    self.stanje = PosiljkaLijekKutija.objects.filter(status=0, depo_lijek=self).count()
    self.save()
 
  

class LijekForm(ModelForm):
  class Meta:
    model = Lijek
    exclude = ('stanje', 'ukupni_ulaz', 'broj_dana', 'mjesecna_potrosnja', 'ukupna_zarada', 'mjesecna_zarada',)
    

class Posiljka(models.Model):
  datum = models.DateTimeField(auto_now_add=True)

  zaduzio = models.ForeignKey(User)
  locked = models.BooleanField(default=0)
  
  def vrijednost(self): 
    return sum([i['kolicina']*i['lijek__cijena'] for i in self.lijekovi.values('lijek__cijena', 'kolicina')])
 
  def broj_artikala(self): 
    return PosiljkaLijek.objects.filter(posiljka=self.id).aggregate(Sum('kolicina'))['kolicina__sum']
    
  def broj_kodova(self):
    
    return self.kutije_depo_lijekova.count() 
    
  def kodirano(self):
    if self.broj_artikala() == self.broj_kodova(): return 'Da'
    else: return 'Ne'
      
  def kodiraj(self):
    for i in self.lijekovi.all():
      i.kodiraj()
  
def validate_kolicina(value):
  from django.core.validators import ValidationError
  
  if not value > 0:
    raise ValidationError('Količina mora biti pozitivna, molimo provjerite!')
   
class PosiljkaLijek(models.Model):
  lijek = models.ForeignKey(Lijek, related_name='depo_posiljka_lijekovi')
  kolicina = models.IntegerField(validators=[validate_kolicina,])
  posiljka = models.ForeignKey(Posiljka, related_name='lijekovi')

  def ukupno(self):
    return self.kolicina * self.lijek.cijena
       
  def kodiraj(self):
    a = self.kolicina - self.kutije_depo_lijekova.count()
    if a>0:
      for i in range(a):
        for i in range(10): 
          try: b = PosiljkaLijekKutija(lijek=self, posiljka=self.posiljka, depo_lijek=self.lijek, naziv=self.lijek.naziv, cijena=self.lijek.cijena, status=9)
          except ValueError: pass
          else: break          
        b.save()                 
         
         
                 
  def get_absolute_url(self):
    return reverse('depo.posiljka.lijek.add')                 
                 
  class Meta:
    verbose_name_plural = 'Lijekovi u pošiljci (DEPO)'
    ordering = ['lijek__naziv',]

  def save(self, *args, **kwargs):    
    super(PosiljkaLijek, self).save(*args, **kwargs)    

    
    
    
  def __init__(self, *args, **kwargs):
    super(PosiljkaLijek, self).__init__(*args, **kwargs) 
    if self.id == None:
      try: self.posiljka = Posiljka.objects.filter(locked=0).latest('id') 
      except: pass 

class PosiljkaLijekForm(ModelForm):
  class Meta:
    model = PosiljkaLijek
    exclude = ('posiljka',)    
    widgets = {               
          'lijek': TextInput(attrs={'class': 'autocomplete', 'autofocus': 'autofocus', 'data-autocomplete-url': '/autocomplete'}),               
      }      
    
class PosiljkaLijekKutija(models.Model):
  STATUS = (
        (0, 'Na stanju'),
        (1, 'Izdan sa skladišta'),
        (2, 'Preuzet u prodaji'),
        (3, 'Povrat na skladište'),
        (4, 'Isporučen kupcu'),        
        (5, 'Razbijen'),
        (6, 'Oštećena ambalaža'),
        (7, 'Istek roka'),
        (8, 'Povrat dobavljaču'),
        (9, 'Dodavanje pošiljke'), 
  )
  lijek = models.ForeignKey(PosiljkaLijek, related_name='kutije_depo_lijekova', db_index=True)  
  posiljka = models.ForeignKey(Posiljka, related_name='kutije_depo_lijekova', db_index=True) 
  depo_lijek = models.ForeignKey(Lijek, related_name='kutije_depo_lijekova', db_index=True)
  id = models.BigIntegerField(db_index=True, primary_key=True, unique=True)  
  created = models.DateTimeField(auto_now_add=True)   
  modified = models.DateTimeField(auto_now=True)     
  status = models.IntegerField(choices=STATUS)   
  user = models.ForeignKey(User, related_name='kutije_depo_lijekova', null=True, blank=True) 
  inventura = models.BooleanField(default=0)
  printed = models.BooleanField(default=0)
  
  naziv = models.CharField(max_length=256, blank=True, null=True)
  cijena = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
  
  
  locked = models.IntegerField(default=0)
  

  def save(self, *args, **kwargs): 
    super(PosiljkaLijekKutija, self).save(*args, **kwargs)    
    self.depo_lijek.azuriraj_stanje() 
    
  def __init__(self, *args, **kwargs):
    super(PosiljkaLijekKutija, self).__init__(*args, **kwargs) 
    if self.id == None:
      from random import randint
      self.id = randint(10**9,10**10-1)
      if PosiljkaLijekKutija.objects.filter(id=self.id).count():
        raise ValueError('Već postoji taj kod u bazi podataka')

  def ime_statusa(self):
    return self.STATUS[self.status][1]
  
  def last_event(self):
    return self.events.latest('modified')
  
  class Meta:
    verbose_name_plural = 'Kutije lijeka u pošiljci'
    ordering = ['id',]
    
class LijekKutijaEvents(models.Model):
  TIP_DOGADAJA = (
        (0, 'Zaprimljen na skladište'),
        (1, 'Izdan sa skladišta'),
        (2, 'Preuzet u prodaji'),        
        (3, 'Povrat na skladište'),
        (4, 'Isporučen kupcu'),
        (5, 'Razbijen'),
        (6, 'Oštećena ambalaža'),
        (7, 'Istek roka'),
        (8, 'Povrat dobavljaču'),
        (9, 'Ispisana naljepnica'),
        (10, 'Dodan u bazu'),        
  )
  kutija = models.ForeignKey(PosiljkaLijekKutija, related_name='events')
  user = models.ForeignKey(User, related_name='events')  
  vanredni = models.BooleanField() 
  created = models.DateTimeField(auto_now_add=True)   
  modified = models.DateTimeField(auto_now=True)     
  vrsta = models.IntegerField(choices=TIP_DOGADAJA)
  

  def ime_statusa(self):
    return self.TIP_DOGADAJA[self.vrsta][1]

  class Meta:
    verbose_name_plural = 'Operacije nad artiklima'
    ordering = ['modified',]
    


class Inventura(models.Model):
  created = models.DateTimeField(auto_now_add=True)      
  modified = models.DateTimeField(auto_now=True)        
  vrsta = models.IntegerField(default=0) 
  user = models.ForeignKey(User, related_name='inventure')
  status = models.IntegerField(default=0) 

  def sve_stima(self): 
    pass
  
  def save(self, *args, **kwargs):    
    super(Inventura, self).save(*args, **kwargs)    
    PosiljkaLijekKutija.objects.filter(status=0).update(inventura=0) 
  
  def nedostaje(self):
    return self.kutije.filter(nedostaje=1).count()
  
  def na_stanju(self):
    return self.kutije.filter(nedostaje=0).count()
  
  def ukupno(self):
    return self.kutije.all().count()
  
  def steta(self):
    return sum([i.kutija.lijek.lijek.cijena for i in self.kutije.filter(nedostaje=1)])        
  
  
  
    
class InventuraKutija(models.Model):
  inventura = models.ForeignKey(Inventura, related_name='kutije', db_index=True)
  kutija = models.ForeignKey(PosiljkaLijekKutija, related_name='kutije')
  created = models.DateTimeField(auto_now_add=True)      
  modified = models.DateTimeField(auto_now=True)        
  status = models.IntegerField()
  nedostaje = models.BooleanField(default=0)
  
  class Meta:
    unique_together=(("inventura", "kutija"),)


class Zahtjev(models.Model):
  STATUS_ZAHTJEVA = (
        (0, 'Zatražen'),
        (1, 'U postupku'),
        (2, 'Proveden'),
        (3, 'Povrat na skladište'),
        (4, 'Isporučen'),        
        (5, 'Odbijeno'),
        (6, 'Storniran'),        
  )
  lijek = models.ForeignKey(Lijek, related_name='zahtjevi') 
  kolicina = models.PositiveIntegerField(verbose_name="Količina", validators=[validate_kolicina,])  
  user = models.ForeignKey(User, related_name='zahtjevi')         
  status = models.IntegerField(choices=STATUS_ZAHTJEVA, default=0)   
  created = models.DateTimeField(auto_now_add=True)   
  modified = models.DateTimeField(auto_now=True)   
  fetched = models.BooleanField(default=0)     
  zabiljezba = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Zabilježba") 
  narucenartikal = models.ForeignKey(NarucenArtikal, related_name='zahtjevi', blank=True, null=True) 
  narudzba = models.ForeignKey(Narudzba, related_name='zahtjevi', blank=True, null=True) 

  class Meta:    
    verbose_name_plural = 'Zahtjevi'
    ordering = ['-modified']

  def ukupna_cijena(self):
    return self.kolicina * self.lijek.cijena

  def status_tekst(self):
    return self.STATUS_ZAHTJEVA[self.status][1]

  def get_absolute_url(self):
    return reverse('depo.zahtjev.izdavanje')
  
class ZahtjevForm(ModelForm):
  class Meta:
    model = Zahtjev
    exclude = ('user', 'status', 'created', 'modified', 'fetched', 'narudzba', 'narucenartikal',)  
    widgets = {               
          'lijek': TextInput(attrs={'class': 'autocomplete', 'autofocus': 'autofocus', 'data-autocomplete-url': '/autocomplete', 'data-autocomplete-callback': 'na_stanju_izdavanje(ui.item.id)'}),     
          'zabiljezba': Textarea(attrs={'cols': 20, 'rows': 10}),
          'tip_klijenta': HiddenInput(attrs={'value': 2}),
      }  



class Stavka(models.Model): 
  artikal = models.ForeignKey(Lijek, related_name='stavke', blank=True, null=True)
  kolicina = models.IntegerField()
  user = models.ForeignKey(User, related_name='depo_stavke')
  
  created = models.DateTimeField()   
  modified = models.DateTimeField(auto_now=True)   
  visible = models.BooleanField()
  locked = models.BooleanField()
  zabiljezba = models.CharField(max_length=1024, blank=True, null=True)

  class Meta:
    verbose_name_plural = 'Stavke'
    ordering = ['-modified']
    

class LogStavke(models.Model): 
  stavka = models.ForeignKey(Stavka, related_name='log')
  user = models.ForeignKey(User, related_name='log')
  event = models.IntegerField()
  datetime = models.DateTimeField(auto_now_add=True)
  
  

