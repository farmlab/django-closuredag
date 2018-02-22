
-- nodeFrom integer := 6;
-- nodeTo integer := 5;
-- new_edge_id integer := 4;

-- INSERT INTO dag_relation ( parent_id, child_id, hops, value_rel)   VALUES (5, 7, 0, 99)
--UPDATE dag_relation SET entry_Edge_id = 4, exit_edge_id = 4, direct_edge_id = 4 WHERE id = 4

---INSERT INTO dag_relation(entry_edge_id, direct_edge_id, exit_edge_id, parent_id, child_id, hops, etype, value_rel) 
-- Incoming edges.
      SELECT id as entry_edge_id, 4 as direct_edge_id, 4 AS exit_edge_id, dr.parent_id AS parent_id, 5 AS child_id, dr.hops + 1 AS hops, 'in' AS etype, 999 AS value_rel
      FROM dag_relation as dr
      WHERE dr.child_id = 6

UNION

-- Outcoming edges.
      SELECT 4 as entry_edge_id, 4 as direct_edge_id, id AS exit_edge_id, 6 AS parent_id, dr.child_id AS child_id, dr.hops + 1 AS hops, 'out' AS etype, 999 AS value_rel
      FROM dag_relation as dr
      WHERE dr.parent_id = 5

UNION

-- Incoming to outgoing.
	SELECT drA.id as entry_edge_id, 4 as direct_edge_id, drB.id AS exit_edge_id, drA.parent_id AS parent_id, drB.child_id AS child_id, drA.hops + drB.hops + 1 AS hops, 'inout' AS etype, 999 AS value_rel
	FROM dag_relation as drA
	CROSS JOIN dag_relation drB
	WHERE drA.child_id = 6
	AND drB.parent_id = 5
