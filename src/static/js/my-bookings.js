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

function createSectionTitle(title) {
  const heading = document.createElement("h3");
  heading.className = "booking-section-title";
  heading.textContent = title;

  bookingsList.appendChild(heading);
}

function renderBookingCard(booking, isPastBooking) {
  const card = document.createElement("article");
  card.className = "booking-card";

  const bookingDate = booking.start_time.slice(0, 10);

  let actionsHtml = "";

  if (!isPastBooking) {
    actionsHtml = `
      <div class="booking-actions">
        <button
          class="update-button"
          onclick="showUpdateForm(${booking.id}, ${booking.room_id})"
        >
          Update
        </button>

        <button
          class="delete-button"
          onclick="deleteBooking(${booking.id})"
        >
          Delete
        </button>
      </div>

      <div class="update-form" id="update-form-${booking.id}">
        <h4>Update Booking</h4>

        <label>Date</label>
        <input
          type="date"
          id="date-${booking.id}"
          value="${bookingDate}"
          onchange="loadAvailableSlots(${booking.id}, ${booking.room_id})"
        >

        <label>Available Time Slots</label>
        <select id="slot-${booking.id}">
          <option value="">Loading slots...</option>
        </select>

        <p class="form-message" id="message-${booking.id}"></p>

        <div class="update-form-actions">
          <button
            class="save-button"
            onclick="updateBooking(${booking.id}, ${booking.room_id})"
          >
            Save Update
          </button>

          <button
            class="cancel-button"
            onclick="hideUpdateForm(${booking.id})"
          >
            Cancel
          </button>
        </div>
      </div>
    `;
  }

  card.innerHTML = `
    <div class="booking-details">
      <h3>Room ${booking.room_number}</h3>

    <p><strong>Campus:</strong> ${booking.campus}</p>
    <p><strong>Start:</strong> ${formatDateTime(booking.start_time)}</p>
    <p><strong>End:</strong> ${formatDateTime(booking.end_time)}</p>

    <p>
      <strong>Status:</strong>
      ${isPastBooking ? "completed" : booking.status}
    </p>

      <p>${booking.description}</p>

      ${isPastBooking ? `
      <p class="past-label">Past booking</p>

      <div class="booking-actions">
        <button
          class="delete-button"
          onclick="deleteBooking(${booking.id})"
        >
          Remove from History
        </button>
      </div>
    ` : ""}

      ${actionsHtml}
    </div>
  `;

  bookingsList.appendChild(card);
}

function renderBookings(bookings) {
  bookingsList.innerHTML = "";

  if (bookings.length === 0) {
    renderEmptyState();
    return;
  }

  const now = new Date();

  const upcomingBookings = bookings.filter(booking =>
    new Date(booking.start_time) >= now
  );

  const pastBookings = bookings.filter(booking =>
    new Date(booking.start_time) < now
  );

  upcomingBookings.sort((a, b) => {
    return new Date(a.start_time) - new Date(b.start_time);
  });

  pastBookings.sort((a, b) => {
    return new Date(b.start_time) - new Date(a.start_time);
  });

  if (upcomingBookings.length > 0) {
    createSectionTitle("Upcoming Bookings");

    upcomingBookings.forEach(booking => {
      renderBookingCard(booking, false);
    });
  }

  if (pastBookings.length > 0) {
    createSectionTitle("Past Bookings");

    pastBookings.forEach(booking => {
      renderBookingCard(booking, true);
    });
  }
}

function showUpdateForm(bookingId, roomId) {
  const form = document.getElementById(`update-form-${bookingId}`);
  form.style.display = "block";

  loadAvailableSlots(bookingId, roomId);
}

function hideUpdateForm(bookingId) {
  const form = document.getElementById(`update-form-${bookingId}`);
  form.style.display = "none";
}

async function loadAvailableSlots(bookingId, roomId) {
  const date = document.getElementById(`date-${bookingId}`).value;
  const slotSelect = document.getElementById(`slot-${bookingId}`);
  const message = document.getElementById(`message-${bookingId}`);

  slotSelect.innerHTML = `<option value="">Loading slots...</option>`;
  message.textContent = "";
  message.className = "form-message";

  const response = await fetch(
    `/api/rooms/${roomId}/available-slots?date=${date}&exclude_booking_id=${bookingId}`
  );

  const slots = await response.json();

  slotSelect.innerHTML = "";

  if (slots.length === 0) {
    slotSelect.innerHTML = `<option value="">No available slots</option>`;
    return;
  }

  slots.forEach(slot => {
    const option = document.createElement("option");

    option.value = `${slot.start_time}|${slot.end_time}`;
    option.textContent =
      `${slot.start_time.slice(11, 16)} - ${slot.end_time.slice(11, 16)}`;

    slotSelect.appendChild(option);
  });
}

async function updateBooking(bookingId, roomId) {
  const slotSelect = document.getElementById(`slot-${bookingId}`);
  const message = document.getElementById(`message-${bookingId}`);

  if (!slotSelect.value) {
    message.textContent = "Please select an available time slot.";
    message.className = "form-message error-message";
    return;
  }

  const [startTime, endTime] = slotSelect.value.split("|");

  const response = await fetch(`/api/bookings/${bookingId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      room_id: roomId,
      start_time: startTime,
      end_time: endTime
    })
  });

  const data = await response.json();

  if (response.ok) {
    message.textContent = "Booking updated successfully.";
    message.className = "form-message success-message";

    setTimeout(() => {
      loadMyBookings();
    }, 700);
  } else {
    message.textContent = data.error || "Could not update booking.";
    message.className = "form-message error-message";
  }
}

function deleteBooking(bookingId) {
  const existingModal = document.getElementById("delete-modal");

  if (existingModal) {
    existingModal.remove();
  }

  const modal = document.createElement("div");
  modal.id = "delete-modal";

  modal.innerHTML = `
    <div class="delete-modal-content">
      <h3>Delete Booking</h3>

      <p>Are you sure you want to delete this booking?</p>

      <div class="delete-modal-buttons">
        <button class="confirm-delete-button" id="confirm-delete">
          Delete
        </button>

        <button class="cancel-delete-button" id="cancel-delete">
          Cancel
        </button>
      </div>

      <p class="form-message" id="delete-message"></p>
    </div>
  `;

  document.body.appendChild(modal);

  document
    .getElementById("cancel-delete")
    .addEventListener("click", () => {
      modal.remove();
    });

  document
    .getElementById("confirm-delete")
    .addEventListener("click", async () => {
      const message = document.getElementById("delete-message");

      const response = await fetch(`/api/bookings/${bookingId}`, {
        method: "DELETE"
      });

      if (response.ok) {
        message.textContent = "Booking deleted successfully.";
        message.className = "form-message success-message";

        setTimeout(() => {
          modal.remove();
          loadMyBookings();
        }, 700);
      } else {
        message.textContent = "Could not delete booking.";
        message.className = "form-message error-message";
      }
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