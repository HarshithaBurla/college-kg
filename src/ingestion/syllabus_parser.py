
import csv
import re
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/pdf_text/R-20 Syllabus(27-6-2024).txt"
)
OUTPUT_FILE = Path("data/processed/syllabus_courses.csv")

FIELDNAMES = [
    "semester",
    "course_code",
    "course_title",
    "lecture_hours",
    "practical_hours",
    "internal_marks",
    "exam_marks",
    "credits",
    "category",
]

SEMESTERS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]

EXPECTED_COUNTS = {
    "I": 9,
    "II": 10,
    "III": 10,
    "IV": 10,
    "V": 9,
    "VI": 9,
    "VII": 8,
    "VIII": 1,
}

# Course codes appearing in the R-20 CSE syllabus.
CODE_PATTERN = re.compile(
    r"^(CS/IT\s*MC\d+|CS/IT\d{3}|CSSL\d+|CS\d{3})\s*(.*)$",
    re.IGNORECASE,
)

# Course row ends with L, P, Internal, Exam, Credits,
# and an optional Category.
TAIL_PATTERN = re.compile(
    r"(?P<lecture>-|\d+(?:\.\d+)?)\s+"
    r"(?P<practical>-|\d+(?:\.\d+)?)\s+"
    r"(?P<internal>-|\d+(?:\.\d+)?)\s+"
    r"(?P<exam>-|\d+(?:\.\d+)?)\s+"
    r"(?P<credits>-|\d+(?:\.\d+)?)"
    r"(?:\s+(?P<category>BS|ES|HS|PC|SC|MC|PE|OE|PR))?\s*$",
    re.IGNORECASE,
)

SEMESTER_PATTERN = re.compile(
    r"Semester\s*[-–—]?\s*"
    r"(VIII|VII|VI|V|IV|III|II|I)\b",
    re.IGNORECASE,
)

# Lines that are not course records.
IGNORE_PATTERN = re.compile(
    r"^("
    r"S\.?\s*No|Course Code|Course Title|Hours Per Week|"
    r"Scheme of Examination|Category|TOTAL\b|"
    r"Basic Science|Engineering Science|Professional Core|"
    r"Professional Elective Course|Professional Elective Courses|"
    r"Open Elective|Open / Job|Skill Oriented|Skill Advanced|"
    r"Industrial/Research Internship|Project/Term Paper|"
    r"Humanities and Social Science|Internship of|"
    r"Internship minimum|Registration for|"
    r"\(R-20\)|B\.Tech/CSE/|RVR & JC|Department of|"
    r"R20 Regulations"
    r")",
    re.IGNORECASE,
)


def clean(value):
    """Normalize whitespace and PDF text artifacts."""
    value = value.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", value).strip()


def parse_content(content, semester, code):
    """Parse one course's title and numeric columns."""
    content = clean(content)
    match = TAIL_PATTERN.search(content)

    if not match:
        return None

    title = clean(content[:match.start()])
    values = match.groupdict()

    if not title:
        return None

    # Read the category extracted from the syllabus.
    category = (values["category"] or "").upper()

    # The source syllabus identifies Project Work as category PR.
    # Its category may be missed because the PDF text is split
    # across lines, so apply this specific correction.
    normalized_code = code.upper().replace(" ", "")

    if normalized_code == "CS/IT461" and not category:
        category = "PR"

    return {
        "semester": semester,
        "course_code": re.sub(r"\s+", " ", code).upper(),
        "course_title": title,
        "lecture_hours": values["lecture"],
        "practical_hours": values["practical"],
        "internal_marks": values["internal"],
        "exam_marks": values["exam"],
        "credits": values["credits"],
        "category": category,
    }


