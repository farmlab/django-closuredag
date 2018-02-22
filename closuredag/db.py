from django.conf import settings
from django.db import connection

import logging

logger = logging.getLogger(__name__)

ENGINE = settings.DATABASES['default']['ENGINE']
POSTGRES = 'django.db.backends.postgresql_psycopg2'
MYSQL = ''

def sql_to_add(table):
    if ENGINE == POSTGRES:
        from psycopg2 import sql
        return sql.SQL("""
            INSERT INTO {0}(entry_edge_id, direct_edge_id, exit_edge_id, parent_id, child_id, hops, etype, value_rel)
            
            -- Incoming edges.
            SELECT id as entry_edge_id, %(newEdgeId)s as direct_edge_id, %(newEdgeId)s AS exit_edge_id, dr.parent_id AS parent_id, %(nodeTo)s AS child_id, dr.hops + 1 AS hops, 'in' AS etype, 999 AS value_rel
            FROM {0} as dr
            WHERE dr.child_id = %(nodeFrom)s

            UNION

            -- Outcoming edges.
            SELECT %(newEdgeId)s as entry_edge_id, %(newEdgeId)s as direct_edge_id, id AS exit_edge_id, %(nodeFrom)s AS parent_id, dr.child_id AS child_id, dr.hops + 1 AS hops, 'out' AS etype, 999 AS value_rel
            FROM {0} as dr
            WHERE dr.parent_id = %(nodeTo)s

            UNION

            -- Incoming to outgoing.
                SELECT drA.id as entry_edge_id, %(newEdgeId)s as direct_edge_id, drB.id AS exit_edge_id, drA.parent_id AS parent_id, drB.child_id AS child_id, drA.hops + drB.hops + 1 AS hops, 'inout' AS etype, 999 AS value_rel
                FROM {0} AS drA
                CROSS JOIN {0} drB
                WHERE drA.child_id = %(nodeFrom)s
                AND drB.parent_id = %(nodeFrom)s
                """).format(sql.Identifier(table))
    else:
        return None


def add_closure_edge(instance, sender):
    param = {
            'nodeFrom': instance.parent_id,
            'nodeTo': instance.child_id,
            'newEdgeId': instance.id
            }

    try:
        sql_str = sql_to_add(sender._meta.db_table)
        cursor = connection.cursor()
        cursor.execute(sql_str,param)
    except NotImplementedError as e:
        logger.info("closure not supported with this engine ({0}), {1}".format(ENGINE, e))


def sql_to_delete(table):
    if ENGINE == POSTGRES: 
        from psycopg2 import sql
        return sql.SQL("""
            DELETE FROM {0} WHERE id IN ( 
                WITH RECURSIVE purge AS (
                	SELECT dr.id
                	FROM {0} as dr
                	WHERE dr.direct_edge_id = %(del_edge_id)s
                UNION
                	SELECT dr.id
                	FROM {0} as dr
                	INNER JOIN purge ON dr.entry_edge_id = purge.id AND dr.exit_edge_id = purge.id
                	WHERE dr.hops > 0
                )
                SELECT * FROM purge
                WHERE id != %(del_edge_id)s
                )
            """).format(sql.Identifier(table))
    else:
        return None


def delete_closure_edge(instance, sender):
    param = {
              'del_edge_id': instance.id
            }
    try:
        sql_str = sql_to_delete(sender._meta.db_table)
        cursor = connection.cursor()
        cursor.execute(sql_str,param)
    except NotImplementedError as e:
        logger.info("closure not supported with this engine ({0}), {1}".format(ENGINE, e))


def update_closure_edge(instance, sender):
    delete_closure_edge(instance, sender)
    add_closure_edge(instance, sender)
