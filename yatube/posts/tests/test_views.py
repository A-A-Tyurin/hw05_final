import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from common_lib.testutils import AppViewsTestBase
from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, Follow

User = get_user_model()
TEST_USER_NAME = 'TestUser'
TEST_GROUP_SLUG = 'test-group-slug'


class PostsViewsTests(TestCase, AppViewsTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create_user(username=TEST_USER_NAME)

        cls.user_following = User.objects.create_user(
            username=f'{TEST_USER_NAME}Follower'
        )

        cls.post_following = Post.objects.create(
            text='Текст тестового поста для подписки',
            author=cls.user_following
        )

        Follow.objects.create(user=cls.user, author=cls.user_following)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
            slug=TEST_GROUP_SLUG,
        )

        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            description='Описание другой тестовой группы',
            slug=f'another-{TEST_GROUP_SLUG}',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Текст тестового поста',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )

        cls.test_config = [
            {
                'url': reverse('index'),
                'context_names_obj_types': [
                    ('posts', Post),
                    ('page', Page)
                ],
                'excepted_objs': [cls.post],
                'login_required': None
            },
            {
                'url': reverse('follow_index'),
                'context_names_obj_types': [
                    ('posts', Post),
                    ('page', Page)
                ],
                'excepted_objs': [cls.post_following],
                'login_required': True
            },
            {
                'url': reverse('group', kwargs={'slug': TEST_GROUP_SLUG}),
                'context_names_obj_types': [
                    ('posts', Post),
                    ('group', Group),
                    ('page', Page)
                ],
                'excepted_objs': [cls.post, cls.group],
                'login_required': None
            },
            {
                'url': reverse('profile', kwargs={'username': TEST_USER_NAME}),
                'context_names_obj_types': [
                    ('posts', Post),
                    ('author', User),
                    ('page', Page)
                ],
                'excepted_objs': [cls.post, cls.post.author],
                'login_required': None
            },
            {
                'url': reverse(
                    'post', kwargs={
                        'username': TEST_USER_NAME,
                        'post_id': cls.post.id
                    }
                ),
                'context_names_obj_types': [
                    ('post', Post), ('comment_form', CommentForm)
                ],
                'excepted_objs': [cls.post],
                'login_required': None
            },
            {
                'url': reverse('post_new'),
                'context_names_obj_types': [('form', PostForm)],
                'excepted_objs': None,
                'login_required': True
            },
            {
                'url': reverse(
                    'post_edit', kwargs={
                        'username': TEST_USER_NAME,
                        'post_id': cls.post.id
                    }
                ),
                'context_names_obj_types': [('form', PostForm)],
                'excepted_objs': None,
                'login_required': True
            }
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_another_group_page_post_with_group(self):
        response = self.guest_client.get(
            reverse(
                'group', kwargs={'slug': self.another_group.slug}
            )
        )

        self.assertNotIn(self.post, response.context.get('posts'))

    def test_index_page_cache(self):
        start_response = self.guest_client.get(reverse('index'))

        Post.objects.create(
            text='Текст еще одного тестового поста',
            group=self.group,
            author=self.user
        )

        response_from_cache = self.guest_client.get(reverse('index'))
        self.assertEqual(start_response.content, response_from_cache.content)

        cache.clear()

        response_cache_clear = self.guest_client.get(reverse('index'))
        self.assertNotEqual(
            response_from_cache.content, response_cache_clear.content
        )

    def test_user_unfollow(self):
        unfollow_link = reverse(
            'profile_unfollow', kwargs={
                'username': self.user_following.username
            }
        )

        response = self.authorized_client.get(unfollow_link, follow=True)

        self.assertRedirects(
            response, reverse('profile', kwargs={
                'username': self.user_following.username
            })
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user, author=self.user_following
            ).exists()
        )

    def test_user_follow(self):
        follow_link = reverse(
            'profile_follow', kwargs={
                'username': self.user_following.username
            }
        )

        response = self.authorized_client.get(follow_link, follow=True)

        self.assertRedirects(
            response, reverse('profile', kwargs={
                'username': self.user_following.username
            })
        )

        self.assertTrue(
            Follow.objects.filter(
                user=self.user, author=self.user_following
            ).exists()
        )

    def test_follow_index_page_for_not_follower(self):
        self.authorized_client.force_login(self.user_following)
        response = self.authorized_client.get(reverse('follow_index'))

        self.assertNotIn(
            self.post_following, response.context.get('posts')
        )
