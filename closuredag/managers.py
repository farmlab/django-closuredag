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
    
    # def dot(self):
        # from graphviz import Digraph
        # # check directory
        # STMP = os.path.join('static',TMP)
        # if not os.path.exists(STMP):
            # os.makedirs(STMP)
        # fpath = 'dotGraph.gv'
        # # data
        # ids = self._ids()
        # nodes = self._root_model().objects.filter(
                # Q(parents__in = ids ) | Q(children__in = ids) | Q(id__in = ids)
                # ).distinct().select_subclasses()
        # relations = self._through_model().objects.filter(
                # Q(child_id__in = nodes._ids() ) & Q(parent_id__in = nodes._ids())
                # ).distinct()
        
        # # build graph
        # cls = self._model_name()
        # dot = Digraph()
        # for n in nodes:
            # ncls = n.__class__.__name__.lower()
            # shp =  'box'  if cls == ncls else 'ellipse'
            # dot.node(str(n.id), str(n), shape=shp)
        
        # for e in relations:
            # lbl = str(e.id)
            # # sty =  'dotted'  if e.etype != 'direct' else 'line'
            # dot.edge(str(e.parent_id), str(e.child_id), label=lbl)
        
        # dot.render(fpath, STMP, view=True, cleanup=True)



    def graph(self, complete=False):
        
        if complete:
            # FIXME: to be changed with the closure table
            # Currently, it does not work when more than 2 vertex from other cat are in between 
            # (e.g. need to traverse the tree )
            ids = self._ids()

            nodes = self._root_model().objects.filter(
                    Q(parents__in = ids ) | Q(children__in = ids) | Q(id__in = ids)
                ).distinct().select_subclasses()
            
            relations = self._through_model().objects.filter(
                Q(child_id__in = nodes._ids() ) & Q(parent_id__in = nodes._ids() )
                )
        else:
            # Only selected nodes
            relations = self._through_model().objects.filter(
                Q(child_id__in = self._ids() ) & Q(parent_id__in = self._ids() )
            )
            nodes = self

        G = {'type':'full'}
        N = []
        E = []
        for n in nodes:
            # Node 
            node = {
                    "id": n.id,
                    "name": n.name,
                    "href": n.get_admin_url(),
                    "type": n.__class__.__name__.lower()
                }
            N.append(node)
      
        # Edge
        for e in relations:
            edge = {
                    "id": e.id,
                    "etype": e.etype,
                    "hops": e.hops,
                    "from": e.parent_id,
                    "to": e.child_id}
            E.append(edge)         
        G['nodes'] = N
        G['edges'] = E

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
        return VertexQuerySet(self.model, using=self._db).select_subclasses()  

