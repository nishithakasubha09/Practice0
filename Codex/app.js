const board = document.getElementById("signal-board");
const cells = Array.from(document.querySelectorAll(".signal-cell"));
const startButton = document.getElementById("start-btn");
const resetButton = document.getElementById("reset-btn");
const soundButton = document.getElementById("sound-btn");
const strictToggle = document.getElementById("strict-toggle");
const modeButtons = Array.from(document.querySelectorAll("[data-mode]"));
const celebrationLayer = document.getElementById("celebration-layer");

const display = {
  status: document.getElementById("round-state"),
  level: document.getElementById("level-value"),
  score: document.getElementById("score-value"),
  best: document.getElementById("best-value"),
  bestScore: document.getElementById("best-score-value"),
  streak: document.getElementById("streak-value"),
  misses: document.getElementById("miss-value"),
  rounds: document.getElementById("round-value"),
  accuracy: document.getElementById("accuracy-value"),
  modeCaption: document.getElementById("mode-caption"),
  guideMessage: document.getElementById("guide-message")
};

const modes = {
  calm: {
    caption: "Steady pace",
    flash: 720,
    pause: 320,
    startDelay: 700,
    multiplier: 1
  },
  focus: {
    caption: "Quicker sequence",
    flash: 560,
    pause: 240,
    startDelay: 560,
    multiplier: 1.25
  },
  sprint: {
    caption: "Fast sequence",
    flash: 430,
    pause: 180,
    startDelay: 460,
    multiplier: 1.55
  }
};

const modeMessages = {
  calm: "Easy mode is ready.",
  focus: "Standard mode is ready.",
  sprint: "Expert mode is ready."
};

const tones = [262, 294, 330, 349, 392, 440, 494, 523, 587];
const storageKey = "science-signal-lab";
const saved = loadSave();

const state = {
  sequence: [],
  level: 0,
  score: 0,
  streak: 0,
  misses: 0,
  rounds: 0,
  inputIndex: 0,
  active: false,
  accepting: false,
  muted: false,
  strict: false,
  mode: "calm",
  bestLevel: saved.bestLevel,
  bestScore: saved.bestScore,
  runToken: 0
};

let audioContext;

setCellsLocked(true);
setStatus("Ready", "Ready to train your memory.");
updateDisplay();

startButton.addEventListener("click", () => {
  if (state.active) {
    endRun("Run Saved", "Your score is recorded.");
    return;
  }

  startRun();
});

resetButton.addEventListener("click", resetRun);

soundButton.addEventListener("click", () => {
  state.muted = !state.muted;
  soundButton.classList.toggle("is-muted", state.muted);
  soundButton.setAttribute("aria-label", state.muted ? "Turn sound on" : "Mute sound");
  soundButton.setAttribute("title", state.muted ? "Turn sound on" : "Mute sound");
});

