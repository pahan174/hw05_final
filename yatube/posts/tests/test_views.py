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
class PostViewsTest(TestCase):
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
        self.author_client.force_login(PostViewsTest.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'posts/index.html': reverse('posts:main'),
            'posts/group_list.html': reverse(
                'posts:url_group',
                kwargs={'slug': PostViewsTest.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.user.username},
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.post.id},
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.post.id},
            ),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        self.assertTemplateUsed(self.authorized_client.get(reverse(
            'posts:post_create')), 'posts/create_post.html')

    def test_post_main_page_show_correct_context(self):
        """Шаблон posts:main сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:main'))

        first_object = response.context['page_obj'][0]
        post_title_0 = response.context['title']
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image

        self.assertEqual(post_title_0, 'Последние обновления на сайте')
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_author_0, PostViewsTest.user.username)
        self.assertEqual(post_group_0, PostViewsTest.group.title)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с картинкой."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostViewsTest.post.id}))

        post_image = response.context['post'].image
        self.assertEqual(post_image, PostViewsTest.post.image)

    def test_post_groups_page_show_correct_context(self):
        """Шаблон posts:url_group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:url_group',
            kwargs={'slug': PostViewsTest.group.slug}))

        first_object = response.context['page_obj'][0]
        post_group_0 = response.context['group'].title
        post_title_0 = response.context['title']
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image

        self.assertEqual(
            post_title_0,
            f'Записи сообщества {PostViewsTest.group.title}')
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_author_0, PostViewsTest.user.username)
        self.assertEqual(post_group_0, PostViewsTest.group.title)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_post_profile_page_show_correct_context(self):
        """Шаблон posts:profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'})
        )

        first_object = response.context['page_obj'][0]
        post_author_0 = response.context['author']
        post_title_0 = response.context['title']
        post_text_0 = first_object.text
        post_cnt_posts_0 = response.context['cnt_posts']
        post_image_0 = first_object.image

        self.assertEqual(
            post_title_0,
            f'Профайл пользователя {PostViewsTest.user.username}')
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, PostViewsTest.user)
        self.assertEqual(post_cnt_posts_0, 1)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_post_groups_page_show_none_context(self):
        """Шаблон posts:url_group сформирован пустым."""
        response = self.authorized_client.get(reverse(
            'posts:url_group',
            kwargs={'slug': 'empty_slug'})
        )

        post_group_0 = response.context['group'].title
        post_title_0 = response.context['title']

        self.assertEqual(
            post_title_0,
            f'Записи сообщества {PostViewsTest.group_empty.title}'
        )
        self.assertEqual(post_group_0, PostViewsTest.group_empty.title)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_guest_client_no_accept_and_edit_post(self):
        '''Неавторизваонный клиент не может получить доступ к созданию поста'''
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, 302)

    def test_guest_client_no_accept_and_edit_post(self):
        '''Неавторизваонный клиент не может редактировать пост'''
        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.post.id},
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_guest_client_no_comment_post(self):
        '''Неавторизваонный клиент не может комментировать пост'''
        response = self.guest_client.get(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostViewsTest.post.id},
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_auth_client_add_folow(self):
        '''Авторизованный пользователь может подписываться
        на других пользователей и тестовй пост появляется в его подписки'''

        self.follow_user = User.objects.create_user(username='follow_user')
        self.follow_client = Client()
        self.follow_client.force_login(self.follow_user)

        # Проверяем, что страница подписок пуста
        response = self.follow_client.get(reverse(
            'posts:follow_index',
        )
        )

        self.assertEqual(len(response.context['page_obj']), 0)

        # подписываемся на автора тестового поста
        response = self.follow_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsTest.post.author},
            ),
        )

        # Проверяем, что страница подписок теперь c одним постом
        response = self.follow_client.get(reverse(
            'posts:follow_index',
        )
        )
        self.assertEqual(len(response.context['page_obj']), 1)

        # отписываемся от автора тестового поста
        response = self.follow_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostViewsTest.post.author},
            ),
        )

        # Проверяем, что страница подписок теперь пустая
        response = self.follow_client.get(reverse(
            'posts:follow_index',
        )
        )
        self.assertEqual(len(response.context['page_obj']), 0)
