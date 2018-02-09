# -*- coding: utf-8 -*-
"""
Factories to build Vertex and Edge model for Directed Acyclic Graph structure.

"""

from django.contrib.contenttypes.models import ContentType
from django.db import models
from closuredag.models import VertexBase
from closuredag.managers import VertexManager


def edge_factory(vertex_model,
                 child_to_field="id",
                 parent_to_field="id",
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


    class Edge(base_model):
        class Meta:
            abstract = not concrete

        parent = models.ForeignKey(
            vertex_model,
            related_name="{0}_child".format(vertex_model_name),
            to_field=parent_to_field, 
            on_delete=models.CASCADE)
        child = models.ForeignKey(
            vertex_model,
            related_name="{0}_parent".format(vertex_model_name),
            to_field=child_to_field,
            on_delete=models.CASCADE)


        def __str__(self):
            return "{0} is child of {1}".format(self.child, self.parent)

        def save(self, *args, **kwargs):
            if not kwargs.pop('disable_circular_check', False):
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
            related_name='_parents')  # VertexBase.parents() is a function
        
        objects = VertexManager()

        class Meta:
            abstract= True

    return Vertex
