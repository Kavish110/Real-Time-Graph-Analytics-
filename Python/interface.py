from neo4j import GraphDatabase
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

 
    def bfs(self, start_node, last_node):
        if isinstance(last_node, int):
            last_node = [last_node]
        # check if the passed node is list of last nodes or not


        with self._driver.session() as session:
            paths = []

            for last in last_node:
                
                answer = (
                    "MATCH (start {name: $start}), (end {name: $last}) "
                    "MATCH path = shortestPath((start)-[*..]-(end)) "
                    "RETURN [node IN nodes(path) | node {name: node.name}] AS path"
                )
                result = session.run(answer, start=start_node, last=last )
                
                for record in result:
                    paths.append({"path": record["path"]})

            return paths



    def pagerank(self, max_iterations=20, weight_property=None):
        with self._driver.session() as session:

    
            # Create a graph projection
            session.run("""
                CALL gds.graph.project(
                    'myGraph',
                    'Location',
                    {
                        TRIP: {
                            properties: ['distance']
                        }
                    }
                )
            """)

            # Run PageRank algorithm
            result = session.run(f"""
                CALL gds.pageRank.stream('myGraph', {{
                    maxIterations: {max_iterations},
                    dampingFactor: 0.85,
                    relationshipWeightProperty: '{weight_property}'
                }})
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC
            """)

            # Collect results
            score = [{"name": record["name"], "score": record["score"]} for record in result]

            # Find max and min PageRank
            max_score = max(score, key=lambda x: x["score"])
            min_score = min(score, key=lambda x: x["score"])

            answer=[max_score,min_score]
            session.run("""
                CALL gds.graph.drop('myGraph') YIELD graphName;
            """)
            return answer


    

    
