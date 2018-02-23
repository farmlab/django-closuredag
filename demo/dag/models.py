from django.db import models
from closuredag.factories import vertex_factory, edge_factory
from closuredag.models import VertexBase
from django.core import urlresolvers


import logging
logger = logging.getLogger(__name__)


class Node(vertex_factory('Relation')):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = 'nodes'


    def __str__(self):
        return '{}-{}({})'.format(self._meta.model_name, self.name, self.id)

    def get_admin_url(self):
        return urlresolvers.reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.id,))

    def to_dict(self):
        data = super(Node,self).to_dict()
        data['href'] = self.get_admin_url()
        data['type'] = self._meta.model_name
        return data


class Relation(edge_factory('Node', concrete=False)):
    """
    Minimal node relation 
    """
    value_rel= models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return '{}->{}'.format(self.parent_id, self.child_id)


class NodeOne(Node):
    value_one = models.CharField(max_length=32, default=99)

    class Meta:
        verbose_name = 'node one'
        verbose_name_plural = 'nodes one'


class NodeTwo(Node):
    value_two = models.CharField(max_length=32, default=99)

    class Meta:
        verbose_name = 'node two'
        verbose_name_plural = 'nodes two'
