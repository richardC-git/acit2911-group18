async function loadDashboard() {
  const welcomeName = document.getElementById("welcome-name");

  const sessionResponse = await fetch("/api/session");
  const sessionData = await sessionResponse.json();

  if (sessionData.logged_in && sessionData.user_name) {
    welcomeName.textContent = sessionData.user_name;
  }

  const roomsResponse = await fetch("/api/rooms");
  const rooms = await roomsResponse.json();

  const bookingsResponse = await fetch("/api/my-bookings");
  const bookings = await bookingsResponse.json();

  bookings.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

  const totalRoomsElement = document.getElementById("total-rooms");
  const todayBookingsElement = document.getElementById("today-bookings");
  const upcomingBookingsCountElement = document.getElementById("upcoming-bookings-count");
  const currentDateElement = document.getElementById("current-date");
  const nextBookingText = document.getElementById("next-booking-text");

  totalRoomsElement.textContent = rooms.length;

  const today = new Date().toISOString().split("T")[0];
  const now = new Date();

  const todaysBookings = bookings.filter(booking =>
    booking.start_time.startsWith(today)
  );

  const upcomingBookings = bookings.filter(booking =>
    new Date(booking.start_time) >= now
  );

  todayBookingsElement.textContent = todaysBookings.length;
  upcomingBookingsCountElement.textContent = upcomingBookings.length;

  const formattedDate = new Date().toLocaleDateString("en-CA", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  currentDateElement.textContent = formattedDate;

  if (upcomingBookings.length > 0) {
    const nextBooking = upcomingBookings[0];

    nextBookingText.textContent =
      `Room ${nextBooking.room_number} from ${nextBooking.start_time} to ${nextBooking.end_time}`;
  } else {
    nextBookingText.textContent = "You have no upcoming bookings.";
  }

  document.getElementById("loading-state").style.display = "none";

  renderUpcomingBookings(upcomingBookings);
}

function renderUpcomingBookings(bookings) {
  const container = document.getElementById("bookings-container");
  const emptyState = document.getElementById("empty-state");

  const oldList = document.querySelector(".bookings-list");

  if (oldList) {
    oldList.remove();
  }

  if (bookings.length === 0) {
    emptyState.style.display = "block";
    return;
  }

  emptyState.style.display = "none";

  const bookingsList = document.createElement("div");
  bookingsList.className = "bookings-list";

  bookings.forEach(booking => {
    const bookingElement = document.createElement("div");
    bookingElement.className = "booking-item";

    bookingElement.innerHTML = `
      <a href="/my-bookings" class="booking-link">
        <div class="booking-room">
          Room ${booking.room_number}
        </div>

        <div class="booking-time">
          ${booking.start_time} → ${booking.end_time}
        </div>
      </a>
    `;

    bookingsList.appendChild(bookingElement);
  });

  container.appendChild(bookingsList);
}

loadDashboard();