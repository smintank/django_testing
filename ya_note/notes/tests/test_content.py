from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):


    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Main_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.another_user = User.objects.create(username='Another_user')
        cls.note = Note.objects.create(
            title='Title', text='text', author=cls.user, slug='slug'
        )
        cls.list_url = reverse('notes:list')

    def test_user_sees_own_notes(self):
        self.client.force_login(self.another_user)
        response = self.client.get(self.list_url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_login_user_get_forms(self):
        urls_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)

    def test_get_correct_context(self):
        response = self.auth_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)