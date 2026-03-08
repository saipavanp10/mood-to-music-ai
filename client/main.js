import { login, register, analyzeMood, getHistory } from './api.js';

let currentUser = null;

const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const video = document.getElementById('webcam');
const resultArea = document.getElementById('result-area');

// --- AUTH LOGIC ---
document.getElementById('login-btn').addEventListener('click', async () => {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    try {
        const data = await login(user, pass);
        currentUser = data;
        showDashboard();
    } catch (e) {
        document.getElementById('auth-error').innerText = e.message;
    }
});

document.getElementById('register-btn').addEventListener('click', async () => {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    try {
        const data = await register(user, pass);
        currentUser = data;
        showDashboard();
    } catch (e) {
        document.getElementById('auth-error').innerText = e.message;
    }
});

document.getElementById('logout-btn').addEventListener('click', () => {
    currentUser = null;
    authSection.classList.remove('hidden');
    dashboardSection.classList.add('hidden');
    stopWebcam();
});

// --- DASHBOARD LOGIC ---
async function showDashboard() {
    authSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    document.getElementById('user-display').innerText = currentUser.username;
    startWebcam();
    loadHistory();
}

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing webcam", err);
        alert("Cannot access webcam!");
    }
}

function stopWebcam() {
    const stream = video.srcObject;
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
    }
}

// --- ANALYSIS LOGIC ---
document.getElementById('analyze-btn').addEventListener('click', async () => {
    if (!video.srcObject) return;

    // Capture Frame
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        try {
            document.getElementById('analyze-btn').innerText = "Processing...";
            const res = await analyzeMood(currentUser.id, blob);

            // Update UI
            resultArea.classList.remove('hidden');
            document.getElementById('mood-text').innerText = `Mood: ${res.mood.toUpperCase()}`;

            const grid = document.getElementById('songs-grid');
            grid.innerHTML = ""; // Clear previous

            res.songs.forEach(song => {
                const card = document.createElement('div');
                card.className = "song-card";
                card.innerHTML = `
          <img src="${song.image}" alt="${song.title}">
          <div class="song-info">
            <h4>${song.title}</h4>
            <p>${song.artist}</p>
            <a href="${song.link}" target="_blank" class="play-btn">Play Now</a>
          </div>
        `;
                grid.appendChild(card);
            });

            loadHistory(); // Refresh history
        } catch (e) {
            alert("Analysis failed: " + e.message);
        } finally {
            document.getElementById('analyze-btn').innerText = "Analyze Mood";
        }
    }, 'image/jpeg');
});

async function loadHistory() {
    try {
        const history = await getHistory(currentUser.id);
        const list = document.getElementById('history-list');
        list.innerHTML = "";
        history.forEach(item => {
            const li = document.createElement('li');
            li.style.borderBottom = "1px solid rgba(255,255,255,0.1)";
            li.style.padding = "5px 0";
            li.innerHTML = `
        <span style="color: #4fd1c5; font-weight: bold;">${item.mood}</span> 
        - <small>${new Date(item.timestamp).toLocaleTimeString()}</small>
      `;
            list.appendChild(li);
        });
    } catch (e) {
        console.error(e);
    }
}
