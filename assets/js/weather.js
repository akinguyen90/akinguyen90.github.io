// WMO weather codes → 日本語ラベル + 絵文字アイコン
// https://open-meteo.com/en/docs → "Weather variable documentation"
const WEATHER_CODES = {
  0:  { label: "快晴",     day: "☀️", night: "🌙" },
  1:  { label: "ほぼ晴れ", day: "🌤️", night: "🌙" },
  2:  { label: "薄曇り",   day: "⛅", night: "☁️" },
  3:  { label: "曇り",     day: "☁️", night: "☁️" },
  45: { label: "霧",       day: "🌫️" },
  48: { label: "霧氷",     day: "🌫️" },
  51: { label: "霧雨(弱)", day: "🌦️" },
  53: { label: "霧雨",     day: "🌦️" },
  55: { label: "霧雨(強)", day: "🌧️" },
  56: { label: "凍える霧雨", day: "🌧️" },
  57: { label: "凍える霧雨", day: "🌧️" },
  61: { label: "小雨",     day: "🌧️" },
  63: { label: "雨",       day: "🌧️" },
  65: { label: "強い雨",   day: "🌧️" },
  66: { label: "凍える雨", day: "🌧️" },
  67: { label: "凍える雨", day: "🌧️" },
  71: { label: "小雪",     day: "🌨️" },
  73: { label: "雪",       day: "🌨️" },
  75: { label: "大雪",     day: "❄️" },
  77: { label: "霧雪",     day: "🌨️" },
  80: { label: "にわか雨", day: "🌦️" },
  81: { label: "にわか雨", day: "🌧️" },
  82: { label: "激しい雨", day: "⛈️" },
  85: { label: "にわか雪", day: "🌨️" },
  86: { label: "激しい雪", day: "❄️" },
  95: { label: "雷雨",     day: "⛈️" },
  96: { label: "雷雨(雹)", day: "⛈️" },
  99: { label: "激しい雷雨", day: "⛈️" },
};

function describe(code, isDay) {
  const info = WEATHER_CODES[code] ?? { label: "不明", day: "❓" };
  const icon = isDay === 0 && info.night ? info.night : info.day;
  return { label: info.label, icon };
}

function tempClass(t) {
  if (t >= 32) return "temp-hot";
  if (t >= 26) return "temp-warm";
  if (t >= 18) return "temp-mild";
  if (t >= 10) return "temp-cool";
  return "temp-cold";
}

function formatUpdated(iso) {
  try {
    const d = new Date(iso);
    const fmt = new Intl.DateTimeFormat("ja-JP", {
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit",
      timeZone: "Asia/Tokyo",
    });
    return fmt.format(d) + " JST";
  } catch {
    return iso;
  }
}

function cardHTML(city) {
  if (city.error) {
    return `
      <article class="weather-card weather-card-error">
        <div class="weather-card-head">
          <h2>${city.name_ja}</h2>
          <span class="weather-card-en">${city.name}</span>
        </div>
        <p class="weather-label">取得失敗: ${city.error}</p>
      </article>
    `;
  }

  const { label, icon } = describe(city.weather_code, city.is_day);
  return `
    <article class="weather-card ${tempClass(city.temperature)}">
      <div class="weather-card-head">
        <h2>${city.name_ja}</h2>
        <span class="weather-card-en">${city.name}</span>
      </div>
      <div class="weather-card-main">
        <span class="weather-icon" aria-hidden="true">${icon}</span>
        <span class="weather-temp">${Math.round(city.temperature)}<span class="weather-temp-unit">°C</span></span>
      </div>
      <p class="weather-label">${label}</p>
      <dl class="weather-details">
        <div><dt>体感</dt><dd>${Math.round(city.apparent_temperature)}°C</dd></div>
        <div><dt>湿度</dt><dd>${city.humidity}%</dd></div>
        <div><dt>風速</dt><dd>${Math.round(city.wind_speed)} km/h</dd></div>
      </dl>
    </article>
  `;
}

async function load() {
  const grid = document.getElementById("weather-grid");
  const updated = document.getElementById("updated-at");

  try {
    const res = await fetch("data/weather.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    updated.textContent = `最終更新: ${formatUpdated(data.updated_at)}`;
    grid.innerHTML = data.cities.map(cardHTML).join("");
    grid.setAttribute("aria-busy", "false");
  } catch (err) {
    console.error(err);
    grid.innerHTML = `<p class="weather-loading">読み込みに失敗しました: ${err.message}</p>`;
    grid.setAttribute("aria-busy", "false");
  }
}

load();
