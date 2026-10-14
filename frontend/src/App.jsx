
import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [game, setGame] = useState(null)
  const [letter, setLetter] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const initialGameStarted = useRef(false)

  async function startNewGame() {
    setLoading(true)
    setMessage('')
    setLetter('')
    setGame(null)

    try {
      const response = await fetch(`${API_URL}/game/new`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Could not start a new game.')
      }

      const data = await response.json()

      const gameResponse = await fetch(`${API_URL}/game/${data.id}`)

      if (!gameResponse.ok) {
        throw new Error('Could not load the game.')
      }

      const gameData = await gameResponse.json()
      setGame(gameData)
      setMessage('Guess a letter to get started!')
    } catch (error) {
      setMessage(error.message || 'Could not connect to the server.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // React StrictMode re-runs effects in development. This guard keeps the
    // non-idempotent "create game" request from running twice.
    if (initialGameStarted.current) {
      return
    }

    initialGameStarted.current = true
    startNewGame()
  }, [])

  async function handleGuess(event) {
    event.preventDefault()

    const guess = letter.trim().toLowerCase()

    if (!guess || guess.length !== 1 || !/^[a-z]$/.test(guess)) {
      setMessage('Please enter one letter from A to Z.')
      return
    }

    if (!game || game.status !== 'InProgress') {
      setMessage('Start a new game to play again.')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/game/${game.id}/guess`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ guess }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        setMessage(data.error || 'Your guess could not be submitted.')
        return
      }

      setGame(data.game_state)
      setLetter('')

      if (data.game_state.status === 'Won') {
        setMessage('Congratulations! You guessed the word!')
      } else if (data.game_state.status === 'Lost') {
        setMessage('Game over! Start a new game to try again.')
      } else if (data.correct) {
        setMessage(`Good guess! "${guess}" is in the word.`)
      } else {
        setMessage(`Sorry, "${guess}" is not in the word.`)
      }
    } catch {
      setMessage('Could not connect to the server. Check that Django is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Hangman</h1>
        <p>Guess the word, one letter at a time!</p>
      </header>

      <main className="game-card">
        <div className="game-status">
          <span>Status</span>
          <strong
            className={
              game?.status === 'Won'
                ? 'won'
                : game?.status === 'Lost'
                  ? 'lost'
                  : ''
            }
          >
            {loading && !game ? 'Loading...' : game?.status || 'Not started'}
          </strong>
        </div>

        <div className="word-display">
          {(game?.word_state || '_____').split('').map((character, index) => (
            <span key={index}>
              {character === '_' ? '_' : character}
            </span>
          ))}
        </div>

        <p className="attempts">
          Incorrect guesses: {game?.incorrect_guesses ?? 0}
        </p>

        <p className="attempts">
          Incorrect guesses remaining: {game?.remaining_incorrect_guesses ?? '-'}
        </p>

        <form className="guess-form" onSubmit={handleGuess}>
          <input
            type="text"
            placeholder="Enter a letter"
            aria-label="Enter a letter"
            maxLength={1}
            value={letter}
            onChange={(event) => setLetter(event.target.value)}
            disabled={loading || !game || game.status !== 'InProgress'}
          />

          <button
            type="submit"
            disabled={loading || !game || game.status !== 'InProgress'}
          >
            Guess
          </button>
        </form>

        <button
          className="new-game-button"
          type="button"
          onClick={startNewGame}
          disabled={loading}
        >
          {loading ? 'Please wait...' : 'New Game'}
        </button>

        <p className="message" aria-live="polite">
          {message}
        </p>
      </main>
    </div>
  )
}

export default App
