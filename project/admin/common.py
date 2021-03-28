from django.http import HttpResponse, HttpResponseRedirect
from coffin.shortcuts import render_to_response
from coffin.template import RequestContext
from project.util import staff_required, login_required


#--------------------------------------------------------------------------------------------------


@login_required
def frontpage(request):
    return render_to_response("admin/frontpage.html",
        {
            "active_page": "frontpage",
        }, context_instance=RequestContext(request)
    )


#--------------------------------------------------------------------------------------------------


@login_required
def eur2hrk(request):
    if request.method == "POST":
        import json
        from order.templatetags.mytagslib import eur2hrk
        from project.util import str_to_float
        from project.main.jinja_lib import format_float

        value_hrk = float(eur2hrk(str_to_float(request.POST.get("value"))))

        res = {
            "value_hrk": value_hrk,
            "value_hrk_str": format_float(value_hrk),
        }

        return HttpResponse(json.dumps(res))

    return HttpResponse("")


#--------------------------------------------------------------------------------------------------


@login_required
def hrk2eur(request):
    if request.method == "POST":
        import json
        from order.templatetags.mytagslib import hrk2eur
        from project.util import str_to_float
        from project.main.jinja_lib import format_float

        value_eur = float(hrk2eur(str_to_float(request.POST.get("value"))))

        res = {
            "value_eur": value_eur,
            "value_eur_str": format_float(value_eur),
        }

        return HttpResponse(json.dumps(res))

    return HttpResponse("")


#--------------------------------------------------------------------------------------------------
