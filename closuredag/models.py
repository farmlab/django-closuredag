# -*- coding: utf-8 -*-
"""
A class to model hierarchies of objects following
Directed Acyclic Graph structure.

"""

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError 
from django.db.models.fields.related import ManyToManyField
from closuredag.exceptions import VertexNotReachableException

from . import app_settings

import logging

logger = logging.getLogger(__name__)


class ToDictMixin(object):
    """Convert instance to dictionnary
    see:   https://stackoverflow.com/questions/21925671/convert-django-model-object-to-dict-with-all-of-the-fields-intact
    """

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            else:
                data[f.name] = f.value_from_object(self)
        return data



class VertexBase(ToDictMixin):
    """
    Main vertex abstract model
    """

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return "# {0}".format(self.pk)

    def add_child(self, descendant, **kwargs):
        """
        Adds a child
        """
        args = kwargs
        args.update({'parent': self, 'child': descendant})
        disable_check = args.pop('disable_circular_check', False)
        cls = self.children.through(**kwargs)
        return cls.save(disable_circular_check=disable_check)

    def add_parent(self, parent, *args, **kwargs):
        """
        Adds a parent
        """
        return parent.add_child(self, **kwargs)

    def remove_child(self, descendant):
        """
        Removes a child
        """
        self.children.through.objects.get(
            parent=self, child=descendant).delete()

    def remove_parent(self, parent):
        """
        Removes a parent
        """
        parent.children.through.objects.get(parent=parent, child=self).delete()

    def descendants_graph(self):
        """
        Returns a graph-like structure with progeny
        TODO: This one as to be improved to be more efficient. make a lot of query on big graph
        """
        graph = {}
        for f in self.children.all():
            graph[f] = f.descendants_graph()
        return graph

    def ancestors_graph(self):
        """
        Returns a graph-like structure with ancestors
        TODO: This one as to be improved to be more efficient. make a lot of query on big graph
        """
        graph = {}
        for f in self.parents():
            graph[f] = f.ancestors_graph()
        return graph

    def descendants(self, direct=False):
        """
        Returns a queryset of descendants
        """
        if direct is True:
            edges = self.children.through.objects.filter(Q(parent=self) & Q(etype="direct"))
            return self.children.filter(vertex_parents__in=edges)
        return self.children

    def ancestors(self, direct=False):
        """
        Returns a set of ancestors
        """
        if direct is True:
            edges = self.children.through.objects.filter(Q(child=self) & Q(etype="direct"))
            return self.parents.filter(vertex_childs__in=edges)
        return self.parents
  
    def descendants_edges_set(self, cached_results=None):
        """
        Returns a set of descendants edges
        """
        if cached_results is None:
            cached_results = dict()
        if self in cached_results.keys():
            return cached_results[self]
        else:
            res = set()
            for f in self.children.all():
                res.add((self, f))
                res.update(
                    f.descendants_edges_set(cached_results=cached_results))
            cached_results[self] = res
            return res

    def ancestors_edges_set(self, cached_results=None):
        """
        Returns a set of ancestors edges
        """
        if cached_results is None:
            cached_results = dict()
        if self in cached_results.keys():
            return cached_results[self]
        else:
            res = set()
            for f in self.parents:
                res.add((f, self))
                res.update(
                    f.ancestors_edges_set(cached_results=cached_results))
            cached_results[self] = res
            return res

    def vertices_set(self):
        """
        Retrun a set of all vertices
        """
        vertices = set()
        vertices.add(self)
        vertices.update(self.ancestors())
        vertices.update(self.descendants())
        return vertices

    def edges_set(self):
        """
        Returns a set of all edges
        """
        edges = set()
        edges.update(self.descendants_edges_set())
        edges.update(self.ancestors_edges_set())
        return edges

    # def distance(self, target):
        # """
        # Returns the shortest hops count to the target vertex
        # """
        # return len(self.path(target))

    # def path(self, target):
        # """
        # Returns the shortest path
        # """
        # if self == target:
            # return []
        # if target in self.children.all():
            # return [target]
        # if target in self.descendants_set():
            # path = None
            # for d in self.children.all():
                # try:
                    # desc_path = d.path(target)
                    # if not path or len(desc_path) < len(path):
                        # path = [d] + desc_path
                # except VertexNotReachableException:
                    # pass
        # else:
            # raise VertexNotReachableException
        # return path

    # def is_root(self):
        # """
        # Check if has children and not ancestors
        # """
        # return bool(self.children.exists() and not self._parents.exists())

    # def is_leaf(self):
        # """
        # Check if has ancestors and not children
        # """
        # return bool(self._parents.exists() and not self.children.exists())

    # def is_island(self):
        # """
        # Check if has no ancestors nor children
        # """
        # return bool(not self.children.exists() and not self._parents.exists())

    # def _get_roots(self, at):
        # """
        # Works on objects: no queries
        # """
        # if not at:
            # return set([self])
        # roots = set()
        # for a2 in at:
            # roots.update(a2._get_roots(at[a2]))
        # return roots

    # def get_roots(self):
        # """
        # Returns roots vertices, if any
        # """
        # at = self.ancestors_graph()
        # roots = set()
        # for a in at:
            # roots.update(a._get_roots(at[a]))
        # return roots

    # def _get_leaves(self, dt):
        # """
        # Works on objects: no queries
        # """
        # if not dt:
            # return set([self])
        # leaves = set()
        # for d2 in dt:
            # leaves.update(d2._get_leaves(dt[d2]))
        # return leaves

    # def get_leaves(self):
        # """
        # Returns leave vertex, if any
        # """
        # dt = self.descendants_graph()
        # leaves = set()
        # for d in dt:
            # leaves.update(d._get_leaves(dt[d]))
        # return leaves
    
    # def to_dict(self):

        # return self.__dict__
   

    
    @staticmethod
    def circular_checker(parent, child):
        """
        Checks that the object is not an ancestor, avoid self links
        """
        if parent == child:
            raise ValidationError('Self links are not allowed.')
        if child in parent.ancestors():
            raise ValidationError('The object is an ancestor.')


class EdgeBase(ToDictMixin, models.Model):
    __old_child_id = None
    __old_parent_id = None
    #Closure attribute see: https://www.codeproject.com/Articles/22824/A-Model-to-Represent-Directed-Acyclic-Graphs-DAG-o?msg=2449056
    # NOTE: Working with foreign key is to heavy, in particular in the admin interface
    entry_edge_id = models.IntegerField(null=True, blank=True)
    direct_edge_id = models.IntegerField(null=True, blank=True)
    exit_edge_id = models.IntegerField(null=True, blank=True)
    hops = models.IntegerField(default=0)
    etype = models.CharField(max_length=20, default="direct")

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(EdgeBase, self).__init__(*args, **kwargs)
        if self.parent_id:
            self.__old_parent_id = self.parent_id  # not self.parent.id to avoid extra query 
        if self.child_id:
            self.__old_child_id = self.child_id # idem as above

    def parent_has_changed(self):
        if self.__old_parent_id:
            return self.parent_id != self.__old_parent_id
        else:
            False
    
    def child_has_changed(self):
        if self.__old_child_id:
            return self.child_id != self.__old_child_id
        else:
            False
