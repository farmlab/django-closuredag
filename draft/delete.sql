-- edge to remove: 4
DELETE FROM dag_relation WHERE id IN ( 
	WITH RECURSIVE purge AS (
		SELECT dr.id
		FROM dag_relation as dr
		WHERE dr.direct_edge_id = 4
	UNION
		SELECT dr.id
		FROM dag_relation as dr
		INNER JOIN purge ON dr.entry_edge_id = purge.id AND dr.exit_edge_id = purge.id
		WHERE dr.hops > 0
	)
	SELECT * FROM purge
	WHERE id != 4
	)

		
