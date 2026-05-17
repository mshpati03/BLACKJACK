# Blackjack21

Main repository for the **Blackjack CV** project: a computer-vision Blackjack game that uses real cards shown to a webcam, YOLO-based detection, and a React + Flask full-stack architecture.

---

## Repository Overview

This repository is organized as a top-level container with the project living in:

```text
blackjack-cv/
```

Inside `blackjack-cv` you will find:

- `backend/` - Flask + Socket.IO API, camera pipeline, YOLO detection, game engine
- `frontend/` - React web interface for gameplay, live camera feed, controls, and game state
- `README.md` - detailed setup, architecture, API, troubleshooting, and model guidance

---

## Project Highlights

- Webcam-based card capture with real-time stream updates
- YOLO (Ultralytics) card detection integrated into game actions
- Stabilized detection pipeline to reduce noisy/false reads
- Full Blackjack round flow with betting and bankroll management
- Player actions: hit, stand, double down, split
- Strategy advisor support for hard/soft hand recommendations

---

## Quick Start

### 1) Open the project folder

```bash
cd blackjack-cv
```

### 2) Follow the full setup guide

Read:

```text
blackjack-cv/README.md
```

That documentation includes:

- backend and frontend installation
- model placement/training instructions
- run commands
- API reference
- detector environment variables
- troubleshooting tips

---

## Recommended GitHub Presentation

For a clean public project page:

1. Keep this root README as a clear entry point.
2. Keep technical implementation details in `blackjack-cv/README.md`.
3. Add screenshots or a short demo GIF in the future for stronger first impression.
4. Add a `LICENSE` file (for example MIT) before public distribution.

---

## License

No license file is currently defined at the repository root.  
If you plan to publish publicly, add a license such as MIT.
