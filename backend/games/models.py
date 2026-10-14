from django.db import models

class Game(models.Model):
    WORDS = (
    'Hangman',
    'Python',
    'Audacix',
    'Bottle',
    'Pen',
    )   
    
    word = models.CharField(max_length=50)
    guessed_letters = models.CharField(max_length=26, blank = True, default='')
    incorrect_guesses = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    @property
    def max_incorrect_guesses(self):
        return (len(self.word) + 1) // 2

    @property
    def remaining_incorrect_guesses(self):
        return max(
            self.max_incorrect_guesses - self.incorrect_guesses,
            0,
        )

    @property
    def is_won(self):
        return all(
            character.lower() in self.guessed_letters.lower() for character in set(self.word)
        )

    @property
    def is_lost(self):
        return self.incorrect_guesses >= self.max_incorrect_guesses

    @property
    def status(self):
        if self.is_won:
            return 'Won'

        if self.is_lost:
            return 'Lost'

        return 'InProgress'
        
    @property
    def masked_word(self):
        guessed = self.guessed_letters.lower()

        return ''.join(
            character if character.lower() in guessed else '_'
            for character in self.word
        )


    def __str__(self):
        return f'Game {self.pk} - {self.status}'
