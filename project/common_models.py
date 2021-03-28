# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType


#--------------------------------------------------------------------------------------------------


def get_content_type(object):
    try:
        return ContentType.objects.get(model__iexact=object.__class__.__name__)
    except:
        return None


#--------------------------------------------------------------------------------------------------


def read_generic_object(content_type, object_id):
    try:
        return content_type.model_class().objects.get(id=object_id)
    except:
        return None


#**************************************************************************************************


class AdminSetter():

    #----------------------------------------------------------------------------------------------

    def set_string(self, attr, value):
        from django.db.models.fields import CharField as CharField
        value = value.strip()

        # if field is CharField, limit the length
        model_attr = self._meta.get_field(attr)
        if isinstance(model_attr, CharField):
            value = value[:model_attr.max_length]

        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_int(self, attr, value, default=0):
        try:
            value = int(value)
        except ValueError:
            value = default
        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_float(self, attr, value, default=0.0):
        try:
            value = float(value.replace(",", "."))
        except ValueError:
            value = default
        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_bool(self, attr, value):
        setattr(self, attr, value != "")

    #----------------------------------------------------------------------------------------------

    def set_url(self, attr, value):
        value = value.strip().lower()
        if not value.startswith(("http://", "https://",)):
            value = "http://" + value
        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_date(self, attr, value):
        import datetime
        try:
            dd, mm, yy = value.split(".")
            value = datetime.date(int(yy), int(mm), int(dd))
        except:
            value = None

        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_datetime(self, attr, value):
        import datetime
        from project.main.util import str_to_int
        try:
            date, time = value.split(" ")
            dd, mm, yy = date.split(".")
            try:
                hh, min = time.split(":")
            except:
                hh = min = 0
            value = datetime.datetime(str_to_int(yy), str_to_int(mm), str_to_int(dd), str_to_int(hh), str_to_int(min), 0)
        except:
            value = None

        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_foreign_object(self, attr, obj_class, id):
        try:
            value = obj_class.objects.get(id=id)
        except:
            value = None
        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    def set_many_to_many(self, attr, obj_class, ids):
        if isinstance(ids, basestring):
            from project.main.util import str_to_int
            ids = [str_to_int(n) for n in ids.split(",") if n]

        # add new objects
        for id in ids:
            try:
                item = obj_class.objects.get(id=id)
                if attr.filter(id=id).count() == 0:
                    attr.add(item)
            except obj_class.DoesNotExist:
                pass
        # remove nonexisting objects
        for item in attr.all():
            if not item.id in ids:
                attr.remove(item)

    #----------------------------------------------------------------------------------------------

    def set_ordering(self, order_changed, order_items_ids):
        from project.main.util import str_to_int

        if order_changed == "1":
            ids = [str_to_int(n) for n in order_items_ids.split(",") if n]
            for n, id in enumerate(ids):
                if id == 0:
                    id = self.id
                self.__class__.objects.filter(id=id).update(order=n)

    #----------------------------------------------------------------------------------------------

    def split_string(self, attr, max_count=5, separator='|'):
        value = getattr(self, attr)
        return ([s for s in value.split(separator) if len(s) > 0] + [""] * max_count)[:max_count]

    #----------------------------------------------------------------------------------------------

    def join_string(self, attr, value, separator='|'):
        value = separator.join([s.strip() for s in value if len(s.strip()) > 0])
        setattr(self, attr, value)

    #----------------------------------------------------------------------------------------------

    @classmethod
    def create_object(cls, id):
        try:
            id = int(id)
        except ValueError:
            id = 0

        new_item = id == 0
        item = None

        if not new_item:
            try:
                item = cls.objects.get(id=id)
            except:
                new_item = True

        if new_item:
            item = cls()
        return item, new_item

    #----------------------------------------------------------------------------------------------

    @classmethod
    def set_publish_objects(cls, ids, state):
        cls.objects.filter(id__in=ids).update(published=state)

    #----------------------------------------------------------------------------------------------

    @classmethod
    def delete_objects(cls, ids):
        for id in ids:
            try:
                item = cls.objects.get(id=id)
                item.delete()
            except cls.DoesNotExist:
                pass

    #----------------------------------------------------------------------------------------------

    @classmethod
    def normalize_order(cls, filter=None):
        items = cls.objects.all() if filter is None else cls.objects.filter(filter)
        for n, item in enumerate(items):
            item.order = n
            item.save()

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************


