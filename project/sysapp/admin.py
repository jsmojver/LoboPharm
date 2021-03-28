from django.contrib import admin
from sysapp.models import UserProfile, LoginImage, ObavijestiPost, Ticket

#class UserProfileAdmin(admin.ModelAdmin):
#  list_display=('id', 'djelatnik',)
#  exclude = ('klijent',)

class LoginImageAdmin(admin.ModelAdmin):
  list_display=('id', 'user', 'created', 'getpng',)

class TicketAdmin(admin.ModelAdmin):
  list_display=('id', 'status', 'autor', 'naslov', 'sadrzaj', 'created',)

admin.site.register(UserProfile)
admin.site.register(LoginImage, LoginImageAdmin)
admin.site.register(ObavijestiPost)
admin.site.register(Ticket, TicketAdmin)
