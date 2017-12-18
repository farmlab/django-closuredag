# -*- coding: utf-8 -*-
"""
Factories to build Vertex and Edge model for Directed Acyclic Graph structure.

"""

from django.db import models
from closuredag.models import VertexBase


def edge_factory(vertex_model,
                 child_to_field="id",
                 parent_to_field="id",
                 concrete=True,
                 base_model=models.Model):
    """
    Dag Edge factory
    """
    try:
        basestring
    except NameError:
        basestring = str
    if isinstance(vertex_model, basestring):
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
            related_name="%s_child" % vertex_model_name,
            to_field=parent_to_field)
        child = models.ForeignKey(
            vertex_model,
            related_name="%s_parent" % vertex_model_name,
            to_field=child_to_field)

        def __unicode__(self):
            return u"%s is child of %s" % (self.child, self.parent)

        def save(self, *args, **kwargs):
            if not kwargs.pop('disable_circular_check', False):
                self.parent.__class__.circular_checker(self.parent, self.child)
            super(Edge, self).save(*args,
                                   **kwargs)  # Call the "real" save() method.

    return Edge


def vertex_factory(edge_model, children_null=True, base_model=models.Model):
    """
    Dag Vertex factory
    """

    class Vertex(base_model, VertexBase):
        class Meta:
            abstract = True

        children = models.ManyToManyField(
            'self',
            blank=children_null,
            symmetrical=False,
            through=edge_model,
            related_name='_parents')  # VertexBase.parents() is a function

    return Vertex
