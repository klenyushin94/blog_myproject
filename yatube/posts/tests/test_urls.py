from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='mike')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_author = Client()
        cls.authorized_client.force_login(PostURLTest.user)
        cls.authorized_author.force_login(PostURLTest.author)

    def setUp(self):
        cache.clear()

# Проверяем доступность публичных адресов гостевой учеткой
    def test_exists_at_desired_location(self):
        """Проверка страниц, доступных гостю"""
        templates_url_names = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/author/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

# Проверяем редиректы приватных адресов
# гостевой учеткой (корректность редиректа тоже проверяем)
    def test_redirect_exists_at_desired_location(self):
        """Проверка страниц, с которых перенаправляют гостя на login"""
        # Шаблоны по адресам
        templates_url_names = {
            '/create/': HTTPStatus.FOUND,
            '/posts/1/edit/': HTTPStatus.FOUND,
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        login_url = reverse('auth:login')
        self.assertRedirects(
            response, f"{login_url}?next=/create/"
        )

    def test_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/post_id/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        login_url = reverse('auth:login')
        self.assertRedirects(
            response, f"{login_url}?next=/posts/1/edit/"
        )

# Проверяем доступность приватных адресов залогиненной учеткой
    def test_create_url_exists_at_desired_location_autorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location(self):
        """Страница /posts/<post_id>/edit/ доступна автору поста."""
        response = self.authorized_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

# Проверяем соответствие шаблонов для публичных адресов
    def test_urls_uses_correct_template_publi(self):
        """Публичный URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/mike/',
            'posts/post_detail.html': '/posts/1/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

# Проверяем соответствие шаблонов для приватных адресов
# (прикрутить subTest не получилось, пусть будет так)
    def test_create_url_uses_correct_template(self):
        """Страница по адресу /create/ использует
        шаблон posts/create_post.html. для авториз. пользователя."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_edit_url_uses_correct_template(self):
        """Страница по адресу /posts/<post_id>/edit использует
        шаблон posts/create_post.html. для автора поста."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

# Проверяем доступность страницы редактирования поста
# из под другой учетной записи
    def test_edit_url_exists_at_desired_location(self):
        """Страница /posts/<post_id>/edit/ не доступна неавтору поста."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_url_redirect_autoriz_on_admin_login(self):
        """Страница по адресу /posts/post_id/edit/ перенаправит авторизованного
        пользователя, но не автора, на страницу просмотра поста.
        """
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/posts/1/'
        )

# Проверяем несуществующую страницу
    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница не откроется (404)"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем недоступность комментирования
    # незаригестрированным пользователем
    def test_comments_no_authorized(self):
        """Страница /posts/<post_id>/comment/ не доступна гостю."""
        response = self.guest_client.get('/posts/1/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
