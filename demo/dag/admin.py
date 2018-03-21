import json

from django.conf.urls import url
from django.contrib import admin
from django.utils.translation import ugettext as _

from admintab.admin import ChangeListAdminMixin as ChangeListAdmin

from closuredag.admin import EdgeAdminMixin, VertexAdminMixin


from .models import Node, Relation, NodeOne, NodeTwo

import logging

logger = logging.getLogger("admin")

@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display=['__str__', 'id', 'etype']

class EdgeParentAdminInline(EdgeAdminMixin, admin.TabularInline):
    model = Relation
    fk_name = 'child'
    extra = 1
    verbose_name = "Parent"
    verbose_name_plural = "Parents"


class EdgeChildAdminInline(EdgeAdminMixin, admin.TabularInline):
    model = Relation
    fk_name = 'parent'
    extra = 1
    verbose_name = _("Child")
    verbose_name_plural = _("Children")


class AbsctractNodeAdmin(VertexAdminMixin, admin.ModelAdmin):
    inlines = [EdgeParentAdminInline, EdgeChildAdminInline]


@admin.register(NodeTwo)
class NodeTwoAdmin(AbsctractNodeAdmin):
    list_display = [ "id", "name"]


@admin.register(NodeOne)
class NodeAdmin(AbsctractNodeAdmin, ChangeListAdmin):
    list_display = [ "id", "name"]
    list_filter = ["name", "value_one"]
    change_list_tab = [ 
            ("Table", "admintab/admin/change_list_base.html"),
            ("DAG", "admintab/change_list_dag.html"),
            ("DAGFULL", "admintab/change_list_dagfull.html"),
            ("DOT", "admintab/change_list_dot.html")
            ]

    
    def changelisttab(self, request, context):
        qs = context["cl"].queryset
        # draw graph
        G = qs.graph()
        context["graph"] = json.dumps(G)
        
        GF = qs.fullgraph()
        context["fullgraph"] = json.dumps(GF)
        
        context["dot"] = qs.dot()
        
        # qs.dot()
        return request, context
    
    @property
    def media(self):
        """
        Add media class to add custom js and css for the graph stuff
        """
        media = super(NodeAdmin, self).media
        css = { "all":()}
        js = []

        css["all"] = ("css/node.css",)
        media.add_css(css)

        js.append("https://d3js.org/d3.v4.min.js")
        js.append("js/dagre-d3.js")
        js.append("js/node.js")
        media.add_js(js)

        return media
