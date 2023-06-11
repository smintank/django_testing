import pytest
from django.conf import settings
from django.urls import reverse


def test_news_order(author_client, bulk_of_news):
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    all_dates = [bulk_of_news.date for bulk_of_news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_news_count(author_client, bulk_of_news):
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_order(author_client, news_id, comment, second_comment):
    url = reverse('news:detail', args=news_id)
    response = author_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form_to_user',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    )
)
@pytest.mark.django_db
def test_client_has_form(news_id, parametrized_client, form_to_user):
    url = reverse('news:detail', args=news_id)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_to_user
