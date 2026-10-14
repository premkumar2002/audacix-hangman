from rest_framework import serializers

from .models import Game


class GameStateSerializer(serializers.ModelSerializer):
    word_state = serializers.CharField(
        source='masked_word',
        read_only=True,
    )
    remaining_incorrect_guesses = serializers.IntegerField(
        read_only=True,
    )
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Game
        fields = (
            'id',
            'status',
            'word_state',
            'incorrect_guesses',
            'remaining_incorrect_guesses',
        )