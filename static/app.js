// Global Application State
let currentLat = 30.90; // Default Ludhiana, Punjab
let currentLon = 75.85;
let currentLang = 'en';
let weatherData = null;
let leafletMap = null;
let leafletMarker = null;
let xaiChart = null;
let isVoiceActive = false;
let authToken = localStorage.getItem('krishi_auth_token') || null;
let currentUser = null;
let lastRecommendedCrop = null;
let chatSessionId = 'session_' + Math.random().toString(36).substring(2, 9);
let currentUiDict = {};

// Language locale map for Web Speech API
const VOICE_LANG_MAP = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'pa': 'pa-IN',
    'mr': 'mr-IN',
    'te': 'te-IN',
    'ta': 'ta-IN',
    'bn': 'bn-IN',
    'gu': 'gu-IN',
    'kn': 'kn-IN'
};

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    fetchWeather(currentLat, currentLon);
    setupLanguageListener();
    setupVoiceListener();
    checkAuthState();
});

// Auth State Check
async function checkAuthState() {
    if (!authToken) {
        updateAuthUI(null);
        return;
    }

    try {
        const res = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        if (data.authenticated) {
            currentUser = data.user;
            updateAuthUI(currentUser);
        } else {
            logoutUser();
        }
    } catch (err) {
        console.error("Auth check failed:", err);
    }
}

function updateAuthUI(user) {
    const btnOpen = document.getElementById('btn-auth-open');
    const badge = document.getElementById('user-profile-badge');
    const nameDisplay = document.getElementById('user-name-display');

    if (user) {
        btnOpen.style.display = 'none';
        badge.style.display = 'flex';
        nameDisplay.innerHTML = `<i class="fa-solid fa-circle-user"></i> ${user.name}`;
    } else {
        btnOpen.style.display = 'inline-flex';
        badge.style.display = 'none';
    }
}

// Open / Close Auth Modal
function openAuthModal() {
    document.getElementById('auth-modal').style.display = 'flex';
}

function closeAuthModal() {
    document.getElementById('auth-modal').style.display = 'none';
}

function switchAuthTab(tab) {
    document.getElementById('auth-tab-login').classList.remove('active');
    document.getElementById('auth-tab-register').classList.remove('active');
    
    if (tab === 'login') {
        document.getElementById('auth-tab-login').classList.add('active');
        document.getElementById('form-login').style.display = 'block';
        document.getElementById('form-register').style.display = 'none';
    } else {
        document.getElementById('auth-tab-register').classList.add('active');
        document.getElementById('form-login').style.display = 'none';
        document.getElementById('form-register').style.display = 'block';
    }
}

// Login Handler
async function handleLogin(e) {
    e.preventDefault();
    const phone = document.getElementById('login-phone').value;
    const pass = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_or_email: phone, password: pass })
        });
        const data = await res.json();
        if (res.ok) {
            authToken = data.token;
            localStorage.setItem('krishi_auth_token', authToken);
            currentUser = data.user;
            updateAuthUI(currentUser);
            closeAuthModal();
            alert(`Welcome back, ${currentUser.name}!`);
        } else {
            alert(data.detail || "Login failed.");
        }
    } catch (err) {
        alert("Error connecting to server.");
    }
}

// Register Handler
async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const phone = document.getElementById('reg-phone').value;
    const pass = document.getElementById('reg-password').value;

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, phone_or_email: phone, password: pass, preferred_language: currentLang })
        });
        const data = await res.json();
        if (res.ok) {
            authToken = data.token;
            localStorage.setItem('krishi_auth_token', authToken);
            currentUser = data.user;
            updateAuthUI(currentUser);
            closeAuthModal();
            alert(`Account created successfully! Welcome, ${currentUser.name}.`);
        } else {
            alert(data.detail || "Registration failed.");
        }
    } catch (err) {
        alert("Error connecting to server.");
    }
}

