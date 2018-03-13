# -*- coding: utf-8 -*-
"""
Factories to build Vertex and Edge model for Directed Acyclic Graph structure.

"""
from django.db import connection
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from closuredag.models import VertexBase, EdgeBase
from closuredag.signals import add_closure_edge
from closuredag.managers import VertexManager

import logging
logger = logging.getLogger(__name__)

def edge_factory(vertex_model,
                 vertex_to_field="id",
                 concrete=True,
                 base_model=models.Model):
    """
    Dag Edge factory
    """
    if isinstance(vertex_model, str):
        try:
            vertex_model_name = vertex_model.split('.')[1]
        except IndexError:
            vertex_model_name = vertex_model
    else:
        vertex_model_name = vertex_model._meta.model_name


    class Edge(EdgeBase, base_model):

        parent = models.ForeignKey(
            vertex_model,
            related_name="vertex_childs",
            # related_name="{0}_child".format(vertex_model_name),
            to_field=vertex_to_field, 
            on_delete=models.CASCADE)
        child = models.ForeignKey(
            vertex_model,
            related_name="vertex_parents",
            # related_name="{0}_parent".format(vertex_model_name),
            to_field=vertex_to_field,
            on_delete=models.CASCADE)

        class Meta:
            abstract = not concrete

        def __str__(self):
            return "{0}".format(self.id)
        
        def save(self, *args, **kwargs):
            self.parent.__class__.circular_checker(self.parent, self.child)
            super(Edge, self).save(*args, **kwargs)


    return Edge


def vertex_factory(edge_model, children_null=True, base_model=models.Model):
    """
    Dag Vertex factory
    """

    class Vertex(base_model, VertexBase):
        """
        An abstract Vertex class that provides a manager to deal with heterogenous sub vertex class.
    
        For use in trees of inherited models, to be able to downcast
        parent instances to their child types.
    
        """       

        children = models.ManyToManyField(
            'self',
            blank=children_null,
            symmetrical=False,
            through=edge_model,
            related_name='parents') 
        
        objects = VertexManager()

        class Meta:
            abstract= True

        def direct_ancestors(self):
            edges = edge_model.objects.filter(Q(child=self) & Q(etype="direct"))
            return self.objects.filter(vertex_child__in = edges)
        
        def direct_descandants(self):
            edges = edge_model.objects.filter(Q(parent=self) & Q(etype="direct"))
            return self.objects.filter(vertex_parent__in = edges)
        
    return Vertex
