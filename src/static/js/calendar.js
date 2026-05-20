const calendarTitle = document.getElementById("calendar-title");
const calendarDates = document.getElementById("calendar-dates");

const today = new Date();
const currentYear = today.getFullYear();
const currentMonth = today.getMonth();

function formatDateKey(year, month, day) {
  const monthText = String(month + 1).padStart(2, "0");
  const dayText = String(day).padStart(2, "0");

  return `${year}-${monthText}-${dayText}`;
}

function formatTime(dateTimeString) {
  return dateTimeString.slice(11, 16);
}

function getBookingsForDate(bookings, dateKey) {
  return bookings
    .filter(booking => booking.start_time.startsWith(dateKey))
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
}

async function loadBookings() {
  const response = await fetch("/api/my-bookings");

  if (!response.ok) {
    window.location.href = "/login";
    return [];
  }

  return await response.json();
}

function renderCalendar(bookings) {
  calendarDates.innerHTML = "";

  const monthName = today.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric"
  });

  calendarTitle.textContent = monthName;

  const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
  const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0);

  const startDay = firstDayOfMonth.getDay();
  const daysInMonth = lastDayOfMonth.getDate();

  const previousMonthLastDay = new Date(currentYear, currentMonth, 0).getDate();

  for (let i = startDay - 1; i >= 0; i--) {
    const dayNumber = previousMonthLastDay - i;

    const dayElement = document.createElement("div");
    dayElement.className = "calendar-day muted";
    dayElement.innerHTML = `<div class="day-number">${dayNumber}</div>`;

    calendarDates.appendChild(dayElement);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateKey = formatDateKey(currentYear, currentMonth, day);
    const dayBookings = getBookingsForDate(bookings, dateKey);

    const dayElement = document.createElement("div");
    dayElement.className = "calendar-day";

    if (
      day === today.getDate() &&
      currentMonth === today.getMonth() &&
      currentYear === today.getFullYear()
    ) {
      dayElement.classList.add("today");
    }

    let bookingsHtml = "";

    dayBookings.forEach(booking => {
    bookingsHtml += `
        <a href="/my-bookings" class="booking-pill">
        Room ${booking.room_number}
        <div class="booking-time">
            ${formatTime(booking.start_time)} - ${formatTime(booking.end_time)}
        </div>
        </a>
    `;
    });

    dayElement.innerHTML = `
      <div class="day-number">${day}</div>
      ${bookingsHtml}
    `;

    calendarDates.appendChild(dayElement);
  }

  const totalCells = calendarDates.children.length;
  const remainingCells = 42 - totalCells;

  for (let day = 1; day <= remainingCells; day++) {
    const dayElement = document.createElement("div");
    dayElement.className = "calendar-day muted";
    dayElement.innerHTML = `<div class="day-number">${day}</div>`;

    calendarDates.appendChild(dayElement);
  }
}

async function loadCalendar() {
  const bookings = await loadBookings();
  renderCalendar(bookings);
}

loadCalendar();