#coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from stdnum.iso7064 import mod_11_10 
from django.forms import ModelForm, Textarea, HiddenInput
from django.core.urlresolvers import reverse



def validate_iso7064(value):
  from django.core.validators import ValidationError
  if not mod_11_10.is_valid(value) and value:
    raise ValidationError('Broj je neispravan, molimo provjerite!')




class Temperatura(models.Model):
  timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
  senzor1 = models.FloatField(blank=True, null=True)
  senzor2 = models.FloatField(blank=True, null=True)

class StatusVeze(models.Model):
  cis = models.BooleanField()
  net = models.BooleanField()
  vpn = models.BooleanField()

class UserProfile(models.Model):  
    user = models.OneToOneField(User)  
    

    oib = models.CharField(max_length=64, null=True, blank=True, validators=[validate_iso7064,])
    oznaka_operatera = models.CharField(max_length=64, null=True, blank=True)
    ip = models.IPAddressField(max_length=64, null=True, blank=True)
    oznaka_naplatnog_uredjaja = models.CharField(max_length=64, null=True, blank=True)
    odjel = models.CharField(max_length=64, null=True, blank=True)
    nove_poruke = models.BooleanField(default=0) 
    izdaje = models.BooleanField(default=0) 
 
    def __str__(self):  
          return "%s" % self.user.get_full_name().encode('utf-8') 
 
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  
 
post_save.connect(create_user_profile, sender=User) 
 
User.profile = property(lambda u: u.get_profile() )


class LoginImage(models.Model):
  user = models.ForeignKey(User)
  password = models.CharField(max_length=128, null=True, blank=True)
  image = models.TextField(null=True,blank=True)
  created = models.DateTimeField(auto_now_add=True)

  def getpng(self):
    return u'<img src="%s" />' % self.image
 
  getpng.allow_tags = True


class InstantMsg(models.Model):
   
  system = models.BooleanField(default=0) 
  broadcast = models.BooleanField(default=0) 
  fetched = models.BooleanField(default=0) 

  msgtype = models.IntegerField(default=0) 
  javascript = models.CharField(max_length=8192, null=True, blank=True) 

  recipient = models.ForeignKey(User, null=True, blank=True, related_name='primljene_poruke')
  sender = models.ForeignKey(User, null=True, blank=True, related_name='poslane_poruke')
   
  naslov = models.CharField(max_length=64, null=True, blank=True)
  sadrzaj = models.CharField(max_length=512, null=True, blank=True)

  def get_absolute_url(self):
    return reverse('sysapp.message.send')                 

class InstantMsgForm(ModelForm):
  class Meta:
    model = InstantMsg
    exclude = ('system', 'fetched', 'msgtype', 'javascript', 'sender',)  
    widgets = {               



      }  

class ObavijestiPost(models.Model):
  created = models.DateTimeField(auto_now_add=True)
  title = models.CharField(max_length=60)
  body = models.TextField()

  def __unicode__(self):
    return self.title

class Ticket(models.Model):
  statusi = {0: 'Otvoreno', 1: 'U postupku', 2: 'Riješeno'}
  status = models.IntegerField(default=0) 
  autor = models.ForeignKey(User, null=True, blank=True, related_name='tickets')
  naslov = models.CharField(max_length=60, blank=True, null=True)
  sadrzaj = models.TextField(blank=True, null=True)
  created = models.DateTimeField(auto_now_add=True)
  
  class Meta:  
    ordering = ['-created']
  
  def get_absolute_url(self):
    return reverse('sysapp.ticket.list')                 

  def get_status(self):
    return self.statusi[self.status]
  
class TicketForm(ModelForm):
  class Meta:
    model = Ticket
    exclude = ('status', 'created',)
    widgets = {
           'sadrzaj': Textarea(attrs={'cols': 20, 'rows': 50}),
           'autor': HiddenInput(attrs={'value': ''}),
      }



