import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class Neo4jConnection:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

    def verify(self):
        self.driver.verify_connectivity()
        print("Neo4j connection successful!")

    def close(self):
        self.driver.close()


if __name__ == "__main__":

    connection = Neo4jConnection()

    try:
        connection.verify()
    finally:
        connection.close()