const defaultState = {
  businessName: "Esquina Barber",
  district: "Boedo",
  tagline: "Cortes de barrio, turnos al toque y agenda sin vueltas.",
  whatsapp: "+54 9 11 2345 6789",
  theme: "barrio",
  font: "sans",
  layout: "poster",
};

const presets = {
  barrio: {
    businessName: "Esquina Barber",
    district: "Boedo",
    tagline: "Cortes de barrio, turnos al toque y agenda sin vueltas.",
    theme: "barrio",
    font: "sans",
    layout: "poster",
  },
  clasica: {
    businessName: "Barberia Modelo",
    district: "Palermo",
    tagline: "Reservas claras para cortes, barba y perfilado sin tanto ida y vuelta por mensaje.",
    theme: "verde",
    font: "sans",
    layout: "split",
  },
  urbana: {
    businessName: "Distrito Barber",
    district: "Villa Crespo",
    tagline: "Cortes frescos, horarios visibles y reserva directa para clientes que quieren resolver rapido.",
    theme: "noir",
    font: "mono",
    layout: "compact",
  },
  premium: {
    businessName: "Navaja Club",
    district: "Recoleta",
    tagline: "Una experiencia de barberia cuidada, con agenda simple y servicios claros desde el primer click.",
    theme: "cobre",
    font: "serif",
    layout: "editorial",
  },
};

const services = [
  {
    id: "corte",
    name: "Corte clasico",
    duration: 35,
    price: 8500,
    description: "Corte a tijera o maquina con terminacion prolija.",
  },
  {
    id: "fade",
    name: "Fade premium",
    duration: 45,
    price: 10500,
    description: "Degrade, lavado y acabado con producto.",
  },
  {
    id: "barba",
    name: "Barba y perfilado",
    duration: 30,
    price: 7200,
    description: "Perfilado con navaja, toalla caliente y aceite.",
  },
  {
    id: "combo",
    name: "Corte + barba",
    duration: 60,
    price: 15000,
    description: "Servicio completo para salir listo del local.",
  },
];

const barbers = [
  { id: "nico", name: "Nico", specialty: "Fade y tijera" },
  { id: "tomi", name: "Tomi", specialty: "Barba y perfilado" },
  { id: "lu", name: "Lu", specialty: "Cortes clasicos" },
];

const days = [
  { id: "hoy", label: "Hoy", date: "Lun 18" },
  { id: "manana", label: "Manana", date: "Mar 19" },
  { id: "miercoles", label: "Miercoles", date: "Mie 20" },
];

const availability = {
  hoy: ["10:00", "10:45", "12:15", "15:30", "17:00", "18:20"],
  manana: ["09:30", "11:00", "13:15", "16:00", "17:45", "19:00"],
  miercoles: ["10:15", "12:00", "14:30", "16:45", "18:10", "19:30"],
};

const bookedSlots = {
  hoy: ["12:15", "18:20"],
  manana: ["11:00"],
  miercoles: ["16:45"],
};

const appointments = [
  ["10:00", "Corte clasico", "Nico", "Confirmado"],
  ["10:45", "Fade premium", "Lu", "Confirmado"],
  ["12:15", "Barba", "Tomi", "Ocupado"],
  ["15:30", "Corte + barba", "Nico", "Confirmado"],
  ["17:00", "Fade premium", "Lu", "Disponible"],
  ["18:20", "Perfilado", "Tomi", "Ocupado"],
];

const state = { ...defaultState };
let selectedTime = "";

const elements = {
  businessName: document.querySelector("#business-name"),
  district: document.querySelector("#district"),
  tagline: document.querySelector("#tagline"),
  whatsapp: document.querySelector("#whatsapp"),
  font: document.querySelector("#font-style"),
  layout: document.querySelector("#layout-style"),
  profileImage: document.querySelector("#profile-image"),
  backgroundImage: document.querySelector("#background-image"),
  logoMarks: document.querySelectorAll("[data-logo-mark]"),
  businessNameTargets: document.querySelectorAll("[data-business-name]"),
  heroEyebrow: document.querySelector("#hero-eyebrow"),
  heroTagline: document.querySelector("#hero-tagline"),
  heroMedia: document.querySelector("#hero-media"),
  whatsappLink: document.querySelector("#whatsapp-link"),
  mailLink: document.querySelector("#mail-link"),
  serviceSelect: document.querySelector("#service"),
  barberSelect: document.querySelector("#barber"),
  daySelect: document.querySelector("#day"),
  timeGrid: document.querySelector("#time-grid"),
  summary: document.querySelector("#summary"),
  form: document.querySelector("#booking-form"),
  toast: document.querySelector("#toast"),
  serviceGrid: document.querySelector("#service-grid"),
  scheduleBoard: document.querySelector("#schedule-board"),
};

const formatMoney = (value) =>
  new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(value);

function initials(value) {
  const parts = value
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2);
  return (parts.map((part) => part[0]).join("") || "N").toUpperCase();
}

