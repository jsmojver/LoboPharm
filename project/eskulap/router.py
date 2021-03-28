class Router(object):
    def db_for_read(self, model, **hints):
        if 'eskulap' == model._meta.app_label:
            return 'eskulap'
        return None

    def db_for_write(self, model, **hints):
        if 'eskulap' == model._meta.app_label:
            return 'eskulap'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if 'eskulap' == obj1._meta.app_label and\
           'eskulap' == obj2._meta.app_label:
            return True
        return None

    def allow_syncdb(self, db, model):
        if 'eskulap' == db:
            return 'eskulap' == model._meta.app_label
        elif 'eskulap' == model._meta.app_label:
            return False
        return None
