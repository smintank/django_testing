from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.templatetags.pytils_translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogic(TestCase):
    NOTE = {'title': 'title', 'text': 'text', 'slug': 'slug'}
    NEW_NOTE = {'title': 'new_title', 'text': 'new_text', 'slug': 'new_slug'}

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User1')
        cls.another_user = User.objects.create(username='User2')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.user)
        cls.auth_another_client = Client()
        cls.auth_another_client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title=cls.NOTE.get('title'),
            text=cls.NOTE.get('text'),
            author=cls.user,
            slug=cls.NOTE.get('slug'),
        )
        cls.create_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

    def test_user_cant_edit_note_of_another_user(self):
        response = self.auth_another_client.post(self.edit_url, self.NEW_NOTE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE.get('title'))
        self.assertEqual(self.note.text, self.NOTE.get('text'))
        self.assertEqual(self.note.slug, self.NOTE.get('slug'))

    def test_user_can_edit_own_note(self):
        response = self.auth_user_client.post(self.edit_url, self.NEW_NOTE)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE.get('title'))
        self.assertEqual(self.note.text, self.NEW_NOTE.get('text'))
        self.assertEqual(self.note.slug, self.NEW_NOTE.get('slug'))

    def test_user_cant_delete_note_of_another_user(self):
        response = self.auth_another_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_delete_own_note(self):
        response = self.auth_user_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_user_client.post(self.create_url, self.NEW_NOTE)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        note = Note.objects.last()
        self.assertEqual(note.title, self.NEW_NOTE.get('title'))
        self.assertEqual(note.text, self.NEW_NOTE.get('text'))
        self.assertEqual(note.slug, self.NEW_NOTE.get('slug'))

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.create_url, self.NEW_NOTE)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_unique_slug(self):
        response = self.auth_user_client.post(self.create_url, self.NOTE)
        warning = self.NOTE.get('slug') + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=warning
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        data = self.NEW_NOTE.copy()
        data.pop('slug')
        response = self.auth_user_client.post(self.create_url, data=data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        new_note = Note.objects.last()
        expected_slug = slugify(self.NEW_NOTE.get('title'))
        self.assertEqual(new_note.slug, expected_slug)
