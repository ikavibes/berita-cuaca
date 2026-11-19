from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Koordinat kota untuk Open-Meteo API (Real-time, akurat, dan tanpa API Key)
CITY_COORDS = {
    # Indonesia
    "Pontianak": {"lat": -0.0263, "lon": 109.3425},
    "Singkawang": {"lat": 0.9085, "lon": 108.9859},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Bandung": {"lat": -6.9175, "lon": 107.6191},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695},
    "Denpasar": {"lat": -8.6705, "lon": 115.2126},
    # Luar Negeri
    "Kuala Lumpur": {"lat": 3.1390, "lon": 101.6869},
    "Singapura": {"lat": 1.3521, "lon": 103.8198},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Seoul": {"lat": 37.5665, "lon": 126.9780},
    "Dubai": {"lat": 25.2048, "lon": 55.2708},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Kairo": {"lat": 30.0444, "lon": 31.2357},
    "Moskwa": {"lat": 55.7558, "lon": 37.6173}
}

# Pengelompokan kota untuk <optgroup> di dropdown
CITY_GROUPS = {
    "Indonesia": ["Pontianak", "Singkawang", "Jakarta", "Bandung",
                  "Surabaya", "Yogyakarta", "Denpasar"],
    "Luar Negeri": ["Kuala Lumpur", "Singapura", "Bangkok", "Tokyo", "Seoul",
                    "Dubai", "London", "Paris", "New York", "Sydney",
                    "Kairo", "Moskwa"]
}

def get_weather_condition(code):
    if code == 0:
        return "Cerah"
    elif code in [1, 2]:
        return "Cerah Berawan"
    elif code == 3:
        return "Berawan"
    elif code in [45, 48]:
        return "Berkabut"
    elif code in [51, 53, 55, 56, 57]:
        return "Gerimis"
    elif code in [61, 63, 66, 80, 81]:
        return "Hujan"
    elif code in [65, 67, 82]:
        return "Hujan Lebat"
    elif code in [95, 96, 99]:
        return "Badai Petir"
    return "Cerah Berawan"

def fetch_real_weather(city_name):
    coords = CITY_COORDS.get(city_name, CITY_COORDS["Pontianak"])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json().get("current", {})
            temp_num = data.get('temperature_2m', 30)
            hum_num = data.get('relative_humidity_2m', 80)
            wind_num = data.get('wind_speed_10m', 10)
            temp = f"{int(temp_num)}°C"
            humidity = f"{hum_num}%"
            wind = f"{int(wind_num)} km/h"
            code = data.get('weather_code', 0)
            condition = get_weather_condition(code)
            desc = f"Data real-time Open-Meteo untuk {city_name}: Suhu {temp}, kondisi {condition} dengan kelembapan {humidity} dan kecepatan angin {wind}."
            return {"temp": temp, "condition": condition, "humidity": humidity,
                    "wind": wind, "wind_kmh": int(wind_num), "code": code, "desc": desc}
    except Exception as e:
        print("Error fetching weather:", e)
    
    return {"temp": "31°C", "condition": "Cerah Berawan", "humidity": "80%",
            "wind": "10 km/h", "wind_kmh": 10, "code": 1,
            "desc": f"Kondisi cuaca terkini di {city_name}."}

NEWS_DATA = [
    {"title": "Waspada Perubahan Cuaca Ekstrem di Wilayah Perkotaan", "date": "06 November 2026", "summary": "Badan Meteorologi mengingatkan masyarakat untuk tetap waspada terhadap potensi perubahan cuaca mendadak."},
    {"title": "Tips Menjaga Kesehatan di Musim Pancaroba", "date": "05 November 2026", "summary": "Konsumsi vitamin C dan jaga asupan cairan tubuh agar tetap bugar menghadapi pancaroba."},
    {"title": "Prakiraan Musim Hujan Mulai Merata di Pulau Jawa", "date": "04 November 2026", "summary": "Sebagian besar wilayah Jawa mulai memasuki awal musim hujan dengan intensitas ringan hingga sedang."}
]

