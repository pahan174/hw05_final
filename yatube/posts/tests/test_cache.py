import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_empty = Group.objects.create(
            title='Пустая группа',
            slug='empty_slug',
            description='Описаний пустой группы',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()
        # авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # клиент тестового автора
        self.author_client = Client()
        self.author_client.force_login(CacheTest.post.author)

    def test_cache(self):
        '''Тестирование кэша'''
        response = self.authorized_client.get(reverse('posts:main'))
        responce_one = response.content
        self.post.delete()

        response_after_delete = self.authorized_client.get(reverse(
            'posts:main'
        ))
        responce_two = response_after_delete.content
        self.assertEqual(responce_one, responce_two)
