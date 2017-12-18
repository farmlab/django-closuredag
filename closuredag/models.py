# -*- coding: utf-8 -*-
"""
A class to model hierarchies of objects following
Directed Acyclic Graph structure.

"""

from django.db import models
from django.core.exceptions import ValidationError

from closuredag.exceptions import VertexNotReachableException


class VertexBase(object):
    """
    Main vertex abstract model
    """

    class Meta:
        ordering = ('-id', )

    def __unicode__(self):
        return u"# %s" % self.pk

    def __str__(self):
        return self.__unicode__()

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

    def parents(self):
        """
        Returns all elements which have 'self' as a direct descendant
        """
        return self.__class__.objects.filter(children=self)

    def descendants_tree(self):
        """
        Returns a tree-like structure with progeny
        TODO: This one as to be improved to be more efficient. make a lot of query on big graph
        """
        tree = {}
        for f in self.children.all():
            tree[f] = f.descendants_tree()
        return tree

    def ancestors_tree(self):
        """
        Returns a tree-like structure with ancestors
        TODO: This one as to be improved to be more efficient. make a lot of query on big graph
        """
        tree = {}
        for f in self.parents():
            tree[f] = f.ancestors_tree()
        return tree

    def descendants_set(self, cached_results=None):
        """
        Returns a set of descendants
        """
        if cached_results is None:
            cached_results = dict()
        if self in cached_results.keys():
            return cached_results[self]
        else:
            res = set()
            for f in self.children.all():
                res.add(f)
                res.update(f.descendants_set(cached_results=cached_results))
            cached_results[self] = res
            return res

    def ancestors_set(self, cached_results=None):
        """
        Returns a set of ancestors
        """
        if cached_results is None:
            cached_results = dict()
        if self in cached_results.keys():
            return cached_results[self]
        else:
            res = set()
            for f in self.parents():
                res.add(f)
                res.update(f.ancestors_set(cached_results=cached_results))
            cached_results[self] = res
            return res

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
            for f in self.parents():
                res.add((f, self))
                res.update(
                    f.ancestors_edges_set(cached_results=cached_results))
            cached_results[self] = res
            return res

    def vertexs_set(self):
        """
        Retrun a set of all vertexs
        """
        vertexs = set()
        vertexs.add(self)
        vertexs.update(self.ancestors_set())
        vertexs.update(self.descendants_set())
        return vertexs

    def edges_set(self):
        """
        Returns a set of all edges
        """
        edges = set()
        edges.update(self.descendants_edges_set())
        edges.update(self.ancestors_edges_set())
        return edges

    def distance(self, target):
        """
        Returns the shortest hops count to the target vertex
        """
        return len(self.path(target))

    def path(self, target):
        """
        Returns the shortest path
        """
        if self == target:
            return []
        if target in self.children.all():
            return [target]
        if target in self.descendants_set():
            path = None
            for d in self.children.all():
                try:
                    desc_path = d.path(target)
                    if not path or len(desc_path) < len(path):
                        path = [d] + desc_path
                except VertexNotReachableException:
                    pass
        else:
            raise VertexNotReachableException
        return path

    def is_root(self):
        """
        Check if has children and not ancestors
        """
        return bool(self.children.exists() and not self._parents.exists())

    def is_leaf(self):
        """
        Check if has ancestors and not children
        """
        return bool(self._parents.exists() and not self.children.exists())

    def is_island(self):
        """
        Check if has no ancestors nor children
        """
        return bool(not self.children.exists() and not self._parents.exists())

    def _get_roots(self, at):
        """
        Works on objects: no queries
        """
        if not at:
            return set([self])
        roots = set()
        for a2 in at:
            roots.update(a2._get_roots(at[a2]))
        return roots

    def get_roots(self):
        """
        Returns roots vertexs, if any
        """
        at = self.ancestors_tree()
        roots = set()
        for a in at:
            roots.update(a._get_roots(at[a]))
        return roots

    def _get_leaves(self, dt):
        """
        Works on objects: no queries
        """
        if not dt:
            return set([self])
        leaves = set()
        for d2 in dt:
            leaves.update(d2._get_leaves(dt[d2]))
        return leaves

    def get_leaves(self):
        """
        Returns leaves vertexs, if any
        """
        dt = self.descendants_tree()
        leaves = set()
        for d in dt:
            leaves.update(d._get_leaves(dt[d]))
        return leaves

    @staticmethod
    def circular_checker(parent, child):
        """
        Checks that the object is not an ancestor, avoid self links
        """
        if parent == child:
            raise ValidationError('Self links are not allowed.')
        if child in parent.ancestors_set():
            raise ValidationError('The object is an ancestor.')
