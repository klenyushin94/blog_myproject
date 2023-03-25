from django.test import TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
        )

    def test_object_name_is_post_fild(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_object_name_is_group_fild(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_title_help_post(self):
        """help_text поля post совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст поста')

    def test_title_help_group(self):
        """help_text поля group совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Группа, к которой будет относиться пост')

    def test_verbose_name_author(self):
        """verbose_name поля author совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose_name = post._meta.get_field('author').verbose_name
        self.assertEqual(verbose_name, 'Автор')

    def test_verbose_name_group(self):
        """verbose_name поля group совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose_name = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_name, 'Группа')
