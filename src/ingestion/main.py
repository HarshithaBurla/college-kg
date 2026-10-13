
from fastapi import FastAPI
from pydantic import BaseModel
from src.graph.neo4j_connection import Neo4jConnection

app = FastAPI(
    title="College Knowledge Graph API",
    description="Question-answering API powered by Neo4j",
    version="1.0.0",
)


class Question(BaseModel):
    question: str


def search_graph(question: str):
    q = question.lower()
    conn = Neo4jConnection()

    try:
        with conn.driver.session() as session:

            if "department" in q:
                query = """
                MATCH (d:Department)
                RETURN d.name AS answer
                ORDER BY answer
                """

            elif "subject" in q or "course" in q:
                query = """
                MATCH (s)
                WHERE s:Subject OR s:Course
                RETURN DISTINCT coalesce(s.name, s.course_title, s.code) AS answer
                ORDER BY answer
                """

            elif "faculty" in q or "teacher" in q or "professor" in q:
                query = """
                MATCH (f:Faculty)
                RETURN f.name AS answer
                ORDER BY answer
                """

            elif "student" in q:
                query = """
                MATCH (s:Student)
                RETURN s.name AS answer
                ORDER BY answer
                """

            elif "program" in q or "degree" in q:
                query = """
                MATCH (p:Program)
                RETURN p.name AS answer
                ORDER BY answer
                """

            elif "college" in q or "name" in q:
                query = """
                MATCH (c:College)
                RETURN c.name AS answer
                """

            else:
                return [
                    "Try asking about departments, courses, faculty, students, programs, or the college."
                ]

            return [
                record["answer"]
                for record in session.run(query)
                if record["answer"] is not None
            ]

    finally:
        conn.close()


@app.get("/")
def home():
    return {"message": "College Knowledge Graph API is running"}


@app.post("/ask")
def ask_question(item: Question):
    answers = search_graph(item.question)

    return {
        "question": item.question,
        "answers": answers,
        "count": len(answers),
    }
