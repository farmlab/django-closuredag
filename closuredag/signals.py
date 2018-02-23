
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from closuredag.models import EdgeBase
from closuredag.db import add_closure_edge, delete_closure_edge, update_closure_edge

import logging

logger = logging.getLogger(__name__)



@receiver(post_save)
def add_closure(sender, instance, created, **kwargs):
    if issubclass(sender, EdgeBase):
        logger.debug( "Post_save EdgeBase")
        
        # add additionnal attribute
        if created and instance.hops == 0 :    
            logger.debug("updating closure attribute")
            instance.entry_edge_id = instance.id
            instance.direct_edge_id = instance.id
            instance.exit_edge_id = instance.id
            
            # new closure edge
            add_closure_edge(instance, sender)
            
            instance.save()
            

        # update closure edge
        if created and (instance.parent_has_changed() or instance.child_has_changed()):
            logger.debug("updating closure edge")
            update_closure_edge(instance, sender) 


@receiver(pre_delete)
def delete_closure(sender, instance, **kwargs):
    if issubclass(sender, EdgeBase):
        logger.debug( "Pre_delete EdgeBase: delete closure edge")
        delete_closure_edge(instance, sender)