function logoutUser() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('krishi_auth_token');
    updateAuthUI(null);
}

// History Drawer Modal
async function openHistoryModal() {
    document.getElementById('history-modal').style.display = 'flex';
    const list = document.getElementById('history-list');
    list.innerHTML = '<p><i class="fa-solid fa-spinner fa-spin"></i> Loading saved records...</p>';

    try {
        const res = await fetch('/api/history', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        renderHistoryList(data.history);
    } catch (err) {
        list.innerHTML = '<p style="color:red;">Failed to load history.</p>';
    }
}

function closeHistoryModal() {
    document.getElementById('history-modal').style.display = 'none';
}

function renderHistoryList(history) {
    const list = document.getElementById('history-list');
    list.innerHTML = '';

    if (!history || history.length === 0) {
        list.innerHTML = '<p style="color:#6b7280;">No past predictions saved yet. Run a recommendation to save history!</p>';
        return;
    }

    history.forEach(item => {
        const card = document.createElement('div');
        card.className = 'history-card';
        card.innerHTML = `
            <div>
                <span class="history-crop-name">🌾 ${item.translated_crop_name} (${item.fit_percentage}% Match)</span>
                <div class="history-date">Date: ${item.date} | Soil: N:${item.soil_data.N}, P:${item.soil_data.P}, K:${item.soil_data.K}, pH:${item.soil_data.pH}</div>
            </div>
            <button class="btn btn-secondary btn-xs" onclick="reloadHistoryRecord(${JSON.stringify(item.soil_data).replace(/"/g, '&quot;')})">Reload Soil</button>
        `;
        list.appendChild(card);
    });
}

function reloadHistoryRecord(soil) {
    document.getElementById('input-n').value = soil.N;
    document.getElementById('val-n').innerText = soil.N;
    document.getElementById('input-p').value = soil.P;
    document.getElementById('val-p').innerText = soil.P;
    document.getElementById('input-k').value = soil.K;
    document.getElementById('val-k').innerText = soil.K;
    document.getElementById('input-ph').value = soil.pH;
    document.getElementById('val-ph').innerText = soil.pH;
    closeHistoryModal();
    alert("Soil values loaded from history! Click Generate Recommendation to view advisory.");
}

// AI Chatbot Widget Logic ("Krishi Mitra")
function toggleChatbot() {
    const win = document.getElementById('chatbot-window');
    win.style.display = (win.style.display === 'none' || !win.style.display) ? 'flex' : 'none';
}

function sendQuickPrompt(text) {
    document.getElementById('chat-input').value = text;
    sendChatMessage();
}

function handleChatKeyPress(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    appendChatBubble(msg, 'user');
    input.value = '';

    const headers = { 'Content-Type': 'application/json' };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                message: msg,
                session_id: chatSessionId,
                lang_code: currentLang,
                context_crop: lastRecommendedCrop
            })
        });
        const data = await res.json();
        appendChatBubble(data.reply, 'bot');

        if (isVoiceActive) {
            speakText(data.reply);
        }
    } catch (err) {
        appendChatBubble("Sorry, I'm having trouble responding right now.", 'bot');
    }
}

