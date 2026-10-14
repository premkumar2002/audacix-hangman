from rest_framework import status
from rest_framework.test import APITestCase

from .models import Game


class GameApiTests(APITestCase):
    def setUp(self):
        self.game = Game.objects.create(word='Bottle')

    def test_new_game_creates_a_game(self):
        response = self.client.post('/game/new', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(Game.objects.count(), 2)

    def test_game_state_hides_the_secret_word(self):
        response = self.client.get(f'/game/{self.game.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['word_state'], '______')
        self.assertNotIn('word', response.data)
        self.assertEqual(response.data['remaining_incorrect_guesses'], 3)

    def test_correct_guess_reveals_the_letter(self):
        response = self.client.post(
            f'/game/{self.game.id}/guess',
            {'guess': 'o'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['correct'])
        self.assertEqual(response.data['game_state']['word_state'], '_o____')
        self.assertEqual(response.data['game_state']['incorrect_guesses'], 0)

    def test_incorrect_guess_uses_one_attempt(self):
        response = self.client.post(
            f'/game/{self.game.id}/guess',
            {'guess': 'z'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['correct'])
        self.assertEqual(response.data['game_state']['incorrect_guesses'], 1)
        self.assertEqual(
            response.data['game_state']['remaining_incorrect_guesses'],
            2,
        )

    def test_duplicate_guess_is_rejected(self):
        self.client.post(
            f'/game/{self.game.id}/guess',
            {'guess': 'o'},
            format='json',
        )

        response = self.client.post(
            f'/game/{self.game.id}/guess',
            {'guess': 'O'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            'You have already guessed this letter.',
        )

    def test_invalid_guess_is_rejected(self):
        response = self.client.post(
            f'/game/{self.game.id}/guess',
            {'guess': 'ab'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            'Ensure this field has no more than 1 characters.',
        )

    def test_two_incorrect_guesses_lose_a_three_letter_game(self):
        game = Game.objects.create(word='Pen')

        for guess in ('x', 'y'):
            response = self.client.post(
                f'/game/{game.id}/guess',
                {'guess': guess},
                format='json',
            )

        self.assertEqual(response.data['game_state']['status'], 'Lost')
        self.assertEqual(
            response.data['game_state']['remaining_incorrect_guesses'],
            0,
        )
