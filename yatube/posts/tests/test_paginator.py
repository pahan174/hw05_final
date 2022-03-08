from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        for i in range(1, 13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=cls.group
            )

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()
        # авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # клиент тестового автора
        self.author_client = Client()
        self.author_client.force_login(PostViewsTest.post.author)

    def test_first_page_index_contains_ten_records(self):
        """Проверка: количество постов на первой странице index равно 10."""
        response = self.client.get(reverse('posts:main'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        """Проверка: на второй странице index должно быть два поста."""
        response = self.client.get(reverse('posts:main') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_first_page_group_list_contains_ten_records(self):
        """Проверка: количество постов на первой странице
         group_list равно 10."""
        response = self.client.get(reverse(
            'posts:url_group',
            kwargs={'slug': 'Тестовый слаг'}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_three_records(self):
        """Проверка: на второй странице group_list должно быть 2 поста."""
        response = self.client.get(reverse(
            'posts:url_group',
            kwargs={
                'slug': 'Тестовый слаг'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_first_page_profile_contains_ten_records(self):
        """Проверка: количество постов на первой странице
         profile равно 10."""
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        """Проверка: на второй странице profile должно быть 2 поста."""
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)
