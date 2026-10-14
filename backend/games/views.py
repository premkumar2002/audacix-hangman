import random

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Game
from .serializers import GameStateSerializer, GuessSerializer


@api_view(['POST'])
def new_game(request):
    """Create a game with a randomly selected word."""
    word = random.choice(Game.WORDS)
    game = Game.objects.create(word=word)

    return Response(
        {'id': game.id},
        status=status.HTTP_201_CREATED,
    )

@api_view(['GET'])
def game_state(request, game_id):
    """Return the public state of one game."""
    game = get_object_or_404(Game, id=game_id)
    serializer = GameStateSerializer(game)

    return Response(serializer.data)


@api_view(['POST'])
def make_guess(request, game_id):
    """Validate and record one letter guess for a game."""
    game = get_object_or_404(Game, id=game_id)

    if game.status != 'InProgress':
        return Response(
            {'error': 'The game has already ended.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    guess_serializer = GuessSerializer(data=request.data)
    if not guess_serializer.is_valid():
        first_error = next(iter(guess_serializer.errors.values()))[0]
        return Response(
            {'error': str(first_error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    guess = guess_serializer.validated_data['guess']

    if guess in game.guessed_letters:
        return Response(
            {'error': 'You have already guessed this letter.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Store every guess once so duplicate guesses cannot change the game twice.
    is_correct_guess = guess in game.word.lower()
    game.guessed_letters += guess
    if not is_correct_guess:
        game.incorrect_guesses += 1

    game.save(update_fields=['guessed_letters', 'incorrect_guesses'])
    serializer = GameStateSerializer(game)

    return Response({
        'correct': is_correct_guess,
        'game_state': serializer.data,
    })
