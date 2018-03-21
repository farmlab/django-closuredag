import os

from django.db import models
from django.db.models import Q
from model_utils.managers import InheritanceQuerySet, InheritanceManager
from django.apps import apps


import logging
logger = logging.getLogger(__name__)

TMP = "tmp"
DOT_PATH=TMP

class VertexQuerySet(InheritanceQuerySet):
    
    def dot(self):
        import pygraphviz as pgv
        
        nodes = self._root_model().objects.filter(
                Q(children__in = self) | Q(parents__in = self) | Q(id__in = self)
                ).distinct()
        edges = self._through_model().objects.filter(
                Q(child_id__in = nodes._ids() ) & Q(parent_id__in = nodes._ids() ) & Q(etype = "direct"))
        
        # build graph
        
        G = pgv.AGraph(directed=True,rankdir='LR')
        G.node_attr['style']='rounded, filled'
        for n in nodes:
            fillcolor = "#FBBE5E" if n in self else "#ACC280"
            G.add_node(n.id, label=str(n), fillcolor=fillcolor, shape="box")
        
        for e in edges:
            G.add_edge(e.parent_id, e.child_id)
        
        # return G.draw(format="svg", prog="dot")
        return G.string()


    def fullgraph(self):
        nodes = self._root_model().objects.prefetch_related("parents", "children").all()
        edges = self._through_model().objects.filter(etype="direct").select_related("parent",
        "child")
        
        G = {}
        N = []
        for n in nodes:
            data = n.to_dict()
            data["selected"] = True if n in self else False
            N.append(data) 
        G['nodes'] =N 
        G['edges'] = [ e.to_dict() for e in edges]

        return G

    def complete_graph(self):
        
        """Return the graph with vertex that are in the queryset and related vertex from other class, with only direct edge )"""
        
        # vertices must be ancestor and descendant of any of the vertex
        nodes = self._root_model().objects.filter(
                Q(children__in = self) | Q(parents__in = self) | Q(id__in = self)
                ).distinct()

        edges = self._through_model().objects.filter(
                Q(child_id__in = nodes._ids() ) & Q(parent_id__in = nodes._ids() ) & Q(etype =
                "direct")
                )
        G = {}
        
        N = []
        for n in nodes:
            data = n.to_dict()
            data["selected"] = True if n in self else False
            N.append(data) 

        G['nodes'] = N
        G['edges'] = [ e.to_dict() for e in edges]
        return G
  
    
    def graph(self):
        """Return the graph with vertex that are in the queryset and their direct edge"""
        edges = self._through_model().objects.filter(
                Q(child_id__in = self._ids() ) & Q(parent_id__in = self._ids() ) & Q(etype =
                "direct")
                )
        G = {}
        N = []
        for n in self:
            data = n.to_dict()
            data["selected"] = True if n in self else False
            N.append(data) 
        G['nodes'] = N
        G['edges'] = [ e.to_dict() for e in edges]
        return G
    

    def _model_name(self):
        return self.model._meta.model_name
    
    def _root_model(self):
        """ Return the dag root model"""
        grand_parent_cls_name = "Vertex"
        for parent_cls in self.model.__bases__:
            for gp_cls in parent_cls.__bases__:
                if gp_cls.__name__ == grand_parent_cls_name:
                    return parent_cls
        return None

    def _through_model(self):
        """ Return the edge model."""
        return self.model.children.through

    def _ids(self):
        """ Return the list of node ids."""
        return self.values_list("id", flat=True)
   
    def qs_edges(self, ids=None):
        """ Returns all edges of the queryset."""
        # edges =  apps.get_model("closuredag", "Edge") # To avoid circular import
        if not ids:
            ids = self.qs_ids()
        return Edge.objects.filter(
                Q(child_id__in = ids ) & Q(parent_id__in = ids )
                )


class VertexManager(InheritanceManager):
    def get_queryset(self):
        """ We manage subclass model """
        return VertexQuerySet(self.model, using=self._db).select_subclasses()  

