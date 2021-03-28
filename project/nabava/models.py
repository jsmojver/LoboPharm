from django.db import models, transaction
from project.common_models import AdminSetter
from order.models import NarucenArtikal, Narudzba
from eskulap import models as em

SI_NARUCENA = 1

# Create your models here.
    
class Konto(models.Model, AdminSetter):
    name = models.CharField(max_length=25, db_index=True)
    sifra = models.BigIntegerField(default=0)
    kontakt = models.CharField(max_length=96)

    class Meta:
        verbose_name_plural = 'Konta'
    
class Nabava(models.Model):
    konto = models.ForeignKey(Konto, related_name='nabave')

    created = models.DateTimeField(auto_now_add=True)     
    modified = models.DateTimeField(auto_now=True) 
    zabiljezba = models.CharField(max_length=512, blank=True, null=True) 

    class Meta:
        verbose_name_plural = 'Nabave'    
    
class NabavaItem(models.Model):
    nabava = models.ForeignKey(Nabava, related_name='itemi')
    artikal = models.ForeignKey(NarucenArtikal)

    zabiljezba = models.CharField(max_length=512, blank=True, null=True) 

    class Meta:
        verbose_name_plural = 'NabavaItemi'    

@transaction.commit_on_success
def SendNarucenoToEskulap(narudzba):
    em.PonudeZ.objects.filter(narudzbaid=narudzba.broj).update(statusidema=SI_NARUCENA)

def NaruciOdDobavljaca():
    # get all konta for which orders are pending
    nar_konta = Narudzba.objects.filter(models.Q(status = 2) | models.Q(status = 10)).order_by('konto_name').values('konto_name').distinct()
    for nk in nar_konta:
        # find konto with selected name
        try:
            konto = Konto.objects.get(name = nk['konto_name'])
            MakeNabava(konto)
        except:
            pass
    pass

def MakeNabava(konto):
    nabava = Nabava(konto=konto)
    nabava.save()
    narudzbe = Narudzba.objects.filter(models.Q(status = 2) | models.Q(status = 10), konto_name = konto.name)
    for n in narudzbe:
        for a in n.artikli.all():
            ni = NabavaItem(nabava=nabava, artikal=a)
            ni.save()
            a.status = 9
            a.save()
        n.status = 9
        n.save()
        SendNarucenoToEskulap(n)
    nabava.save()

