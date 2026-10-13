
import pandas as pd
from src.graph.neo4j_connection import Neo4jConnection


def load_departments(connection, csv_path):
    data = pd.read_csv(csv_path)
    rows = data.fillna("").to_dict(orient="records")

    query = """
    MATCH (c:College {id: 'COL001'})
    UNWIND $rows AS row
    MERGE (d:Department {id: row.id})
    SET d.name = row.name,
        d.description = row.description
    MERGE (c)-[:HAS_DEPARTMENT]->(d)
    """

    with connection.driver.session() as session:
        session.run(query, rows=rows).consume()

    print(f"Loaded {len(rows)} departments.")


def load_programs(connection, csv_path):
    data = pd.read_csv(csv_path)
    rows = data.fillna("").to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    MATCH (d:Department {id: row.department_id})
    MERGE (p:Program {id: row.id})
    SET p.name = row.name,
        p.degree = row.degree,
        p.duration_years = toInteger(row.duration_years)
    MERGE (d)-[:HAS_PROGRAM]->(p)
    WITH p
    MATCH (c:College {id: 'COL001'})
    MERGE (c)-[:OFFERS_PROGRAM]->(p)
    """

    with connection.driver.session() as session:
        session.run(query, rows=rows).consume()

    print(f"Loaded {len(rows)} programs.")


def load_subjects(connection, csv_path):
    data = pd.read_csv(csv_path)
    rows = data.fillna("").to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    MATCH (d:Department {id: row.department_id})
    MATCH (p:Program {id: row.program_id})
    MERGE (s:Subject {id: row.id})
    SET s.name = row.name,
        s.credits = toInteger(row.credits)
    MERGE (d)-[:HAS_SUBJECT]->(s)
    MERGE (s)-[:PART_OF]->(p)
    """

    with connection.driver.session() as session:
        session.run(query, rows=rows).consume()

    print(f"Loaded {len(rows)} subjects.")


def load_faculty(connection, csv_path):
    data = pd.read_csv(csv_path)
    rows = data.fillna("").to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    MATCH (d:Department {id: row.department_id})
    MERGE (f:Faculty {id: row.id})
    SET f.name = row.name,
        f.email = row.email,
        f.designation = row.designation
    MERGE (f)-[:WORKS_IN]->(d)
    """

    with connection.driver.session() as session:
        session.run(query, rows=rows).consume()

    print(f"Loaded {len(rows)} faculty members.")


def main():
    connection = Neo4jConnection()

    try:
        connection.verify()

        load_departments(connection, "data/csv/departments.csv")
        load_programs(connection, "data/csv/programs.csv")
        load_subjects(connection, "data/csv/subjects.csv")
        load_faculty(connection, "data/csv/faculty.csv")

        print("CSV ingestion completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
