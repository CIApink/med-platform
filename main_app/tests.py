from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_index_view(self):
        """测试主页视图"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_sign_in_view(self):
        """测试登录视图"""
        response = self.client.get(reverse('sign_in'))
        self.assertEqual(response.status_code, 200)

    def test_sign_up_view(self):
        """测试注册视图"""
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)

    def test_data_download_view(self):
        """测试数据下载视图"""
        response = self.client.get(reverse('data_download'))
        self.assertEqual(response.status_code, 200)
