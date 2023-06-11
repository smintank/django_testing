from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import WARNING, BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    url = reverse('news:detail', args=news_id)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client, author, news_id, news, form_data
):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_id):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(comment_id, news_id, author_client):
    news_url = reverse('news:detail', args=news_id)
    url = reverse('news:delete', args=comment_id)
    response = author_client.delete(url)
    assertRedirects(response, f'{news_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, comment_id):
    url = reverse('news:delete', args=comment_id)
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client, comment, comment_id, news_id, form_data
):
    news_url = reverse('news:detail', args=news_id)
    url = reverse('news:edit', args=comment_id)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment_id, form_data, comment
):
    url = reverse('news:edit', args=comment_id)
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
