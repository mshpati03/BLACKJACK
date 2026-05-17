# Blackjack CV

Blackjack CV is a full-stack React + Flask blackjack application that combines **computer vision**, **real-time gameplay**, and **React course requirements** in one project.

The app lets the player interact with a blackjack table through a React frontend, while a Flask backend handles the game logic, camera integration, card detection, and live updates. In addition to gameplay, the project now includes **routing**, a **player setup form**, and **match history CRUD** using `localStorage`.

---

## Project Purpose

This project was developed as a final React project and demonstrates practical use of:

- React
- Components
- Props
- State management
- Hooks (`useState`, `useEffect`)
- React Router
- Forms
- API integration
- LocalStorage
- CRUD operations
- Clean project structure
- UI design

It also extends the project with a more advanced concept: integrating a React interface with a Flask backend and YOLO-based card detection.

---

## Main Features

### Gameplay
- Blackjack game interface built in React
- Betting system
- Player actions: Hit, Stand, Double Down, Split
- Dealer logic and score handling
- Round result modal
- Balance tracking

### Computer Vision
- Webcam-based card capture
- YOLO / Ultralytics card detection
- Flask backend for detection and game state
- Live communication with Socket.IO

### React Project Requirements
- Multi-page navigation with React Router
- Home / Player Setup page
- Game page
- Match History page
- Form for player data input
- Data listing through saved match history
- CRUD operations:
  - Create saved match record
  - Read saved match history
  - Update notes for a record
  - Delete records
- LocalStorage persistence for match history and player profile

---

## Project Structure

```text
blackjack-cv/
│   README.md
│
├───backend
│   │   app.py
│   │   requirements.txt
│   │   train.py
│   │
│   ├───game
│   │       blackjack.py
│   │       card_labels.py
│   │       strategy.py
│   │       __init__.py
│   │
│   └───vision
│       │   camera_service.py
│       │   detector.py
│       │   __init__.py
│       │
│       └───models
│               best.pt
│
└───frontend
    │   package.json
    │   package-lock.json
    │
    ├───public
    │       index.html
    │
    └───src
        │   App.css
        │   App.jsx
        │   index.js
        │
        ├───components
        ├───pages
        └───utils
```

---

## Technologies Used

### Frontend
- React
- React Router DOM
- Axios
- Socket.IO Client
- CSS

### Backend
- Flask
- Flask-CORS
- Flask-SocketIO
- Eventlet

### Computer Vision / AI
- OpenCV
- Ultralytics YOLO
- NumPy
- Roboflow

---

## Installation

## 1. Clone the repository

```bash
git clone <your-repository-link>
cd blackjack-cv
```

## 2. Install frontend dependencies

```bash
cd frontend
npm install
npm install react-router-dom
```

## 3. Install backend dependencies

```bash
cd ../backend
pip install -r requirements.txt
```

---

## Running the Project

You need to run both backend and frontend.

### Start the backend

From the `backend` folder:

```bash
python app.py
```

### Start the frontend

From the `frontend` folder:

```bash
npm start
```

The frontend will usually run on:

```text
http://localhost:3000
```

The backend will usually run on:

```text
http://localhost:5001
```

---

## How the App Works

1. The player starts on the **Home / Player Setup** page.
2. The player enters a name and optional note.
3. The app navigates to the **Game** page.
4. The Flask backend manages the blackjack state and computer vision flow.
5. When a round finishes, the result is saved in **localStorage**.
6. The player can open the **History** page to:
   - view saved matches,
   - edit notes,
   - delete records,
   - clear all history.

---

## CRUD Features

The project includes full basic CRUD functionality through the Match History page:

- **Create**: a completed round is saved automatically
- **Read**: all saved rounds are listed in the History page
- **Update**: the note of a saved round can be edited
- **Delete**: a saved round can be removed

This was added to satisfy the React final project requirement for CRUD and persistent data storage.

---

## Academic Requirements Covered

This project satisfies the requested React project requirements:

- React application
- At least 5 components
- `useState`
- `useEffect`
- Forms
- Data listing
- CRUD operations
- Routing with React Router
- LocalStorage persistence
- API integration
- Organized project structure
- Functional UI

---

## Notes

- The backend depends on the detection model file:
  `backend/vision/models/best.pt`
- If the frontend cannot connect, make sure the Flask backend is running on port `5001`
- If PowerShell blocks `npm`, use Command Prompt or fix PowerShell execution policy
- If `node` or `npm` are not recognized, make sure Node.js is installed and added to PATH

---

## Future Improvements

- Add screenshots or demo GIFs
- Add a deploy link
- Add authentication or player profiles
- Add statistics dashboard for wins/losses
- Improve leaderboard and filtering options

---

## License

No license has been added yet.  
If you plan to publish the project publicly, consider adding an MIT license.