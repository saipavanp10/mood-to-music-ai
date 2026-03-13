const API_URL = window.location.hostname === 'localhost'
    ? "http://localhost:8000"                          // local dev
    : "https://mood-to-music-api.onrender.com";        // ← replace with your actual Render URL

export async function login(username, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Login failed");
    }
    return response.json();
}

export async function register(username, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Registration failed");
    }
    return response.json();
}

export async function analyzeMood(userId, imageBlob) {
    const formData = new FormData();
    formData.append("file", imageBlob, "capture.jpg");

    const response = await fetch(`${API_URL}/analyze?user_id=${userId}`, {
        method: "POST",
        body: formData,
    });
    if (!response.ok) throw new Error("Analysis failed");
    return response.json();
}

export async function getHistory(userId) {
    const response = await fetch(`${API_URL}/history/${userId}`);
    if (!response.ok) throw new Error("Failed to fetch history");
    return response.json();
}

export async function getAdminHistory() {
    const response = await fetch(`${API_URL}/admin/history`);
    if (!response.ok) throw new Error("Failed to fetch admin history");
    return response.json();
}

export async function clearHistory(userId) {
    const response = await fetch(`${API_URL}/history/${userId}`, {
        method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to clear history");
    return response.json();
}
