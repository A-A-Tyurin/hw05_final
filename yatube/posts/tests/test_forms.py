import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
TEST_USER_NAME = 'TestUser'
TEST_GROUP_SLUG = 'test-group-slug'

LOGIN_URL = reverse('login')


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create_user(username=TEST_USER_NAME)

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_new(self):
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Текст нового тестового поста',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

        post = Post.objects.first()

        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image.name, 'posts/small.gif')

    def test_post_edit(self):
        post_new = Post.objects.create(
            text='Текст тестового поста',
            author=self.user
        )

        form_data = {
            'text': 'Измененный текст тестового поста'
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': TEST_USER_NAME,
                'post_id': post_new.id
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'post', kwargs={
                    'username': TEST_USER_NAME,
                    'post_id': post_new.id
                }
            )
        )

        post_edit = Post.objects.get(
            text=form_data['text'],
            author__username=TEST_USER_NAME
        )
        self.assertEquals(post_new.id, post_edit.id)

    def test_post_new_anonymous(self):
        form_data = {
            'text': 'Текст нового тестового поста',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True
        )
        link = reverse('post_new')
        self.assertRedirects(
            response,
            f'{LOGIN_URL}?next={link}'
        )

    def test_post_comment_anonymous(self):
        form_data = {
            'text': 'Текст комментария к посту',
        }
        post_kwargs = {
            'username': TEST_USER_NAME,
            'post_id': self.post.id
        }
        link = reverse('add_comment', kwargs=post_kwargs)
        response = self.guest_client.post(
            link,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, f'{LOGIN_URL}?next={link}')
