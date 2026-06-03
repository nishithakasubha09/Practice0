# Science Signal Lab

This folder contains a complete rewrite of the practice app from `C:\Nishithas Codes\Practiceahhaha`.

## Review notes

- The original project had several separate practice files, embedded CSS, placeholder content, and one working Simon-style game.
- The game logic worked, but it had limited structure, no persistent scoring, minimal accessibility, no responsive polish, and no separation between HTML, CSS, and JavaScript.
- The rewrite consolidates the useful concept into one finished browser app.

## What changed

- Rebuilt the app as a polished science-themed memory game.
- Split the code into `index.html`, `styles.css`, and `app.js`.
- Added responsive layout for desktop and mobile.
- Added level, score, best level, best score, streak, misses, and accuracy tracking.
- Added difficulty modes, strict mode, reset, sound toggle, keyboard input, and persistent best scores using `localStorage`.
- Added accessible labels, focus states, and live status updates.
- Added a lightweight animated canvas background for a more finished visual experience.
- Updated the experience to be age-neutral for ages 5-16, with abstract signal tiles, neutral labels, scalable difficulty, concise feedback, and a subtle completion animation after each cleared round.

## Run

Open `index.html` in a browser.
