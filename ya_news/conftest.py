from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def bulk_of_news():
    today = datetime.today()
    bulk_of_news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return bulk_of_news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    return comment


@pytest.fixture
def second_comment(news, author):
    now = timezone.now()
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Tекст комментария 2'
    )
    comment.created = now + timedelta(hours=1)
    comment.save()
    return comment


@pytest.fixture
def comment_id(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {'text': NEW_COMMENT_TEXT}
