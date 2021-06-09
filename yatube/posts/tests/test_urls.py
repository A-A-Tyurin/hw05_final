from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from common_lib.testutils import AppUrlsTestBase
from posts.models import Group, Post

User = get_user_model()
TEST_GROUP_SLUG = 'test-group-slug'
TEST_USER_NAME = 'TestUser'


class PostsUrlsTests(TestCase, AppUrlsTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username=TEST_USER_NAME)

        cls.not_author = User.objects.create_user(
            username=f'{TEST_USER_NAME}_1'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
            slug=TEST_GROUP_SLUG,
        )

        cls.post = Post.objects.create(
            text='Текст тестового поста',
            group=cls.group,
            author=cls.user
        )

        cls.urls = [
            {
                'url': reverse('index'),
                'link': '/',
                'login_required': None,
                'template': 'posts_view.html'
            },
            {
                'url': reverse('post_new'),
                'link': '/new/',
                'login_required': True,
                'template': 'post_form.html'
            },
            {
                'url': reverse('group', kwargs={'slug': TEST_GROUP_SLUG}),
                'link': f'/group/{TEST_GROUP_SLUG}/',
                'login_required': None,
                'template': 'posts_view.html'
            },
            {
                'url': reverse('profile', kwargs={'username': TEST_USER_NAME}),
                'link': f'/{TEST_USER_NAME}/',
                'login_required': None,
                'template': 'posts_view.html'
            },
            {
                'url': reverse('post', kwargs={
                    'username': TEST_USER_NAME,
                    'post_id': cls.post.id
                }),
                'link': f'/{TEST_USER_NAME}/{cls.post.id}/',
                'login_required': None,
                'template': 'post_view.html'
            },
            {
                'url': reverse('post_edit', kwargs={
                    'username': TEST_USER_NAME,
                    'post_id': cls.post.id
                }),
                'link': f'/{TEST_USER_NAME}/{cls.post.id}/edit/',
                'login_required': True,
                'template': 'post_form.html'
            },
        ]

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_edit_page_redirect_not_author(self):
        self.authorized_client.force_login(self.not_author)

        link = reverse('post_edit', kwargs={
            'username': TEST_USER_NAME,
            'post_id': self.post.id
        })

        response = self.authorized_client.get(link, follow=True)
        self.assertRedirects(
            response, reverse('post', kwargs={
                'username': TEST_USER_NAME,
                'post_id': self.post.id
            })
        )

    def test_404_page(self):
        response = self.guest_client.get('/address-non-exists-page/')
        self.assertEqual(response.status_code, 404)
