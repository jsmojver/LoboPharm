from django.http import HttpResponse, HttpResponseRedirect
from coffin.shortcuts import render_to_response
from coffin.template import RequestContext
from project.util import login_required


#--------------------------------------------------------------------------------------------------


@login_required
def njemacka_item_list(request):
    from django.db.models import Q
    from project.util import decode_cookie_value, str_to_int
    from project.meds.models import Artikal

    filter_search = decode_cookie_value(request.COOKIES.get("njemacko_trziste_filter_search", ""))

    q = Q()
    if len(filter_search) != 0:
        q &= Q(name__icontains=filter_search)

    if request.method == "POST":
        operation = request.POST.get("operation")
        if operation == "delete":
            ids = [str_to_int(n) for n in request.POST.get("selected_items").split(",") if n]
            Artikal.delete_objects(ids)

            return HttpResponseRedirect(request.path)

    return render_to_response("admin/meds/njemacka_list.html",
        {
            "items": Artikal.objects.filter(q),
            "filter_search": filter_search,
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def njemacka_item_edit(request, id=0):
    from project.meds.models import Artikal
    from project.util import str_to_float

    item, new_item = Artikal.create_object(id)

    if request.method == "POST":
        post = lambda key: request.POST.get(key, "")
        item.set_string("name", post("name"))
        item.ApoEk = str_to_float(post("ApoEk")) * 100.0
        item.ApoVk = str_to_float(post("ApoVk")) * 100.0
        item.save()

        return HttpResponseRedirect(post("backlink"))

    return render_to_response("admin/meds/njemacka_edit.html",
        {
            "item": item,
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def njemacka_calc_prices(request, atc_id=0):
    if request.method == "POST":
        from project.util import str_to_float
        from project.meds.models import artikal_calc_maloprodajna_cijena, artikal_calc_veleprodajna_cijena
        from order.templatetags.mytagslib import eur2hrk
        from project.main.jinja_lib import format_float
        import json

        atc_id = int(atc_id)

        ApoEk = str_to_float(request.POST.get("ApoEk")) * 100.0
        ApoVk = str_to_float(request.POST.get("ApoVk")) * 100.0

        veleprodajna_cijena_eur = artikal_calc_veleprodajna_cijena(ApoEk, ApoVk)
        veleprodajna_cijena_kn = eur2hrk(veleprodajna_cijena_eur)
        maloprodajna_cijena_eur = artikal_calc_maloprodajna_cijena(ApoEk, ApoVk, atc_id)
        maloprodajna_cijena_kn = eur2hrk(maloprodajna_cijena_eur)

        res = {
            "veleprodajna_cijena_eur": float(veleprodajna_cijena_eur),
            "veleprodajna_cijena_kn": float(veleprodajna_cijena_kn),
            "maloprodajna_cijena_eur": float(maloprodajna_cijena_eur),
            "maloprodajna_cijena_kn": float(maloprodajna_cijena_kn),
            "veleprodajna_cijena_eur_str": format_float(veleprodajna_cijena_eur),
            "veleprodajna_cijena_kn_str": format_float(veleprodajna_cijena_kn),
            "maloprodajna_cijena_eur_str": format_float(maloprodajna_cijena_eur),
            "maloprodajna_cijena_kn_str": format_float(maloprodajna_cijena_kn),
        }
        return HttpResponse(json.dumps(res))

    return HttpResponse("")


#--------------------------------------------------------------------------------------------------


@login_required
def ostala_trzista_item_list(request):
    from django.db.models import Q
    from project.util import decode_cookie_value, str_to_int
    from project.order.models import ArtikalDrugoTrziste

    filter_search = decode_cookie_value(request.COOKIES.get("ostala_trzista_filter_search", ""))

    q = Q()
    if len(filter_search) != 0:
        q &= Q(ime__icontains=filter_search) | \
            Q(trziste__naziv__icontains=filter_search)

    if request.method == "POST":
        operation = request.POST.get("operation")
        if operation == "delete":
            ids = [str_to_int(n) for n in request.POST.get("selected_items").split(",") if n]
            ArtikalDrugoTrziste.delete_objects(ids)

            return HttpResponseRedirect(request.path)

    return render_to_response("admin/meds/ostala_trzista_list.html",
        {
            "items": ArtikalDrugoTrziste.objects.filter(q),
            "filter_search": filter_search,
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def ostala_trzista_item_edit(request, id=0):
    from project.order.models import ArtikalDrugoTrziste, Trziste
    from project.meds.models import AtcCode
    from project.util import str_to_float

    item, new_item = ArtikalDrugoTrziste.create_object(id)

    if request.method == "POST":
        post = lambda key: request.POST.get(key, "")
        item.set_string("ime", post("ime"))
        item.set_foreign_object("trziste", Trziste, post("trziste"))
        item.cijena = str_to_float(post("cijena"))
        item.set_string("kolicina", post("kolicina"))
        item.set_string("jedinice", post("jedinice"))
        atc_sifra = post('atc_sifra')
        if atc_sifra != None and len(atc_sifra) > 0: 
            rs = AtcCode.objects.filter(sifra__iexact=atc_sifra)
            if rs.count() > 0:
                item.ATC = rs[0]
            else:
                item.ATC = None
        else:
            item.ATC = None
        item.save()

        return HttpResponseRedirect(post("backlink"))

    return render_to_response("admin/meds/ostala_trzista_item_edit.html",
        {
            "item": item,
            "trzista": Trziste.objects.all(),
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def ostala_trzista_calc_prices(request):
    if request.method == "POST":
        from project.util import str_to_float
        from project.order.models import artikal_drugo_trziste_calc_maloprodajna_cijena, artikal_drugo_trziste_calc_veleprodajna_cijena
        from project.order.models import Trziste
        from order.templatetags.mytagslib import eur2hrk
        from project.main.jinja_lib import format_float
        import json

        nabavna_cijena = str_to_float(request.POST.get("nabavna_cijena"))
        atc_sifra = request.POST.get('atc_sifra')

        try:
            trziste = Trziste.objects.get(id=request.POST.get("trziste"))
        except:
            return HttpResponse("")

        veleprodajna_cijena_eur = artikal_drugo_trziste_calc_veleprodajna_cijena(nabavna_cijena, trziste)
        veleprodajna_cijena_kn = eur2hrk(veleprodajna_cijena_eur)
        maloprodajna_cijena_eur = artikal_drugo_trziste_calc_maloprodajna_cijena(nabavna_cijena, trziste, atc_sifra=atc_sifra)
        maloprodajna_cijena_kn = eur2hrk(maloprodajna_cijena_eur)

        res = {
            "veleprodajna_cijena_eur": float(veleprodajna_cijena_eur),
            "veleprodajna_cijena_kn": float(veleprodajna_cijena_kn),
            "maloprodajna_cijena_eur": float(maloprodajna_cijena_eur),
            "maloprodajna_cijena_kn": float(maloprodajna_cijena_kn),
            "veleprodajna_cijena_eur_str": format_float(veleprodajna_cijena_eur),
            "veleprodajna_cijena_kn_str": format_float(veleprodajna_cijena_kn),
            "maloprodajna_cijena_eur_str": format_float(maloprodajna_cijena_eur),
            "maloprodajna_cijena_kn_str": format_float(maloprodajna_cijena_kn),
        }
        return HttpResponse(json.dumps(res))

    return HttpResponse("")


#--------------------------------------------------------------------------------------------------


@login_required
def depo_item_list(request):
    from django.db.models import Q
    from project.util import decode_cookie_value, str_to_int
    from project.depo.models import Lijek

    filter_search = decode_cookie_value(request.COOKIES.get("depo_filter_search", ""))

    q = Q()
    if len(filter_search) != 0:
        q &= Q(naziv__icontains=filter_search) | \
            Q(depo__naziv__icontains=filter_search)

    if request.method == "POST":
        operation = request.POST.get("operation")
        if operation == "delete":
            ids = [str_to_int(n) for n in request.POST.get("selected_items").split(",") if n]
            Lijek.delete_objects(ids)

            return HttpResponseRedirect(request.path)

    return render_to_response("admin/meds/depo_list.html",
        {
            "items": Lijek.objects.filter(q),
            "filter_search": filter_search,
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def depo_item_edit(request, id=0):
    from project.depo.models import Lijek, Depo
    from project.util import str_to_float

    item, new_item = Lijek.create_object(id)

    if request.method == "POST":
        post = lambda key: request.POST.get(key, "")
        item.set_string("naziv", post("naziv"))
        item.set_foreign_object("depo", Depo, post("depo"))
        item.nabavna_cijena_eur = str_to_float(post("nabavna_cijena_eur"))
        item.cijena = str_to_float(post("cijena"))
        item.save()

        return HttpResponseRedirect(post("backlink"))

    return render_to_response("admin/meds/depo_item_edit.html",
        {
            "item": item,
            "depoi": Depo.objects.all(),
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def trzista_item_list(request):
    from project.util import str_to_float
    from project.meds.models import Trziste

    if request.method == "POST":
        cmd = request.POST.get("cmd")
        if cmd == "edit":
            id = request.POST.get("id")
            koeficijent_ljekarne = str_to_float(request.POST.get("koef_vpc"))
            koeficijent_pacijenti = str_to_float(request.POST.get("koef_mpc"))
            Trziste.objects.filter(id=id).update(koeficijent_ljekarne=koeficijent_ljekarne, koeficijent_pacijenti=koeficijent_pacijenti)
            return HttpResponseRedirect(request.path)

    return render_to_response("admin/meds/trzista_list.html",
        {
            "items": Trziste.objects.all().order_by("naziv"),
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def konta_item_list(request):
    from django.db.models import Q
    from project.util import decode_cookie_value, str_to_int
    from project.nabava.models import Konto

    return render_to_response("admin/meds/konta_list.html",
        {
            "items": Konto.objects.all(),
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def konta_item_edit(request, id=0):
    from project.nabava.models import Konto
    from project.util import str_to_int

    item, new_item = Konto.create_object(id)

    if request.method == "POST":
        post = lambda key: request.POST.get(key, "")
        item.set_string("name", post("name"))
        item.sifra = str_to_int(post("sifra"))
        item.set_string("kontakt", post("kontakt"))
        item.save()

        return HttpResponseRedirect(post("backlink"))

    return render_to_response("admin/meds/konta_item_edit.html",
        {
            "item": item,
            "active_page": "meds",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------