function cleanPhone(value) {
  return value.replace(/\D/g, "");
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("is-visible");
  window.setTimeout(() => elements.toast.classList.remove("is-visible"), 4200);
}

function persistState() {
  const payload = {
    businessName: state.businessName,
    district: state.district,
    tagline: state.tagline,
    whatsapp: state.whatsapp,
    theme: state.theme,
    font: state.font,
    layout: state.layout,
  };
  localStorage.setItem("nexora-barber-state", JSON.stringify(payload));
}

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem("nexora-barber-state") || "{}");
    Object.assign(state, defaultState, saved);
  } catch {
    Object.assign(state, defaultState);
  }
}

function syncInputs() {
  elements.businessName.value = state.businessName;
  elements.district.value = state.district;
  elements.tagline.value = state.tagline;
  elements.whatsapp.value = state.whatsapp;
  elements.font.value = state.font;
  elements.layout.value = state.layout;
  document.querySelectorAll(".swatch[data-theme]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.theme === state.theme);
  });
}

function updatePreview() {
  document.body.dataset.theme = state.theme;
  document.body.dataset.font = state.font;
  document.body.dataset.layout = state.layout;
  document.title = `${state.businessName} | Nexora`;
  elements.businessNameTargets.forEach((target) => {
    target.textContent = state.businessName;
  });
  elements.logoMarks.forEach((target) => {
    if (!target.style.backgroundImage) {
      target.textContent = initials(state.businessName);
    }
  });
  elements.heroEyebrow.textContent = `Barberia en ${state.district}`;
  elements.heroTagline.textContent = state.tagline;
  const phone = cleanPhone(state.whatsapp);
  elements.whatsappLink.href = phone ? `https://wa.me/${phone}` : "https://wa.me/";
  const subject = encodeURIComponent(`Quiero una demo para ${state.businessName}`);
  elements.mailLink.href = `mailto:nexoratecharg@gmail.com?subject=${subject}`;
  updateSummary();
}

function applyState(patch, shouldPersist = true) {
  Object.assign(state, patch);
  syncInputs();
  updatePreview();
  if (shouldPersist) persistState();
}

function fillSelect(select, items, getLabel) {
  select.innerHTML = items
    .map((item) => `<option value="${item.id}">${getLabel(item)}</option>`)
    .join("");
}

