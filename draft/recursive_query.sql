WITH RECURSIVE graph AS (
SELECT dn.id, 0 AS depth
FROM dag_node as dn
WHERE dn.id = 4
UNION
SELECT dr.child_id as id, 0 as depth
		FROM dag_node as dn
		JOIN dag_relation AS dr ON dn.id = dr.parent_id
		JOIN graph ON graph.id = dr.parent_id
		) SELECT * FROM graph
