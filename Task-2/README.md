# Meteorograph — Interactive Weather Application

A live atmospheric readout for any city on Earth. Built for **Task 2** of the DevRise Internship Program (Batch 1, 2026).

Meteorograph fetches real-time weather from the OpenWeatherMap API and reflects it back visually: an animated sky backdrop that shifts between sun, cloud, rain, snow, mist, and thunderstorm; an accent color that slides from cool blue to warm amber to coral as the temperature rises; and an instrument-style dial showing the current reading at a glance.

## Features

- 🔎 Search any city by name, with graceful handling of blank input, unknown cities, and API failures
- 📍 "Use my location" button via the browser Geolocation API
- ⏳ Loading skeleton while the request is in flight
- ⚠️ Distinct, readable error states (bad city, no key, rate limit, network failure)
- 🌡️ Metric / Imperial unit toggle (°C ⇄ °F)
- 🎨 Dynamic theme: sky gradient, particles (rain / snow / stars), and accent color all respond to live condition and temperature data
- 🕘 Recent searches, remembered per browser
- ♿ Semantic HTML, visible focus states, `aria-live` status updates, `prefers-reduced-motion` support
- 📱 Fully responsive, from small phones to desktop

## Tech

Plain HTML, CSS, and JavaScript — no build step, no framework, no dependencies. Async/await is used throughout for the fetch/response cycle, with explicit `try/catch` error paths for each failure mode.

## Project structure

```
weather-app/
├── index.html      # Markup: control panel, states, animated SVG backdrop
├── style.css        # Design tokens, dynamic theme rules, responsive layout
├── script.js         # Fetch logic, error handling, theming, rendering
├── vercel.json       # Deployment config (static site)
└── README.md
```

## Setup — run it locally

1. Get a free API key at [openweathermap.org](https://home.openweathermap.org/users/sign_up). New keys can take up to a couple of hours to activate.
2. Open `index.html` in a browser (or serve the folder with any static server, e.g. `npx serve .`).
3. Expand **"API key setup"** at the bottom of the page, paste your key, and click **Save key**. The key is stored only in `localStorage` in your own browser — it is never committed to the repo or sent anywhere but OpenWeatherMap.
4. Search a city, or click **My location**.

## Usage

- Type a city name and press **Take reading** (or hit Enter).
- Click a chip under **Recent readings** to look it up again.
- Toggle **°C / °F** at any time — the current reading re-renders instantly.
- If a request fails, the error card explains what happened and how to fix it (bad spelling, inactive key, offline, etc).

## Deploying to Vercel

**Option A — Vercel dashboard (no CLI needed)**

1. Push this folder to a new GitHub repository.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repository.
3. Framework preset: **Other** (it's a static site — no build command needed).
4. Click **Deploy**. You'll get a live URL in under a minute.

**Option B — Vercel CLI**

```bash
npm i -g vercel
cd weather-app
vercel
```

Follow the prompts (accept the defaults — no build step is required). Run `vercel --prod` to promote to production.

> Note: the OpenWeatherMap key is entered by each visitor in the browser (see Setup above), so there is nothing to configure as a Vercel environment variable for this version.

## Evaluation checklist (per Task 2 brief)

- [x] API integration with a standard weather service (OpenWeatherMap)
- [x] Async JavaScript (`async`/`await`) for all HTTP requests
- [x] Error handling for invalid cities, blank input, and API failures (401 / 404 / 429 / network)
- [x] Clean, responsive UI with consistent spacing and a defined type/color system
- [x] Dynamic theme adjustments driven by temperature and condition codes

## Credits

Weather data: [OpenWeatherMap](https://openweathermap.org/). Fonts: Fraunces, Space Grotesk, IBM Plex Mono (Google Fonts).
