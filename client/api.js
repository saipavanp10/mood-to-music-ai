const API_URL = "http://localhost:8000";

export async function login(username, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) throw new Error("Login failed");
    return response.json();
}

export async function register(username, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) throw new Error("Registration failed");
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
