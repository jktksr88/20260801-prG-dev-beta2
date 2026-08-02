(() => {
  "use strict";

  const API = "/api/v1";
  const TOKEN_KEY = "groe.tokens";
  const LANG_KEY = "groe.language";
  const root = document.getElementById("root");

  const copy = {
    en: {
      tagline: "Grow what fits.",
      navPlan: "Plan a garden", navPlants: "50 plants", navGardens: "My gardens", signIn: "Sign in", signOut: "Sign out",
      heroEyebrow: "A beginner-first edible garden planner",
      heroTitleA: "Turn your space into", heroTitleB: "something you can grow.",
      heroBody: "Tell GROE about your space, sunlight and care routine. It checks what is physically realistic and creates three different plans.",
      start: "Start planning", explore: "Explore the plant library", noAccount: "No account needed to receive recommendations.",
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
      gardensTitle: "Your saved gardens", noGardens: "You have not saved a garden yet.", open: "Open", delete: "Delete",
      plantsTitle: "50 edible crop profiles", plantsBody: "Curated for the Indonesian beta. Fields still needing agronomist review are labelled.", search: "Search plants",
      diaryTitle: "GROE Diary", diaryBody: "Record what changed and ask a question. Entries are text only.", growthStage: "Growth stage", entry: "What happened?", question: "Question for GROE (optional)", addEntry: "Save diary entry", noEntries: "No diary entries yet.", fallback: "Deterministic fallback guidance",
      publicPlan: "Read-only shared plan", home: "Home", retry: "Try again", close: "Close", loading: "Loading…",
      authRequired: "Create an account or sign in to save plans and use the diary.",
      invalid: "Please enter valid dimensions before continuing.",
      requestFailed: "Something went wrong. Please try again."
    },
    id: {
      tagline: "Tanam yang sesuai.",
      navPlan: "Buat rencana", navPlants: "50 tanaman", navGardens: "Kebun saya", signIn: "Masuk", signOut: "Keluar",
      heroEyebrow: "Perencana kebun pangan untuk pemula",
      heroTitleA: "Ubah ruangmu menjadi", heroTitleB: "sesuatu yang bisa ditanam.",
      heroBody: "Ceritakan ruang, sinar matahari, dan rutinitas perawatanmu. GROE memeriksa apa yang realistis lalu membuat tiga rencana berbeda.",
      start: "Mulai merencanakan", explore: "Lihat pustaka tanaman", noAccount: "Tidak perlu akun untuk menerima rekomendasi.",
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
      mapTitle: "Tata letak kebun berskala", save: "Simpan kebun ini", saved: "Kebun tersimpan", share: "Bagikan rencana", diary: "Buka diary",
      selectedBecause: "Alasan GROE memilihnya", adjustments: "Penyesuaian", warning: "Catatan penting", verification: "Status data",
      loginTitle: "Simpan kebun GROE", registerTitle: "Buat akun GROE", email: "Email", password: "Kata sandi", login: "Masuk", register: "Buat akun", switchRegister: "Belum punya akun? Buat akun", switchLogin: "Sudah punya akun? Masuk",
      gardensTitle: "Kebun tersimpan", noGardens: "Belum ada kebun yang disimpan.", open: "Buka", delete: "Hapus",
      plantsTitle: "50 profil tanaman pangan", plantsBody: "Dikurasi untuk beta Indonesia. Data yang masih perlu tinjauan agronom ditandai.", search: "Cari tanaman",
      diaryTitle: "GROE Diary", diaryBody: "Catat perubahan dan ajukan pertanyaan. Diary hanya berupa teks.", growthStage: "Tahap pertumbuhan", entry: "Apa yang terjadi?", question: "Pertanyaan untuk GROE (opsional)", addEntry: "Simpan catatan", noEntries: "Belum ada catatan diary.", fallback: "Panduan fallback deterministik",
      publicPlan: "Rencana publik hanya-baca", home: "Beranda", retry: "Coba lagi", close: "Tutup", loading: "Memuat…",
      authRequired: "Buat akun atau masuk untuk menyimpan rencana dan menggunakan diary.",
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
    plants: [],
    plantSearch: "",
    gardens: [],
    diaryEntries: [],
    diaryStage: "seedling",
    diaryText: "",
    diaryQuestion: ""
  };

  state.input = defaultInput(state.lang);
  state.saveName = state.lang === "id" ? "Kebun saya" : "My garden";

  function defaultInput(lang) {
    return {
      location: { city: "Jakarta" },
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
    plants: () => request("/plants?page_size=50"),
    shared: slug => request(`/public/plans/${encodeURIComponent(slug)}`),
    diary: planId => request(`/diary?plan_id=${encodeURIComponent(planId)}`),
    addDiary: payload => request("/diary", { method: "POST", body: JSON.stringify(payload) })
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
          <button data-action="navigate" data-view="plants">${esc(t("navPlants"))}</button>
          <button data-action="navigate" data-view="gardens">${esc(t("navGardens"))}</button>
        </nav>
        <div class="header-actions">
          <div class="lang-switch" aria-label="Language">
            <button class="${state.lang === "en" ? "active" : ""}" data-action="set-lang" data-lang="en">EN</button>
            <button class="${state.lang === "id" ? "active" : ""}" data-action="set-lang" data-lang="id">ID</button>
          </div>
          <button class="button small secondary" data-action="${state.authenticated ? "logout" : "open-auth"}">${esc(state.authenticated ? t("signOut") : t("signIn"))}</button>
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
              <button class="text-button" data-action="navigate" data-view="plants">${esc(t("explore"))}</button>
            </div>
            <small class="quiet-proof">✓ ${esc(t("noAccount"))}</small>
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
      content = `
        <span class="eyebrow">GROE / 01</span><h1>${esc(t("cityTitle"))}</h1><p class="lead">${esc(t("cityBody"))}</p>
        <label class="field hero-field"><span>${esc(t("city"))}</span><input data-field="city" value="${attr(input.location.city)}" placeholder="Jakarta, Bandung, Surabaya…"></label>
        <div class="context-card"><span class="context-icon">◎</span><div><b>${esc(input.location.city || "Indonesia")}</b><small>Broad climate context with weather fallback</small></div></div>
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

    const canContinue = state.step !== 2 || area > 0;
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

  function plotMap(plan) {
    const layout = plan.layout || {};
    const boundary = layout.plot_boundary || [[0,0],[2,0],[2,1.5],[0,1.5]];
    const xs = boundary.map(p => Number(p[0]));
    const ys = boundary.map(p => Number(p[1]));
    const maxX = Math.max(...xs, 1);
    const maxY = Math.max(...ys, 1);
    const pad = 0.15;
    const points = boundary.map(p => `${Number(p[0]) + pad},${Number(p[1]) + pad}`).join(" ");
    const placements = (layout.placements || []).map((p, i) => {
      const active = state.selectedCrop === p.slug;
      const x = Number(p.x_m || 0) + pad;
      const y = Number(p.y_m || 0) + pad;
      const w = Math.max(.12, Number(p.width_m || .2));
      const h = Math.max(.12, Number(p.height_m || .2));
      const label = state.lang === "id" ? p.name_id : p.name_en;
      const fill = ["#7fa678","#d6a84f","#7c78a0","#6e9bad","#d17d62"][i % 5];
      return `
        <g class="placement ${active ? "active" : ""}" data-action="select-crop" data-slug="${attr(p.slug)}">
          <rect x="${x}" y="${y}" width="${w}" height="${h}" rx=".08" fill="${fill}" stroke="#f8f3e8" stroke-width="${active ? ".055" : ".025"}"></rect>
          <circle cx="${x+w/2}" cy="${y+h/2}" r="${Math.min(w,h)*.22}" fill="rgba(255,255,255,.5)"></circle>
          ${w > .32 && h > .22 ? `<text x="${x+w/2}" y="${y+h/2+.025}" text-anchor="middle" font-size=".08" fill="#173128" font-weight="700">${esc(label.slice(0,9))}</text>` : ""}
          ${p.trellis ? `<line x1="${x}" y1="${y}" x2="${x+w}" y2="${y}" stroke="#f4d35e" stroke-width=".035" stroke-dasharray=".06 .04"></line>` : ""}
        </g>
      `;
    }).join("");
    return `
      <div class="map-wrap"><svg class="plot-svg" viewBox="0 0 ${maxX + pad * 2} ${maxY + pad * 2}" role="img" aria-label="Scaled garden layout">
        <defs><pattern id="soil" width=".12" height=".12" patternUnits="userSpaceOnUse"><rect width=".12" height=".12" fill="#755c45"></rect><circle cx=".03" cy=".04" r=".008" fill="#9a7b5d"></circle></pattern></defs>
        <polygon points="${points}" fill="url(#soil)" stroke="#4b392b" stroke-width=".06" stroke-linejoin="round"></polygon>
        ${placements}
        <text x="${pad}" y="${maxY + pad * 2 - .04}" font-size=".08" fill="#fff">1 unit = 1 metre</text>
      </svg></div>
    `;
  }

  function detail() {
    const plan = state.selected;
    if (!plan) return errorPage();
    if (!state.selectedCrop && plan.crops?.length) state.selectedCrop = plan.crops[0].slug;
    const crop = (plan.crops || []).find(c => c.slug === state.selectedCrop) || (plan.crops || [])[0];
    const cropButtons = (plan.crops || []).map((c, i) => {
      const label = state.lang === "id" ? c.name_id : c.name_en;
      return `<button class="${state.selectedCrop === c.slug ? "active" : ""}" data-action="select-crop" data-slug="${attr(c.slug)}"><span class="crop-symbol c${i%5}">${esc(label.slice(0,1))}</span><span><b>${esc(label)}</b><small>${esc(c.quantity)} × · ${Math.round(c.score)}%</small></span></button>`;
    }).join("");
    let cropDetail = "";
    if (crop) {
      cropDetail = `
        <div class="crop-detail"><span class="eyebrow">PLANT PROFILE</span><h2>${esc(state.lang === "id" ? crop.name_id : crop.name_en)}</h2><em>${esc(crop.scientific_name)}</em>
        <div class="crop-chips"><span>${esc(crop.category)}</span><span>${esc(crop.classification)}</span><span>${esc(crop.verification_status)}</span></div>
        <h4>${esc(t("selectedBecause"))}</h4><p>${esc((crop.reason_codes || []).join(" · ") || plan.why_it_fits)}</p>
        ${crop.adjustment_codes?.length ? `<h4>${esc(t("adjustments"))}</h4><p>${esc(crop.adjustment_codes.join(" · "))}</p>` : ""}
        ${crop.hard_constraints?.length ? `<h4>${esc(t("warning"))}</h4><p>${esc(crop.hard_constraints.join(" · "))}</p>` : ""}
        </div>
      `;
    }
    return `
      <main class="page detail-page">
        <button class="back-link" data-action="navigate" data-view="${state.readOnly ? "landing" : "results"}">← ${esc(state.readOnly ? t("home") : t("back"))}</button>
        ${state.readOnly ? `<div class="public-banner">${esc(t("publicPlan"))}</div>` : ""}
        <header class="detail-header">
          <div><span class="eyebrow">SELECTED PLAN</span><h1>${esc(state.lang === "id" ? plan.name_id : plan.name_en)}</h1><p>${esc(state.lang === "id" ? plan.proposition_id : plan.proposition_en)}</p></div>
          <div class="detail-actions">
            ${state.readOnly ? "" : `<button class="button primary" data-action="save-plan">${esc(state.savedPlan ? t("saved") : t("save"))}</button>`}
            <button class="button secondary" data-action="share-plan">${esc(t("share"))}</button>
            ${state.savedPlan ? `<button class="button secondary" data-action="open-diary">${esc(t("diary"))}</button>` : ""}
          </div>
        </header>
        ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
        <section class="layout-grid">
          <div class="layout-panel">
            <div class="panel-title"><div><span class="eyebrow">2D PLAN</span><h2>${esc(t("mapTitle"))}</h2></div><div class="map-legend"><span><i class="legend-plant"></i>Plant footprint</span><span><i class="legend-trellis"></i>Trellis</span></div></div>
            ${plotMap(plan)}
            <div class="layout-stats"><div><b>${plan.layout ? Number(plan.layout.plot_area_m2).toFixed(1) : "—"} m²</b><small>${esc(t("area"))}</small></div><div><b>${esc(plan.total_plants)}</b><small>${esc(t("plants"))}</small></div><div><b>${esc(plan.containers_required)}</b><small>containers</small></div><div><b>${esc(plan.weekly_care_minutes)} min</b><small>${esc(t("care"))}</small></div></div>
          </div>
          <aside class="crop-panel"><div class="crop-list">${cropButtons}</div>${cropDetail}</aside>
        </section>
        ${!state.readOnly && !state.savedPlan ? `<section class="save-strip"><label class="field"><span>Garden name</span><input data-field="save-name" value="${attr(state.saveName)}"></label><label class="inline-check"><input data-field="save-public" type="checkbox" ${state.savePublic ? "checked" : ""}> Create a read-only share link</label></section>` : ""}
      </main>
    `;
  }

  function plants() {
    const q = state.plantSearch.toLowerCase();
    const filtered = state.plants.filter(p => `${p.name_en || ""} ${p.name_id || ""} ${p.scientific_name || ""}`.toLowerCase().includes(q));
    const cards = filtered.map((p, i) => {
      const params = p.parameters || {};
      return `<article class="plant-tile"><div class="botanical-symbol b${i%6}">✣</div><small>${esc(p.category)}</small><h3>${esc(state.lang === "id" ? p.name_id : p.name_en)}</h3><em>${esc(p.scientific_name)}</em><div class="tile-meta"><span>${esc(params.minimum_direct_sun_hours ?? "—")} h sun</span><span>${esc(params.days_to_first_harvest_min ?? "—")} d</span><span>${esc(params.difficulty_level ?? "—")}</span></div><p class="review-label">${esc(p.verification_status || "provisionally_sourced")}</p></article>`;
    }).join("");
    return `
      <main class="page">
        <button class="back-link" data-action="navigate" data-view="landing">← ${esc(t("home"))}</button>
        <header class="catalog-head"><div><span class="eyebrow">GROE PLANT LIBRARY</span><h1>${esc(t("plantsTitle"))}</h1><p>${esc(t("plantsBody"))}</p></div><label class="search-box">⌕<input data-field="plant-search" placeholder="${attr(t("search"))}" value="${attr(state.plantSearch)}"></label></header>
        ${state.error ? `<div class="alert error">${esc(state.error)}</div>` : ""}
        ${state.loading ? `<div class="loading-card"><div class="spinner"></div><p>${esc(t("loading"))}</p></div>` : `<div class="catalog-grid">${cards}</div>`}
      </main>
    `;
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
    const entries = state.diaryEntries.map(item => `
      <article class="diary-entry concern-${attr(item.concern_level || "low")}"><div class="entry-date"><b>${esc(new Date(item.entry_date).toLocaleDateString())}</b><span>${esc(item.growth_stage || "—")}</span></div><p>${esc(item.entry_text)}</p>${item.user_question ? `<blockquote>${esc(item.user_question)}</blockquote>` : ""}${item.ai_response ? `<div class="groe-response"><b>GROE</b><p>${esc(item.ai_response)}</p><small>${esc(item.recommended_next_action || t("fallback"))}</small></div>` : ""}</article>
    `).join("");
    return `
      <main class="page diary-page"><button class="back-link" data-action="navigate" data-view="detail">← ${esc(t("back"))}</button><span class="eyebrow">TEXT-ONLY GARDEN RECORD</span><h1>${esc(t("diaryTitle"))}</h1><p class="lead">${esc(t("diaryBody"))}</p>
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
        <span class="eyebrow">GROE ACCOUNT</span><h2>${esc(state.authMode === "login" ? t("loginTitle") : t("registerTitle"))}</h2><p>${esc(t("authRequired"))}</p>
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
    return `<footer><b>GROE</b><span>Grow Resources in Omni-sustainable Environment</span></footer>`;
  }

  function render() {
    document.documentElement.lang = state.lang;
    let body;
    if (state.view === "landing") body = landing();
    else if (state.view === "planner") body = planner();
    else if (state.view === "results") body = results();
    else if (state.view === "detail") body = detail();
    else if (state.view === "plants") body = plants();
    else if (state.view === "gardens") body = gardens();
    else if (state.view === "diary") body = diary();
    else body = errorPage();
    root.innerHTML = `<div class="app">${header()}${body}${authModal()}${footer()}</div>`;
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
    }
    if (view === "gardens") {
      if (!state.authenticated) {
        state.showAuth = true;
        state.pendingAction = "gardens";
        render();
        return;
      }
      state.view = "gardens";
      render();
      await loadGardens();
      return;
    }
    if (view === "plants") {
      state.view = "plants";
      render();
      if (!state.plants.length) await loadPlants();
      return;
    }
    if (view === "diary") {
      if (!state.savedPlan) return;
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
    if (!state.authenticated) {
      state.showAuth = true;
      state.pendingAction = "save";
      render();
      return;
    }
    if (!state.selected) return;
    state.loading = true;
    state.error = "";
    render();
    try {
      state.savedPlan = await api.savePlan({
        name: state.saveName || (state.lang === "id" ? "Kebun saya" : "My garden"),
        language: state.lang,
        planner_input: state.input,
        plan_data: state.selected,
        is_public: state.savePublic
      });
    } catch (e) {
      state.error = e.message;
    } finally {
      state.loading = false;
      render();
    }
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

  async function loadPlants() {
    state.loading = true;
    state.error = "";
    render();
    try {
      const data = await api.plants();
      state.plants = data.items || [];
    } catch (e) {
      state.error = e.message;
    } finally {
      state.loading = false;
      render();
    }
  }

  async function loadGardens() {
    state.loading = true;
    state.error = "";
    render();
    try {
      const data = await api.plans();
      state.gardens = data.items || [];
    } catch (e) {
      state.error = e.message;
    } finally {
      state.loading = false;
      render();
    }
  }

  async function loadDiary() {
    state.loading = true;
    state.error = "";
    render();
    try {
      state.diaryEntries = await api.diary(state.savedPlan.id);
    } catch (e) {
      state.error = e.message;
    } finally {
      state.loading = false;
      render();
    }
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
    if (!state.savedPlan || !state.diaryText.trim()) return;
    state.loading = true;
    state.error = "";
    render();
    try {
      await api.addDiary({
        plan_id: state.savedPlan.id,
        crop_profile_id: null,
        map_zone: null,
        growth_stage: state.diaryStage,
        entry_text: state.diaryText.trim(),
        user_question: state.diaryQuestion.trim() || null,
        language: state.lang
      });
      state.diaryText = "";
      state.diaryQuestion = "";
      state.diaryEntries = await api.diary(state.savedPlan.id);
    } catch (e) {
      state.error = e.message;
    } finally {
      state.loading = false;
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
    else if (action === "select-crop") { state.selectedCrop = el.dataset.slug; render(); }
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
      try { await api.deletePlan(el.dataset.id); await loadGardens(); }
      catch (e) { state.error = e.message; render(); }
    }
  });

  root.addEventListener("input", event => {
    const field = event.target.dataset.field;
    if (!field) return;
    const value = event.target.type === "checkbox" ? event.target.checked : event.target.value;
    if (field === "city") state.input.location.city = value;
    else if (field === "plot-length") state.input.plot.length_m = Number(value);
    else if (field === "plot-width") state.input.plot.width_m = Number(value);
    else if (field === "vertical") state.input.vertical_allowed = value;
    else if (field === "rack") state.input.tiered_rack_allowed = value;
    else if (field === "container-depth") state.input.container_depth_cm = Number(value);
    else if (field === "save-name") state.saveName = value;
    else if (field === "save-public") state.savePublic = value;
    else if (field === "plant-search") { state.plantSearch = value; render(); }
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
