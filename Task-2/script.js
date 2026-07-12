/* =========================================================
   Meteorograph — application logic
   ========================================================= */

const OWM_BASE = "https://api.openweathermap.org/data/2.5/weather";
const STORAGE_KEY = "meteorograph.apiKey";
const RECENTS_KEY = "meteorograph.recents";
const UNIT_KEY = "meteorograph.unit";

const els = {
  form: document.getElementById("searchForm"),
  input: document.getElementById("cityInput"),
  submitBtn: document.getElementById("submitBtn"),
  geoBtn: document.getElementById("geoBtn"),
  unitToggle: document.getElementById("unitToggle"),
  unitLabel: document.getElementById("unitLabel"),
  status: document.getElementById("statusMessage"),

  loading: document.getElementById("loadingState"),
  error: document.getElementById("errorState"),
  errorTitle: document.getElementById("errorTitle"),
  errorDetail: document.getElementById("errorDetail"),
  result: document.getElementById("resultState"),

  cityName: document.getElementById("cityName"),
  placeMeta: document.getElementById("placeMeta"),
  conditionTag: document.getElementById("conditionTag"),
  dialProgress: document.getElementById("dialProgress"),
  tempReading: document.getElementById("tempReading"),
  feelsLike: document.getElementById("feelsLike"),
  weatherIcon: document.getElementById("weatherIcon"),
  humidityVal: document.getElementById("humidityVal"),
  windVal: document.getElementById("windVal"),
  pressureVal: document.getElementById("pressureVal"),
  visibilityVal: document.getElementById("visibilityVal"),
  sunriseVal: document.getElementById("sunriseVal"),
  sunsetVal: document.getElementById("sunsetVal"),
  updatedAt: document.getElementById("updatedAt"),

  recentWrap: document.getElementById("recentWrap"),
  recentChips: document.getElementById("recentChips"),

  apiKeyInput: document.getElementById("apiKeyInput"),
  saveKeyBtn: document.getElementById("saveKeyBtn"),

  starsGroup: document.querySelector(".stars"),
  rainGroup: document.querySelector(".rain"),
  snowGroup: document.querySelector(".snow"),
  lightningFlash: document.querySelector(".lightning-flash"),
};

let state = {
  unit: localStorage.getItem(UNIT_KEY) || "metric", // metric = C, imperial = F
  lastData: null,
  lightningTimer: null,
};

/* ---------------------------------------------------------
   API key handling
   --------------------------------------------------------- */
function getApiKey() {
  return localStorage.getItem(STORAGE_KEY) || "";
}

els.apiKeyInput.value = getApiKey();

els.saveKeyBtn.addEventListener("click", () => {
  const key = els.apiKeyInput.value.trim();
  if (!key) {
    setStatus("Enter a key before saving.");
    return;
  }
  localStorage.setItem(STORAGE_KEY, key);
  setStatus("API key saved to this browser.");
});

/* ---------------------------------------------------------
   Recent searches
   --------------------------------------------------------- */
function getRecents() {
  try {
    return JSON.parse(localStorage.getItem(RECENTS_KEY)) || [];
  } catch {
    return [];
  }
}

function addRecent(cityLabel) {
  let recents = getRecents().filter((c) => c.toLowerCase() !== cityLabel.toLowerCase());
  recents.unshift(cityLabel);
  recents = recents.slice(0, 6);
  localStorage.setItem(RECENTS_KEY, JSON.stringify(recents));
  renderRecents();
}

function renderRecents() {
  const recents = getRecents();
  if (!recents.length) {
    els.recentWrap.hidden = true;
    return;
  }
  els.recentWrap.hidden = false;
  els.recentChips.innerHTML = "";
  recents.forEach((city) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "recent-chip";
    chip.textContent = city;
    chip.addEventListener("click", () => {
      els.input.value = city;
      fetchAndRender({ city });
    });
    els.recentChips.appendChild(chip);
  });
}

/* ---------------------------------------------------------
   UI state helpers
   --------------------------------------------------------- */
function setStatus(msg) {
  els.status.textContent = msg;
}

