const contextValue = document.getElementById('contextValue');
const gestureValue = document.getElementById('gestureValue');
const phraseValue = document.getElementById('phraseValue');
const errorBox = document.getElementById('errorBox');
const trainBtn = document.getElementById('trainBtn');
const contextButtons = [...document.querySelectorAll('.btn-context')];

function setError(message = '') {
  errorBox.textContent = message;
}

function setActiveContext(contextName) {
  contextButtons.forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.context === contextName);
  });
}

async function refreshState() {
  try {
    const res = await fetch('/get_state');
    const data = await res.json();

    contextValue.textContent = data.context;
    gestureValue.textContent = data.gesture;
    phraseValue.textContent = data.phrase;
    setActiveContext(data.context);

  } catch (err) {
    setError(err.message);
  }
}

async function setContext(contextName) {
  setError('');
  try {
    const res = await fetch('/set_context', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: contextName }),
    });

    await refreshState();

  } catch (err) {
    setError(err.message);
  }
}

async function trainGesture() {
  setError('');

  const gestureName = prompt('Enter gesture name:');
  if (!gestureName || !gestureName.trim()) {
    setError("❌ Gesture name required");
    return;
  }

  const cafeMsg = prompt('Cafe message:');
  if (cafeMsg === null) return;

  const hospitalMsg = prompt('Hospital message:');
  if (hospitalMsg === null) return;

  const collegeMsg = prompt('College message:');
  if (collegeMsg === null) return;

  const bankMsg = prompt('Bank message:');
  if (bankMsg === null) return;

  console.log("🔥 Sending request...");

  try {
    const res = await fetch('/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gesture_name: gestureName.trim(),
        messages: {
          cafe: cafeMsg.trim(),
          hospital: hospitalMsg.trim(),
          college: collegeMsg.trim(),
          bank: bankMsg.trim()
        }
      }),
    });

    const data = await res.json();

    console.log("🔥 Response:", data);

    if (!res.ok) throw new Error(data.error || 'Training failed');

    setError(`✅ Gesture trained: ${data.gesture_name}`);

  } catch (err) {
    console.error(err);
    setError("❌ Training failed");
  }
}

trainBtn.addEventListener('click', trainGesture);

contextButtons.forEach((btn) => {
  btn.addEventListener('click', () => setContext(btn.dataset.context));
});

refreshState();
setInterval(refreshState, 500);