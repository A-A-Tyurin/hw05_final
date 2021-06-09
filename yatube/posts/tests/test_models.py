from django.contrib.auth import get_user_model
from django.test import TestCase

from common_lib.testutils import AppModelsTestBase
from posts.models import Group, Post

User = get_user_model()
TEST_GROUP_SLUG = 'test-group-slug'
TEST_USER_NAME = 'TestUser'


class PostsModelsTest(TestCase, AppModelsTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user = User.objects.create_user(username=TEST_USER_NAME)

        group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
            slug=TEST_GROUP_SLUG,
        )

        post = Post.objects.create(
            text='Текст тестового поста' * 10,
            group=group,
            author=user
        )

        cls.test_config = [
            {
                'obj': post,
                'excepted_str': post.text[:15],
                'verbose_names': {
                    'text': 'Текст'
                },
                'help_text': {
                    'text': 'Опишите суть поста'
                }
            },
            {
                'obj': group,
                'excepted_str': group.title,
                'verbose_names': {
                    'title': 'Заголовок группы',
                    'slug': 'Адрес для страницы группы',
                    'description': 'Описание'
                },
                'help_text': {
                    'title': 'Дайте короткое название группе',
                    'slug': ('Укажите адрес для страницы задачи. '
                             'Используйте только латиницу, цифры, '
                             'дефисы и знаки подчёркивания'),
                    'description': 'Напишите описание группы'
                }
            }
        ]