function showLoading() {
  els.loading.hidden = false;
  els.error.hidden = true;
  els.result.hidden = true;
  els.submitBtn.disabled = true;
  els.submitBtn.querySelector("span").textContent = "Reading…";
}

function showError(title, detail) {
  els.loading.hidden = true;
  els.error.hidden = false;
  els.result.hidden = true;
  els.errorTitle.textContent = title;
  els.errorDetail.textContent = detail;
  resetButton();
}

function showResult() {
  els.loading.hidden = true;
  els.error.hidden = true;
  els.result.hidden = false;
  resetButton();
}

function resetButton() {
  els.submitBtn.disabled = false;
  els.submitBtn.querySelector("span").textContent = "Take reading";
}

/* ---------------------------------------------------------
   Unit toggle
   --------------------------------------------------------- */
function refreshUnitLabel() {
  els.unitLabel.textContent = state.unit === "metric" ? "°C" : "°F";
  els.unitToggle.setAttribute("aria-pressed", state.unit === "imperial");
}
refreshUnitLabel();

els.unitToggle.addEventListener("click", () => {
  state.unit = state.unit === "metric" ? "imperial" : "metric";
  localStorage.setItem(UNIT_KEY, state.unit);
  refreshUnitLabel();
  if (state.lastData) renderWeather(state.lastData);
});

/* ---------------------------------------------------------
   Fetching
   --------------------------------------------------------- */
async function fetchWeatherByCity(city, apiKey) {
  const url = `${OWM_BASE}?q=${encodeURIComponent(city)}&appid=${apiKey}&units=${state.unit}`;
  return requestWeather(url);
}

async function fetchWeatherByCoords(lat, lon, apiKey) {
  const url = `${OWM_BASE}?lat=${lat}&lon=${lon}&appid=${apiKey}&units=${state.unit}`;
  return requestWeather(url);
}

async function requestWeather(url) {
  let response;
  try {
    response = await fetch(url);
  } catch (networkErr) {
    const err = new Error("network");
    err.cause = networkErr;
    throw err;
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const err = new Error("api");
    err.status = response.status;
    err.message2 = body.message || "";
    throw err;
  }

  return response.json();
}

async function fetchAndRender({ city, lat, lon }) {
  const apiKey = getApiKey();

  if (!apiKey) {
    showError(
      "No API key on file.",
      "Open “API key setup” below and paste your free OpenWeatherMap key to activate live readings."
    );
    setStatus("");
    return;
  }

  if (city !== undefined && !city.trim()) {
    showError("The input is blank.", "Type a city name before taking a reading.");
    setStatus("");
    return;
  }

  showLoading();
  setStatus("Contacting OpenWeatherMap…");

  try {
    const data = city
      ? await fetchWeatherByCity(city.trim(), apiKey)
      : await fetchWeatherByCoords(lat, lon, apiKey);

    state.lastData = data;
    renderWeather(data);
    showResult();
    setStatus(`Reading captured for ${data.name}.`);
    addRecent(`${data.name}${data.sys?.country ? ", " + data.sys.country : ""}`);
  } catch (err) {
    handleFetchError(err, city);
  }
}

function handleFetchError(err, city) {
  if (err.message === "network") {
    showError(
      "Couldn't reach the weather service.",
      "Check your internet connection and try again in a moment."
    );
  } else if (err.status === 401) {
    showError(
      "That API key isn't active yet.",
      "New OpenWeatherMap keys can take up to a couple of hours to activate. Double-check the key in “API key setup.”"
    );
  } else if (err.status === 404) {
    showError(
      `Couldn't find “${city}.”`,
      "Check the spelling, or try a more specific name like “City, Country code.”"
    );
  } else if (err.status === 429) {
    showError(
      "Too many requests.",
      "The API rate limit was hit. Wait a minute and try again."
    );
  } else {
    showError(
      "The reading failed.",
      err.message2 || "An unexpected error occurred while contacting the weather service."
    );
  }
  setStatus("");
}

/* ---------------------------------------------------------
   Form + geolocation events
   --------------------------------------------------------- */
els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  fetchAndRender({ city: els.input.value });
});

