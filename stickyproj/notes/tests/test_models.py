import time

from django.test import TestCase
from django.urls import reverse
from notes.models import Note


class NoteModelTest(TestCase):
    """Unit tests for the Note model"""

    def setUp(self):
        """Create a sample note for testing"""
        self.note = Note.objects.create(
            title="Test Note",
            content="This is a test note"
        )

    def test_note_creation(self):
        """Test that a Note instance is successfully created"""
        self.assertEqual(self.note.title, "Test Note")
        self.assertEqual(self.note.content, "This is a test note")
        self.assertIsNotNone(self.note.timestamp)

    def test_note_str_representation(self):
        """Test the string representation of a Note"""
        expected_str = f"Test Note ({self.note.timestamp:%Y-%m-%d %H:%M}"
        self.assertEqual(str(self.note), expected_str)

    def test_note_ordering(self):
        """Test that newer notes appear first according to timestamp descending."""
        first = self.note  # Created in setUp()
        time.sleep(0.001) # tiny pause (1ms) to ensure distinct timestamps
        second = Note.objects.create(title="Second Note", content="Another note")
        notes = list(Note.objects.all())

        # The most recent note should appear first
        self.assertEqual(notes[0], second)
        self.assertEqual(notes[1], first)


class NoteViewsTest(TestCase):
    """Unit tests for Note views"""

    def setUp(self):
        """Set up a note to test view-related behaviour"""
        self.note = Note.objects.create(title="View Note", content="Content for view testing")

    def test_note_list_view(self):
        """Test that the note list view returns a 200 response and contains note data"""
        response = self.client.get(reverse('notes:note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Note")
        self.assertTemplateUsed(response, 'notes/note_list.html')

    def test_note_detail_view(self):
        """Test that the note detail view displays the correct note"""
        response = self.client.get(reverse('notes:note_detail', kwargs={'pk': self.note.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.content)
        self.assertTemplateUsed(response, 'notes/note_detail.html')

    def test_note_create_view(self):
        """Test creating a new note through the create view"""
        response = self.client.post(reverse('notes:note_create'), {
            'title': 'New Note',
            'content': 'Created via test client'
        })
        self.assertEqual(response.status_code, 302) # Redirect after success
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_note_delete_view(self):
        """Test deleting a note through the delete view"""
        response = self.client.post(reverse('notes:note_delete', kwargs={'pk': self.note.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
