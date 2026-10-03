"""Unit tests for core.py functionality"""

import datetime
import json
import unittest
from unittest.mock import patch

import core


class TestCore(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.today = datetime.date(2024, 10, 3)
        self.sample_deadlines = [
            {
                "id": "1",
                "title": "Midterm Exam",
                "course": "CS101",
                "date": "2024-10-15",
                "time": "14:00",
                "type": "exam",
                "est_hours": 8,
                "weight": 5,
                "confidence": "high",
                "notes": "Bring calculator",
                "source": "photo"
            },
            {
                "id": "2",
                "title": "Project Submission",
                "course": "CS101",
                "date": "2024-10-20",
                "time": None,
                "type": "project",
                "est_hours": 15,
                "weight": 4,
                "confidence": "medium",
                "notes": "Submit on portal",
                "source": "typed"
            }
        ]

    def test_parse_json_safely_valid(self):
        """Test parsing valid JSON with fences"""
        text = "Here are the results:\n```json\n[{\"title\": \"Test\", \"date\": \"2024-10-15\"}]\n```"
        result = core.parse_json_safely(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test')

    def test_parse_json_safely_prose(self):
        """Test parsing JSON with surrounding prose"""
        text = "I found these deadlines: [{\"title\": \"Test\", \"date\": \"2024-10-15\"}] that's all!"
        result = core.parse_json_safely(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test')

    def test_parse_json_safely_invalid(self):
        """Test handling of invalid JSON"""
        text = "This is not valid JSON: [invalid]"
        result = core.parse_json_safely(text)
        self.assertEqual(result, [])

    def test_parse_json_safely_empty(self):
        """Test handling of empty array"""
        text = "[]"
        result = core.parse_json_safely(text)
        self.assertEqual(result, [])

    def test_merge_deadlines(self):
        """Test deadline merging and deduplication"""
        existing = [
            {"title": "Test", "date": "2024-10-15", "confidence": "low"}
        ]
        new = [
            {"title": "Test", "date": "2024-10-15", "confidence": "high", "notes": "New note"}
        ]
        merged = core.merge_deadlines(existing, new)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['confidence'], 'high')
        self.assertEqual(merged[0]['notes'], 'New note')

    def test_urgency_label(self):
        """Test urgency label calculation"""
        # Overdue
        d = {"date": "2024-09-30"}
        label, days = core.urgency_label(d, self.today)
        self.assertEqual(label, "🔴")
        self.assertEqual(days, -3)

        # < 48 hours
        d = {"date": (self.today + datetime.timedelta(days=1)).isoformat()}
        label, days = core.urgency_label(d, self.today)
        self.assertEqual(label, "🔴")

        # 7 days
        d = {"date": (self.today + datetime.timedelta(days=7)).isoformat()}
        label, days = core.urgency_label(d, self.today)
        self.assertEqual(label, "🟠")

        # 14 days
        d = {"date": (self.today + datetime.timedelta(days=14)).isoformat()}
        label, days = core.urgency_label(d, self.today)
        self.assertEqual(label, "🟡")

        # Later
        d = {"date": (self.today + datetime.timedelta(days=21)).isoformat()}
        label, days = core.urgency_label(d, self.today)
        self.assertEqual(label, "🟢")

    def test_build_study_plan(self):
        """Test study plan generation"""
        deadlines = [
            {
                "title": "Exam",
                "date": "2024-10-10",
                "est_hours": 6,
                "weight": 5
            },
            {
                "title": "Assignment",
                "date": "2024-10-08",
                "est_hours": 4,
                "weight": 3
            }
        ]
        sessions, unschedulable = core.build_study_plan(
            deadlines, daily_max_hours=3, today=self.today
        )
        self.assertGreater(len(sessions), 0)
        self.assertEqual(len(unschedulable), 0)

    def test_find_crunch_days(self):
        """Test crunch day detection"""
        deadlines = [
            {"date": "2024-10-15", "est_hours": 10},
            {"date": "2024-10-16", "est_hours": 12},
            {"date": "2024-10-22", "est_hours": 5}
        ]
        crunch = core.find_crunch_days(deadlines)
        self.assertEqual(len(crunch), 1)
        self.assertEqual(crunch[0]["hours"], 22)

    def test_build_ics(self):
        """Test iCalendar generation"""
        ics = core.build_ics(self.sample_deadlines)
        self.assertIsInstance(ics, bytes)
        self.assertIn(b"BEGIN:VCALENDAR", ics)
        self.assertIn(b"VERSION:2.0", ics)
        self.assertIn(b"END:VCALENDAR", ics)

    def test_to_csv(self):
        """Test CSV export"""
        csv_data = core.to_csv(self.sample_deadlines)
        self.assertIsInstance(csv_data, bytes)
        decoded = csv_data.decode('utf-8')
        self.assertIn("id,title,course,date", decoded)
        self.assertIn("1,Midterm Exam,CS101,2024-10-15", decoded)

    def test_build_digest_text(self):
        """Test text digest building"""
        digest = core.build_digest_text("John", self.sample_deadlines, self.today)
        self.assertIn("Hello John", digest)
        self.assertIn("Midterm Exam", digest)
        self.assertIn("Project Submission", digest)

    def test_build_digest_html(self):
        """Test HTML digest building"""
        digest = core.build_digest_html("John", self.sample_deadlines, self.today)
        self.assertIn("<html>", digest)
        self.assertIn("Hello John", digest)
        self.assertIn("<table", digest)

    def test_escape_ics_text(self):
        """Test iCalendar text escaping"""
        escaped = core._escape_ics_text("test,;newline\n")
        self.assertEqual(escaped, "test\\,\\;newline\\n")


if __name__ == '__main__':
    unittest.main()