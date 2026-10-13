
import pandas as pd
from src.graph.neo4j_connection import Neo4jConnection

CSV_FILE = "data/processed/syllabus_courses.csv"

def main():
    df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

    connection = Neo4jConnection()
    try:
        connection.verify()

        with connection.driver.session() as session:
            session.run(
                """
                MERGE (p:Program {id: $program_id})
                ON CREATE SET
                    p.name = $program_name,
                    p.degree = 'B.Tech',
                    p.duration_years = 4
                """,
                program_id="P001",
                program_name="B.Tech Computer Science and Engineering",
            )

            result = session.run(
                """
                UNWIND $rows AS row
                MERGE (c:Course {code: row.course_code})
                SET c.name = row.course_title,
                    c.semester = row.semester,
                    c.lecture_hours = row.lecture_hours,
                    c.practical_hours = row.practical_hours,
                    c.internal_marks = row.internal_marks,
                    c.exam_marks = row.exam_marks,
                    c.credits = row.credits,
                    c.category = row.category
                WITH c
                MATCH (p:Program {id: $program_id})
                MERGE (c)-[:PART_OF]->(p)
                RETURN count(c) AS processed
                """,
                rows=df.to_dict(orient="records"),
                program_id="P001",
            )

            print("Course records processed:", result.single()["processed"])

        print("Syllabus course import completed.")

    finally:
        connection.close()

if __name__ == "__main__":
    main()
