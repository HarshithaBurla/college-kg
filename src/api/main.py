
import json
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai

from src.graph.neo4j_connection import Neo4jConnection

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

gemini = genai.Client(api_key=api_key)

app = FastAPI(
    title="College Knowledge Graph API",
    description="Gemini-powered dynamic question answering using Neo4j",
    version="2.0.0",
)


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


def get_schema(session):
    """Read the current Neo4j graph structure."""

    nodes = session.run("""
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels, keys(n) AS properties
        LIMIT 100
    """).data()

    relationships = session.run("""
        MATCH (a)-[r]->(b)
        RETURN DISTINCT labels(a) AS source,
               type(r) AS relationship,
               labels(b) AS target
        LIMIT 100
    """).data()

    return (
        "NODE LABELS AND PROPERTIES:\n"
        + json.dumps(nodes, default=str)
        + "\nRELATIONSHIPS:\n"
        + json.dumps(relationships, default=str)
    )


def generate_query(question, schema):
    prompt = f"""
You convert natural-language questions into read-only Neo4j Cypher.

Use only the schema below. Never invent node labels, properties,
or relationship types.

SCHEMA:
{schema}

QUESTION:
{question}

Rules:
- Return one Cypher query only, with no Markdown.
- Use MATCH, OPTIONAL MATCH, UNWIND, or WITH as the starting clause.
- Never modify the database.
- Never use CREATE, MERGE, SET, DELETE, REMOVE, DROP, CALL,
  LOAD CSV, APOC, USE, SHOW, or administrative commands.
- For list questions, return useful fields and use LIMIT 100.
- For count questions, return a count.
- Match names case-insensitively when appropriate.
- Use actual relationships in the schema to answer relationship questions.
- Do not guess missing information.
"""

    response = gemini.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    query = (response.text or "").strip()
    query = re.sub(r"^```(?:cypher)?\s*", "", query, flags=re.I)
    query = re.sub(r"\s*```$", "", query).strip()
    return query.rstrip(";").strip()


def validate_query(query):
    """Basic checks before running generated Cypher."""

    if not query:
        raise ValueError("Gemini returned an empty query.")

    if ";" in query or "--" in query or "/*" in query:
        raise ValueError("Query rejected by safety checks.")

    if not re.match(
        r"^(MATCH|OPTIONAL\s+MATCH|UNWIND|WITH)\b",
        query,
        flags=re.I,
    ):
        raise ValueError("Query rejected by safety checks.")

    forbidden = re.compile(
        r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|ALTER|"
        r"GRANT|DENY|CALL|LOAD|APOC|USE|SHOW|TERMINATE|"
        r"START|STOP|FOREACH)\b",
        flags=re.I,
    )

    if forbidden.search(query):
        raise ValueError("Query rejected by safety checks.")

    if not re.search(r"\bLIMIT\s+\d+\b", query, flags=re.I):
        query += " LIMIT 100"

    return query


def safe_value(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [safe_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): safe_value(v) for k, v in value.items()}
    return str(value)


def make_answer(question, rows):
    if not rows:
        return "No matching information was found in the knowledge graph."

    prompt = f"""
Answer the question using only the database results below.
Do not invent facts. If the results are incomplete, say so.
Give a concise, clear answer.

QUESTION:
{question}

DATABASE RESULTS:
{json.dumps(rows, ensure_ascii=False, default=str)[:18000]}
"""

    response = gemini.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return (response.text or "").strip() or (
        f"Found {len(rows)} matching record(s)."
    )


@app.get("/")
def home():
    return {
        "message": "Gemini-powered College Knowledge Graph API is running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(item: Question):
    question = item.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Enter a question.")

    conn = Neo4jConnection()

    try:
        with conn.driver.session() as session:
            schema = get_schema(session)
            query = validate_query(generate_query(question, schema))
            records = session.run(query).data()

            rows = [
                {
                    str(key): safe_value(value)
                    for key, value in record.items()
                }
                for record in records
            ]

        answer = make_answer(question, rows)

        return {
            "question": question,
            "answer": answer,
            "cypher": query,
            "rows": rows,
            "answers": [answer],
            "count": len(rows),
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        print(
            f"Question processing failed: "
            f"{type(error).__name__}: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Question processing failed. Check the API terminal, "
                "Gemini model availability, API quota, and Neo4j connection."
            ),
        )

    finally:
        conn.close()
