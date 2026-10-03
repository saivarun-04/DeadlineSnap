"""Core logic for DeadlineSnap.

All pure functions are placed here so they can be unit‑tested without any Streamlit or Gemini dependencies.
"""

import datetime
import json
import csv
import io
import html
from typing import List, Dict, Any, Optional, Tuple

# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

def parse_json_safely(text: str) -> List[Dict[str, Any]]:
    """Extract a JSON array from Gemini output.

    Gemini may wrap the JSON in code fences or add prose before/after.
    This function finds the first '[' and the matching ']' and attempts
    ``json.loads`` on that slice. If parsing fails, an empty list is returned.
    """
    start = text.find('[')
    end = text.rfind(']')
    if start == -1 or end == -1 or end <= start:
        return []
    candidate = text[start : end + 1]
    try:
        data = json.loads(candidate)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        return []
    return []

# ---------------------------------------------------------------------------
# Deadline merging / deduplication
# ---------------------------------------------------------------------------

def _normalize_key(item: Dict[str, Any]) -> Tuple[str, str]:
    """Return a tuple used for deduplication: (title.lower(), date)."""
    title = str(item.get("title", "")).strip().lower()
    date = item.get("date", "")
    return (title, date)

def merge_deadlines(existing: List[Dict[str, Any]], new_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge *new_items* into *existing*.

    - Items are deduplicated on (title, date).
    - If a duplicate exists, the existing entry is kept *unless* the new
      entry has a higher ``confidence`` (high > medium > low) or provides
      fields that are ``None`` in the existing record.
    - Each item gets a unique ``id`` (UUID4 string) if not already present.
    """
    import uuid

    # Build lookup for existing items
    lookup: Dict[Tuple[str, str], Dict[str, Any]] = { _normalize_key(it): it for it in existing }

    confidence_rank = {"high": 3, "medium": 2, "low": 1}

    for item in new_items:
        # Ensure required keys exist
        if not item.get("title") or not item.get("date"):
            continue
        key = _normalize_key(item)
        if key in lookup:
            existing_item = lookup[key]
            # Prefer higher confidence
            new_conf = confidence_rank.get(item.get("confidence", "low"), 1)
            old_conf = confidence_rank.get(existing_item.get("confidence", "low"), 1)
            if new_conf > old_conf:
                existing_item.update(item)
            else:
                # Fill missing fields only
                for k, v in item.items():
                    if existing_item.get(k) in (None, "") and v not in (None, ""):
                        existing_item[k] = v
        else:
            # Assign an id
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            lookup[key] = item
    # Return list sorted by date then time
    merged = list(lookup.values())
    def sort_key(it: Dict[str, Any]):
        dt = it.get("date", "9999-12-31")
        tm = it.get("time") or "00:00"
        return f"{dt} {tm}"
    merged.sort(key=sort_key)
    return merged

# ---------------------------------------------------------------------------
# Urgency labeling
# ---------------------------------------------------------------------------

def urgency_label(deadline: Dict[str, Any], today: datetime.date) -> Tuple[str, int]:
    """Return an emoji label and days left for *deadline*.

    - Overdue or <48h: 🔴
    - ≤7 days: 🟠
    - ≤14 days: 🟡
    - Else: 🟢
    """
    try:
        d = datetime.datetime.strptime(deadline["date"], "%Y-%m-%d").date()
    except Exception:
        return ("⚪", 0)
    delta = (d - today).days
    if delta < 0 or delta < 2:
        return ("🔴", delta)
    if delta <= 7:
        return ("🟠", delta)
    if delta <= 14:
        return ("🟡", delta)
    return ("🟢", delta)

# ---------------------------------------------------------------------------
# Study plan builder
# ---------------------------------------------------------------------------

def build_study_plan(
    deadlines: List[Dict[str, Any]],
    daily_max_hours: float,
    today: datetime.date,
    start_buffer_days: int = 0,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Create a study plan.

    Returns a tuple ``(sessions, unschedulable)`` where *sessions* is a list of
    dicts with ``date``, ``title`` and ``hours`` and *unschedulable* contains the
    original deadline items that could not be fitted.
    """
    # Sort by weight descending, then earliest deadline first
    items = sorted(
        deadlines,
        key=lambda d: (-int(d.get("weight", 1)), d.get("date")),
    )
    # Map date -> remaining hours
    plan: Dict[datetime.date, float] = {}
    sessions: List[Dict[str, Any]] = []
    unschedulable: List[Dict[str, Any]] = []

    for item in items:
        est = float(item.get("est_hours", 1))
        due = datetime.datetime.strptime(item["date"], "%Y-%m-%d").date()
        # Work backwards from due date, respecting buffer and today
        day = due - datetime.timedelta(days=1)  # start the day before deadline
        while est > 0 and day >= today + datetime.timedelta(days=start_buffer_days):
            remaining = plan.get(day, daily_max_hours)
            if remaining > 0:
                allocate = min(remaining, est, 2.0)  # max 2h per session
                plan[day] = remaining - allocate
                sessions.append({
                    "date": day.isoformat(),
                    "title": item["title"],
                    "hours": allocate,
                })
                est -= allocate
            day -= datetime.timedelta(days=1)
        if est > 0:
            unschedulable.append(item)
    # Sort sessions chronologically
    sessions.sort(key=lambda s: s["date"])
    return sessions, unschedulable

# ---------------------------------------------------------------------------
# Crunch day detector
# ---------------------------------------------------------------------------

def find_crunch_days(deadlines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a list of weeks (ISO week dict) that are overloaded.

    A week is considered a crunch if it contains 2+ deadlines *and* the sum of
    ``est_hours`` exceeds 20.
    """
    week_info: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for d in deadlines:
        try:
            date_obj = datetime.datetime.strptime(d["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        iso_year, iso_week, _ = date_obj.isocalendar()
        key = (iso_year, iso_week)
        info = week_info.setdefault(key, {"count": 0, "hours": 0.0, "sample_dates": []})
        info["count"] += 1
        info["hours"] += float(d.get("est_hours", 0))
        info["sample_dates"].append(date_obj.isoformat())
    crunch_weeks = []
    for (y, w), info in week_info.items():
        if info["count"] >= 2 and info["hours"] > 20:
            crunch_weeks.append({
                "year": y,
                "week": w,
                "deadlines": info["count"],
                "hours": round(info["hours"], 1),
                "sample_dates": info["sample_dates"][:3],
            })
    return crunch_weeks

# ---------------------------------------------------------------------------
# Digest builders (text & HTML)
# ---------------------------------------------------------------------------

def build_digest_text(name: str, deadlines: List[Dict[str, Any]], today: datetime.date) -> str:
    """Plain‑text digest used for email fallback.
    """
    lines = [f"Hello {name},", "", "Here is a summary of your upcoming deadlines:", ""]
    for d in deadlines:
        label, days = urgency_label(d, today)
        line = f"{label} {d['date']}"
        if d.get('time'):
            line += f" {d['time']}"
        line += f" – {d['title']}"
        if d.get('course'):
            line += f" ({d['course']})"
        if d.get('notes'):
            line += f" – {d['notes']}"
        lines.append(line)
    lines.append("")
    lines.append("Best of luck with your studies! – DeadlineSnap")
    return "\n".join(lines)

def build_digest_html(name: str, deadlines: List[Dict[str, Any]], today: datetime.date) -> str:
    """HTML version of the digest with simple inline CSS.
    """
    rows = []
    for d in deadlines:
        label, _ = urgency_label(d, today)
        colour = {
            "🔴": "#ff4d4d",
            "🟠": "#ffae42",
            "🟡": "#ffd700",
            "🟢": "#90ee90",
        }.get(label, "#e0e0e0")
        rows.append(f"""
        <tr style='background:{colour}'>
            <td>{html.escape(d.get('date',''))}</td>
            <td>{html.escape(d.get('time') or '')}</td>
            <td>{html.escape(d.get('title',''))}</td>
            <td>{html.escape(d.get('course') or '')}</td>
            <td>{html.escape(d.get('notes') or '')}</td>
        </tr>
        """)
    table = "\n".join(rows)
    html_body = f"""
    <html><body>
    <p>Hello {html.escape(name)},</p>
    <p>Here is a summary of your upcoming deadlines:</p>
    <table style='border-collapse:collapse;width:100%'>
        <thead>
            <tr><th>Date</th><th>Time</th><th>Title</th><th>Course</th><th>Notes</th></tr>
        </thead>
        <tbody>{table}</tbody>
    </table>
    <p>Best of luck with your studies!<br/>– DeadlineSnap</p>
    </body></html>
    """
    return html_body

# ---------------------------------------------------------------------------
# .ics builder
# ---------------------------------------------------------------------------

def _escape_ics_text(text: str) -> str:
    """Escape commas, semicolons and newlines for iCalendar.
    """
    return text.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;').replace('\n', '\\n')

def build_ics(deadlines: List[Dict[str, Any]], include_study: bool = False, study_sessions: Optional[List[Dict[str, Any]]] = None) -> bytes:
    """Create an iCalendar file.

    *deadlines* are rendered as VEVENTs. If *include_study* is True and
    *study_sessions* is provided, those are added as separate events with the
    summary "Study: <title>".
    """
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//DeadlineSnap//EN"]
    now = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    def add_event(uid: str, dtstart: str, summary: str, description: str = "", dtend: Optional[str] = None, alarm_minutes: int = 1440):
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{now}")
        lines.append(f"DTSTART:{dtstart}")
        if dtend:
            lines.append(f"DTEND:{dtend}")
        lines.append(f"SUMMARY:{_escape_ics_text(summary)}")
        if description:
            lines.append(f"DESCRIPTION:{_escape_ics_text(description)}")
        # 1‑day reminder by default, can be overridden later
        lines.append("BEGIN:VALARM")
        lines.append(f"TRIGGER:-PT{alarm_minutes}M")
        lines.append("ACTION:DISPLAY")
        lines.append(f"DESCRIPTION:Reminder for {_escape_ics_text(summary)}")
        lines.append("END:VALARM")
        lines.append("END:VEVENT")
    # deadlines
    for d in deadlines:
        uid = f"deadline-{d.get('id', d.get('title','')).replace(' ', '_')}@deadlinesnap"
        date = d["date"]
        time = d.get("time")
        if time:
            dtstart = f"{date.replace('-','')}T{time.replace(':','')}00"
            dtend = dtstart  # same moment event
        else:
            dtstart = f"{date.replace('-','')}"
            dtend = None
        summary = f"{d.get('title','')} ({d.get('course','')})".strip()
        add_event(uid, dtstart, summary, d.get('notes',''), dtend)
    # study sessions
    if include_study and study_sessions:
        for s in study_sessions:
            uid = f"study-{s['date']}-{s['title'].replace(' ', '_')}@deadlinesnap"
            dtstart = f"{s['date'].replace('-','')}T090000"  # 9am default start
            dtend = f"{s['date'].replace('-','')}T{(9 + int(s['hours'])):02d}0000"
            add_event(uid, dtstart, f"Study: {s['title']}", alarm_minutes=60)
    lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(lines) + "\r\n"
    return ics_content.encode('utf-8')

# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def to_csv(deadlines: List[Dict[str, Any]]) -> bytes:
    """Return a CSV representation (UTF‑8) of *deadlines*.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "title", "course", "date", "time", "type", "est_hours", "weight", "confidence", "notes", "source"
    ])
    writer.writeheader()
    for d in deadlines:
        writer.writerow({k: d.get(k, "") for k in writer.fieldnames})
    return output.getvalue().encode('utf-8')
