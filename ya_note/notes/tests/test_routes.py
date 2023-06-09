from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User')
        cls.another_user = User.objects.create(username='Another_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.another_user)
        cls.note = Note.objects.create(title='title', text='text', author=cls.user)
        cls.urls_status = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )

    def test_page_availability_for_everyone(self):
        for name in 'users:login', 'users:logout', 'users:signup', 'notes:home':
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_edit_and_delete_for_another_client(self):
        for name in 'notes:edit', 'notes:delete':
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_and_delete_for_login_client(self):
        self.client.force_login(self.user)
        for name, args in self.urls_status:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anon_client(self):
        login_url = reverse('users:login')
        for name, args in self.urls_status:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)



