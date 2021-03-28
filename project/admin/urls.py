from django.conf.urls import patterns, include

urlpatterns = patterns('',
    (r'^$', "project.admin.common.frontpage"),
    (r'^meds/njemacka/$', "project.admin.meds.njemacka_item_list"),
    (r'^meds/njemacka/item/edit/$', "project.admin.meds.njemacka_item_edit"),
    (r'^meds/njemacka/item/edit/(?P<id>\d+)/$', "project.admin.meds.njemacka_item_edit"),
    (r'^meds/njemacka/calc_prices/(?P<atc_id>\d+)/$', "project.admin.meds.njemacka_calc_prices"),
    (r'^meds/ostala_trzista/$', "project.admin.meds.ostala_trzista_item_list"),
    (r'^meds/ostala_trzista/item/edit/$', "project.admin.meds.ostala_trzista_item_edit"),
    (r'^meds/ostala_trzista/item/edit/(?P<id>\d+)/$', "project.admin.meds.ostala_trzista_item_edit"),
    (r'^meds/ostala_trzista/calc_prices/$', "project.admin.meds.ostala_trzista_calc_prices"),
    (r'^meds/depo/$', "project.admin.meds.depo_item_list"),
    (r'^meds/depo/item/edit/$', "project.admin.meds.depo_item_edit"),
    (r'^meds/depo/item/edit/(?P<id>\d+)/$', "project.admin.meds.depo_item_edit"),
    (r'^meds/trzista/$', "project.admin.meds.trzista_item_list"),
    (r'^meds/konta/$', "project.admin.meds.konta_item_list"),
    (r'^meds/konta/item/edit/$', "project.admin.meds.konta_item_edit"),
    (r'^meds/konta/item/edit/(?P<id>\d+)/$', "project.admin.meds.konta_item_edit"),

    (r'^eur2hrk/$', "project.admin.common.eur2hrk"),
    (r'^hrk2eur/$', "project.admin.common.hrk2eur"),
)
