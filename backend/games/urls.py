from django.urls import path

from . import views


urlpatterns = [
    path('game/new', views.new_game, name='new-game'),
    path('game/<int:game_id>', views.game_state, name='game-state'),
    path('game/<int:game_id>/guess', views.make_guess, name='make-guess')
]
