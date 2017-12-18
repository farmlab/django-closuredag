#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_closuredag
------------

Tests for `closuredag` models module.
"""
import multiprocessing

from django.test import TestCase
from django.db.models import CharField
from django.shortcuts import render_to_response
from django.core.exceptions import ValidationError

from closuredag.factories import vertex_factory, edge_factory
from tests.graph_test_output import expected_graph_output


class ConcreteVertex(vertex_factory('ConcreteEdge')):
    """
    Test vertex, adds just one field
    """
    name = CharField(max_length=32)

    def __str__(self):
        return '# %s' % self.name

    class Meta:
        app_label = 'closuredag'


class ConcreteEdge(edge_factory('ConcreteVertex', concrete=False)):
    """
    Test edge, adds just one field
    """
    name = CharField(max_length=32, blank=True, null=True)

    class Meta:
        app_label = 'closuredag'


class ClosuredagTestCase(TestCase):
    def setUp(self):
        for i in range(1, 11):
            ConcreteVertex(name="%s" % i).save()

    def test_01_objects_were_created(self):
        for i in range(1, 11):
            self.assertEqual(
                ConcreteVertex.objects.get(name="%s" % i).name, "%s" % i)

    def test_02_dag(self):
        # Get vertexs
        for i in range(1, 11):
            globals()["p%s" % i] = ConcreteVertex.objects.get(pk=i)

        # Creates a DAG
        p1.add_child(p5)
        p5.add_child(p7)

        graph = p1.descendants_graph()
        # {<ConcreteVertex: # 5>: {<ConcreteVertex: # 7>: {}}}
        self.assertIn(p5, graph)
        self.assertEqual(len(graph), 1)
        self.assertIn(p7, graph[p5])
        self.assertEqual(graph[p5][p7], {})

        l = [p.pk for p in p1.descendants_set()]
        l.sort()
        self.assertEqual(l, [5, 7])

        p1.add_child(p6)
        p2.add_child(p6)
        p3.add_child(p7)
        p6.add_child(p7)
        p6.add_child(p8)
        l = [p.pk for p in p2.descendants_set()]
        l.sort()
        self.assertEqual(l, [6, 7, 8])

        # ValidationError: [u'The object is a descendant.']
        # self.assertRaises(ValidationError, p2.add_child, p8)

        try:
            p2.add_child(p8)
        except ValidationError as e:
            self.assertEqual(e.message, 'The object is a descendant.')

        # Checks that p8 was not added two times
        l = [p.pk for p in p2.descendants_set()]
        l.sort()
        self.assertEqual(l, [6, 7, 8])

        p6.add_parent(p4)
        p9.add_parent(p3)
        p9.add_parent(p6)
        self.assertRaises(ValidationError, p9.add_child, p2)
        try:
            p9.add_child(p2)
        except ValidationError as e:
            self.assertEqual(e.message, 'The object is an ancestor.')

        graph = p1.descendants_graph()
        self.assertIn(p5, graph)
        self.assertIn(p6, graph)
        self.assertIn(p7, graph[p5])
        self.assertIn(p7, graph[p6])
        self.assertIn(p8, graph[p6])
        self.assertIn(p9, graph[p6])
        self.assertEqual(len(graph), 2)
        self.assertEqual(len(graph[p5]), 1)
        self.assertEqual(len(graph[p6]), 3)

        l = [p.pk for p in p1.descendants_set()]
        l.sort()
        self.assertEqual(l, [5, 6, 7, 8, 9])
        self.assertEqual(p1.distance(p8), 2)

        # Test additional fields for edge
        p9.add_child(p10, name='test_name')
        self.assertEqual(
            p9.children.through.objects.filter(child=p10)[0].name,
            u'test_name')

        self.assertEqual([p.name for p in p1.path(p7)], ['6', '7'])
        self.assertEqual([p.name for p in p1.path(p10)], ['6', '9', '10'])
        self.assertEqual(p1.distance(p7), 2)

        self.assertEqual([p.name for p in p1.get_leaves()], ['8', '10', '7'])
        self.assertEqual([p.name for p in p8.get_roots()], ['1', '2', '4'])

        self.assertTrue(p1.is_root())
        self.assertFalse(p1.is_leaf())
        self.assertFalse(p10.is_root())
        self.assertTrue(p10.is_leaf())
        self.assertFalse(p6.is_leaf())
        self.assertFalse(p6.is_root())

        self.assertRaises(ValidationError, p6.add_child, p6)
        try:
            p6.add_child(p6)
        except ValidationError as e:
            self.assertEqual(e.message, 'Self links are not allowed.')

        # Remove a link and test island
        p10.remove_parent(p9)
        self.assertFalse(p10 in p9.descendants_set())
        self.assertTrue(p10.is_island())

        self.assertEqual([p.name for p in p6.ancestors_set()], ['1', '2', '4'])

        p1.remove_child(p6)
        self.assertEqual([p.name for p in p6.ancestors_set()], ['2', '4'])

        self.assertFalse(p1 in p6.ancestors_set())

        # Testing the view
        response = render_to_response('graph.html',
                                      {'dag_list': ConcreteVertex.objects.all()})
        self.assertEqual(
            response.content.decode('utf-8'), expected_graph_output)

    def test_03_deep_dag(self):
        """
        Create a deep graph and check that graph operations run in a
        reasonable amount of time (linear in size of graph, not
        exponential).
        """

        def run_test():
            # There are on the order of 1 million paths through the graph, so
            # results for intermediate vertexs need to be cached
            n = 20

            for i in range(2 * n):
                ConcreteVertex(pk=i).save()

            # Create edges
            for i in range(0, 2 * n - 2, 2):
                p1 = ConcreteVertex.objects.get(pk=i)
                p2 = ConcreteVertex.objects.get(pk=i + 1)
                p3 = ConcreteVertex.objects.get(pk=i + 2)
                p4 = ConcreteVertex.objects.get(pk=i + 3)

                p1.add_child(p3)
                p1.add_child(p4)
                p2.add_child(p3)
                p2.add_child(p4)

            # Compute descendants of a root vertex
            ConcreteVertex.objects.get(pk=0).descendants_set()

            # Compute ancestors of a leaf vertex
            ConcreteVertex.objects.get(pk=2 * n - 1).ancestors_set()

            ConcreteVertex.objects.get(
                pk=0).add_child(ConcreteVertex.objects.get(pk=2 * n - 1))

        # Run the test, raising an error if the code times out
        p = multiprocessing.Process(target=run_test)
        p.start()
        p.join(10)
        if p.is_alive():
            p.terminate()
            p.join()
            raise RuntimeError('Graph operations take too long!')
