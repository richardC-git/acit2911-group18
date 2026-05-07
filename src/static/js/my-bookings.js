const bookingsList = document.getElementById("bookings-list");

function formatDateTime(dateTimeString) {
  const [date, time] = dateTimeString.split(" ");
  return `${date} at ${time}`;
}

function renderEmptyState() {
  bookingsList.innerHTML = `
    <section class="empty-card">
      <div class="empty-content">
        <p class="icon">Calendar</p>
        <h3>No bookings found</h3>
        <p>You currently do not have any room bookings.</p>
        <a href="/rooms">Book a Room</a>
      </div>
    </section>
  `;
}

function renderBookings(bookings) {
  bookingsList.innerHTML = "";

  if (bookings.length === 0) {
    renderEmptyState();
    return;
  }

  bookings.forEach(booking => {
    const card = document.createElement("article");
    card.className = "booking-card";

    card.innerHTML = `
      <div class="booking-details">
        <h3>Room ${booking.room_number}</h3>

        <p><strong>Campus:</strong> ${booking.campus}</p>
        <p><strong>Start:</strong> ${formatDateTime(booking.start_time)}</p>
        <p><strong>End:</strong> ${formatDateTime(booking.end_time)}</p>
        <p><strong>Status:</strong> ${booking.status}</p>

        <p>${booking.description}</p>
      </div>
    `;

    bookingsList.appendChild(card);
  });
}

async function loadMyBookings() {
  const response = await fetch("/api/my-bookings");

  if (!response.ok) {
    bookingsList.innerHTML = `
      <section class="empty-card">
        <div class="empty-content">
          <p class="icon">Calendar</p>
          <h3>Could not load bookings</h3>
          <p>Please try again later.</p>
        </div>
      </section>
    `;
    return;
  }

  const bookings = await response.json();

  renderBookings(bookings);
}

loadMyBookings();