class TreeObject():
    traverse_to_root_path = None

    #----------------------------------------------------------------------------------------------

    def get_children(self):
        return self.__class__.objects.filter(parent=self, published=True)

    #----------------------------------------------------------------------------------------------

    def get_other_tree_items(self):

        def read_child(parent_id):
            res = []
            for c in self.__class__.objects.filter(parent__id=parent_id).exclude(id=self.id):
                res.append(c)
                res += read_child(c.id)
            return res

        return read_child(None)

    #----------------------------------------------------------------------------------------------

    def get_parent_count(self, target_parent=None):

        parent_count = 0
        p_id = self.parent_id
        finished = False

        while not finished:
            if p_id != 0:
                items = self.__class__.objects.filter(id=p_id).values("parent_id")
                if len(items) > 0 and not (target_parent is not None and p_id == target_parent.id):
                    p_id = items[0]["parent_id"]
                    parent_count += 1
                else:
                    finished = True
            else:
                finished = True

        return parent_count

    #----------------------------------------------------------------------------------------------

    def traverse_to_root(self, include_self=True, fields=[]):

        if self.traverse_to_root_path is None:
            p = self
            res = []

            while p.id != 0:
                if include_self or p != self:
                    res += [p]

                if p.parent_id != 0:
                    try:
                        if fields != []:
                            p = self.__class__.objects.get(id=p.parent.id).only(*fields)
                        else:
                            p = self.__class__.objects.get(id=p.parent.id)
                    except:
                        break
                else:
                    break

            res.reverse()
            for level, p in enumerate(res):
                p.level = level

            self.traverse_to_root_path = res

        return self.traverse_to_root_path

    #----------------------------------------------------------------------------------------------

    def get_siblings_with_self(self):
        return self.__class__.objects.filter(parent__id=self.parent_id)

    #----------------------------------------------------------------------------------------------

    def get_list_indent(self):
        return "&nbsp;&nbsp;&nbsp;&nbsp;" * self.get_parent_count()

    #----------------------------------------------------------------------------------------------

    def get_list_indent_px(self):
        return 20 * self.get_parent_count()

    #----------------------------------------------------------------------------------------------

    def get_descendants(self, fields=[]):

        def get_child_nodes(node):
            res = []
            if fields != []:
                for p in self.__class__.objects.filter(parent=node, published=True):
                    res.append(p)
                    res += get_child_nodes(p)
            else:
                for p in self.__class__.objects.filter(parent=node, published=True).only(*fields):
                    res.append(p)
                    res += get_child_nodes(p)
            return res

        return get_child_nodes(self)

    #----------------------------------------------------------------------------------------------

    def get_descendant_ids(self):

        def get_child_nodes(node_id):
            res = []
            for p in self.__class__.objects.filter(parent__id=node_id, published=True).values_list("id", flat=True):
                res.append(p)
                res += get_child_nodes(p)
            return res

        return get_child_nodes(self.id)

    #----------------------------------------------------------------------------------------------

    def format_path_name(self, separator="/"):
        path = []
        for c in self.traverse_to_root():
            path.append(c.caption_hr)
        separator = " %s " % separator
        return separator.join(path)

    #----------------------------------------------------------------------------------------------

    @classmethod
    def get_all_items(cls, published=None, start_node=None):
        def get_child_nodes(item):
            res = []
            items = cls.objects.filter(parent=item)
            if published is not None:
                items = items.filter(published=published)
            for c in items:
                res.append(c)
                res += get_child_nodes(c)
            return res

        root_nodes = cls.objects.filter(parent=start_node)
        if published is not None:
            root_nodes = root_nodes.filter(published=published)
        res = []
        for c in root_nodes:
            res += [c] + get_child_nodes(c)

        return res

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************


class AuthorInfo(models.Model):
    created_by = models.ForeignKey("CustomUser", related_name="created_by", blank=True, null=True)
    modified_by = models.ForeignKey("CustomUser", related_name="modified_by", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'author_infos'


#**************************************************************************************************


class AuthorInfoHandler():

    #----------------------------------------------------------------------------------------------

    def get_author_info(self):
        try:
            info = self.author_info
        except:
            info = None

        if info is None:
            info = AuthorInfo()
            info.save()
            self.author_info = info
        return self.author_info

    #----------------------------------------------------------------------------------------------

    def set_created(self, user):
        info = self.get_author_info()
        info.created_by = user
        info.modified_by = user
        info.save()

    #----------------------------------------------------------------------------------------------

    def set_modified(self, user):
        info = self.get_author_info()
        info.modified_by = user
        info.save()

    #----------------------------------------------------------------------------------------------

    def delete_author_info(self):
        try:
            self.author_info.delete()
        except:
            pass

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************