strictToggle.addEventListener("change", () => {
  state.strict = strictToggle.checked;
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

cells.forEach((cell) => {
  cell.addEventListener("click", () => chooseCell(Number(cell.dataset.cell)));
});

document.addEventListener("keydown", (event) => {
  if (event.repeat) {
    return;
  }

  if (event.key >= "1" && event.key <= "9") {
    chooseCell(Number(event.key) - 1);
    return;
  }

  if (event.code === "Space") {
    event.preventDefault();
    if (!state.active) {
      startRun();
    }
  }

  if (event.key.toLowerCase() === "r") {
    resetRun();
  }
});

function startRun() {
  state.runToken += 1;
  state.sequence = [];
  state.level = 0;
  state.score = 0;
  state.streak = 0;
  state.misses = 0;
  state.rounds = 0;
  state.inputIndex = 0;
  state.active = true;
  state.accepting = false;
  startButton.textContent = "Stop";
  setStatus("Get Ready", "Watch the sequence.");
  updateDisplay();
  nextRound(state.runToken);
}

function resetRun() {
  state.runToken += 1;
  state.sequence = [];
  state.level = 0;
  state.score = 0;
  state.streak = 0;
  state.misses = 0;
  state.rounds = 0;
  state.inputIndex = 0;
  state.active = false;
  state.accepting = false;
  startButton.textContent = "Start";
  setStatus("Ready", "Ready to train your memory.");
  setCellsLocked(true);
  clearCellStates();
  updateDisplay();
}

async function nextRound(token) {
  state.accepting = false;
  setCellsLocked(true);
  clearCellStates();

  state.level += 1;
  state.rounds += 1;
  state.inputIndex = 0;
  state.sequence.push(nextSignal());
  updateDisplay();
  setStatus("Watch", "Follow the highlighted signals.");

  await wait(modes[state.mode].startDelay);
  if (!isCurrentRun(token)) {
    return;
  }

  await playSequence(token);
  if (!isCurrentRun(token)) {
    return;
  }

  state.accepting = true;
  setCellsLocked(false);
  setStatus("Your Turn", "Repeat the sequence.");
}

async function playSequence(token) {
  const mode = modes[state.mode];

  for (const index of state.sequence) {
    if (!isCurrentRun(token)) {
      return;
    }

    await flashCell(index, "active", mode.flash);
    await wait(mode.pause);
  }
}

function chooseCell(index) {
  if (!state.active || !state.accepting) {
    return;
  }

  const expected = state.sequence[state.inputIndex];

  if (index !== expected) {
    handleMiss(index);
    return;
  }

  flashCell(index, "active", 180);
  playTone(index, "tap");
  state.inputIndex += 1;

  if (state.inputIndex === state.sequence.length) {
    completeRound();
  }
}

async function handleMiss(index) {
  const token = state.runToken;
  state.accepting = false;
  state.misses += 1;
  state.streak = 0;
  setCellsLocked(true);
  board.classList.add("is-board-shaking");
  flashCell(index, "miss", 260);
  playTone(index, "miss");
  updateDisplay();
  setStatus("Try Again", "Watch the sequence again.");

  window.setTimeout(() => board.classList.remove("is-board-shaking"), 320);

  if (state.strict) {
    await wait(520);
    if (isCurrentRun(token)) {
      endRun("Run Complete", "Your score is recorded.");
    }
    return;
  }

  setStatus("Watch Again", "The sequence will replay.");
  state.inputIndex = 0;
  await wait(760);

  if (!isCurrentRun(token)) {
    return;
  }

  await playSequence(token);
  if (!isCurrentRun(token)) {
    return;
  }

  state.accepting = true;
  setCellsLocked(false);
  setStatus("Your Turn", "Repeat the sequence.");
}

async function completeRound() {
  const token = state.runToken;
  const mode = modes[state.mode];
  state.accepting = false;
  setCellsLocked(true);
  state.streak += 1;
  state.score += Math.round((state.level * 100 + state.streak * 35) * mode.multiplier);
  recordBest();
  updateDisplay();
  setStatus("Level Clear", "Sequence completed.");
  spawnCelebration();

  await wait(760);
  if (isCurrentRun(token)) {
    nextRound(token);
  }
}

function endRun(message, guideText = "Ready when you are.") {
  state.runToken += 1;
  state.active = false;
  state.accepting = false;
  startButton.textContent = "New Game";
  setCellsLocked(true);
  clearCellStates();
  recordBest();
  updateDisplay();
  setStatus(message, guideText);
}

function nextSignal() {
  const previous = state.sequence[state.sequence.length - 1];
  let candidate = Math.floor(Math.random() * cells.length);

  if (cells.length > 1 && candidate === previous) {
    candidate = (candidate + 1 + Math.floor(Math.random() * (cells.length - 1))) % cells.length;
  }

  return candidate;
}

function flashCell(index, type, duration) {
  const cell = cells[index];
  if (!cell) {
    return Promise.resolve();
  }

  const className = type === "miss" ? "is-miss" : "is-active";
  cell.classList.add(className);

  if (type !== "miss") {
    playTone(index, "signal");
  }

  return wait(duration).then(() => {
    cell.classList.remove(className);
  });
}

function setCellsLocked(isLocked) {
  cells.forEach((cell) => {
    cell.disabled = isLocked;
  });
}

function clearCellStates() {
  cells.forEach((cell) => {
    cell.classList.remove("is-active", "is-miss");
  });
}

function setMode(mode) {
  if (!modes[mode]) {
    return;
  }

  state.mode = mode;
  modeButtons.forEach((button) => {
    const isSelected = button.dataset.mode === mode;
    button.classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-checked", String(isSelected));
  });
  display.modeCaption.textContent = modes[mode].caption;

  if (!state.active) {
    setStatus("Ready", modeMessages[mode]);
  }
}

function updateDisplay() {
  display.level.textContent = state.level.toLocaleString();
  display.score.textContent = state.score.toLocaleString();
  display.best.textContent = state.bestLevel.toLocaleString();
  display.bestScore.textContent = state.bestScore.toLocaleString();
  display.streak.textContent = state.streak.toLocaleString();
  display.misses.textContent = state.misses.toLocaleString();
  display.rounds.textContent = state.rounds.toLocaleString();
  display.accuracy.textContent = `${getAccuracy()}%`;
}

function getAccuracy() {
  const attempts = state.rounds + state.misses;
  if (attempts === 0) {
    return 100;
  }

  return Math.max(0, Math.round((state.rounds / attempts) * 100));
}

function setStatus(text, guideText) {
  display.status.textContent = text;

  if (guideText) {
    display.guideMessage.textContent = guideText;
  }
}

function spawnCelebration() {
  if (!celebrationLayer) {
    return;
  }

  const colors = ["#198a8a", "#df6146", "#d99b28", "#70a653", "#4f75cf", "#c04d82"];
  const centerX = window.innerWidth * 0.5;
  const centerY = Math.min(window.innerHeight * 0.62, 620);

  for (let index = 0; index < 22; index += 1) {
    const sparkle = document.createElement("span");
    const size = randomBetween(9, 18);
    sparkle.className = "sparkle";
    sparkle.style.setProperty("--x", `${centerX + randomBetween(-80, 80)}px`);
    sparkle.style.setProperty("--y", `${centerY + randomBetween(-36, 36)}px`);
    sparkle.style.setProperty("--dx", `${randomBetween(-180, 180)}px`);
    sparkle.style.setProperty("--dy", `${randomBetween(-210, 120)}px`);
    sparkle.style.setProperty("--size", `${size}px`);
    sparkle.style.setProperty("--radius", index % 3 === 0 ? "3px" : "999px");
    sparkle.style.setProperty("--color", colors[index % colors.length]);
    celebrationLayer.appendChild(sparkle);
    window.setTimeout(() => sparkle.remove(), 940);
  }
}

function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

function recordBest() {
  let changed = false;

  if (state.level > state.bestLevel) {
    state.bestLevel = state.level;
    changed = true;
  }

  if (state.score > state.bestScore) {
    state.bestScore = state.score;
    changed = true;
  }

  if (changed) {
    saveBest();
  }
}

function loadSave() {
  try {
    const parsed = JSON.parse(localStorage.getItem(storageKey) || "{}");
    return {
      bestLevel: Number(parsed.bestLevel) || 0,
      bestScore: Number(parsed.bestScore) || 0
    };
  } catch {
    return {
      bestLevel: 0,
      bestScore: 0
    };
  }
}

function saveBest() {
  try {
    localStorage.setItem(storageKey, JSON.stringify({
      bestLevel: state.bestLevel,
      bestScore: state.bestScore
    }));
  } catch {
    return undefined;
  }

  return undefined;
}

function playTone(index, variant) {
  if (state.muted) {
    return;
  }

  const AudioCtor = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtor) {
    return;
  }

  if (!audioContext) {
    audioContext = new AudioCtor();
  }

  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  const now = audioContext.currentTime;
  const baseFrequency = tones[index] || 330;
  const frequency = variant === "miss" ? 120 : baseFrequency;

  oscillator.type = variant === "miss" ? "sawtooth" : "sine";
  oscillator.frequency.setValueAtTime(frequency, now);
  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(variant === "signal" ? 0.11 : 0.08, now + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + (variant === "signal" ? 0.22 : 0.14));
  oscillator.connect(gain).connect(audioContext.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.24);
}

function isCurrentRun(token) {
  return token === state.runToken && state.active;
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function initField() {
  const canvas = document.getElementById("lab-field");
  const context = canvas.getContext("2d");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const particles = [];
  let width = 0;
  let height = 0;
  let ratio = 1;

  function resize() {
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    seed();
    draw();
  }

  function seed() {
    particles.length = 0;
    const count = Math.max(34, Math.min(78, Math.floor((width * height) / 18000)));

    for (let index = 0; index < count; index += 1) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.22,
        vy: (Math.random() - 0.5) * 0.22,
        radius: Math.random() * 1.8 + 1.2
      });
    }
  }

  function draw() {
    context.clearRect(0, 0, width, height);
    context.lineWidth = 1;

    particles.forEach((particle, index) => {
      if (!reduceMotion) {
        particle.x += particle.vx;
        particle.y += particle.vy;

        if (particle.x < 0 || particle.x > width) {
          particle.vx *= -1;
        }

        if (particle.y < 0 || particle.y > height) {
          particle.vy *= -1;
        }
      }

      context.beginPath();
      context.fillStyle = "rgba(32, 36, 33, 0.28)";
      context.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      context.fill();

      for (let next = index + 1; next < particles.length; next += 1) {
        const other = particles[next];
        const distance = Math.hypot(particle.x - other.x, particle.y - other.y);

        if (distance < 118) {
          context.beginPath();
          context.strokeStyle = `rgba(25, 138, 138, ${0.16 - distance / 900})`;
          context.moveTo(particle.x, particle.y);
          context.lineTo(other.x, other.y);
          context.stroke();
        }
      }
    });

    if (!reduceMotion) {
      window.requestAnimationFrame(draw);
    }
  }

  window.addEventListener("resize", resize);
  resize();
}

initField();
