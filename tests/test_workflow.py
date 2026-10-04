from agents.graph import investigation_graph


complaint = """
My name is Rahul Sharma. Yesterday at around 8 PM,
while I was returning home near Central Market, Nagpur,
a man on a motorcycle snatched my mobile phone from my hand
and drove away. The phone is a Samsung Galaxy worth about
25000 rupees.
"""


result = investigation_graph.invoke(
    {
        "complaint_text": complaint,
        "agent_trace": [],
    }
)


print()
print("=" * 60)
print("FINAL AGENT RESULT")
print("=" * 60)

print()
print("STATUS:")
print(result.get("status"))

print()
print("CRIME CATEGORY:")
print(result.get("crime_category"))

print()
print("CONFIDENCE:")
print(result.get("crime_confidence"))

print()
print("MISSING INFORMATION:")
print(result.get("missing_information"))

print()
print("LEGAL SECTIONS:")
for section in result.get("legal_sections", []):
    print(
        f"{section.get('act_code')} "
        f"{section.get('section_number')} - "
        f"{section.get('section_title')}"
    )

print()
print("FIR NARRATIVE:")
print(result.get("fir_narrative"))

print()
print("AGENT TRACE:")
for item in result.get("agent_trace", []):
    print("-", item)

print()
print("=" * 60)