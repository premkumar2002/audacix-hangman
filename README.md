# Audacix Hangman

A Hangman game built as a full-stack application for the Audacix coding exercise.

- **Backend:** Django 4.2 and Django REST Framework
- **Database:** SQLite
- **Frontend:** React and Vite
- **API format:** JSON

The backend owns the game rules and persistent state. The React frontend calls the
API and renders the current state for the player.

## Features

- Starts a game with a random word from:
  `Hangman`, `Python`, `Audacix`, `Bottle`, and `Pen`
- Allows incorrect guesses equal to half the word length, rounded up
- Reveals correctly guessed letters while masking the others with underscores
- Tracks incorrect guesses and remaining attempts
- Detects `InProgress`, `Won`, and `Lost` states
- Rejects invalid and duplicate guesses
- Stores every game in SQLite
- Provides a simple React user interface

## Project structure

```text
audacix-hangman/
├── backend/
│   ├── config/                 # Django project configuration
│   ├── games/                  # Hangman application
│   │   ├── migrations/         # Database migration history
│   │   ├── models.py           # Game database model and game rules
│   │   ├── serializers.py      # JSON validation and representation
│   │   ├── urls.py             # Game API routes
│   │   ├── views.py            # HTTP request handlers
│   │   └── tests.py            # Backend API tests
│   ├── db.sqlite3              # Local SQLite database
│   ├── manage.py               # Django command-line utility
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── App.css              # Component styles
│   │   ├── index.css            # Global styles
│   │   └── main.jsx             # React entry point
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Prerequisites

- Python 3.9 or newer
- Node.js and npm
- Git

## Run the backend

Open a terminal in the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will run at:

```text
http://127.0.0.1:8000
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\activate
```

## Run the frontend

Open a second terminal in the repository root:

```bash
cd frontend
npm install
npm run dev
```

Vite will display the local frontend address, normally:

```text
http://localhost:5173
```

The Django CORS setting allows this local frontend origin to call the backend.
The Django server and the Vite server must both be running.

## API reference

All API requests and responses use JSON.

### 1. Start a new game

```http
POST /game/new
```

Request body:

```json
{}
```

Response:

```json
{
  "id": 37
}
```

The ID identifies the database row for this particular game. The selected word
is stored in the database but is never returned to the frontend.

Example with curl:

```bash
curl -X POST http://127.0.0.1:8000/game/new \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. Read game state

```http
GET /game/<id>
```

Example:

```http
GET /game/37
```

Response:

```json
{
  "id": 37,
  "status": "InProgress",
  "word_state": "______",
  "incorrect_guesses": 0,
  "remaining_incorrect_guesses": 3
}
```

Possible values for `status` are:

- `InProgress`: the player can continue guessing
- `Won`: every distinct letter has been guessed
- `Lost`: the incorrect guess limit has been reached

If the game ID does not exist, the API returns HTTP `404`.

### 3. Submit a guess

```http
POST /game/<id>/guess
```

Request:

```json
{
  "guess": "o"
}
```

Response for a correct guess:

```json
{
  "correct": true,
  "game_state": {
    "id": 37,
    "status": "InProgress",
    "word_state": "_o____",
    "incorrect_guesses": 0,
    "remaining_incorrect_guesses": 3
  }
}
```

Response for an incorrect guess:

```json
{
  "correct": false,
  "game_state": {
    "id": 37,
    "status": "InProgress",
    "word_state": "_o____",
    "incorrect_guesses": 1,
    "remaining_incorrect_guesses": 2
  }
}
```

Invalid or duplicate guesses return HTTP `400` with an error message:

```json
{
  "error": "You have already guessed this letter."
}
```

## API flow

### Starting a game

```text
React calls POST /game/new
        ↓
Django chooses a random word
        ↓
Game.objects.create(...) writes a row to SQLite
        ↓
Django returns the new game ID
        ↓
React calls GET /game/<id>
        ↓
Django serializes the public game state
        ↓
React displays the masked word and attempts
```