function appendChatBubble(text, sender) {
    const container = document.getElementById('chat-messages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}-bubble`;
    bubble.innerHTML = parseMarkdownBold(text);
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

// Slider value display updates
function updateSliderVal(param, val) {
    document.getElementById(`val-${param}`).innerText = val;
}

// Switch Soil Input Tabs
function switchSoilTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (tab === 'manual') {
        document.getElementById('tab-manual-btn').classList.add('active');
        document.getElementById('tab-manual').classList.add('active');
    } else {
        document.getElementById('tab-upload-btn').classList.add('active');
        document.getElementById('tab-upload').classList.add('active');
    }
}

// Initialize Leaflet Map
function initMap() {
    leafletMap = L.map('map').setView([currentLat, currentLon], 8);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(leafletMap);

    leafletMarker = L.marker([currentLat, currentLon], { draggable: true }).addTo(leafletMap);

    leafletMarker.on('dragend', function (e) {
        const latlng = leafletMarker.getLatLng();
        currentLat = latlng.lat;
        currentLon = latlng.lng;
        fetchWeather(currentLat, currentLon);
    });

    leafletMap.on('click', function (e) {
        currentLat = e.latlng.lat;
        currentLon = e.latlng.lng;
        leafletMarker.setLatLng([currentLat, currentLon]);
        fetchWeather(currentLat, currentLon);
    });
}

// Detect GPS Browser Geolocation
function detectGPSLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                currentLat = pos.coords.latitude;
                currentLon = pos.coords.longitude;
                leafletMap.setView([currentLat, currentLon], 10);
                leafletMarker.setLatLng([currentLat, currentLon]);
                fetchWeather(currentLat, currentLon);
            },
            (err) => {
                alert("GPS detection unavailable. Click anywhere on the map to pick location.");
            }
        );
    } else {
        alert("Browser Geolocation is not supported.");
    }
}

// Fetch Live Weather from Backend
async function fetchWeather(lat, lon) {
    try {
        const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
        weatherData = await res.json();
        
        document.getElementById('location-name').innerText = weatherData.location_name || `Lat: ${lat.toFixed(2)}, Lon: ${lon.toFixed(2)}`;
        document.getElementById('weather-temp').innerText = `${weatherData.temperature}°C`;
        document.getElementById('weather-humidity').innerText = `${weatherData.humidity}%`;
        document.getElementById('weather-rain').innerText = `${weatherData.rainfall} mm`;

        const forecastRow = document.getElementById('forecast-row');
        forecastRow.innerHTML = '';
        if (weatherData.forecast && weatherData.forecast.length > 0) {
            weatherData.forecast.forEach(f => {
                const card = document.createElement('div');
                card.className = 'forecast-card';
                card.innerHTML = `
                    <div class="f-date">${f.date}</div>
                    <div class="f-temp">${f.max_temp}°C</div>
                    <div style="font-size:10px; opacity:0.8;">🌧 ${f.precip}mm</div>
                `;
                forecastRow.appendChild(card);
            });
        }
    } catch (err) {
        console.error("Error fetching weather:", err);
    }
}

