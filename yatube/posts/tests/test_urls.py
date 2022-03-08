from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слуг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()

        # авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # клиент тестового автора
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.post.author)

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_post_create_url_authorized_client(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_authorized_client(self):
        """Проверяем шаблон /create/ авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_url_exist_anonymous(self):
        """Проверяем доступность страниц для неавторизванных пользователей"""
        group = PostURLTests.group
        post = PostURLTests.post
        username = PostURLTests.user.username
        url_names = {
            '/': 200,
            f'/group/{group.slug}/': 200,
            f'/posts/{post.id}/': 200,
            f'/profile/{username}/': 200,
            'unexisting page': 404,
        }
        for addres, code in url_names.items():
            with self.subTest(addres=addres):
                response = self.guest_client.get(addres)
                self.assertEqual(response.status_code, code)

    def test_edit_post_for_author(self):
        """Проверяем доступность страницы редактирования для автора поста"""
        post = PostURLTests.post
        response = self.author_client.get(f'/posts/{post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_for_author(self):
        """Проверяем шаблон /edit/ автору поста."""
        post = PostURLTests.post
        response = self.author_client.get(f'/posts/{post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_uses_correct_template(self):
        """Проверяем шаблоны страниц для неавторизванных пользователей"""
        group = PostURLTests.group
        post = PostURLTests.post
        username = PostURLTests.user.username
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{group.slug}/',
            'posts/post_detail.html': f'/posts/{post.id}/',
            'posts/profile.html': f'/profile/{username}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