els.geoBtn.addEventListener("click", () => {
  if (!("geolocation" in navigator)) {
    showError("Geolocation isn't available.", "Your browser doesn't support location lookup — search by city name instead.");
    return;
  }
  showLoading();
  setStatus("Locating you…");
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      fetchAndRender({ lat: pos.coords.latitude, lon: pos.coords.longitude });
    },
    () => {
      showError("Location access denied.", "Allow location access, or search for a city by name instead.");
      setStatus("");
    },
    { timeout: 10000 }
  );
});

/* ---------------------------------------------------------
   Rendering weather data
   --------------------------------------------------------- */
function renderWeather(data) {
  const tempUnit = state.unit === "metric" ? "°C" : "°F";
  const speedUnit = state.unit === "metric" ? "m/s" : "mph";
  const condition = data.weather?.[0]?.main || "Clear";
  const description = data.weather?.[0]?.description || condition;
  const temp = Math.round(data.main.temp);
  const feels = Math.round(data.main.feels_like);

  els.cityName.textContent = data.name || "Unknown location";
  els.placeMeta.textContent = `${data.sys?.country || ""} · ${formatCoord(data.coord)}`;
  els.conditionTag.textContent = description;

  els.tempReading.textContent = `${temp}${tempUnit}`;
  els.feelsLike.textContent = `feels like ${feels}${tempUnit}`;

  els.humidityVal.textContent = `${data.main.humidity}%`;
  els.windVal.textContent = `${data.wind?.speed ?? "—"} ${speedUnit}`;
  els.pressureVal.textContent = `${data.main.pressure} hPa`;
  els.visibilityVal.textContent = data.visibility != null ? `${(data.visibility / 1000).toFixed(1)} km` : "—";

  const tz = data.timezone || 0;
  els.sunriseVal.textContent = data.sys?.sunrise ? formatTime(data.sys.sunrise, tz) : "—";
  els.sunsetVal.textContent = data.sys?.sunset ? formatTime(data.sys.sunset, tz) : "—";

  els.updatedAt.textContent = `Updated ${new Date().toLocaleTimeString()}`;

  updateDial(temp);
  els.weatherIcon.innerHTML = getIconSvg(condition);

  applyTheme({ condition, tempC: state.unit === "metric" ? temp : fToC(temp), data, tz });
}

function formatCoord(coord) {
  if (!coord) return "";
  const lat = coord.lat.toFixed(1);
  const lon = coord.lon.toFixed(1);
  return `${lat}, ${lon}`;
}

function formatTime(unixSeconds, tzOffsetSeconds) {
  const d = new Date((unixSeconds + tzOffsetSeconds) * 1000);
  return d.toUTCString().match(/\d\d:\d\d/)[0];
}

function fToC(f) {
  return ((f - 32) * 5) / 9;
}

function updateDial(temp) {
  const circumference = 603; // 2 * PI * 96
  const min = -20, max = 45;
  const clamped = Math.max(min, Math.min(max, temp));
  const pct = (clamped - min) / (max - min);
  const offset = circumference * (1 - pct);
  els.dialProgress.style.strokeDashoffset = offset;
}

/* ---------------------------------------------------------
   Dynamic theme — maps condition/temp/time to the backdrop
   --------------------------------------------------------- */
function applyTheme({ condition, tempC, data, tz }) {
  const body = document.body;
  const key = mapConditionKey(condition);
  body.setAttribute("data-condition", key);

  const bucket = tempC <= 5 ? "cold" : tempC <= 18 ? "cool" : tempC <= 27 ? "mild" : tempC <= 34 ? "warm" : "hot";
  body.setAttribute("data-temp", bucket);

  const isDay = computeIsDay(data);
  body.setAttribute("data-daytime", isDay ? "day" : "night");

  const accent = temperatureToAccent(tempC);
  body.style.setProperty("--accent-current", accent);

  buildStars(!isDay);
  buildPrecipitation(key);
  toggleLightning(key === "thunderstorm");
}

