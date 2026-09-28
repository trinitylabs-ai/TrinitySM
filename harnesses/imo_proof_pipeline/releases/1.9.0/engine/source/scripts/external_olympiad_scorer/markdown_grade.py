"""Markdown serialization of the existing grade contract; no grading-policy change."""
from __future__ import annotations

import json
import re

from .contract import SCHEMA, validate_grade

FIELDS=("Score","Verdict","Answer Supported","Dependency Impact","Repair Complexity",
        "Olympiad Treatment","First Issue","Summary","Strengths","Errors")
OUTPUT_INSTRUCTIONS="""Return only Markdown with exactly these level-one headings,
in this order. Do not emit JSON or wrap the response in a code fence.
# Score
One integer from 0 to 7.
# Verdict
pass, minor_gap, substantial_gap, major_gap, or incorrect
# Answer Supported
true or false
# Dependency Impact
none, local, or load_bearing
# Repair Complexity
none, routine_direct, local_nontrivial, or new_idea
# Olympiad Treatment
full_credit, minor_deduction, partial_credit, or major_deduction
# First Issue
A nonempty description; use NONE if there is no issue.
# Summary
A nonempty concise justification of the grade.
# Strengths
NONE, or one-line Markdown bullets.
# Errors
NONE, or one-line bullets formatted as - severity: description.
Allowed severities: cosmetic, minor, substantial, major.
"""


def parse(text):
    text=text.replace("\r\n","\n").strip()
    pieces=re.split(r"(?m)^# ([^\n]+)\n",text)
    if pieces[0] or pieces[1::2]!=list(FIELDS):
        raise ValueError("grade requires the ten Markdown sections in order")
    fields=dict(zip(FIELDS,[value.strip() for value in pieces[2::2]],strict=True))
    if not re.fullmatch(r"[0-7]",fields["Score"]): raise ValueError("invalid Markdown score")
    if fields["Answer Supported"] not in {"true","false"}: raise ValueError("invalid supported flag")
    result={name.lower().replace(" ","_"):value for name,value in fields.items()}
    result["score"]=int(result["score"])
    result["answer_supported"]=result["answer_supported"]=="true"
    for name in ("strengths","errors"):
        value=result[name]
        if value=="NONE": result[name]=[];continue
        lines=value.splitlines()
        if not lines or any(not line.startswith("- ") or not line[2:].strip() for line in lines):
            raise ValueError("grade lists require Markdown bullets or NONE")
        result[name]=[line[2:].strip() for line in lines]
    errors=[]
    for item in result["errors"]:
        severity,sep,description=item.partition(": ")
        if not sep or not description: raise ValueError("error requires severity: description")
        errors.append({"severity":severity,"description":description})
    result["errors"]=errors
    schema=json.loads(SCHEMA.read_text())
    for name,definition in schema["properties"].items():
        if "enum" in definition and result[name] not in definition["enum"]:
            raise ValueError("invalid enum for "+name)
    if not result["first_issue"] or not result["summary"]: raise ValueError("empty grade explanation")
    return validate_grade(result)
