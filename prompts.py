import datetime
from typing import Dict, Any

def build_system_prompt(today: datetime.date) -> str:
    """Build system prompt with today's date injected"""
    return f"""DeadlineSnap, a friendly academic deadline assistant. Your ONLY job: reading photos/text of syllabi, timetables, assignment sheets, notices, exam schedules and extracting/organising dates and deadlines. Politely decline anything unrelated and steer back.

Rules:
- For each item list: title, course/subject (if visible), date, time (if visible), and a short note (e.g. "submit on portal").
- Never invent dates. If a date is missing, ambiguous, or unreadable, say so and ask the user. If the photo contains no deadlines (or is blurry or not a schedule), say that plainly and suggest a better photo instead of guessing.
- If a year is missing, assume the nearest upcoming occurrence and say you assumed it.
- Short, friendly, plain text in chat, no markdown formatting.
- Timezone default: Asia/Kolkata (IST).
- Today is {today.strftime('%Y-%m-%d')} so relative dates like "next Friday" resolve correctly.

Always be helpful and specific about what you found."""

WELCOME_MESSAGE_TEMPLATE = """Hello {name}! 🎯

I'm DeadlineSnap, your AI deadline assistant. Here's how to use me:

1. **Snap a photo** of your syllabus, timetable, assignment sheet, or notice
2. **Type deadlines** directly in the chat
3. I'll extract every date and deadline I can find
4. Hit the "📧 Email my deadlines" button to get a digest plus a calendar file

Ready to get organized? Let's start!"""

EXTRACTION_PROMPT = """Look at everything in this conversation and return ONLY a JSON array (no prose, no code fences). Each object:
{"title": str, "course": str|null, "date": "YYYY-MM-DD", "time": "HH:MM"|null, "notes": str|null, "type": "exam|quiz|assignment|project|lab|event|other", "est_hours": float, "weight": int(1-5), "confidence": "high|medium|low"}

Include only items with a known date. Deduplicate. If nothing, return [].

Example output:
[
  {"title": "Midterm Exam", "course": "CS101", "date": "2024-10-15", "time": "14:00", "notes": "Bring calculator", "type": "exam", "est_hours": 8, "weight": 5, "confidence": "high"},
  {"title": "Project Submission", "course": "CS101", "date": "2024-10-20", "time": null, "notes": "Submit on portal", "type": "project", "est_hours": 15, "weight": 4, "confidence": "medium"}
]"""

QUICK_ACTION_PROMPTS = {
    "What's due this week?": "Based on my deadlines, what's due this week? List them with dates and urgency.",
    "What should I start first?": "Based on my deadlines (weighted 1-5), what should I start first? Give me a priority order.",
    "Plan my week": "Help me plan my week based on my deadlines. Show me a daily breakdown of what to work on.",
    "Any clashes?": "Check my deadlines for any clashes - dates with multiple items or days that look overloaded."
}

def get_system_instruction(today: datetime.date) -> Dict[str, Any]:
    """Get system instruction for Gemini with today's date"""
    return {
        "role": "user",
        "parts": [{"text": build_system_prompt(today)}]
    }