The frontend uses two requests because the new-game endpoint is required to
return the newly created ID, while the state endpoint returns the full public
state.

### Submitting a guess

```text
Player types one letter and submits the form
        ↓
React validates that it is one letter from A to Z
        ↓
React calls POST /game/<id>/guess
        ↓
Django validates the JSON using GuessSerializer
        ↓
Django checks whether the letter was already guessed
        ↓
Django checks the letter against the secret word
        ↓
Django updates guessed_letters and incorrect_guesses
        ↓
Django saves the updated row with game.save(...)
        ↓
Django returns correct plus the updated public state
        ↓
React stores the new state with setGame(...)
        ↓
React re-renders the word and status
```

## How SQLite stores and retrieves game data

SQLite is a file-based relational database. In this project, the file is:

```text
backend/db.sqlite3
```

The `Game` class in `backend/games/models.py` describes the database table:

| Model field | Purpose |
|---|---|
| `id` | Automatically generated unique identifier |
| `word` | Secret selected word |
| `guessed_letters` | Letters already submitted by the player |
| `incorrect_guesses` | Number of incorrect guesses |
| `created_at` | Time when the game was created |
|

Django turns the model into a database table named approximately:

```text
games_game
```

The migration file in `backend/games/migrations/0001_initial.py` describes how
to create that table. Running `python manage.py migrate` applies the migration
to `db.sqlite3`.

### Writing data

The new-game view writes a row with:

```python
Game.objects.create(word=word)
```

The guess view updates the existing row with:

```python
```

### Reading data

The URL contains the game ID. Django uses it to retrieve one row:

```python
```

If the row exists, `GameStateSerializer` converts the model object into JSON.
If it does not exist, Django returns HTTP `404`.

The real word is not included in the serializer fields. Instead, the calculated
`masked_word` property produces values such as:

```text
______
_o____
_ottle
```

This means the browser can display the game without receiving the answer.

## Backend concepts

### Models

A Django model is a Python class representing database data. `Game` stores the
minimum state needed to restore a game after another API request.

### Views

A view receives an HTTP request, performs application logic, and returns an HTTP
response. The three views are responsible for creating a game, reading a game,
and recording a guess.

### Serializers

DRF serializers perform two related jobs:

1. `GuessSerializer` validates incoming JSON.
2. `GameStateSerializer` converts a `Game` object into safe response JSON.

### Migrations

Migrations are versioned database changes generated from model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## React concepts used in the frontend

`frontend/src/App.jsx` contains the main component.

### State

```jsx
const [game, setGame] = useState(null)
```

`game` is the current value and `setGame` updates it. When state changes, React
renders the component again with the new state.

The component also stores the input letter, user message, and loading state.

### Controlled input

The input uses React state as its source of truth:

```jsx
value={letter}
onChange={(event) => setLetter(event.target.value)}
```

This lets the component validate and clear the field after a successful guess.

### Form submission

`handleGuess` calls `event.preventDefault()` so the browser does not reload the
page. It validates the input, sends the JSON request with `fetch`, then updates
React state with the API response.

### Effect and initial game

`useEffect` starts one game when the component first loads. The
`initialGameStarted` ref prevents React development `StrictMode` from creating
two games when it re-runs the effect during development checks.

### Conditional rendering

The status class and message change based on the current state:

```jsx
game?.status === 'Won'
game?.status === 'Lost'
game?.status === 'InProgress'
```

The guess form is disabled when there is no active game, while a request is in
progress, or after the game has ended.

## Check commands

Backend:

```bash
cd backend
source .venv/bin/activate
python manage.py check
python manage.py test
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Development notes

The current Django settings are for local development. Before deploying to a
public environment, move the secret key into an environment variable, disable
debug mode, configure production hosts, and configure the production frontend
API URL.
