(() => {
  "use strict";

  const API = "/api/v1";
  const BUILD = "8.1.0";
  const TOKEN_KEY = "groe.tokens";
  const LANG_KEY = "groe.language";
  const GUEST_DIARY_KEY = "groe.guestDiary.v2";
  const LOCAL_GARDENS_KEY = "groe.localGardens.v1";
  const LOCAL_LOCATIONS = [
    ["Jakarta", "DKI Jakarta", -6.2088, 106.8456, 8], ["Bandung", "Jawa Barat", -6.9175, 107.6191, 768],
    ["Surabaya", "Jawa Timur", -7.2575, 112.7521, 5], ["Medan", "Sumatera Utara", 3.5952, 98.6722, 25],
    ["Semarang", "Jawa Tengah", -6.9667, 110.4167, 8], ["Yogyakarta", "DI Yogyakarta", -7.7956, 110.3695, 113],
    ["Makassar", "Sulawesi Selatan", -5.1477, 119.4327, 8], ["Palembang", "Sumatera Selatan", -2.9761, 104.7754, 8],
    ["Denpasar", "Bali", -8.65, 115.2167, 4], ["Bogor", "Jawa Barat", -6.595, 106.8167, 265],
    ["Depok", "Jawa Barat", -6.4025, 106.7942, 95], ["Tangerang", "Banten", -6.1783, 106.6319, 18],
    ["Bekasi", "Jawa Barat", -6.2383, 106.9756, 19], ["Malang", "Jawa Timur", -7.9839, 112.6214, 506],
    ["Batam", "Kepulauan Riau", 1.0456, 104.0305, 8], ["Pekanbaru", "Riau", 0.5071, 101.4478, 12],
    ["Padang", "Sumatera Barat", -0.9471, 100.4172, 5], ["Samarinda", "Kalimantan Timur", -0.5022, 117.1536, 8],
    ["Balikpapan", "Kalimantan Timur", -1.2379, 116.8529, 52], ["Banjarmasin", "Kalimantan Selatan", -3.3186, 114.5944, 1],
    ["Pontianak", "Kalimantan Barat", -0.0263, 109.3425, 3], ["Manado", "Sulawesi Utara", 1.4748, 124.8421, 5],
    ["Jayapura", "Papua", -2.5337, 140.7181, 20], ["Mataram", "Nusa Tenggara Barat", -8.5833, 116.1167, 26]
  ].map(([name, admin1, latitude, longitude, elevation]) => ({ name, admin1, admin2: null, display_name: `${name}, ${admin1}`, latitude, longitude, elevation, source: "built_in" }));
  let locationSearchTimer = null;
  const root = document.getElementById("root");

  const copy = {
    en: {
      tagline: "Grow what fits.",
      navPlan: "Plan a garden", navGardens: "My gardens", signIn: "Sign in", signOut: "Sign out",
      heroEyebrow: "A beginner-first edible garden planner",
      heroTitleA: "Turn your space into", heroTitleB: "something you can grow.",
      heroBody: "Tell GROE about your space, sunlight and care routine. It checks what is physically realistic and creates three different plans.",
      start: "Start planning", noAccount: "No account needed to receive recommendations.",
      howTitle: "From empty space to a feasible plan.",
      how1: "Describe your space", how1b: "Choose a shape, enter dimensions and tell us how much sun it receives.",
      how2: "Compare three plans", how2b: "Easy Start, Fast Harvest and Balanced Kitchen use different crops and spatial strategies.",
      how3: "See the real layout", how3b: "GROE places containers, crops, access areas and vertical modules within your actual dimensions.",
      step: "Step", back: "Back", next: "Continue", generate: "Generate my plans", generating: "Building feasible plans…",
      cityTitle: "Where will you grow?", cityBody: "Your city helps GROE understand broad Indonesian climate conditions.", city: "City or location",
      spaceTitle: "How much space do you have?", spaceBody: "Choose a simple shape and enter measurements in metres.",
      rectangle: "Rectangle", square: "Square", l_shape: "L-shape", custom: "Custom polygon", length: "Length", width: "Width", area: "Area",
      conditionsTitle: "What are the growing conditions?", surface: "Growing surface", soil: "Direct soil", containers: "Containers only", mixed: "Soil + containers",
      sunlight: "Direct sunlight", shade: "Mostly shaded", partial: "Partial sun", full: "Full sun",
      careTitle: "How much care feels realistic?", low: "Low maintenance", regular: "Regular care", hands_on: "Hands-on gardening",
      goalTitle: "What matters most?", easy: "Easy first harvest", fast: "Fast harvest", kitchen: "Everyday kitchen produce", variety: "Practical variety", yield: "Highest practical yield",
      optionsTitle: "A few useful options", vertical: "Vertical structures allowed", rack: "Tiered container rack allowed", depth: "Available container depth",
      resultsTitle: "Three ways your space can grow.", resultsBody: "Each plan is deterministic and based on the same conditions, but prioritises a different outcome.",
      select: "View this plan", score: "feasibility", crops: "crop profiles", plants: "plants", care: "weekly care", harvest: "first harvest", days: "days", tradeoff: "Trade-off",
      mapTitle: "Your scaled garden layout", save: "Save this garden", saved: "Garden saved", share: "Share plan", diary: "Open diary",
      selectedBecause: "Why GROE selected it", adjustments: "Adjustments", warning: "Important note", verification: "Data status",
      loginTitle: "Save your GROE garden", registerTitle: "Create your GROE account", email: "Email", password: "Password", login: "Sign in", register: "Create account", switchRegister: "New here? Create an account", switchLogin: "Already have an account? Sign in",
      gardensTitle: "Your browser-saved gardens", noGardens: "You have not saved a garden yet.", open: "Open", delete: "Delete",
      diaryTitle: "GROE Diary", diaryBody: "Record what changed and ask a question. Entries are text only.", growthStage: "Growth stage", entry: "What happened?", question: "Question for GROE (optional)", addEntry: "Save diary entry", noEntries: "No diary entries yet.", fallback: "Deterministic fallback guidance",
      publicPlan: "Read-only shared plan", home: "Home", retry: "Try again", close: "Close", loading: "Loading…",
      authRequired: "Create an account or sign in only to save plans and sync diary history.",
      invalid: "Please enter valid dimensions before continuing.",
      requestFailed: "Something went wrong. Please try again."
    },
    id: {
      tagline: "Tanam yang sesuai.",
      navPlan: "Buat rencana", navGardens: "Kebun saya", signIn: "Masuk", signOut: "Keluar",
      heroEyebrow: "Perencana kebun pangan untuk pemula",
      heroTitleA: "Ubah ruangmu menjadi", heroTitleB: "sesuatu yang bisa ditanam.",
      heroBody: "Ceritakan ruang, sinar matahari, dan rutinitas perawatanmu. GROE memeriksa apa yang realistis lalu membuat tiga rencana berbeda.",
      start: "Mulai merencanakan", noAccount: "Tidak perlu akun untuk menerima rekomendasi.",
      howTitle: "Dari ruang kosong menjadi rencana yang layak.",
      how1: "Jelaskan ruangmu", how1b: "Pilih bentuk, masukkan ukuran, dan beri tahu berapa lama sinar matahari langsung diterima.",
      how2: "Bandingkan tiga rencana", how2b: "Easy Start, Fast Harvest, dan Balanced Kitchen memakai tanaman dan strategi ruang yang berbeda.",
      how3: "Lihat tata letak nyata", how3b: "GROE menempatkan wadah, tanaman, jalur akses, dan modul vertikal sesuai ukuran ruangmu.",
      step: "Langkah", back: "Kembali", next: "Lanjut", generate: "Buat rencana saya", generating: "Menyusun rencana yang layak…",
      cityTitle: "Di mana kamu akan menanam?", cityBody: "Kota membantu GROE memahami kondisi iklim Indonesia secara umum.", city: "Kota atau lokasi",
      spaceTitle: "Berapa luas ruang yang tersedia?", spaceBody: "Pilih bentuk sederhana dan masukkan ukuran dalam meter.",
      rectangle: "Persegi panjang", square: "Persegi", l_shape: "Bentuk L", custom: "Poligon khusus", length: "Panjang", width: "Lebar", area: "Luas",
      conditionsTitle: "Bagaimana kondisi tempat tanam?", surface: "Permukaan tanam", soil: "Tanah langsung", containers: "Hanya wadah", mixed: "Tanah + wadah",
      sunlight: "Sinar matahari langsung", shade: "Mayoritas teduh", partial: "Matahari sebagian", full: "Matahari penuh",
      careTitle: "Seberapa banyak perawatan yang realistis?", low: "Perawatan rendah", regular: "Perawatan rutin", hands_on: "Aktif berkebun",
      goalTitle: "Apa yang paling penting?", easy: "Panen pertama yang mudah", fast: "Panen cepat", kitchen: "Bahan dapur sehari-hari", variety: "Variasi praktis", yield: "Hasil praktis tertinggi",
      optionsTitle: "Beberapa pilihan tambahan", vertical: "Struktur vertikal diperbolehkan", rack: "Rak wadah bertingkat diperbolehkan", depth: "Kedalaman wadah yang tersedia",
      resultsTitle: "Tiga cara ruangmu bisa tumbuh.", resultsBody: "Setiap rencana memakai kondisi yang sama, tetapi memprioritaskan hasil yang berbeda.",
      select: "Lihat rencana", score: "kelayakan", crops: "profil tanaman", plants: "tanaman", care: "perawatan mingguan", harvest: "panen pertama", days: "hari", tradeoff: "Konsekuensi",
      mapTitle: "Tata letak kebun berskala", save: "Simpan kebun ini", saved: "Kebun tersimpan di browser", share: "Bagikan rencana", diary: "Buka diary",
      selectedBecause: "Alasan GROE memilihnya", adjustments: "Penyesuaian", warning: "Catatan penting", verification: "Status data",
      loginTitle: "Simpan kebun GROE", registerTitle: "Buat akun GROE", email: "Email", password: "Kata sandi", login: "Masuk", register: "Buat akun", switchRegister: "Belum punya akun? Buat akun", switchLogin: "Sudah punya akun? Masuk",
      gardensTitle: "Kebun tersimpan di browser", noGardens: "Belum ada kebun yang disimpan.", open: "Buka", delete: "Hapus",
      diaryTitle: "GROE Diary", diaryBody: "Catat perubahan dan ajukan pertanyaan. Diary hanya berupa teks.", growthStage: "Tahap pertumbuhan", entry: "Apa yang terjadi?", question: "Pertanyaan untuk GROE (opsional)", addEntry: "Simpan catatan", noEntries: "Belum ada catatan diary.", fallback: "Panduan fallback deterministik",
      publicPlan: "Rencana publik hanya-baca", home: "Beranda", retry: "Coba lagi", close: "Tutup", loading: "Memuat…",
      authRequired: "Buat akun atau masuk hanya untuk menyimpan rencana dan menyinkronkan riwayat diary.",
      invalid: "Masukkan ukuran yang valid sebelum melanjutkan.",
      requestFailed: "Terjadi masalah. Silakan coba lagi."
    }
  };

  const state = {
    lang: localStorage.getItem(LANG_KEY) === "id" ? "id" : "en",
    view: "landing",
    step: 1,
    input: null,
    response: null,
    selected: null,
    selectedCrop: null,
    savedPlan: null,
    readOnly: false,
    loading: false,
    error: "",
    authenticated: !!getTokens(),
    showAuth: false,
    authMode: "login",
    authEmail: "",
    authPassword: "",
    pendingAction: null,
    saveName: "",
    savePublic: true,
    gardens: [],
    diaryEntries: [],
    diaryStage: "seedling",
    diaryText: "",
    diaryQuestion: "",
    locationSuggestions: [],
    locationLoading: false,
    locationSearched: false,
    geolocationLoading: false,
    weather: null,
    weatherLoading: false,
    showCropGuide: false
  };

  state.input = defaultInput(state.lang);
  state.saveName = state.lang === "id" ? "Kebun saya" : "My garden";

  function defaultInput(lang) {
    return {
      location: { city: "", latitude: null, longitude: null, elevation_m: null, display_name: "" },
      plot: { shape: "rectangle", length_m: 2, width_m: 1.5, sun_direction: "north" },
      surface: "containers",
      sunlight: "partial",
      care_commitment: "regular",
      primary_goal: "kitchen",
      desired_crops: [],
      excluded_crops: [],
      vertical_allowed: true,
      tiered_rack_allowed: false,
      water_access: "normal",
      child_or_pet_concerns: false,
      container_depth_cm: 30,
      language: lang
    };
  }

  function t(key) {
    return copy[state.lang][key] || copy.en[key] || key;
  }

  function lt(en, id) {
    return state.lang === "id" ? id : en;
  }

  function formatWeatherTime(value) {
    if (!value) return "";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value).replace("T", " ");
    return parsed.toLocaleString(state.lang === "id" ? "id-ID" : "en-US", {
      day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
    });
  }

  function localLocationMatches(query) {
    const q = query.trim().toLocaleLowerCase("id-ID");
    if (q.length < 2) return [];
    return LOCAL_LOCATIONS.filter(item => `${item.name} ${item.admin1}`.toLocaleLowerCase("id-ID").includes(q)).slice(0, 8);
  }

  async function directWeather(location) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const params = new URLSearchParams({
        latitude: String(location.latitude), longitude: String(location.longitude),
        current: "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m",
        timezone: "auto"
      });
      const response = await fetch(`https://api.open-meteo.com/v1/forecast?${params.toString()}`, { signal: controller.signal });
      if (!response.ok) throw new Error("weather unavailable");
      const data = await response.json();
      const current = data.current || {};
      return {
        provider: "open_meteo_browser", provider_available: true,
        updated_at: current.time, retrieved_at: new Date().toISOString(),
        current_temperature_c: current.temperature_2m,
        apparent_temperature_c: current.apparent_temperature,
        humidity_percent: current.relative_humidity_2m,
        precipitation_mm: current.precipitation,
        rain_mm: current.rain,
        wind_speed_kmh: current.wind_speed_10m,
        weather_code: current.weather_code,
        weather_label: lt("Current conditions", "Kondisi saat ini")
      };
    } finally { clearTimeout(timeout); }
  }

  function readGuestDiary() {
    try { return JSON.parse(localStorage.getItem(GUEST_DIARY_KEY) || "[]"); }
    catch (_) { return []; }
  }

  function writeGuestDiary(entries) {
    localStorage.setItem(GUEST_DIARY_KEY, JSON.stringify(entries.slice(0, 40)));
  }

  const CROP_COLORS = ["#3f7f5b", "#c58c2f", "#6f62a4", "#2f7f8e", "#b85f50", "#66873c", "#9a5f82", "#8a6846", "#39726e", "#a66b35"];
  const CROP_CODES = {
    "kangkung":"KG", "bayam-hijau":"BH", "selada":"SL", "pakcoy":"PK", "caisim-sawi-hijau":"CS", "kailan":"KL", "kale":"KA", "kubis":"KB", "katuk":"KT", "seledri":"SD", "daun-bawang":"DB", "kenikir":"KN",
    "tomat":"TM", "tomat-ceri":"TC", "cabai-rawit":"CR", "cabai-merah":"CM", "paprika":"PP", "terong":"TR", "mentimun":"MT", "pare":"PR", "okra":"OK", "kacang-panjang":"KP", "buncis":"BC", "oyong-gambas":"OY", "labu-kuning":"LK", "labu-siam":"LS", "melon":"ML", "semangka":"SM", "stroberi":"ST", "nanas":"NN", "pepaya-kerdil":"PY",
    "kemangi":"KM", "basil":"BS", "mint":"MN", "ketumbar":"KB", "serai":"SR", "pandan":"PD", "rosemary":"RM", "kucai":"KC", "jeruk-purut":"JP",
    "lobak-putih":"LP", "wortel":"WT", "bit":"BT", "ubi-jalar":"UJ", "kentang":"KN", "bawang-merah":"BM", "bawang-putih":"BP", "jahe":"JH", "kunyit":"KY", "kencur":"KR"
  };

  function cropVisual(slug, category) {
    let hash = 0;
    for (const ch of String(slug || category || "crop")) hash = ((hash << 5) - hash + ch.charCodeAt(0)) | 0;
    const color = CROP_COLORS[Math.abs(hash) % CROP_COLORS.length];
    const code = CROP_CODES[slug] || String(slug || "PL").split("-").map(part => part[0]).join("").slice(0, 2).toUpperCase();
    const kind = category === "root" ? "root" : category === "fruiting" ? "fruit" : category === "herb" ? "herb" : "leaf";
    return { color, code, kind };
  }

  function cropIconSvg(visual, className = "crop-icon") {
    const shape = visual.kind === "root"
      ? `<path d="M50 34c17 0 25 12 20 27-4 13-13 24-20 31-7-7-16-18-20-31-5-15 3-27 20-27Z" fill="currentColor"/><path d="M48 35c-10-12-8-21 1-29 5 12 5 21-1 29Zm5 0c3-13 11-19 22-18-5 12-12 18-22 18Z" fill="currentColor" opacity=".72"/>`
      : visual.kind === "fruit"
        ? `<circle cx="50" cy="57" r="25" fill="currentColor"/><path d="M49 34c-2-13 4-22 17-27 0 12-6 21-17 27Zm3 2c10-8 20-8 30-1-11 6-21 7-30 1Z" fill="currentColor" opacity=".72"/>`
        : visual.kind === "herb"
          ? `<path d="M50 88V32" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><ellipse cx="34" cy="49" rx="17" ry="10" transform="rotate(28 34 49)" fill="currentColor"/><ellipse cx="67" cy="38" rx="17" ry="10" transform="rotate(-28 67 38)" fill="currentColor"/><ellipse cx="34" cy="70" rx="16" ry="9" transform="rotate(25 34 70)" fill="currentColor" opacity=".75"/>`
          : `<path d="M50 89V47" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><ellipse cx="34" cy="44" rx="22" ry="13" transform="rotate(32 34 44)" fill="currentColor"/><ellipse cx="66" cy="35" rx="22" ry="13" transform="rotate(-32 66 35)" fill="currentColor" opacity=".78"/>`;
    return `<svg class="${attr(className)}" viewBox="0 0 100 100" aria-hidden="true" style="color:${attr(visual.color)}">${shape}<text x="50" y="60" text-anchor="middle" dominant-baseline="middle" font-size="20" font-weight="900" fill="#fff">${esc(visual.code)}</text></svg>`;
  }

  function esc(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function attr(value) {
    return esc(value);
  }

  function getTokens() {
    try { return JSON.parse(localStorage.getItem(TOKEN_KEY) || "null"); }
    catch (_) { return null; }
  }

  function setTokens(tokens) {
    if (tokens) localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
    else localStorage.removeItem(TOKEN_KEY);
  }

  async function request(path, options = {}, retry = true) {
    const tokens = getTokens();
    const headers = new Headers(options.headers || {});
    if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
    if (tokens?.access_token) headers.set("Authorization", `Bearer ${tokens.access_token}`);

    let response;
    try {
      response = await fetch(API + path, { ...options, headers });
    } catch (_) {
      throw new Error("Unable to reach the GROE service. Please wait a moment and try again.");
    }

    if (response.status === 401 && retry && tokens?.refresh_token) {
      const refreshed = await fetch(API + "/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: tokens.refresh_token })
      });
      if (refreshed.ok) {
        setTokens(await refreshed.json());
        return request(path, options, false);
      }
      setTokens(null);
      state.authenticated = false;
    }

    if (!response.ok) {
      let detail = "Request failed";
      try {
        const body = await response.json();
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body);
      } catch (_) {}
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  const api = {
    recommendations: input => request("/planner/recommendations", { method: "POST", body: JSON.stringify(input) }),
    register: (email, password, preferred_language) => request("/auth/register", { method: "POST", body: JSON.stringify({ email, password, preferred_language }) }),
    login: (email, password) => request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
    plans: () => request("/plans"),
    savePlan: payload => request("/plans", { method: "POST", body: JSON.stringify(payload) }),
    deletePlan: id => request(`/plans/${encodeURIComponent(id)}`, { method: "DELETE" }),
    locations: query => request(`/weather/locations?q=${encodeURIComponent(query)}&language=${encodeURIComponent(state.lang)}`),
    weather: location => {
      const params = new URLSearchParams({ city: location.city, latitude: String(location.latitude), longitude: String(location.longitude), language: state.lang });
      if (location.elevation_m != null) params.set("elevation_m", String(location.elevation_m));
      return request(`/weather/context?${params.toString()}`);
    },
    shared: slug => request(`/public/plans/${encodeURIComponent(slug)}`),
    diary: planId => request(`/diary?plan_id=${encodeURIComponent(planId)}`),
    addDiary: payload => request("/diary", { method: "POST", body: JSON.stringify(payload) }),
    guestDiary: payload => request("/diary/guest-advice", { method: "POST", body: JSON.stringify(payload) })
  };

  function header() {
    return `
      <header class="site-header">
        <button class="brand" data-action="navigate" data-view="landing" aria-label="GROE home">
          <span class="brand-mark">G</span>
          <span><b>GROE</b><small>${esc(t("tagline"))}</small></span>
        </button>
        <nav>
          <button data-action="navigate" data-view="planner">${esc(t("navPlan"))}</button>
          <button data-action="navigate" data-view="gardens">${esc(t("navGardens"))}</button>
        </nav>
        <div class="header-actions">
          <span class="beta-mode-chip">${esc(lt("Guest beta", "Beta tanpa akun"))}</span>
          <div class="lang-switch" aria-label="Language">
            <button class="${state.lang === "en" ? "active" : ""}" data-action="set-lang" data-lang="en">EN</button>
            <button class="${state.lang === "id" ? "active" : ""}" data-action="set-lang" data-lang="id">ID</button>
          </div>
        </div>
      </header>
    `;
  }

  function landing() {
    const dots = Array.from({ length: 12 }, (_, i) =>
      `<i class="plant-dot p${i % 5}" style="left:${12 + (i % 4) * 23}%;top:${13 + Math.floor(i / 4) * 30}%"></i>`
    ).join("");
    return `
      <main>
        <section class="hero">
          <div class="hero-copy">
            <span class="eyebrow">${esc(t("heroEyebrow"))}</span>
            <h1>${esc(t("heroTitleA"))}<br><em>${esc(t("heroTitleB"))}</em></h1>
            <p>${esc(t("heroBody"))}</p>
            <div class="hero-actions">
              <button class="button primary large" data-action="navigate" data-view="planner">${esc(t("start"))}<span>→</span></button>
            </div>
            <small class="quiet-proof">✓ ${esc(lt("No sign-in required. Plans and diary stay in this browser during beta.", "Tidak perlu masuk. Rencana dan diary tersimpan di browser selama beta."))}</small>
            <div class="v8-feature-strip" aria-label="GROE beta features">
              <span><b>01</b>${esc(lt("Live location + weather", "Lokasi + cuaca live"))}</span>
              <span><b>02</b>${esc(lt("Pot-aware space planning", "Perhitungan ruang berbasis ukuran pot"))}</span>
              <span><b>03</b>${esc(lt("Guest AI diary", "AI diary tanpa akun"))}</span>
            </div>
          </div>
          <div class="hero-visual" aria-hidden="true">
            <div class="orbit orbit-one"></div><div class="orbit orbit-two"></div>
            <div class="demo-card">
              <div class="demo-head"><span>2.0 m × 1.5 m</span><b>Balanced Kitchen</b></div>
              <div class="demo-map"><div class="demo-bed">${dots}<span class="path-line"></span><span class="trellis-line"></span></div></div>
              <div class="demo-stats"><span><b>6</b> crops</span><span><b>14</b> plants</span><span><b>28</b> days</span></div>
            </div>
            <span class="floating-tag tag-a">Scaled layout</span><span class="floating-tag tag-b">Beginner ready</span>
          </div>
        </section>
        <section class="how-section">
          <span class="eyebrow">HOW GROE WORKS</span><h2>${esc(t("howTitle"))}</h2>
          <div class="how-grid">
            <article><span>01</span><div class="how-icon">⌗</div><h3>${esc(t("how1"))}</h3><p>${esc(t("how1b"))}</p></article>
            <article><span>02</span><div class="how-icon">◫</div><h3>${esc(t("how2"))}</h3><p>${esc(t("how2b"))}</p></article>
            <article><span>03</span><div class="how-icon">✣</div><h3>${esc(t("how3"))}</h3><p>${esc(t("how3b"))}</p></article>
          </div>
        </section>
      </main>
    `;
  }

  function option(value, current, title, icon, action, body = "") {
    return `
      <button type="button" class="option-card ${current === value ? "selected" : ""}" data-action="${action}" data-value="${attr(value)}">
        <span class="option-icon">${esc(icon)}</span><b>${esc(title)}</b>${body ? `<small>${esc(body)}</small>` : ""}<i class="check">✓</i>
      </button>
    `;
  }

  function planner() {
    const input = state.input;
    const area = Math.max(0, Number(input.plot.length_m || 0) * Number(input.plot.width_m || 0));
    let content = "";

    if (state.step === 1) {
      const suggestions = state.locationSuggestions.map(item => `
        <button type="button" class="location-option" data-action="select-location"
          data-name="${attr(item.name)}" data-display="${attr(item.display_name || item.name)}"
          data-latitude="${attr(item.latitude)}" data-longitude="${attr(item.longitude)}" data-elevation="${attr(item.elevation ?? "")}">
          <b>${esc(item.name)}</b><small>${esc([item.admin2, item.admin1].filter(Boolean).join(", "))} · ${esc(item.source === "open_meteo" ? lt("live directory", "direktori live") : lt("Indonesia fallback", "cadangan Indonesia"))}</small>
        </button>`).join("");
      const weather = state.weather;
      const weatherCard = state.weatherLoading
        ? `<div class="weather-card loading-weather"><div class="spinner"></div><span>${esc(lt("Updating local weather…", "Memperbarui cuaca lokal…"))}</span></div>`
        : weather
          ? `<div class="weather-card ${weather.provider_available ? "live" : "fallback"}">
              <div class="weather-card-top"><div class="weather-main"><span>${weather.provider_available ? "☀︎" : "◎"}</span><div><small>${esc(weather.weather_label || lt("Current conditions", "Kondisi saat ini"))}</small><b>${weather.current_temperature_c ?? weather.mean_temperature_c ?? "—"}°C</b></div></div><button type="button" class="weather-refresh" data-action="refresh-weather">↻ ${esc(lt("Refresh", "Perbarui"))}</button></div>
              <div class="weather-metrics"><span><b>${weather.humidity_percent ?? "—"}%</b><small>${esc(lt("humidity", "kelembapan"))}</small></span><span><b>${weather.precipitation_mm ?? "—"} mm</b><small>${esc(lt("rain now", "hujan saat ini"))}</small></span><span><b>${weather.wind_speed_kmh ?? "—"} km/h</b><small>${esc(lt("wind", "angin"))}</small></span><span><b>${weather.apparent_temperature_c ?? "—"}°C</b><small>${esc(lt("feels like", "terasa seperti"))}</small></span></div>
              <small class="weather-status">${esc(weather.provider_available ? lt("Live weather from Open-Meteo", "Cuaca langsung dari Open-Meteo") : lt("Weather unavailable; broad climate fallback is active", "Cuaca tidak tersedia; perkiraan iklim umum digunakan"))}${weather.updated_at || weather.retrieved_at ? ` · ${esc(formatWeatherTime(weather.updated_at || weather.retrieved_at))}` : ""}</small>
            </div>`
          : "";
      content = `
        <span class="eyebrow">GROE / 01</span><h1>${esc(t("cityTitle"))}</h1><p class="lead">${esc(lt("Type at least three letters, then choose the correct location from the dropdown.", "Ketik minimal tiga huruf, lalu pilih lokasi yang benar dari daftar."))}</p>
        <div class="location-combobox">
          <label class="field hero-field"><span>${esc(t("city"))}</span><input autocomplete="off" data-field="city" value="${attr(input.location.city)}" placeholder="Jakarta, Bandung, Surabaya…"></label>
          <button type="button" class="use-location-button" data-action="use-geolocation" ${state.geolocationLoading ? "disabled" : ""}>⌖ ${esc(state.geolocationLoading ? t("loading") : lt("Use my current location", "Gunakan lokasi saya"))}</button>
          ${state.locationLoading ? `<div class="location-loading">${esc(t("loading"))}</div>` : ""}
          ${suggestions ? `<div class="location-dropdown">${suggestions}</div>` : ""}
          ${state.locationSearched && !state.locationLoading && !suggestions ? `<div class="location-empty">${esc(lt("No matching Indonesian location found. Try a nearby city name.", "Lokasi Indonesia tidak ditemukan. Coba nama kota terdekat."))}</div>` : ""}
        </div>
        ${input.location.latitude != null ? `<div class="context-card selected-location"><span class="context-icon">⌖</span><div><b>${esc(input.location.display_name || input.location.city)}</b><small>${Number(input.location.latitude).toFixed(3)}, ${Number(input.location.longitude).toFixed(3)} · ${esc(lt("Location selected", "Lokasi dipilih"))}</small></div></div>` : `<p class="selection-hint">${esc(lt("Select a result so GROE can retrieve temperature and humidity.", "Pilih hasil agar GROE dapat mengambil suhu dan kelembapan."))}</p>`}
        ${weatherCard}
      `;
    } else if (state.step === 2) {
      content = `
        <span class="eyebrow">GROE / 02</span><h1>${esc(t("spaceTitle"))}</h1><p class="lead">${esc(t("spaceBody"))}</p>
        <div class="shape-row">
          ${option("rectangle", input.plot.shape, t("rectangle"), "▭", "set-shape")}
          ${option("square", input.plot.shape, t("square"), "□", "set-shape")}
          ${option("l_shape", input.plot.shape, t("l_shape"), "⌞", "set-shape")}
        </div>
        <div class="dimension-card">
          <div class="dimension-inputs">
            <label class="field"><span>${esc(t("length"))}</span><div><input data-field="plot-length" type="number" min="0.3" step="0.1" value="${attr(input.plot.length_m)}"><b>m</b></div></label>
            <label class="field"><span>${esc(t("width"))}</span><div><input data-field="plot-width" type="number" min="0.3" step="0.1" value="${attr(input.plot.width_m)}"><b>m</b></div></label>
            <div class="area-readout"><small>${esc(t("area"))}</small><b>${area.toFixed(2)} m²</b></div>
          </div>
          <div class="shape-preview ${attr(input.plot.shape)}"><span>${esc(input.plot.length_m)} m</span><i></i><b>${esc(input.plot.width_m)} m</b></div>
        </div>
      `;
    } else if (state.step === 3) {
      content = `
        <span class="eyebrow">GROE / 03–04</span><h1>${esc(t("conditionsTitle"))}</h1>
        <h2>${esc(t("surface"))}</h2>
        <div class="option-grid three">
          ${option("soil", input.surface, t("soil"), "▰", "set-surface")}
          ${option("containers", input.surface, t("containers"), "◉", "set-surface")}
          ${option("mixed", input.surface, t("mixed"), "◫", "set-surface")}
        </div>
        <div class="question-divider"></div><h2>${esc(t("sunlight"))}</h2>
        <div class="option-grid three">
          ${option("shade", input.sunlight, t("shade"), "◔", "set-sun", "< 3 h")}
          ${option("partial", input.sunlight, t("partial"), "◑", "set-sun", "3–6 h")}
          ${option("full", input.sunlight, t("full"), "●", "set-sun", "> 6 h")}
        </div>
      `;
    } else if (state.step === 4) {
      content = `
        <span class="eyebrow">GROE / 05–06</span><h1>${esc(t("careTitle"))}</h1>
        <div class="option-grid three">
          ${option("low", input.care_commitment, t("low"), "◷", "set-care")}
          ${option("regular", input.care_commitment, t("regular"), "◴", "set-care")}
          ${option("hands_on", input.care_commitment, t("hands_on"), "✦", "set-care")}
        </div>
        <div class="question-divider"></div><h2>${esc(t("goalTitle"))}</h2>
        <div class="option-grid goals">
          ${option("easy", input.primary_goal, t("easy"), "◒", "set-goal")}
          ${option("fast", input.primary_goal, t("fast"), "↗", "set-goal")}
          ${option("kitchen", input.primary_goal, t("kitchen"), "⌂", "set-goal")}
          ${option("variety", input.primary_goal, t("variety"), "✣", "set-goal")}
          ${option("yield", input.primary_goal, t("yield"), "▥", "set-goal")}
        </div>
      `;
    } else {
      content = `
        <span class="eyebrow">GROE / OPTIONAL</span><h1>${esc(t("optionsTitle"))}</h1>
        <div class="toggle-list">
          <label><span><b>${esc(t("vertical"))}</b><small>Trellises are used only for compatible crops.</small></span><input data-field="vertical" type="checkbox" ${input.vertical_allowed ? "checked" : ""}><i></i></label>
          <label><span><b>${esc(t("rack"))}</b><small>Deep and heavy containers remain on the lowest tier.</small></span><input data-field="rack" type="checkbox" ${input.tiered_rack_allowed ? "checked" : ""}><i></i></label>
        </div>
        <label class="range-field"><span>${esc(t("depth"))}</span><output>${esc(input.container_depth_cm || 30)} cm</output><input data-field="container-depth" type="range" min="10" max="70" step="5" value="${attr(input.container_depth_cm || 30)}"></label>
      `;
    }

    const canContinue = (state.step !== 1 || state.input.location.latitude != null) && (state.step !== 2 || area > 0);
    return `
      <main class="planner-page"><div class="planner-shell">
        <div class="progress"><span>${esc(t("step"))} ${state.step} / 5</span><div><i style="width:${state.step * 20}%"></i></div></div>
        ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
        ${state.loading ? `<div class="loading-card"><div class="spinner"></div><h2>${esc(t("generating"))}</h2><p>GROE is scoring crop profiles, enforcing physical constraints and creating distinct layouts.</p></div>` : `<section class="question-screen">${content}</section>`}
        ${state.loading ? "" : `<div class="planner-nav"><button class="button secondary" data-action="planner-back">← ${esc(t("back"))}</button>${state.step < 5 ? `<button class="button primary" data-action="planner-next" ${canContinue ? "" : "disabled"}>${esc(t("next"))} →</button>` : `<button class="button primary" data-action="generate">${esc(t("generate"))} ✦</button>`}</div>`}
      </div></main>
    `;
  }

  function planCard(plan) {
    const name = state.lang === "id" ? plan.name_id : plan.name_en;
    const proposition = state.lang === "id" ? plan.proposition_id : plan.proposition_en;
    const bubbles = (plan.crops || []).slice(0, 6).map((crop, i) => {
      const label = state.lang === "id" ? crop.name_id : crop.name_en;
      return `<span class="bubble b${i % 5}" title="${attr(label)}">${esc(label.slice(0, 1))}</span>`;
    }).join("");
    return `
      <article class="plan-card accent-${attr(plan.accent || "green")}">
        <div class="plan-card-top"><span>${Math.round(plan.feasibility_score || 0)}% ${esc(t("score"))}</span><i>${esc(plan.beginner_difficulty)}</i></div>
        <h3>${esc(name)}</h3><p class="plan-proposition">${esc(proposition)}</p>
        <div class="crop-bubbles">${bubbles}</div>
        <div class="plan-metrics"><div><b>${esc(plan.crop_profile_count)}</b><small>${esc(t("crops"))}</small></div><div><b>${esc(plan.total_plants)}</b><small>${esc(t("plants"))}</small></div><div><b>${esc(plan.expected_first_harvest_days || "—")}</b><small>${esc(t("days"))}</small></div></div>
        <div class="trade"><small>${esc(t("tradeoff"))}</small><p>${esc(plan.trade_off)}</p></div>
        <button class="button primary full" data-action="select-plan" data-key="${attr(plan.key)}">${esc(t("select"))} →</button>
      </article>
    `;
  }

  function results() {
    const r = state.response;
    if (!r) return errorPage();
    return `
      <main class="page results-page">
        <button class="back-link" data-action="navigate" data-view="planner">← ${esc(t("back"))}</button>
        <header class="results-heading">
          <div><span class="eyebrow">GROE RECOMMENDATIONS</span><h1>${esc(t("resultsTitle"))}</h1><p>${esc(t("resultsBody"))}</p></div>
          <div class="condition-summary"><span>${r.plot?.area_m2 ? Number(r.plot.area_m2).toFixed(1) : "—"} m²</span><span>${esc(r.input_summary.location.city)}</span><span>${esc(t(r.input_summary.sunlight))}</span></div>
        </header>
        <div class="plans-grid">${r.plans.map(planCard).join("")}</div>
        <p class="engine-note">Deterministic engine ${esc(r.engine_version)} · Data ${esc(r.data_version)}</p>
      </main>
    `;
  }

  function polygonPoints(points, pad) {
    return (points || []).map(p => `${Number(p[0]) + pad},${Number(p[1]) + pad}`).join(" ");
  }

  function plotMap(plan) {
    const layout = plan.layout || {};
    const boundary = layout.plot_boundary || [[0,0],[2,0],[2,1.5],[0,1.5]];
    const xs = boundary.map(p => Number(p[0]));
    const ys = boundary.map(p => Number(p[1]));
    const maxX = Math.max(...xs, 1);
    const maxY = Math.max(...ys, 1);
    const pad = 0.18;
    const points = polygonPoints(boundary, pad);
    const surfaceMode = state.input?.surface || "soil";
    const plotFill = surfaceMode === "containers" ? "url(#floor)" : surfaceMode === "mixed" ? "url(#mixed)" : "url(#soil)";
    const access = layout.access_zone ? `<polygon points="${polygonPoints(layout.access_zone, pad)}" fill="#d8cbb8" opacity=".94" stroke="#ae9d85" stroke-width=".018"></polygon>` : "";
    const placements = (layout.placements || []).map(p => {
      const active = state.selectedCrop === p.slug;
      const x = Number(p.x_m || 0) + pad;
      const y = Number(p.y_m || 0) + pad;
      const w = Math.max(.12, Number(p.width_m || .2));
      const h = Math.max(.12, Number(p.height_m || .2));
      const label = state.lang === "id" ? p.name_id : p.name_en;
      const visual = cropVisual(p.slug, p.category);
      const cx = x + w / 2;
      const cy = y + h / 2;
      const fontSize = Math.max(.10, Math.min(w, h) * .42);
      const isHanging = p.structure_type === "hanging_pot";
      const shape = isHanging
        ? `<line x1="${cx}" y1="${y}" x2="${cx}" y2="${y+h*.22}" stroke="#5d5145" stroke-width=".022"></line>
           <line x1="${x+w*.18}" y1="${y+h*.08}" x2="${x+w*.82}" y2="${y+h*.08}" stroke="#5d5145" stroke-width=".026"></line>
           <line x1="${x+w*.18}" y1="${y+h*.08}" x2="${x+w*.32}" y2="${y+h*.38}" stroke="#80583d" stroke-width=".018"></line>
           <line x1="${x+w*.82}" y1="${y+h*.08}" x2="${x+w*.68}" y2="${y+h*.38}" stroke="#80583d" stroke-width=".018"></line>
           <path d="M ${x+w*.22} ${y+h*.38} L ${x+w*.78} ${y+h*.38} Q ${x+w*.70} ${y+h*.88} ${cx} ${y+h*.90} Q ${x+w*.30} ${y+h*.88} ${x+w*.22} ${y+h*.38} Z" fill="#c78f61" stroke="#80583d" stroke-width="${active ? ".05" : ".025"}"></path>
           <ellipse cx="${cx}" cy="${y+h*.53}" rx="${w*.22}" ry="${h*.18}" fill="${visual.color}" opacity=".94"></ellipse>`
        : p.structure_type === "pot" || p.shape === "container"
          ? `<circle cx="${cx}" cy="${cy}" r="${Math.min(w,h)*.46}" fill="#d7b28c" stroke="#8b6547" stroke-width="${active ? ".05" : ".025"}"></circle><circle cx="${cx}" cy="${cy}" r="${Math.min(w,h)*.34}" fill="${visual.color}" opacity=".92"></circle>`
          : `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx=".06" fill="${visual.color}" opacity=".9" stroke="#f8f3e8" stroke-width="${active ? ".05" : ".022"}"></rect>`;
      const codeY = isHanging ? y + h*.58 : cy + fontSize*.24;
      return `
        <g class="placement ${active ? "active" : ""}" data-action="open-crop-guide" data-slug="${attr(p.slug)}" tabindex="0" role="button">
          ${shape}
          <text x="${cx}" y="${codeY}" text-anchor="middle" font-size="${Math.max(.075,fontSize*.66)}" font-family="system-ui" font-weight="900" fill="#fff">${esc(visual.code)}</text>
          ${p.trellis ? `<line x1="${x}" y1="${y}" x2="${x+w}" y2="${y}" stroke="#f0c94c" stroke-width=".035" stroke-dasharray=".055 .035"></line>` : ""}
        </g>`;
    }).join("");

    const modules = (layout.vertical_modules || []).map((module, index) => {
      if (module.type === "tiered_rack") {
        const x = Number(module.x_m ?? 0) + pad;
        const y = Number(module.y_m ?? 0) + pad;
        const w = Number(module.module_width_m || .65);
        return `<g class="map-module"><rect x="${x}" y="${y}" width="${w}" height=".14" rx=".025" fill="#7f6c5c" stroke="#fff" stroke-width=".018"></rect><line x1="${x+.05}" y1="${y}" x2="${x+.05}" y2="${y+.18}" stroke="#57483d" stroke-width=".025"></line><line x1="${x+w-.05}" y1="${y}" x2="${x+w-.05}" y2="${y+.18}" stroke="#57483d" stroke-width=".025"></line></g>`;
      }
      if (module.type === "hanging_pot") return "";
      return "";
    }).join("");

    const compost = layout.compost ? `<rect x="${Number(layout.compost.x_m)+pad}" y="${Number(layout.compost.y_m)+pad}" width="${layout.compost.width_m}" height="${layout.compost.height_m}" rx=".04" fill="#5d4936" stroke="#cdb28f" stroke-width=".025"></rect><text x="${Number(layout.compost.x_m)+pad+layout.compost.width_m/2}" y="${Number(layout.compost.y_m)+pad+layout.compost.height_m/2+.02}" text-anchor="middle" font-size=".08" fill="#fff">C</text>` : "";

    return `
      <div class="map-wrap"><svg class="plot-svg" viewBox="0 0 ${maxX + pad * 2} ${maxY + pad * 2}" role="img" aria-label="Scaled garden layout">
        <defs>
          <pattern id="soil" width=".12" height=".12" patternUnits="userSpaceOnUse"><rect width=".12" height=".12" fill="#7b614a"></rect><circle cx=".03" cy=".04" r=".008" fill="#a88867"></circle></pattern>
          <pattern id="floor" width=".16" height=".16" patternUnits="userSpaceOnUse"><rect width=".16" height=".16" fill="#ebe6dc"></rect><path d="M0 .16L.16 0" stroke="#ddd5c7" stroke-width=".012"></path></pattern>
          <pattern id="mixed" width=".2" height=".2" patternUnits="userSpaceOnUse"><rect width=".2" height=".2" fill="#a88a69"></rect><rect width=".1" height=".2" fill="#7b614a"></rect></pattern>
        </defs>
        <polygon points="${points}" fill="${plotFill}" stroke="#4b392b" stroke-width=".055" stroke-linejoin="round"></polygon>
        ${access}${placements}${modules}${compost}
        <g class="sun-arrow"><circle cx="${pad+.12}" cy="${pad+.12}" r=".09" fill="#f3c94f"></circle><text x="${pad+.12}" y="${pad+.15}" text-anchor="middle" font-size=".1">☀</text></g>
        <text x="${pad}" y="${maxY + pad * 2 - .035}" font-size=".072" fill="#fff">1 unit = 1 metre</text>
      </svg></div>`;
  }

  function mapLegend(plan) {
    const placements = plan.layout?.placements || [];
    const hasPot = placements.some(p => p.structure_type === "pot");
    const hasSoil = placements.some(p => p.shape === "soil");
    const modules = plan.layout?.vertical_modules || [];
    const hasRack = modules.some(m => m.type === "tiered_rack");
    const hasHanging = placements.some(p => p.structure_type === "hanging_pot");
    const hasTrellis = modules.some(m => m.type === "trellis") || (plan.layout?.placements || []).some(p => p.trellis);
    const items = [
      ["soil", lt("Soil bed", "Tanah langsung"), hasSoil],
      ["pot", lt("Pot", "Pot"), hasPot],
      ["hanging", lt("Hanging pot", "Pot gantung"), hasHanging],
      ["path", lt("Access path", "Jalur akses"), !!plan.layout?.access_zone],
      ["rack", lt("Plant stand / rack", "Stand / rak tanaman"), hasRack],
      ["trellis", lt("Trellis", "Teralis"), hasTrellis],
      ["compost", lt("Compost point", "Titik kompos"), !!plan.layout?.compost]
    ];
    return `<div class="map-legend expanded">${items.map(([type,label,used]) => `<span class="${used ? "used" : "unused"}"><i class="legend-${type}"></i>${esc(label)}</span>`).join("")}</div>`;
  }

  function cropLegend(plan) {
    const crops = plan.crops || [];
    if (!crops.length) return "";
    return `<div class="crop-map-key"><b>${esc(lt("Plant key", "Kunci tanaman"))}</b><div>${crops.map(crop => {
      const visual = cropVisual(crop.slug, crop.category);
      const label = state.lang === "id" ? crop.name_id : crop.name_en;
      return `<span style="--crop:${attr(visual.color)}">${cropIconSvg(visual, "crop-key-icon")}<b>${esc(visual.code)}</b>${esc(label)}</span>`;
    }).join("")}</div></div>`;
  }

  function potSummary(plan) {
    const groups = new Map();
    for (const crop of plan.crops || []) {
      if (!crop.container_spec) continue;
      const p = crop.container_spec;
      const key = `${p.recommended_diameter_cm}-${p.recommended_depth_cm}-${p.recommended_volume_l}`;
      const current = groups.get(key) || { count: 0, p };
      current.count += Number(crop.quantity || 0);
      groups.set(key, current);
    }
    if (!groups.size) return "";
    const rows = [...groups.values()].map(({ count, p }) => `<span><b>${count}×</b> Ø ${p.recommended_diameter_cm} cm · ${p.recommended_depth_cm} cm ${esc(lt("deep", "dalam"))} · ${p.recommended_volume_l} L</span>`).join("");
    return `<div class="pot-summary"><div><b>${esc(lt("Pot sizes included in the space calculation", "Ukuran pot sudah dihitung dalam kebutuhan ruang"))}</b><small>${esc(lt("GROE uses the larger of ideal pot diameter and plant spacing for every footprint.", "GROE memakai nilai terbesar antara diameter pot ideal dan jarak tanaman untuk setiap tapak."))}</small></div><div class="pot-summary-list">${rows}</div></div>`;
  }

  function plantCard(crop) {
    const label = state.lang === "id" ? crop.name_id : crop.name_en;
    const p = crop.parameters || {};
    const visual = cropVisual(crop.slug, crop.category);
    const pot = crop.container_spec;
    const harvest = `${p.days_to_first_harvest_min ?? "—"}–${p.days_to_first_harvest_max ?? "—"}`;
    const thirdMetric = pot
      ? `<b>Ø ${esc(pot.recommended_diameter_cm)} cm</b><small>${esc(lt("ideal GROE pot", "pot ideal GROE"))}</small>`
      : `<b>${esc(p.preferred_spacing_cm ?? "—")} cm</b><small>${esc(lt("plant spacing", "jarak tanam"))}</small>`;
    return `<article class="recommendation-plant-card" style="--crop:${attr(visual.color)}">
      <div class="plant-card-visual"><span class="suitability-badge">${Math.round(crop.score || 0)}% ${esc(lt("fit", "cocok"))}</span>${cropIconSvg(visual, "plant-card-icon")}<span class="plant-code">${esc(visual.code)}</span></div>
      <div class="plant-card-body"><h3>${esc(label)}</h3><em>${esc(crop.scientific_name)}</em>
        <div class="plant-card-metrics"><span><b>${esc(harvest)}</b><small>${esc(lt("days to harvest", "hari hingga panen"))}</small></span><span><b>${esc(p.preferred_direct_sun_hours ?? p.minimum_direct_sun_hours ?? "—")}</b><small>${esc(lt("sun hours", "jam matahari"))}</small></span><span>${thirdMetric}</span></div>
        ${pot ? `<p class="pot-note">${esc(lt(`Recommended: ${pot.recommended_depth_cm} cm deep · ${pot.recommended_volume_l} L`, `Rekomendasi: kedalaman ${pot.recommended_depth_cm} cm · ${pot.recommended_volume_l} L`))}</p>` : ""}
        <div class="plant-card-footer"><span>${esc(crop.quantity)} ${esc(lt("plants", "tanaman"))}</span><button data-action="open-crop-guide" data-slug="${attr(crop.slug)}">${esc(lt("View guide", "Lihat panduan"))} →</button></div>
      </div>
    </article>`;
  }

  function detail() {
    const plan = state.selected;
    if (!plan) return errorPage();
    if (!state.selectedCrop && plan.crops?.length) state.selectedCrop = plan.crops[0].slug;
    return `
      <main class="page detail-page">
        <button class="back-link" data-action="navigate" data-view="${state.readOnly ? "landing" : "results"}">← ${esc(state.readOnly ? t("home") : t("back"))}</button>
        ${state.readOnly ? `<div class="public-banner">${esc(t("publicPlan"))}</div>` : ""}
        <header class="detail-header">
          <div><span class="eyebrow">SELECTED PLAN</span><h1>${esc(state.lang === "id" ? plan.name_id : plan.name_en)}</h1><p>${esc(state.lang === "id" ? plan.proposition_id : plan.proposition_en)}</p></div>
          <div class="detail-actions">
            ${state.readOnly ? "" : `<button class="button primary" data-action="save-plan">${esc(state.savedPlan ? t("saved") : t("save"))}</button>`}
            <button class="button secondary" data-action="share-plan">${esc(t("share"))}</button>
            ${state.readOnly ? "" : `<button class="button secondary" data-action="open-diary">${esc(t("diary"))}</button>`}
          </div>
        </header>
        ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
        <section class="layout-panel map-first">
          <div class="panel-title"><div><span class="eyebrow">2D PLAN</span><h2>${esc(t("mapTitle"))}</h2><p>${esc(lt("Each crop keeps the same symbol and colour everywhere in GROE.", "Setiap tanaman memakai simbol dan warna yang sama di seluruh GROE."))}</p></div></div>
          ${plotMap(plan)}
          ${cropLegend(plan)}
          ${mapLegend(plan)}
          ${potSummary(plan)}
          <div class="layout-stats"><div><b>${plan.layout ? Number(plan.layout.plot_area_m2).toFixed(1) : "—"} m²</b><small>${esc(t("area"))}</small></div><div><b>${esc(plan.total_plants)}</b><small>${esc(t("plants"))}</small></div><div><b>${esc(plan.containers_required)}</b><small>${esc(lt("pots", "pot"))}</small></div><div><b>${esc(plan.weekly_care_minutes)} min</b><small>${esc(t("care"))}</small></div></div>
        </section>
        <section class="plant-recommendations-section">
          <div class="plant-section-head"><div><span class="eyebrow">${esc(lt("PLANT RECOMMENDATIONS", "REKOMENDASI TANAMAN"))}</span><h2>${esc(lt("Your plant combination", "Kombinasi tanaman Anda"))}</h2></div><p>${esc(lt("Open a card for planting, care and post-harvest guidance.", "Buka kartu untuk panduan menanam, merawat, dan pascapanen."))}</p></div>
          <div class="recommendation-plant-grid">${(plan.crops || []).map(plantCard).join("")}</div>
        </section>
        ${!state.readOnly && !state.savedPlan ? `<section class="save-strip local-save-strip"><label class="field"><span>${esc(lt("Garden name", "Nama kebun"))}</span><input data-field="save-name" value="${attr(state.saveName)}"></label><div><b>${esc(lt("Saved locally during beta", "Tersimpan lokal selama beta"))}</b><small>${esc(lt("No sign-in. This garden stays in this browser.", "Tanpa masuk. Kebun ini tersimpan di browser ini."))}</small></div></section>` : ""}
      </main>`;
  }

  function guideList(items) {
    return Array.isArray(items) && items.length ? `<ol>${items.map(item => `<li>${esc(item)}</li>`).join("")}</ol>` : `<p>${esc(lt("Guidance is still being reviewed.", "Panduan masih dalam proses peninjauan."))}</p>`;
  }

  function cropGuideModal() {
    if (!state.showCropGuide || !state.selected) return "";
    const crop = (state.selected.crops || []).find(item => item.slug === state.selectedCrop);
    if (!crop) return "";
    const label = state.lang === "id" ? crop.name_id : crop.name_en;
    const guidance = state.lang === "id" ? (crop.guidance_id || {}) : (crop.guidance_en || {});
    const p = crop.parameters || {};
    const visual = cropVisual(crop.slug, crop.category);
    const pot = crop.container_spec;
    return `<div class="dialog-backdrop crop-guide-backdrop" role="dialog" aria-modal="true">
      <div class="crop-guide-dialog"><button class="dialog-close" data-action="close-crop-guide">×</button>
        <header style="--crop:${attr(visual.color)}">${cropIconSvg(visual, "guide-crop-icon")}<div><span class="eyebrow">${esc(crop.classification || "recommended")} · ${Math.round(crop.score || 0)}% ${esc(lt("fit", "cocok"))}</span><h2>${esc(label)}</h2><em>${esc(crop.scientific_name)}</em></div></header>
        <div class="guide-metrics"><span><b>${p.days_to_first_harvest_min ?? "—"}–${p.days_to_first_harvest_max ?? "—"}</b><small>${esc(lt("days to harvest", "hari hingga panen"))}</small></span><span><b>${p.preferred_spacing_cm ?? "—"} cm</b><small>${esc(lt("plant spacing", "jarak tanaman"))}</small></span><span><b>${pot ? `Ø ${pot.recommended_diameter_cm} × ${pot.recommended_depth_cm} cm` : `${p.preferred_root_depth_cm ?? "—"} cm`}</b><small>${esc(pot ? lt("recommended pot", "pot rekomendasi") : lt("root depth", "kedalaman akar"))}</small></span><span><b>${esc(crop.quantity)}</b><small>${esc(lt("units in your plan", "unit di denah Anda"))}</small></span></div>
        ${pot ? `<div class="guide-pot-callout"><b>${esc(lt("Ideal pot for this plan", "Pot ideal untuk rencana ini"))}</b><span>Ø ${pot.recommended_diameter_cm} cm · ${pot.recommended_depth_cm} cm ${esc(lt("deep", "dalam"))} · ${pot.recommended_volume_l} L</span><small>${esc(lt("Calculated from the crop minimums and preferred spacing stored in GROE metadata.", "Dihitung dari batas minimum tanaman dan jarak ideal yang tersimpan dalam metadata GROE."))}</small></div>` : ""}
        <section><h3>${esc(lt("How to start", "Cara menanam dari awal"))}</h3>${guideList(guidance.planting_steps)}</section>
        <section><h3>${esc(lt("How to care", "Cara merawat"))}</h3>${guideList(guidance.care_steps)}</section>
        <section><h3>${esc(lt("After harvest", "Setelah panen"))}</h3>${guideList(guidance.harvest_steps)}<p>${esc(guidance.post_harvest || "")}</p></section>
        <section class="guide-warning"><h3>${esc(lt("Warning signs", "Tanda peringatan"))}</h3>${guideList(guidance.warning_signs)}</section>
      </div>
    </div>`;
  }


  function gardens() {
    const cards = state.gardens.map((p, i) => {
      const plan = p.plan_data || {};
      return `<article class="saved-card"><div class="saved-card-art"><span>${String(i+1).padStart(2,"0")}</span><i></i><i></i><i></i></div><div><small>${esc(new Date(p.created_at).toLocaleDateString())}</small><h3>${esc(p.name)}</h3><p>${esc(state.lang === "id" ? plan.name_id : plan.name_en)}</p><div class="saved-actions"><button class="button primary small" data-action="open-plan" data-id="${attr(p.id)}">${esc(t("open"))}</button><button class="text-button danger" data-action="delete-plan" data-id="${attr(p.id)}">${esc(t("delete"))}</button></div></div></article>`;
    }).join("");
    return `
      <main class="page"><button class="back-link" data-action="navigate" data-view="landing">← ${esc(t("home"))}</button><span class="eyebrow">SAVED PLANS</span><h1>${esc(t("gardensTitle"))}</h1>
      ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
      ${state.loading ? `<div class="loading-card"><div class="spinner"></div><p>${esc(t("loading"))}</p></div>` : state.gardens.length ? `<div class="garden-grid">${cards}</div>` : `<div class="empty-state"><div class="empty-plot"><i></i><i></i><i></i></div><h2>${esc(t("noGardens"))}</h2><button class="button primary" data-action="navigate" data-view="planner">${esc(t("start"))}</button></div>`}
      </main>
    `;
  }

  function diary() {
    const guestMode = true;
    const entries = state.diaryEntries.map(item => {
      const cropStatus = item.detected_crop_name
        ? `<span class="detected-crop-badge">${esc(lt("Detected plant", "Tanaman terdeteksi"))}: <b>${esc(item.detected_crop_name)}</b></span>`
        : item.clarification_needed
          ? `<span class="detected-crop-badge clarification">${esc(lt("Plant needs clarification", "Tanaman perlu diperjelas"))}</span>`
          : "";
      return `
      <article class="diary-entry concern-${attr(item.concern_level || "low")}"><div class="entry-date"><b>${esc(new Date(item.entry_date).toLocaleDateString())}</b><span>${esc(item.growth_stage || "—")}</span></div>${cropStatus}<p>${esc(item.entry_text)}</p>${item.user_question ? `<blockquote>${esc(item.user_question)}</blockquote>` : ""}${item.ai_response ? `<div class="groe-response"><b>GROE ${item.provider_status === "ai_provider" ? "AI" : ""}</b><p>${esc(item.ai_response)}</p><small>${esc(item.recommended_next_action || t("fallback"))}</small></div>` : ""}</article>`;
    }).join("");
    return `
      <main class="page diary-page"><button class="back-link" data-action="navigate" data-view="detail">← ${esc(t("back"))}</button><span class="eyebrow">TEXT-ONLY GARDEN RECORD</span><h1>${esc(t("diaryTitle"))}</h1><p class="lead">${esc(t("diaryBody"))}</p>
      ${guestMode ? `<div class="guest-diary-banner"><b>${esc(lt("No sign-in needed for testing", "Tidak perlu masuk untuk mencoba"))}</b><span>${esc(lt("Entries stay in this browser during beta. Cloud sync can be reintroduced later.", "Catatan tersimpan di browser ini selama beta. Sinkronisasi cloud dapat diaktifkan kembali nanti."))}</span></div>` : `<div class="guest-diary-banner synced"><b>${esc(lt("Synced diary", "Diary tersinkronisasi"))}</b><span>${esc(lt("This history is connected to your saved garden.", "Riwayat ini terhubung ke kebun tersimpan Anda."))}</span></div>`}
      ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
      <form class="diary-form" data-form="diary"><label class="field"><span>${esc(t("growthStage"))}</span><select data-field="diary-stage"><option value="sowing" ${state.diaryStage==="sowing"?"selected":""}>Sowing</option><option value="seedling" ${state.diaryStage==="seedling"?"selected":""}>Seedling</option><option value="vegetative" ${state.diaryStage==="vegetative"?"selected":""}>Vegetative</option><option value="flowering" ${state.diaryStage==="flowering"?"selected":""}>Flowering</option><option value="fruiting" ${state.diaryStage==="fruiting"?"selected":""}>Fruiting</option><option value="harvest" ${state.diaryStage==="harvest"?"selected":""}>Harvest</option></select></label><label class="field"><span>${esc(t("entry"))}</span><textarea data-field="diary-text" required rows="5">${esc(state.diaryText)}</textarea></label><label class="field"><span>${esc(t("question"))}</span><textarea data-field="diary-question" rows="3">${esc(state.diaryQuestion)}</textarea></label><button class="button primary" ${state.loading ? "disabled" : ""}>${esc(state.loading ? t("loading") : t("addEntry"))}</button></form>
      <section class="timeline">${entries || `<div class="empty-state"><h2>${esc(t("noEntries"))}</h2></div>`}</section>
      </main>
    `;
  }

  function authModal() {
    if (!state.showAuth) return "";
    return `
      <div class="dialog-backdrop" role="dialog" aria-modal="true"><div class="auth-dialog"><button class="dialog-close" data-action="close-auth">×</button>
        <span class="eyebrow">GROE ACCOUNT</span><h2>${esc(state.authMode === "login" ? t("loginTitle") : t("registerTitle"))}</h2><p>${esc(lt("An account is only required to save gardens and sync diary history across devices.", "Akun hanya diperlukan untuk menyimpan kebun dan menyinkronkan riwayat diary antar perangkat."))}</p>
        ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
        <form data-form="auth"><label class="field"><span>${esc(t("email"))}</span><input data-field="auth-email" type="email" required value="${attr(state.authEmail)}"></label><label class="field"><span>${esc(t("password"))}</span><input data-field="auth-password" type="password" required minlength="8" value="${attr(state.authPassword)}"></label><button class="button primary full" ${state.loading ? "disabled" : ""}>${esc(state.loading ? t("loading") : state.authMode === "login" ? t("login") : t("register"))}</button></form>
        <button class="switch-auth" data-action="switch-auth">${esc(state.authMode === "login" ? t("switchRegister") : t("switchLogin"))}</button>
      </div></div>
    `;
  }

  function errorPage() {
    return `<main class="page"><div class="empty-state"><h2>${esc(state.error || t("requestFailed"))}</h2><button class="button primary" data-action="navigate" data-view="landing">${esc(t("home"))}</button></div></main>`;
  }

  function footer() {
    return `<footer><b>GROE</b><span>Grow Resources in Omni-sustainable Environment</span><small class="build-badge">Beta build ${BUILD} · diary recognition + map truth release</small></footer>`;
  }

  function render() {
    document.documentElement.lang = state.lang;
    let body;
    if (state.view === "landing") body = landing();
    else if (state.view === "planner") body = planner();
    else if (state.view === "results") body = results();
    else if (state.view === "detail") body = detail();
    else if (state.view === "gardens") body = gardens();
    else if (state.view === "diary") body = diary();
    else body = errorPage();
    root.innerHTML = `<div class="app">${header()}${body}${cropGuideModal()}${footer()}</div>`;
  }

  async function navigate(view) {
    state.error = "";
    if (view === "planner" && state.view !== "results") {
      state.step = 1;
      state.input = defaultInput(state.lang);
      state.response = null;
      state.selected = null;
      state.savedPlan = null;
      state.readOnly = false;
      state.locationSuggestions = [];
      state.locationSearched = false;
      state.weather = null;
    }
    if (view === "gardens") {
      state.view = "gardens";
      render();
      await loadGardens();
      return;
    }
    if (view === "diary") {
      if (!state.selected) return;
      state.view = "diary";
      render();
      await loadDiary();
      return;
    }
    state.view = view;
    render();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function generate() {
    state.loading = true;
    state.error = "";
    render();
    try {
      state.input.language = state.lang;
      state.response = await api.recommendations(state.input);
      state.view = "results";
    } catch (e) {
      state.error = e.message || t("requestFailed");
    } finally {
      state.loading = false;
      render();
      window.scrollTo(0, 0);
    }
  }

  async function savePlan() {
    if (!state.selected) return;
    const gardens = readLocalGardens();
    const record = {
      id: state.savedPlan?.id || `local-${Date.now()}`,
      name: state.saveName || (state.lang === "id" ? "Kebun saya" : "My garden"),
      language: state.lang,
      planner_input: state.input,
      plan_data: state.selected,
      is_public: false,
      created_at: state.savedPlan?.created_at || new Date().toISOString(),
      storage: "browser"
    };
    const next = [record, ...gardens.filter(item => item.id !== record.id)].slice(0, 20);
    localStorage.setItem(LOCAL_GARDENS_KEY, JSON.stringify(next));
    state.savedPlan = record;
    render();
  }

  async function sharePlan() {
    if (!state.selected) return;
    const name = state.lang === "id" ? state.selected.name_id : state.selected.name_en;
    const url = state.savedPlan?.is_public ? `${location.origin}/shared/${state.savedPlan.share_slug}` : location.href;
    try {
      if (navigator.share) await navigator.share({ title: `GROE — ${name}`, text: `GROE — ${name}`, url });
      else {
        await navigator.clipboard.writeText(url);
        alert("Link copied");
      }
    } catch (_) {}
  }


  function readLocalGardens() {
    try { return JSON.parse(localStorage.getItem(LOCAL_GARDENS_KEY) || "[]"); }
    catch (_) { return []; }
  }

  async function loadGardens() {
    state.loading = true;
    state.error = "";
    render();
    state.gardens = readLocalGardens();
    state.loading = false;
    render();
  }

  async function loadDiary() {
    state.loading = true;
    state.error = "";
    render();
    state.diaryEntries = readGuestDiary();
    state.loading = false;
    render();
  }

  async function handleAuthSubmit() {
    state.loading = true;
    state.error = "";
    render();
    try {
      const tokens = state.authMode === "register"
        ? await api.register(state.authEmail, state.authPassword, state.lang)
        : await api.login(state.authEmail, state.authPassword);
      setTokens(tokens);
      state.authenticated = true;
      state.showAuth = false;
      state.authPassword = "";
      const pending = state.pendingAction;
      state.pendingAction = null;
      render();
      if (pending === "save") await savePlan();
      else if (pending === "gardens") await navigate("gardens");
    } catch (e) {
      state.error = e.message;
      state.loading = false;
      render();
      return;
    }
    state.loading = false;
    render();
  }

  async function submitDiary() {
    if (!state.selected || !state.diaryText.trim()) return;
    state.loading = true;
    state.error = "";
    render();
    try {
      const advice = await api.guestDiary({
        plan_data: state.selected,
        planner_input: state.input,
        crop: null,
        previous_entries: readGuestDiary().slice(0, 6),
        growth_stage: state.diaryStage,
        entry_text: state.diaryText.trim(),
        user_question: state.diaryQuestion.trim() || null,
        language: state.lang
      });
      const entry = {
        id: `guest-${Date.now()}`,
        entry_date: new Date().toISOString(),
        growth_stage: state.diaryStage,
        entry_text: state.diaryText.trim(),
        user_question: state.diaryQuestion.trim() || null,
        ai_response: advice.ai_response,
        concern_level: advice.concern_level,
        detected_topics: advice.detected_topics,
        recommended_next_action: advice.recommended_next_action,
        follow_up_date: advice.follow_up_date,
        provider_status: advice.provider_status,
        detected_crop_slug: advice.detected_crop_slug,
        detected_crop_name: advice.detected_crop_name,
        crop_detection_confidence: advice.crop_detection_confidence,
        crop_detection_method: advice.crop_detection_method,
        clarification_needed: advice.clarification_needed,
        clarification_options: advice.clarification_options || []
      };
      state.diaryEntries = [entry, ...readGuestDiary()];
      writeGuestDiary(state.diaryEntries);
      state.diaryText = "";
      state.diaryQuestion = "";
    } catch (e) {
      state.error = e.message;
    } finally {
      state.loading = false;
      render();
    }
  }

  async function searchLocations(query) {
    const cleaned = query.trim();
    if (cleaned.length < 3) {
      state.locationSuggestions = [];
      state.locationLoading = false;
      state.locationSearched = false;
      render();
      return;
    }
    const local = localLocationMatches(cleaned);
    state.locationSuggestions = local;
    state.locationLoading = true;
    state.locationSearched = false;
    render();
    try {
      const data = await api.locations(cleaned);
      if (state.input.location.city.trim() === cleaned) {
        const merged = [...(data.items || []), ...local];
        const seen = new Set();
        state.locationSuggestions = merged.filter(item => {
          const key = `${item.name}|${item.admin1 || ""}`.toLowerCase();
          if (seen.has(key)) return false;
          seen.add(key); return true;
        }).slice(0, 10);
        state.locationSearched = true;
      }
    } catch (_) {
      state.locationSuggestions = local;
      state.locationSearched = true;
      if (!local.length) state.error = lt("Location search is temporarily unavailable. Try a major Indonesian city.", "Pencarian lokasi sementara tidak tersedia. Coba kota besar di Indonesia.");
    } finally {
      state.locationLoading = false;
      render();
      const field = root.querySelector('[data-field="city"]');
      if (field) { field.focus(); field.setSelectionRange(field.value.length, field.value.length); }
    }
  }

  async function useBrowserLocation() {
    if (!navigator.geolocation) {
      state.error = lt("This browser does not provide location access. Type a city instead.", "Browser ini tidak menyediakan akses lokasi. Ketik nama kota saja.");
      render();
      return;
    }
    state.geolocationLoading = true;
    state.error = "";
    render();
    navigator.geolocation.getCurrentPosition(async position => {
      state.input.location = {
        city: lt("Current location", "Lokasi saat ini"),
        display_name: lt("Current browser location", "Lokasi browser saat ini"),
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        elevation_m: position.coords.altitude
      };
      state.locationSuggestions = [];
      state.locationSearched = false;
      state.geolocationLoading = false;
      await loadWeather();
    }, error => {
      state.geolocationLoading = false;
      state.error = error.code === 1
        ? lt("Location permission was declined. Type and select a city instead.", "Izin lokasi ditolak. Ketik dan pilih kota sebagai gantinya.")
        : lt("Your current location could not be read. Type and select a city instead.", "Lokasi saat ini tidak dapat dibaca. Ketik dan pilih kota sebagai gantinya.");
      render();
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 });
  }

  async function loadWeather() {
    if (state.input.location.latitude == null || state.input.location.longitude == null) return;
    state.weatherLoading = true;
    state.weather = null;
    state.error = "";
    render();
    try {
      const backendWeather = await api.weather(state.input.location);
      if (backendWeather?.provider_available) state.weather = backendWeather;
      else {
        try { state.weather = await directWeather(state.input.location); }
        catch (_) { state.weather = backendWeather; }
      }
    } catch (e) {
      try { state.weather = await directWeather(state.input.location); }
      catch (_) { state.error = lt("Live weather is unavailable. GROE will use broad climate assumptions for planning.", "Cuaca live tidak tersedia. GROE akan memakai asumsi iklim umum untuk perencanaan."); }
    } finally {
      state.weatherLoading = false;
      render();
    }
  }

  root.addEventListener("click", async event => {
    const el = event.target.closest("[data-action]");
    if (!el) return;
    const action = el.dataset.action;

    if (action === "navigate") await navigate(el.dataset.view);
    else if (action === "set-lang") {
      state.lang = el.dataset.lang;
      localStorage.setItem(LANG_KEY, state.lang);
      state.input.language = state.lang;
      if (state.saveName === "My garden" || state.saveName === "Kebun saya") state.saveName = state.lang === "id" ? "Kebun saya" : "My garden";
      render();
    }
    else if (action === "use-geolocation") await useBrowserLocation();
    else if (action === "refresh-weather") await loadWeather();
    else if (action === "select-location") {
      state.input.location = {
        city: el.dataset.name || el.dataset.display,
        display_name: el.dataset.display || el.dataset.name,
        latitude: Number(el.dataset.latitude),
        longitude: Number(el.dataset.longitude),
        elevation_m: el.dataset.elevation === "" ? null : Number(el.dataset.elevation)
      };
      state.locationSuggestions = [];
      state.locationSearched = false;
      await loadWeather();
    }
    else if (action === "open-crop-guide") { state.selectedCrop = el.dataset.slug; state.showCropGuide = true; render(); }
    else if (action === "close-crop-guide") { state.showCropGuide = false; render(); }
    else if (action === "open-auth") { state.error = ""; state.showAuth = true; render(); }
    else if (action === "close-auth") { state.error = ""; state.showAuth = false; state.pendingAction = null; render(); }
    else if (action === "switch-auth") { state.error = ""; state.authMode = state.authMode === "login" ? "register" : "login"; render(); }
    else if (action === "logout") { setTokens(null); state.authenticated = false; state.savedPlan = null; await navigate("landing"); }
    else if (action === "planner-back") {
      if (state.step === 1) await navigate("landing");
      else { state.step -= 1; state.error = ""; render(); window.scrollTo(0, 0); }
    }
    else if (action === "planner-next") {
      const area = Number(state.input.plot.length_m || 0) * Number(state.input.plot.width_m || 0);
      if (state.step === 1 && state.input.location.latitude == null) { state.error = lt("Choose a location from the dropdown first.", "Pilih lokasi dari daftar terlebih dahulu."); render(); return; }
      if (state.step === 2 && area <= 0) { state.error = t("invalid"); render(); return; }
      state.step = Math.min(5, state.step + 1); state.error = ""; render(); window.scrollTo(0, 0);
    }
    else if (action === "set-shape") { state.input.plot.shape = el.dataset.value; render(); }
    else if (action === "set-surface") { state.input.surface = el.dataset.value; render(); }
    else if (action === "set-sun") { state.input.sunlight = el.dataset.value; render(); }
    else if (action === "set-care") { state.input.care_commitment = el.dataset.value; render(); }
    else if (action === "set-goal") { state.input.primary_goal = el.dataset.value; render(); }
    else if (action === "generate") await generate();
    else if (action === "select-plan") {
      const plan = state.response?.plans.find(p => p.key === el.dataset.key);
      if (plan) {
        state.selected = plan; state.selectedCrop = plan.crops?.[0]?.slug || null; state.savedPlan = null; state.readOnly = false;
        await navigate("detail");
      }
    }
    else if (action === "select-crop") { state.selectedCrop = el.dataset.slug; state.showCropGuide = true; render(); }
    else if (action === "save-plan") await savePlan();
    else if (action === "share-plan") await sharePlan();
    else if (action === "open-diary") await navigate("diary");
    else if (action === "open-plan") {
      const p = state.gardens.find(item => item.id === el.dataset.id);
      if (p) {
        state.savedPlan = p; state.selected = p.plan_data; state.selectedCrop = p.plan_data?.crops?.[0]?.slug || null; state.input = p.planner_input || state.input; state.readOnly = false;
        await navigate("detail");
      }
    }
    else if (action === "delete-plan") {
      if (!confirm(`${t("delete")}?`)) return;
      const next = readLocalGardens().filter(item => item.id !== el.dataset.id);
      localStorage.setItem(LOCAL_GARDENS_KEY, JSON.stringify(next));
      await loadGardens();
    }
  });

  root.addEventListener("input", event => {
    const field = event.target.dataset.field;
    if (!field) return;
    const value = event.target.type === "checkbox" ? event.target.checked : event.target.value;
    if (field === "city") {
      state.input.location.city = value;
      state.input.location.display_name = "";
      state.input.location.latitude = null;
      state.input.location.longitude = null;
      state.input.location.elevation_m = null;
      state.weather = null;
      state.locationSearched = false;
      clearTimeout(locationSearchTimer);
      locationSearchTimer = setTimeout(() => searchLocations(String(value)), 350);
    }
    else if (field === "plot-length") state.input.plot.length_m = Number(value);
    else if (field === "plot-width") state.input.plot.width_m = Number(value);
    else if (field === "vertical") state.input.vertical_allowed = value;
    else if (field === "rack") state.input.tiered_rack_allowed = value;
    else if (field === "container-depth") state.input.container_depth_cm = Number(value);
    else if (field === "save-name") state.saveName = value;
    else if (field === "save-public") state.savePublic = value;
    else if (field === "auth-email") state.authEmail = value;
    else if (field === "auth-password") state.authPassword = value;
    else if (field === "diary-stage") state.diaryStage = value;
    else if (field === "diary-text") state.diaryText = value;
    else if (field === "diary-question") state.diaryQuestion = value;

    if (field === "plot-length" || field === "plot-width" || field === "container-depth") render();
  });

  root.addEventListener("change", event => {
    const field = event.target.dataset.field;
    if (field === "vertical") { state.input.vertical_allowed = event.target.checked; render(); }
    else if (field === "rack") { state.input.tiered_rack_allowed = event.target.checked; render(); }
    else if (field === "save-public") state.savePublic = event.target.checked;
    else if (field === "diary-stage") state.diaryStage = event.target.value;
  });

  root.addEventListener("submit", async event => {
    const form = event.target.dataset.form;
    if (!form) return;
    event.preventDefault();
    if (form === "auth") await handleAuthSubmit();
    else if (form === "diary") await submitDiary();
  });

  async function boot() {
    render();
    const match = location.pathname.match(/^\/shared\/([^/]+)/);
    if (match) {
      state.loading = true;
      render();
      try {
        const p = await api.shared(match[1]);
        state.savedPlan = p;
        state.selected = p.plan_data;
        state.selectedCrop = p.plan_data?.crops?.[0]?.slug || null;
        state.readOnly = true;
        state.view = "detail";
      } catch (e) {
        state.error = e.message;
      } finally {
        state.loading = false;
        render();
      }
    }
  }

  boot();
})();