function renderServices() {
  elements.serviceGrid.innerHTML = services
    .map(
      (service) => `
        <article class="service-item">
          <h3>${service.name}</h3>
          <p>${service.description}</p>
          <div class="service-meta">
            <span>${service.duration} min</span>
            <span>${formatMoney(service.price)}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderSchedule() {
  elements.scheduleBoard.innerHTML = appointments
    .map(
      ([time, service, barber, status]) => `
        <article class="appointment">
          <strong>${time} - ${service}</strong>
          <span>${barber}</span>
          <span>${status}</span>
        </article>
      `,
    )
    .join("");
}

function renderTimes() {
  const day = elements.daySelect.value;
  const disabled = bookedSlots[day] || [];
  const times = availability[day] || [];
  selectedTime = times.find((time) => !disabled.includes(time)) || "";

  elements.timeGrid.innerHTML = times
    .map((time) => {
      const isDisabled = disabled.includes(time);
      const isSelected = time === selectedTime;
      return `
        <button
          class="time-option${isSelected ? " is-selected" : ""}"
          type="button"
          data-time="${time}"
          ${isDisabled ? "disabled" : ""}
          aria-pressed="${isSelected ? "true" : "false"}"
        >
          ${time}
        </button>
      `;
    })
    .join("");

  updateSummary();
}

function getSelectedService() {
  return services.find((service) => service.id === elements.serviceSelect.value) || services[0];
}

function getSelectedBarber() {
  return barbers.find((barber) => barber.id === elements.barberSelect.value) || barbers[0];
}

function getSelectedDay() {
  return days.find((day) => day.id === elements.daySelect.value) || days[0];
}

function updateSummary() {
  if (!elements.summary) return;
  const service = getSelectedService();
  const barber = getSelectedBarber();
  const day = getSelectedDay();
  elements.summary.innerHTML = `
    <strong>${service.name}</strong> con ${barber.name}<br>
    ${day.label} ${day.date} - ${selectedTime || "elegi horario"} - ${service.duration} min<br>
    Total estimado: ${formatMoney(service.price)}
  `;
}

function readImage(file, onLoad) {
  if (!file || !file.type.startsWith("image/")) return;
  const reader = new FileReader();
  reader.addEventListener("load", () => onLoad(reader.result));
  reader.readAsDataURL(file);
}

function setLogoImage(dataUrl) {
  elements.logoMarks.forEach((target) => {
    target.style.backgroundImage = `url("${dataUrl}")`;
    target.textContent = "";
  });
}

function clearLogoImage() {
  elements.logoMarks.forEach((target) => {
    target.style.backgroundImage = "";
    target.textContent = initials(state.businessName);
  });
}

function setupBuilder() {
  elements.businessName.addEventListener("input", (event) => {
    applyState({ businessName: event.target.value || defaultState.businessName });
  });
  elements.district.addEventListener("input", (event) => {
    applyState({ district: event.target.value || defaultState.district });
  });
  elements.tagline.addEventListener("input", (event) => {
    applyState({ tagline: event.target.value || defaultState.tagline });
  });
  elements.whatsapp.addEventListener("input", (event) => {
    applyState({ whatsapp: event.target.value });
  });
  elements.font.addEventListener("change", (event) => {
    applyState({ font: event.target.value });
  });
  elements.layout.addEventListener("change", (event) => {
    applyState({ layout: event.target.value });
  });
  document.querySelectorAll(".swatch[data-theme]").forEach((button) => {
    button.addEventListener("click", () => applyState({ theme: button.dataset.theme }));
  });
  document.querySelectorAll("[data-preset]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-preset]").forEach((option) => option.classList.remove("is-active"));
      button.classList.add("is-active");
      applyState(presets[button.dataset.preset]);
    });
  });
  elements.profileImage.addEventListener("change", (event) => {
    readImage(event.target.files[0], setLogoImage);
  });
  elements.backgroundImage.addEventListener("change", (event) => {
    readImage(event.target.files[0], (dataUrl) => {
      elements.heroMedia.style.backgroundImage = `url("${dataUrl}")`;
    });
  });
  document.querySelector("#reset-builder").addEventListener("click", () => {
    localStorage.removeItem("nexora-barber-state");
    elements.heroMedia.style.backgroundImage = "";
    elements.profileImage.value = "";
    elements.backgroundImage.value = "";
    clearLogoImage();
    document.querySelectorAll("[data-preset]").forEach((option) => option.classList.remove("is-active"));
    document.querySelector('[data-preset="barrio"]').classList.add("is-active");
    applyState(defaultState, false);
    showToast("Identidad restablecida.");
  });
  document.querySelector("#copy-summary").addEventListener("click", async () => {
    const summaryText = [
      `Barberia: ${state.businessName}`,
      `Barrio: ${state.district}`,
      `Frase: ${state.tagline}`,
      `WhatsApp: ${state.whatsapp}`,
      `Estilo: ${state.theme} / ${state.font} / ${state.layout}`,
    ].join("\n");
    try {
      await navigator.clipboard.writeText(summaryText);
      showToast("Resumen copiado.");
    } catch {
      showToast(summaryText);
    }
  });
}

function getAnchorTarget(hash) {
  if (!hash || hash === "#") return null;
  try {
    return document.querySelector(hash);
  } catch {
    return null;
  }
}

function scrollToAnchor(hash, behavior = "smooth") {
  const target = getAnchorTarget(hash);
  if (!target) return false;
  const topbar = document.querySelector(".topbar");
  const offset = (topbar ? topbar.offsetHeight : 0) + 14;
  const targetTop = target.getBoundingClientRect().top + window.scrollY - offset;
  window.scrollTo({ top: Math.max(0, targetTop), behavior });
  return true;
}

function setupNavigation() {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  const navLinks = [...document.querySelectorAll(".nav-links a")];
  const setActiveLink = (hash) => {
    navLinks.forEach((link) => {
      link.classList.toggle("is-active", link.getAttribute("href") === hash);
    });
  };

  anchorLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const hash = link.getAttribute("href");
      if (!scrollToAnchor(hash)) return;
      event.preventDefault();
      window.history.pushState(null, "", hash);
      setActiveLink(hash);
    });
  });

  if (window.location.hash) {
    setActiveLink(window.location.hash);
    window.requestAnimationFrame(() => scrollToAnchor(window.location.hash, "auto"));
  } else {
    setActiveLink("#identidad");
  }
}

function setupBooking() {
  fillSelect(elements.serviceSelect, services, (service) => `${service.name} - ${formatMoney(service.price)}`);
  fillSelect(elements.barberSelect, barbers, (barber) => `${barber.name} - ${barber.specialty}`);
  fillSelect(elements.daySelect, days, (day) => `${day.label} - ${day.date}`);

  elements.serviceSelect.addEventListener("change", updateSummary);
  elements.barberSelect.addEventListener("change", updateSummary);
  elements.daySelect.addEventListener("change", renderTimes);

  elements.timeGrid.addEventListener("click", (event) => {
    const button = event.target.closest(".time-option");
    if (!button || button.disabled) return;
    selectedTime = button.dataset.time;
    document.querySelectorAll(".time-option").forEach((option) => {
      const active = option === button;
      option.classList.toggle("is-selected", active);
      option.setAttribute("aria-pressed", String(active));
    });
    updateSummary();
  });

  elements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    const service = getSelectedService();
    const barber = getSelectedBarber();
    const day = getSelectedDay();
    showToast(
      `Reserva demo confirmada: ${service.name} con ${barber.name}, ${day.label} a las ${selectedTime}.`,
    );
  });

  renderTimes();
}

loadState();
renderServices();
renderSchedule();
setupBooking();
setupBuilder();
setupNavigation();
syncInputs();
updatePreview();
