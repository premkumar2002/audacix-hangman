import random

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Game
from .serializers import GameStateSerializer


@api_view(['POST'])
def new_game(request):
    word = random.choice(Game.WORDS)
    game = Game.objects.create(word=word)

    return Response(
        {'id': game.id},
        status=status.HTTP_201_CREATED,
    )

@api_view(['GET'])
def game_state(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    serializer = GameStateSerializer(game)

    return Response(serializer.data)


@api_view(['POST'])
def make_guess(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    guess = request.data.get('guess')

    if not isinstance(guess, str) or len(guess) != 1 or not guess.isalpha():
        return Response(
            {'error': 'Please provide a single letter.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    guess = guess.lower()

    if game.status != 'InProgress':
        return Response(
            {'error': 'The game has already ended.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if guess in game.guessed_letters:
        return Response(
            {'error': 'You have already guessed this letter.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    is_correct_guess = guess in game.word.lower()
    game.guessed_letters += guess
    if not is_correct_guess:
        game.incorrect_guesses += 1

    game.save()
    serializer = GameStateSerializer(game)

    return Response({
        'correct': is_correct_guess,
        'game_state': serializer.data,
    })
