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

const formatMoney = (value) =>
  new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(value);

const serviceSelect = document.querySelector("#service");
const barberSelect = document.querySelector("#barber");
const daySelect = document.querySelector("#day");
const timeGrid = document.querySelector("#time-grid");
const summary = document.querySelector("#summary");
const form = document.querySelector("#booking-form");
const toast = document.querySelector("#toast");
const serviceGrid = document.querySelector("#service-grid");
const scheduleBoard = document.querySelector("#schedule-board");

let selectedTime = "";

function fillSelect(select, items, getLabel) {
  select.innerHTML = items
    .map((item) => `<option value="${item.id}">${getLabel(item)}</option>`)
    .join("");
}

function renderServices() {
  serviceGrid.innerHTML = services
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
  scheduleBoard.innerHTML = appointments
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
  const day = daySelect.value;
  const disabled = bookedSlots[day] || [];
  const times = availability[day] || [];
  selectedTime = times.find((time) => !disabled.includes(time)) || "";

  timeGrid.innerHTML = times
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
  return services.find((service) => service.id === serviceSelect.value) || services[0];
}

function getSelectedBarber() {
  return barbers.find((barber) => barber.id === barberSelect.value) || barbers[0];
}

function getSelectedDay() {
  return days.find((day) => day.id === daySelect.value) || days[0];
}

function updateSummary() {
  const service = getSelectedService();
  const barber = getSelectedBarber();
  const day = getSelectedDay();
  summary.innerHTML = `
    <strong>${service.name}</strong> con ${barber.name}<br>
    ${day.label} ${day.date} - ${selectedTime || "elegi horario"} - ${service.duration} min<br>
    Total estimado: ${formatMoney(service.price)}
  `;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("is-visible");
  window.setTimeout(() => toast.classList.remove("is-visible"), 4200);
}

function setupBooking() {
  fillSelect(serviceSelect, services, (service) => `${service.name} - ${formatMoney(service.price)}`);
  fillSelect(barberSelect, barbers, (barber) => `${barber.name} - ${barber.specialty}`);
  fillSelect(daySelect, days, (day) => `${day.label} - ${day.date}`);

  serviceSelect.addEventListener("change", updateSummary);
  barberSelect.addEventListener("change", updateSummary);
  daySelect.addEventListener("change", renderTimes);

  timeGrid.addEventListener("click", (event) => {
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

  form.addEventListener("submit", (event) => {
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

renderServices();
renderSchedule();
setupBooking();
