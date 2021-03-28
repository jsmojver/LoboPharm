#coding=utf-8



from constants import *
from time import strftime
import locale, serial

def debug_barcode_print(barcode):
  return '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02%s\x00\x0a\n\n\n' % (barcode)

def to852(instring):
  return instring.decode('utf-8').encode('cp852')
  
def generiraj_potvrdu(narucitelj, datum, lijekovi, polog, sluzbenik, barcode):
  

  EUR = '\x1b\x74\x10\x80\x1b\x74\x12'

  p = "\x1b\x40" 

  p += '\x1c\x70\x01\x00'  
  p += '\x1b\x74\x12' 
  p += TXT_ALIGN_CT + TXT_NORMAL 
  p += strftime("%A, %d. %B %Y.  %H:%M:%S").decode('utf-8').encode('cp852') + '\n' 

  p += TXT_ALIGN_CT + TXT_2HEIGHT
  p += '\n\x1b\x45\x01- P O T V R D A -\x1b\x45\x00\n\n'
  p += TXT_NORMAL + TXT_ALIGN_CT
  tmp = 'Naručitelj: \x1b\x45\x01\x1b\x2d\x01 %s \x1b\x2d\x00\x1b\x45\x00\n' % narucitelj
  p += tmp.decode('utf-8').encode('cp852')
  tmp = 'Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01 %s \x1b\x2d\x00\x1b\x45\x00' % datum
  p += tmp.decode('utf-8').encode('cp852')
  p += '\n\n'
  p += '\x1b\x21\x01' 
  p += '\x1b\x45\x01' + '{:<45}'.format('Lijek') + '{:>9}'.format('Količina') + '\x1b\x45\x00'
  p += '\x1b\x21\x00' 
  for i in range(42): p += '\xcd'
  p += '\n\x1b\x21\x01' 
  
  ukupna_cijena = 0

  for i in lijekovi:
    x = float(i[1]) * float(i[2])
    p += '{:<49}'.format(i[0][:27]) + '{:>9}'.format('%.2f' % x)
    ukupna_cijena += x

  p += '\x1b\x21\x00'
  for i in range(42): p += '\xcd' 
  p += TXT_ALIGN_CT + TXT_NORMAL

  p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
  p += '%s\x00\x0a' % barcode

  p += TXT_ALIGN_CT
  p += '\n  Hvala na posjeti!  \n'
  p += '\x1c\x70\x02\x00'

  
  p += '\n\n\n\n\n\n'
  p += PAPER_FULL_CUT

  return p

def addpoint(value):
    
    value = str(value)
    return '{0}.{1}'.format(value[:-2],value[-2:])
  
class Potvrda:
    
    def __init__(self):
      self.narucitelj = ''
      self.datum = ''
      self.lijekovi = [] 
      self.polog = 0
      self.sluzbenik = ''
      self.barcode = ''

    def render(self):
      EUR = '\x1b\x74\x10\x80\x1b\x74\x12'
      p = "\x1b\x40" 
      p += '\x1d\x28\x4c\x06\x00\x30\x45\x20\x21\x01\x01'  
      p += '\n\x1b\x74\x12' + TXT_ALIGN_CT + TXT_NORMAL 
      p += strftime("%A, %d. %B %Y.  %H:%M:%S").decode('utf-8').encode('cp852') + '\n' 
      p += TXT_ALIGN_CT + TXT_2HEIGHT + '\n\x1b\x45\x01- P O T V R D A -\x1b\x45\x00\n\n'
      p += TXT_NORMAL + TXT_ALIGN_CT

      p += ('Naručitelj: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00\n' % self.narucitelj).decode('utf-8').encode('cp852')
      p += ('Datum narudžbe: \x1b\x45\x01\x1b\x2d\x01%s\x1b\x2d\x00\x1b\x45\x00 \n\n' % self.datum).decode('utf-8').encode('cp852')
      p += '\x1b\x21\x01' 
      p += '\x1b\x45\x01' + '{:<45}'.format('Lijek') + '{:>9}'.format('Količina').decode('utf-8').encode('cp852') + '\x1b\x45\x00'
      p += '\x1b\x21\x00' 
      p += '\n'
      for i in range(42): p += '\xcd' 
      p += '\n\x1b\x21\x01' 
   
      for i in self.lijekovi:
        x = int(i[1]) * int(i[2])
        p += '{:<45}'.format(i[0][:27]) + '{:>9}'.format(int(i[1])) 
        p += '\n'

      p += '\x1b\x21\x00'
      for i in range(42): p += '\xcd' 
      p += '\n\n'
 
      p += '\x1b\x61\x01\x1d\x68\x50\x1d\x48\x02\x1d\x6b\x02'
      p += '%s\x00\x0a' % self.barcode
      p += TXT_ALIGN_CT + '\n  Hvala na posjeti!  \n\x1c\x70\x02\x00\n\n\n\n\n\n' + PAPER_FULL_CUT

      return p

    def render_html(self):
      vrijeme = strftime("%A, %d. %B %Y.  %H:%M:%S")
      objekt = self
      ukupna_cijena = 0
      popis=[]    
      for i in self.lijekovi:
        x = float(i[1]) * float(i[2])
        popis.append(('{:<29}'.format(i[0][:27]),'{:>5}'.format(i[1]),'{:>11}'.format(i[2]),'{:>11}'.format(int(x))))
        ukupna_cijena += x
      platiti = int(ukupna_cijena - float(self.polog))
      ukupna_cijena=int(ukupna_cijena)
      from django.template.loader import render_to_string
      return render_to_string('escpos2.html', locals())

