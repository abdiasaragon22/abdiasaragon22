from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Game

class SmokeTests(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            xml_id=1,
            title='Test Game',
            developer='Dev',
            publisher='Pub',
            genre='Action',
            platform='PC',
            release_date='2024-01-01',
            description='Test description',
        )
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_game_detail_status_code(self):
        url = reverse('gamerank:game_detail', args=[self.game.xml_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_game_creation(self):
        self.assertEqual(self.game.title, 'Test Game')


    def test_home_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