function mapConditionKey(main) {
  const m = (main || "").toLowerCase();
  if (m.includes("thunder")) return "thunderstorm";
  if (m.includes("drizzle")) return "drizzle";
  if (m.includes("rain")) return "rain";
  if (m.includes("snow")) return "snow";
  if (["mist", "fog", "haze", "smoke", "dust", "sand", "ash"].some((k) => m.includes(k))) return "mist";
  if (m.includes("cloud")) return "clouds";
  return "clear";
}

function computeIsDay(data) {
  if (!data.sys?.sunrise || !data.sys?.sunset) return true;
  const now = Math.floor(Date.now() / 1000);
  return now > data.sys.sunrise && now < data.sys.sunset;
}

function temperatureToAccent(tempC) {
  // interpolate a hue: cold cyan (195) -> mild amber (35) -> hot coral (10)
  const stops = [
    { t: -10, color: [99, 199, 232] },
    { t: 10, color: [130, 190, 220] },
    { t: 20, color: [242, 200, 120] },
    { t: 28, color: [242, 166, 90] },
    { t: 38, color: [240, 110, 80] },
  ];
  let lo = stops[0], hi = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (tempC >= stops[i].t && tempC <= stops[i + 1].t) {
      lo = stops[i]; hi = stops[i + 1]; break;
    }
  }
  const span = hi.t - lo.t || 1;
  const ratio = Math.max(0, Math.min(1, (tempC - lo.t) / span));
  const rgb = lo.color.map((c, i) => Math.round(c + (hi.color[i] - c) * ratio));
  return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}

/* ---------------------------------------------------------
   Backdrop particle builders
   --------------------------------------------------------- */
function buildStars(show) {
  els.starsGroup.innerHTML = "";
  if (!show) return;
  const frag = document.createDocumentFragment();
  for (let i = 0; i < 60; i++) {
    const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", Math.random() * 1440);
    c.setAttribute("cy", Math.random() * 480);
    c.setAttribute("r", (Math.random() * 1.3 + 0.4).toFixed(2));
    c.style.opacity = (Math.random() * 0.6 + 0.3).toFixed(2);
    c.style.animation = `twinkle ${(Math.random() * 3 + 2).toFixed(1)}s ease-in-out ${(Math.random() * 2).toFixed(1)}s infinite`;
    frag.appendChild(c);
  }
  els.starsGroup.appendChild(frag);

  if (!document.getElementById("twinkle-kf")) {
    const style = document.createElement("style");
    style.id = "twinkle-kf";
    style.textContent = "@keyframes twinkle{0%,100%{opacity:.2}50%{opacity:.9}}";
    document.head.appendChild(style);
  }
}

function buildPrecipitation(conditionKey) {
  els.rainGroup.innerHTML = "";
  els.snowGroup.innerHTML = "";

  if (conditionKey === "rain" || conditionKey === "drizzle" || conditionKey === "thunderstorm") {
    const count = conditionKey === "drizzle" ? 40 : 80;
    for (let i = 0; i < count; i++) {
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      const x = Math.random() * 1500 - 30;
      const len = Math.random() * 14 + 10;
      line.setAttribute("x1", x);
      line.setAttribute("y1", -20);
      line.setAttribute("x2", x - 6);
      line.setAttribute("y2", -20 + len);
      line.style.animation = `fall ${(Math.random() * 0.5 + 0.6).toFixed(2)}s linear ${(Math.random() * 1).toFixed(2)}s infinite`;
      els.rainGroup.appendChild(line);
    }
    ensureKeyframe("fall", "@keyframes fall{0%{transform:translateY(0)}100%{transform:translateY(940px)}}");
  }

  if (conditionKey === "snow") {
    for (let i = 0; i < 70; i++) {
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      const x = Math.random() * 1440;
      c.setAttribute("cx", x);
      c.setAttribute("cy", -10);
      c.setAttribute("r", (Math.random() * 2 + 1.2).toFixed(2));
      c.style.animation = `snowfall ${(Math.random() * 4 + 4).toFixed(2)}s linear ${(Math.random() * 4).toFixed(2)}s infinite`;
      els.snowGroup.appendChild(c);
    }
    ensureKeyframe("snowfall", "@keyframes snowfall{0%{transform:translate(0,0)}50%{transform:translate(20px,470px)}100%{transform:translate(-10px,940px)}}");
  }
}

