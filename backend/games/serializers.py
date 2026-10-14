from rest_framework import serializers

from .models import Game


class GuessSerializer(serializers.Serializer):
    """Validate the single letter submitted by the player."""

    guess = serializers.CharField(
        min_length=1,
        max_length=1,
        trim_whitespace=True,
    )

    def validate_guess(self, value):
        if not value.isalpha():
            raise serializers.ValidationError(
                'Please provide a single letter.'
            )

        return value.lower()


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