def extract_courses(text):
    """Extract course records from the syllabus text."""
    courses = []
    current_semester = None
    pending_code = None
    pending_content = []

    def save_pending():
        """Save the pending course if it can be parsed."""
        nonlocal pending_code, pending_content

        if pending_code is None or current_semester is None:
            return

        content = clean(" ".join(pending_content))

        course = parse_content(
            content,
            current_semester,
            pending_code,
        )

        if course:
            courses.append(course)
        elif content:
            print(
                f"WARNING: Could not parse Semester "
                f"{current_semester}: {pending_code} | {content}"
            )

        pending_code = None
        pending_content = []

    for raw_line in text.splitlines():
        line = clean(raw_line)

        if not line:
            continue

        # Ignore page markers.
        if line.startswith("--- Page"):
            continue

        # Detect semester headings before processing courses.
        semester_match = SEMESTER_PATTERN.search(line)

        if semester_match:
            save_pending()
            current_semester = semester_match.group(1).upper()
            continue

        if current_semester is None:
            continue

        # Stop after the Semester VIII curriculum table.
        if current_semester == "VIII" and re.match(
            r"^TOTAL\b", line, re.IGNORECASE
        ):
            save_pending()
            break

        if IGNORE_PATTERN.match(line):
            continue

        # Support both:
        # 1 CS/IT111 ...
        # CS/IT461 on a separate line
        serial_match = re.match(r"^\d+\s+(.+)$", line)
        remainder = serial_match.group(1) if serial_match else line

        code_match = CODE_PATTERN.match(remainder)

        if code_match:
            # Finish the previous course before starting another.
            save_pending()

            pending_code = clean(code_match.group(1))
            pending_content = [clean(code_match.group(2))]

            # Save immediately if the row is already complete.
            course = parse_content(
                " ".join(pending_content),
                current_semester,
                pending_code,
            )

            if course:
                courses.append(course)
                pending_code = None
                pending_content = []

            continue

        # Course titles and numeric columns may span several lines.
        if pending_code is not None:
            # Avoid attaching unrelated page headers to a course.
            if line.startswith(
                (
                    "(R-20)",
                    "B.Tech/CSE/",
                    "RVR & JC",
                    "Department of",
                )
            ):
                save_pending()
                continue

            pending_content.append(line)

            # Save when the numeric columns are complete.
            course = parse_content(
                " ".join(pending_content),
                current_semester,
                pending_code,
            )

            if course:
                courses.append(course)
                pending_code = None
                pending_content = []

    else:
        # Save the final pending course if the loop ends normally.
        save_pending()

    # Deduplicate by semester and course code.
    unique_courses = []
    seen = set()

    for course in courses:
        key = (course["semester"], course["course_code"])

        if key not in seen:
            seen.add(key)
            unique_courses.append(course)

    return unique_courses


def main():
    if not INPUT_FILE.exists():
        print(f"ERROR: Input text file not found: {INPUT_FILE}")
        print("Run the PDF text extraction script first.")
        return

    text = INPUT_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )

    courses = extract_courses(text)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FIELDNAMES,
        )
        writer.writeheader()
        writer.writerows(courses)

    print(f"\nUnique course rows: {len(courses)}")
    print(f"Saved: {OUTPUT_FILE}")
    print("\nRows by semester:")

    all_counts_match = True

    for semester in SEMESTERS:
        count = sum(
            1
            for course in courses
            if course["semester"] == semester
        )

        expected = EXPECTED_COUNTS[semester]
        status = "OK" if count == expected else "CHECK"

        if count != expected:
            all_counts_match = False

        print(
            f"Semester {semester}: {count} "
            f"(expected {expected}) - {status}"
        )

    print("\nSemester VIII courses:")

    semester_viii_courses = [
        course
        for course in courses
        if course["semester"] == "VIII"
    ]

    if semester_viii_courses:
        for course in semester_viii_courses:
            print(
                f'{course["course_code"]} | '
                f'{course["course_title"]} | '
                f'credits: {course["credits"]} | '
                f'category: {course["category"]}'
            )
    else:
        print("No Semester VIII courses found.")

    if all_counts_match and len(courses) == 66:
        print("\nAll expected semester counts match.")
        print("Review the CSV contents before importing into Neo4j.")
    else:
        print("\nSome semester counts still need correction.")
        print("Do not import this CSV into Neo4j yet.")


if __name__ == "__main__":
    main()