PAGE_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Berita Cuaca - Kelompok 3</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }

        /* ==== Tema warna kartu sesuai cuaca ==== */
        .wx-card { transition: box-shadow .7s ease, border-color .7s ease; }
        .wx-clear   { box-shadow: 0 0 60px -15px rgba(251,191,36,.55); border-color: rgba(251,191,36,.40) !important; }
        .wx-cloudy  { box-shadow: 0 0 60px -18px rgba(148,163,184,.55); border-color: rgba(148,163,184,.40) !important; }
        .wx-fog     { box-shadow: 0 0 60px -18px rgba(226,232,240,.50); border-color: rgba(226,232,240,.35) !important; }
        .wx-drizzle { box-shadow: 0 0 60px -15px rgba(56,189,248,.50); border-color: rgba(56,189,248,.40) !important; }
        .wx-rain    { box-shadow: 0 0 65px -12px rgba(14,165,233,.60); border-color: rgba(14,165,233,.50) !important; }
        .wx-heavy   { box-shadow: 0 0 75px -10px rgba(37,99,235,.75); border-color: rgba(59,130,246,.65) !important; }
        .wx-storm   { box-shadow: 0 0 85px -8px  rgba(168,85,247,.80); border-color: rgba(168,85,247,.70) !important; }

        /* ==== Matahari animasi (cuaca cerah) — sebagai latar belakang ==== */
        #sun {
            position: absolute; top: -14px; right: 27%;
            width: 144px; height: 144px;
            opacity: 0; transition: opacity 1s ease; z-index: 0;
            pointer-events: none;
        }
        #sun.on { opacity: .9; }
        #sun .sun-core {
            position: absolute; inset: 34%; border-radius: 50%;
            background: radial-gradient(circle at 42% 38%, #fffde7 0%, #fde047 42%, #f59e0b 100%);
            box-shadow: 0 0 24px 10px rgba(253,224,71,.45), 0 0 90px 40px rgba(251,191,36,.18);
            animation: denyut 4.5s ease-in-out infinite;
            filter: blur(.4px);
        }
        #sun .sun-rays {
            position: absolute; inset: 0; border-radius: 50%;
            background: repeating-conic-gradient(from 0deg,
                rgba(253,224,71,.55) 0deg 2.5deg,
                rgba(253,224,71,0)   2.5deg 17deg);
            -webkit-mask: radial-gradient(circle, transparent 50%, #000 56%);
            mask: radial-gradient(circle, transparent 50%, #000 56%);
            animation: putar 22s linear infinite;
            filter: blur(1.1px);
        }
        @keyframes putar { to { transform: rotate(360deg); } }
        @keyframes denyut { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        @media (prefers-reduced-motion: reduce) {
            #sun .sun-rays, #sun .sun-core { animation: none; }
        }
        /* layar kecil: sembunyikan matahari agar tidak menabrak judul/dropdown */
        @media (max-width: 1024px) {
            #sun { display: none; }
        }

        /* ==== Kilat badai ==== */
        #lightning {
            position: absolute; inset: 0; border-radius: 1rem;
            background: radial-gradient(ellipse at 50% 0%, rgba(255,255,255,.95), rgba(196,181,253,.35) 55%, transparent 80%);
            opacity: 0; pointer-events: none; mix-blend-mode: screen; z-index: 5;
        }
        #lightning.flash { animation: kilat .9s ease-out; }
        @keyframes kilat {
            0%   { opacity: 0; }
            6%   { opacity: .55; }
            10%  { opacity: .08; }
            16%  { opacity: .40; }
            24%  { opacity: 0; }
            32%  { opacity: .22; }
            42%  { opacity: 0; }
        }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col">
    <!-- Navbar / Header -->
    <header class="bg-slate-800 border-b border-slate-700 py-4 px-6 shadow-md">
        <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
                <h1 class="text-2xl font-bold text-sky-400">☀️ Portal Berita Cuaca</h1>
                <p class="text-sm text-slate-400">Mata Pelajaran Dasar Pemrograman (DP)</p>
            </div>
            <div class="bg-slate-700/60 px-4 py-2 rounded-xl border border-slate-600 flex items-center gap-3">
                <div class="text-right">
                    <p class="text-xs text-sky-300 font-medium">Kelompok {{ group.kelompok }}</p>
                    <p class="text-sm font-bold text-white">Project: {{ group.project }}</p>
                    <p class="text-xs text-slate-400">Anggota: {{ group.anggota | join(', ') }}</p>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto p-6 flex-grow w-full grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <!-- Left 2 columns: Weather Dashboard & City Selector -->
        <section class="md:col-span-2 space-y-6">
            <!-- Weather Card -->
            <div id="weather-card" class="wx-card bg-gradient-to-br from-slate-800 to-slate-800/80 p-6 rounded-2xl border border-slate-700 shadow-xl relative overflow-hidden"
                 data-condition="{{ weather.condition }}" data-code="{{ weather.code }}" data-wind="{{ weather.wind_kmh }}">
                <div id="sun" aria-hidden="true">
                    <div class="sun-rays"></div>
                    <div class="sun-core"></div>
                </div>
                <canvas id="weather-fx" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
                <div id="lightning"></div>
                <div class="relative z-10">
                <div class="flex justify-between items-start mb-6">
                    <div>
                        <h2 class="text-xl font-bold text-white">Prakiraan Cuaca Terkini</h2>
                        <p class="text-sm text-slate-400">Pilih kota untuk melihat kondisi cuaca</p>
                        <p class="text-xs text-emerald-400 mt-1">
                            <span class="inline-block w-2 h-2 bg-emerald-400 rounded-full animate-pulse align-middle"></span>
                            Realtime • diperbarui <span id="last-update">-</span>
                        </p>
                    </div>
                    <form method="GET" class="flex gap-2">
                        <select name="city" onchange="this.form.submit()" class="bg-slate-700 text-white text-sm rounded-xl px-3 py-2 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-sky-500">
                            {% for grup, kota_list in city_groups.items() %}
                            <optgroup label="{{ grup }}">
                                {% for c in kota_list %}
                                <option value="{{ c }}" {% if c == city %}selected{% endif %}>{{ c }}</option>
                                {% endfor %}
                            </optgroup>
                            {% endfor %}
                        </select>
                    </form>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 items-center">
                    <div class="bg-slate-700/50 p-4 rounded-xl border border-slate-600/50">
                        <p class="text-xs text-slate-400">Kota</p>
                        <p id="weather-city" class="text-lg font-bold text-sky-300">{{ city }}</p>
                    </div>
                    <div class="bg-slate-700/50 p-4 rounded-xl border border-slate-600/50">
                        <p class="text-xs text-slate-400">Suhu</p>
                        <p id="weather-temp" class="text-2xl font-bold text-amber-400">{{ weather.temp }}</p>
                    </div>
                    <div class="bg-slate-700/50 p-4 rounded-xl border border-slate-600/50">
                        <p class="text-xs text-slate-400">Kondisi</p>
                        <p class="text-sm font-bold text-emerald-400">
                            <span id="weather-icon" class="mr-1"></span><span id="weather-condition">{{ weather.condition }}</span>
                        </p>
                    </div>
                    <div class="bg-slate-700/50 p-4 rounded-xl border border-slate-600/50">
                        <p class="text-xs text-slate-400">Kelembapan</p>
                        <p id="weather-humidity" class="text-sm font-bold text-sky-200">{{ weather.humidity }}</p>
                    </div>
                    <div class="bg-slate-700/50 p-4 rounded-xl border border-slate-600/50">
                        <p class="text-xs text-slate-400">Kecepatan Angin</p>
                        <p id="weather-wind" class="text-sm font-bold text-indigo-300">💨 {{ weather.wind }}</p>
                    </div>
                </div>

                <div class="mt-6 bg-slate-900/40 p-4 rounded-xl border border-slate-700/50">
                    <p class="text-xs text-slate-400 uppercase tracking-wider mb-1">Analisis Cuaca</p>
                    <p id="weather-desc" class="text-sm text-slate-200">{{ weather.desc }}</p>
                </div>
                </div>
            </div>

            <!-- Weather Articles / News -->
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl">
                <h3 class="text-lg font-bold text-white mb-4">📰 Berita Cuaca & Artikel Pilihan</h3>
                <div class="space-y-4">
                    {% for item in news %}
                    <article class="bg-slate-700/40 p-4 rounded-xl border border-slate-700 hover:border-sky-500/50 transition-all">
                        <div class="flex justify-between items-center mb-1">
                            <h4 class="font-semibold text-white text-base">{{ item.title }}</h4>
                            <span class="text-xs text-slate-400">{{ item.date }}</span>
                        </div>
                        <p class="text-sm text-slate-300">{{ item.summary }}</p>
                    </article>
                    {% endfor %}
                </div>
            </div>
        </section>

        <!-- Right Column: Project Info & Members -->
        <aside class="space-y-6">
            <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl">
                <h3 class="text-lg font-bold text-white mb-3">📌 Informasi Kelompok</h3>
                <ul class="space-y-3 text-sm text-slate-300">
                    <li class="flex justify-between pb-2 border-b border-slate-700">
                        <span class="text-slate-400">Mata Pelajaran:</span>
                        <span class="font-semibold text-white">Dasar Pemrograman (DP)</span>
                    </li>
                    <li class="flex justify-between pb-2 border-b border-slate-700">
                        <span class="text-slate-400">Kelompok:</span>
                        <span class="font-semibold text-sky-400">3</span>
                    </li>
                    <li class="flex justify-between pb-2 border-b border-slate-700">
                        <span class="text-slate-400">Judul Project:</span>
                        <span class="font-semibold text-amber-300">Berita Cuaca</span>
                    </li>
                    <li class="flex flex-col pt-1">
                        <span class="text-slate-400 mb-1">Anggota Kelompok:</span>
                        <div class="bg-slate-700/50 p-3 rounded-xl border border-slate-600 space-y-1">
                            {% for nama in group.anggota %}
                            <p class="font-medium text-white">• {{ nama }}</p>
                            {% endfor %}
                        </div>
                    </li>
                </ul>
            </div>

            <div class="bg-gradient-to-br from-sky-900/40 to-slate-800 p-6 rounded-2xl border border-sky-800/40 shadow-xl text-center">
                <p class="text-sky-300 font-semibold mb-2">🚀 Cara Menjalankan di VS Code</p>
                <p class="text-xs text-slate-300 mb-4">Buka terminal di VS Code, instal Flask, lalu jalankan aplikasinya.</p>
                <div class="bg-slate-900 p-3 rounded-lg text-xs font-mono text-emerald-400 overflow-x-auto text-left space-y-1">
                    <p>pip install flask requests</p>
                    <p>python app.py</p>
                </div>
            </div>
        </aside>
    </main>

    <!-- Footer -->
    <footer class="bg-slate-800 border-t border-slate-700 py-4 text-center text-xs text-slate-400">
        <p>&copy; 2026 Kelompok 3 - Project Berita Cuaca (Dasar Pemrograman)</p>
    </footer>

    <script>
        (() => {
            // ====== Konfigurasi ======
            const REFRESH_MS = 30000;

            const card = document.getElementById('weather-card');
            const canvas = document.getElementById('weather-fx');
            const ctx = canvas.getContext('2d');
            const lightning = document.getElementById('lightning');
            const condEl = document.getElementById('weather-condition');
            const iconEl = document.getElementById('weather-icon');
            const sun = document.getElementById('sun');
            const windEl = document.getElementById('weather-wind');

            const dims = { w: 0, h: 0 };
            let mode = 'clear';
            let windKmh = 0;
            let drops = [];
            let clouds = [];
            let stormTimer = null;
            let last = performance.now();

            // drops = jumlah tetes, speed = px/detik, len = panjang garis
            const CFG = {
                clear:   { drops: 0,   speed: 0,   len: 0,  alpha: 0,    clouds: 3 },
                cloudy:  { drops: 0,   speed: 0,   len: 0,  alpha: 0,    clouds: 5 },
                fog:     { drops: 0,   speed: 0,   len: 0,  alpha: 0,    clouds: 3 },
                drizzle: { drops: 80,  speed: 260, len: 8,  alpha: 0.50, clouds: 3 },
                rain:    { drops: 190, speed: 500, len: 15, alpha: 0.70, clouds: 4 },
                heavy:   { drops: 330, speed: 740, len: 22, alpha: 0.85, clouds: 5 },
                storm:   { drops: 400, speed: 900, len: 26, alpha: 0.85, clouds: 6 }
            };
            const THEME = {
                clear: 'wx-clear', cloudy: 'wx-cloudy', fog: 'wx-fog',
                drizzle: 'wx-drizzle', rain: 'wx-rain', heavy: 'wx-heavy', storm: 'wx-storm'
            };
            const COLOR = {
                clear: '#fbbf24', cloudy: '#cbd5e1', fog: '#e2e8f0', drizzle: '#7dd3fc',
                rain: '#38bdf8', heavy: '#60a5fa', storm: '#c084fc'
            };
            const ICON = {
                'Cerah': '☀️', 'Cerah Berawan': '⛅', 'Berawan': '☁️',
                'Berkabut': '🌫️', 'Gerimis': '🌦️', 'Hujan': '🌧️',
                'Hujan Lebat': '⛈️', 'Badai Petir': '⛈️'
            };

            function classify(code) {
                if (code >= 95) return 'storm';                      // badai petir
                if ([65, 67, 82].includes(code)) return 'heavy';     // hujan lebat
                if ([61, 63, 66, 80, 81].includes(code)) return 'rain';
                if ([51, 53, 55, 56, 57].includes(code)) return 'drizzle';
                if ([45, 48].includes(code)) return 'fog';
                if (code === 3) return 'cloudy';
                return 'clear';
            }

            function setText(id, value) {
                const el = document.getElementById(id);
                if (el && value !== undefined && value !== null) el.textContent = value;
            }

            function resize() {
                const r = card.getBoundingClientRect();
                const dpr = Math.min(window.devicePixelRatio || 1, 2);
                dims.w = r.width;
                dims.h = r.height;
                canvas.width = Math.max(1, Math.round(r.width * dpr));
                canvas.height = Math.max(1, Math.round(r.height * dpr));
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                build();
            }

            function build() {
                const cfg = CFG[mode];
                drops = Array.from({ length: cfg.drops }, () => ({
                    x: Math.random() * dims.w,
                    y: Math.random() * dims.h,
                    v: cfg.speed * (0.75 + Math.random() * 0.5),
                    len: cfg.len * (0.7 + Math.random() * 0.6),
                    a: cfg.alpha * (0.5 + Math.random() * 0.5)
                }));
                clouds = Array.from({ length: cfg.clouds }, () => ({
                    x: Math.random() * dims.w,
                    y: 10 + Math.random() * dims.h * 0.3,
                    r: 40 + Math.random() * 80,
                    a: 0.05 + Math.random() * 0.07,
                    v: 5 + Math.random() * 9
                }));
            }

            function draw(now) {
                const dt = Math.min((now - last) / 1000, 0.05);
                last = now;
                ctx.clearRect(0, 0, dims.w, dims.h);

                // Cahaya matahari saat cerah
                if (mode === 'clear') {
                    const pulse = 0.10 + 0.05 * Math.sin(now / 900);
                    const g = ctx.createRadialGradient(dims.w * 0.85, 0, 10, dims.w * 0.85, 0, dims.w * 0.55);
                    g.addColorStop(0, 'rgba(251,191,36,' + pulse + ')');
                    g.addColorStop(1, 'rgba(251,191,36,0)');
                    ctx.fillStyle = g;
                    ctx.fillRect(0, 0, dims.w, dims.h);
                }

                // Awan melayang
                clouds.forEach(c => {
                    c.x += c.v * dt;
                    if (c.x - c.r > dims.w) c.x = -c.r;
                    const g = ctx.createRadialGradient(c.x, c.y, 1, c.x, c.y, c.r);
                    g.addColorStop(0, 'rgba(226,232,240,' + (c.a * 2) + ')');
                    g.addColorStop(1, 'rgba(226,232,240,0)');
                    ctx.fillStyle = g;
                    ctx.beginPath();
                    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
                    ctx.fill();
                });

                // Kabut
                if (mode === 'fog') {
                    for (let i = 0; i < 3; i++) {
                        const y = dims.h * (0.3 + i * 0.22) + Math.sin(now / 1600 + i) * 8;
                        const g = ctx.createLinearGradient(0, y - 40, 0, y + 40);
                        g.addColorStop(0, 'rgba(226,232,240,0)');
                        g.addColorStop(0.5, 'rgba(226,232,240,0.18)');
                        g.addColorStop(1, 'rgba(226,232,240,0)');
                        ctx.fillStyle = g;
                        ctx.fillRect(0, y - 40, dims.w, 80);
                    }
                }

                // Hujan / gerimis (makin deras = makin banyak & cepat)
                const vx = windKmh * 1.8 + (drops.length ? 40 : 0);
                drops.forEach(d => {
                    d.y += d.v * dt;
                    d.x += vx * dt;
                    if (d.y > dims.h + 20) { d.y = -20; d.x = Math.random() * dims.w; }
                    if (d.x > dims.w + 20) d.x = -20;
                    ctx.beginPath();
                    ctx.moveTo(d.x, d.y);
                    ctx.lineTo(d.x - vx * 0.02, d.y - d.len);
                    ctx.strokeStyle = 'rgba(147,197,253,' + Math.min(0.9, d.a) + ')';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                });

                // Garis angin kalau angin kencang (>= 20 km/h)
                if (windKmh >= 20) {
                    const n = Math.min(18, Math.round(windKmh / 2));
                    for (let i = 0; i < n; i++) {
                        const speed = 12 - Math.min(9, windKmh / 8);
                        const x = ((now / speed) + i * 90) % (dims.w + 200) - 100;
                        const y = (i * 53 + now / 12) % dims.h;
                        const len = 30 + (windKmh % 40);
                        ctx.beginPath();
                        ctx.moveTo(x, y);
                        ctx.lineTo(x + len, y);
                        ctx.strokeStyle = 'rgba(255,255,255,' + (0.06 + Math.min(0.18, windKmh / 400)) + ')';
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }

                requestAnimationFrame(draw);
            }

            function startLightning() {
                stopLightning();
                const tick = () => {
                    lightning.classList.remove('flash');
                    void lightning.offsetWidth;
                    lightning.classList.add('flash');
                    stormTimer = setTimeout(tick, 2500 + Math.random() * 4500);
                };
                stormTimer = setTimeout(tick, 1200);
            }

            function stopLightning() {
                if (stormTimer) clearTimeout(stormTimer);
                stormTimer = null;
                lightning.classList.remove('flash');
            }

            function applyEffect(condition, code, wind) {
                windKmh = Number(wind) || 0;
                mode = classify(Number(code));

                Object.values(THEME).forEach(c => card.classList.remove(c));
                card.classList.add(THEME[mode]);

                if (condEl) {
                    condEl.textContent = condition;
                    condEl.style.color = COLOR[mode];
                }
                if (iconEl) iconEl.textContent = ICON[condition] || '🌡️';
                if (sun) sun.classList.toggle('on', mode === 'clear');
                if (windEl) {
                    windEl.style.color = windKmh >= 40 ? '#f87171'
                        : windKmh >= 20 ? '#fbbf24' : '#a5b4fc';
                }

                if (mode === 'storm') startLightning(); else stopLightning();
                build();
            }

            async function refreshWeather() {
                const cityEl = document.getElementById('weather-city');
                if (!cityEl) return;
                const city = cityEl.textContent.trim();
                try {
                    const res = await fetch('/api/weather?city=' + encodeURIComponent(city), { cache: 'no-store' });
                    if (!res.ok) return;
                    const data = await res.json();
                    setText('weather-temp', data.temp);
                    setText('weather-humidity', data.humidity);
                    setText('weather-wind', '💨 ' + data.wind);
                    setText('weather-desc', data.desc);
                    setText('last-update', new Date().toLocaleTimeString('id-ID'));
                    applyEffect(data.condition, data.code, data.wind_kmh);
                } catch (err) {
                    console.warn('Gagal update cuaca realtime:', err);
                    setText('last-update', 'gagal terhubung');
                }
            }

            // ====== Inisialisasi ======
            resize();
            applyEffect(card.dataset.condition, card.dataset.code, card.dataset.wind);
            requestAnimationFrame(draw);
            window.addEventListener('resize', resize);
            if (window.ResizeObserver) new ResizeObserver(resize).observe(card);

            setText('last-update', new Date().toLocaleTimeString('id-ID'));
            setInterval(refreshWeather, REFRESH_MS);
        })();
    </script>
</body>
</html>

"""

@app.route('/', methods=['GET', 'POST'])
def index():
    # Mendukung POST (form) maupun GET (?city=...) agar mudah dibagikan/diuji
    selected_city = request.values.get('city', 'Pontianak')
    if selected_city not in CITY_COORDS:
        selected_city = "Pontianak"
    
    current_weather = fetch_real_weather(selected_city)
    
    group_info = {
        "kelompok": "3",
        "project": "Berita Cuaca",
        "anggota": [
            "Muhammad Akmal",
            "Hadrianus Samudra",
            "Reyfan Bagus Setiawan",
            "Riki Anderas Muxi"
        ]
    }
    
    return render_template_string(PAGE_TEMPLATE, 
                           city=selected_city, 
                           cities=list(CITY_COORDS.keys()), 
                           city_groups=CITY_GROUPS,
                           weather=current_weather, 
                           news=NEWS_DATA,
                           group=group_info)

@app.route('/api/weather')
def api_weather():
    """Endpoint JSON untuk update realtime tanpa reload halaman."""
    city = request.args.get('city', 'Pontianak')
    if city not in CITY_COORDS:
        city = 'Pontianak'
    data = fetch_real_weather(city)
    data['city'] = city
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