// Handle Soil Report File Upload
async function handleFileUpload(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    const formData = new FormData();
    formData.append("file", file);

    const statusBox = document.getElementById('ocr-status');
    statusBox.style.display = 'block';
    statusBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Parsing report text...';

    try {
        const res = await fetch('/api/parse-report', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        applyExtractedSoilData(data.extracted_soil_data);
    } catch (err) {
        console.error("OCR parse error:", err);
        statusBox.innerHTML = '<span style="color:red;">Failed to read soil report file. Try sample button.</span>';
    }
}

// Load Sample Report for Fast Demoing
async function loadSampleReport() {
    try {
        const res = await fetch('/api/sample-report');
        const data = await res.json();
        applyExtractedSoilData(data);
        document.getElementById('tab-upload-btn').click();
    } catch (err) {
        console.error("Error loading sample report:", err);
    }
}

function applyExtractedSoilData(soil) {
    document.getElementById('input-n').value = soil.N;
    document.getElementById('val-n').innerText = soil.N;
    document.getElementById('input-p').value = soil.P;
    document.getElementById('val-p').innerText = soil.P;
    document.getElementById('input-k').value = soil.K;
    document.getElementById('val-k').innerText = soil.K;
    document.getElementById('input-ph').value = soil.ph;
    document.getElementById('val-ph').innerText = soil.ph;
    
    if (soil.soil_type) {
        document.getElementById('input-soil-type').value = soil.soil_type;
    }

    const statusBox = document.getElementById('ocr-status');
    statusBox.style.display = 'block';
    statusBox.innerHTML = `
        <div class="ocr-badge"><i class="fa-solid fa-circle-check"></i> Report Parsed Successfully</div>
        <div class="extracted-grid">
            <div><strong>N:</strong> ${soil.N} kg/ha</div>
            <div><strong>P:</strong> ${soil.P} kg/ha</div>
            <div><strong>K:</strong> ${soil.K} kg/ha</div>
            <div><strong>pH:</strong> ${soil.ph}</div>
            <div><strong>Moisture:</strong> ${soil.moisture || 20}%</div>
            <div><strong>Soil:</strong> ${soil.soil_type || 'Loamy'}</div>
        </div>
    `;
}

// Get Recommendation from Backend
async function getRecommendation() {
    const btn = document.getElementById('btn-submit');
    const origText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-gear fa-spin"></i> Processing Recommendation...';
    btn.disabled = true;

    const payload = {
        N: parseFloat(document.getElementById('input-n').value),
        P: parseFloat(document.getElementById('input-p').value),
        K: parseFloat(document.getElementById('input-k').value),
        ph: parseFloat(document.getElementById('input-ph').value),
        temperature: weatherData ? weatherData.temperature : 26.0,
        humidity: weatherData ? weatherData.humidity : 65.0,
        rainfall: weatherData ? weatherData.rainfall : 120.0,
        soil_type: document.getElementById('input-soil-type').value,
        season: document.getElementById('input-season').value,
        lang_code: currentLang
    };

    const headers = { 'Content-Type': 'application/json' };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const res = await fetch('/api/recommend', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        lastRecommendedCrop = data.recommended_crop;
        renderResults(data);
    } catch (err) {
        console.error("Recommendation error:", err);
        alert("Failed to connect to recommendation server.");
    } finally {
        btn.innerHTML = origText;
        btn.disabled = false;
    }
}

// Render Results Dashboard
function renderResults(data) {
    document.getElementById('results-placeholder').style.display = 'none';
    document.getElementById('results-container').style.display = 'block';

    document.getElementById('rec-crop-name').innerText = data.recommended_crop;
    document.getElementById('rec-translated-name').innerText = data.translated_crop_name;
    document.getElementById('rec-confidence').innerText = `${data.xai_explanation.overall_fit_percentage}%`;

    const altTags = document.getElementById('alt-crops-list');
    altTags.innerHTML = '';
    if (data.top_crops && data.top_crops.length > 1) {
        data.top_crops.slice(1).forEach(alt => {
            const span = document.createElement('span');
            span.className = 'alt-tag';
            span.innerText = `${alt.translated_crop} (${alt.confidence_percentage}%)`;
            altTags.appendChild(span);
        });
    }

    const xai = data.xai_explanation;
    document.getElementById('xai-summary').innerHTML = parseMarkdownBold(xai.summary);
    
    const reasonsList = document.getElementById('xai-reasons-list');
    reasonsList.innerHTML = '';
    if (xai.key_reasons) {
        xai.key_reasons.forEach(r => {
            const li = document.createElement('li');
            li.innerHTML = parseMarkdownBold(r);
            reasonsList.appendChild(li);
        });
    }

    const details = xai.crop_details || {};
    document.getElementById('agro-season').innerText = details.sowing_season || "Kharif / Rabi";
    document.getElementById('agro-water').innerText = details.water_requirement || "Moderate";
    document.getElementById('agro-duration').innerText = details.duration || "100-120 days";
    document.getElementById('agro-fertilizer').innerText = details.fertilizer || "Apply balanced NPK";
    document.getElementById('agro-tips').innerText = details.care_tips || "Ensure proper weeding and field drainage.";

    renderRadarChart(xai.radar_scores);
    renderSchemes(data.schemes);

    if (isVoiceActive) {
        speakText(`Top recommended crop is ${data.translated_crop_name}. Match score is ${xai.overall_fit_percentage} percent.`);
    }
}

// Render Chart.js Radar Chart
function renderRadarChart(scores) {
    const ctx = document.getElementById('xai-chart').getContext('2d');
    if (xaiChart) {
        xaiChart.destroy();
    }

    const labels = Object.keys(scores);
    const values = Object.values(scores);

    xaiChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Parameter Match Score (%)',
                data: values,
                backgroundColor: 'rgba(82, 183, 136, 0.25)',
                borderColor: '#2d6a4f',
                borderWidth: 2,
                pointBackgroundColor: '#1b4332'
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: { color: 'rgba(0,0,0,0.1)' },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Render Government Schemes Cards
function renderSchemes(schemes) {
    const grid = document.getElementById('schemes-list');
    grid.innerHTML = '';

    if (!schemes || schemes.length === 0) {
        grid.innerHTML = '<p style="font-size:13px; color:#6b7280;">No specific scheme listed for this crop.</p>';
        return;
    }

    schemes.forEach(s => {
        const card = document.createElement('div');
        card.className = 'scheme-card';
        card.innerHTML = `
            <div class="scheme-header">
                <span class="scheme-name">${s.name}</span>
                <span class="scheme-type">${s.type}</span>
            </div>
            <div class="scheme-benefit"><strong>Benefit:</strong> ${s.benefit}</div>
            <div class="scheme-footer">
                <span><strong>Eligibility:</strong> ${s.eligibility}</span>
                <a href="${s.link}" target="_blank" class="scheme-link"><i class="fa-solid fa-arrow-up-right-from-square"></i> Portal</a>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Setup Multilingual Language Change Handler with 100% Comprehensive Coverage
function setupLanguageListener() {
    const sel = document.getElementById('language-select');
    sel.addEventListener('change', async (e) => {
        currentLang = e.target.value;
        try {
            const res = await fetch(`/api/translations?lang=${currentLang}`);
            const data = await res.json();
            currentUiDict = data.ui_strings || {};
            applyLanguageStrings(currentUiDict);
            
            // Re-fetch recommendation if results are visible
            if (document.getElementById('results-container').style.display !== 'none') {
                getRecommendation();
            }
        } catch (err) {
            console.error("Translation fetch error:", err);
        }
    });
}

function applyLanguageStrings(ui) {
    if (!ui) return;
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (ui[key]) {
            el.innerText = ui[key];
        }
    });
}

// Enhanced Warm & Natural Speech Synthesis (Web Speech API)
function setupVoiceListener() {
    const btn = document.getElementById('voice-btn');
    btn.addEventListener('click', () => {
        isVoiceActive = !isVoiceActive;
        btn.style.background = isVoiceActive ? 'rgba(82, 183, 136, 0.4)' : 'rgba(255,255,255,0.1)';
        if (isVoiceActive) {
            speakText("Voice assistance activated. I will read recommendations in your language.");
        } else {
            window.speechSynthesis.cancel();
        }
    });
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        
        // Clean text of markdown stars before reading
        const cleanText = text.replace(/\*\*/g, '').replace(/👉/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        
        // Set locale based on selected language
        utterance.lang = VOICE_LANG_MAP[currentLang] || 'en-IN';
        
        // Adjust tone settings for a warm, natural, friendly agricultural voice
        utterance.rate = 0.88; // Calm & friendly pace for farmers
        utterance.pitch = 1.05; // Slightly warmer tone

        // Pick localized voice if available in browser
        const voices = window.speechSynthesis.getVoices();
        const targetLocale = VOICE_LANG_MAP[currentLang] || 'en-IN';
        const matchingVoice = voices.find(v => v.lang.startsWith(targetLocale) || v.lang.includes(currentLang));
        if (matchingVoice) {
            utterance.voice = matchingVoice;
        }

        window.speechSynthesis.speak(utterance);
    }
}

function parseMarkdownBold(str) {
    if (!str) return '';
    return str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}