function ensureKeyframe(id, rule) {
  if (document.getElementById(`kf-${id}`)) return;
  const style = document.createElement("style");
  style.id = `kf-${id}`;
  style.textContent = rule;
  document.head.appendChild(style);
}

function toggleLightning(active) {
  clearInterval(state.lightningTimer);
  if (!active) return;
  const strike = () => {
    els.lightningFlash.setAttribute("x", 0);
    els.lightningFlash.setAttribute("y", 0);
    els.lightningFlash.setAttribute("width", 1440);
    els.lightningFlash.setAttribute("height", 900);
    els.lightningFlash.classList.remove("strike");
    void els.lightningFlash.offsetWidth;
    els.lightningFlash.classList.add("strike");
  };
  strike();
  state.lightningTimer = setInterval(strike, Math.random() * 4000 + 4000);
}

/* ---------------------------------------------------------
   Icon set — custom line-art matched to the instrument style
   --------------------------------------------------------- */
function getIconSvg(condition) {
  const key = mapConditionKey(condition);
  const icons = {
    clear: `<svg viewBox="0 0 64 64" fill="none"><circle cx="32" cy="32" r="14" stroke="currentColor" stroke-width="2.5"/><g stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="32" y1="4" x2="32" y2="12"/><line x1="32" y1="52" x2="32" y2="60"/><line x1="4" y1="32" x2="12" y2="32"/><line x1="52" y1="32" x2="60" y2="32"/><line x1="12" y1="12" x2="18" y2="18"/><line x1="46" y1="46" x2="52" y2="52"/><line x1="52" y1="12" x2="46" y2="18"/><line x1="18" y1="46" x2="12" y2="52"/></g></svg>`,
    clouds: `<svg viewBox="0 0 64 64" fill="none"><path d="M20 44h26a10 10 0 0 0 1-19.9A14 14 0 0 0 20 26 9 9 0 0 0 20 44Z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/></svg>`,
    mist: `<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="8" y1="22" x2="56" y2="22"/><line x1="14" y1="32" x2="50" y2="32"/><line x1="8" y1="42" x2="56" y2="42"/></svg>`,
    rain: `<svg viewBox="0 0 64 64" fill="none"><path d="M18 36h26a10 10 0 0 0 1-19.9A14 14 0 0 0 18 18 9 9 0 0 0 18 36Z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><g stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="22" y1="46" x2="18" y2="56"/><line x1="34" y1="46" x2="30" y2="56"/><line x1="46" y1="46" x2="42" y2="56"/></g></svg>`,
    drizzle: `<svg viewBox="0 0 64 64" fill="none"><path d="M18 34h26a10 10 0 0 0 1-19.9A14 14 0 0 0 18 16 9 9 0 0 0 18 34Z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><g stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="24" y1="44" x2="22" y2="50"/><line x1="34" y1="44" x2="32" y2="50"/><line x1="44" y1="44" x2="42" y2="50"/></g></svg>`,
    thunderstorm: `<svg viewBox="0 0 64 64" fill="none"><path d="M18 32h26a10 10 0 0 0 1-19.9A14 14 0 0 0 18 14 9 9 0 0 0 18 32Z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M33 38 24 52h8l-3 10 12-16h-8l4-8Z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" fill="currentColor"/></svg>`,
    snow: `<svg viewBox="0 0 64 64" fill="none"><path d="M18 34h26a10 10 0 0 0 1-19.9A14 14 0 0 0 18 16 9 9 0 0 0 18 34Z" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><g stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="24" y1="44" x2="24" y2="56"/><line x1="18" y1="50" x2="30" y2="50"/><line x1="42" y1="44" x2="42" y2="56"/><line x1="36" y1="50" x2="48" y2="50"/></g></svg>`,
  };
  return icons[key] || icons.clear;
}

/* ---------------------------------------------------------
   Init
   --------------------------------------------------------- */
renderRecents();
buildStars(false);
setStatus(getApiKey() ? "Ready. Search a city or use your location." : "Add an OpenWeatherMap API key below to begin.");
