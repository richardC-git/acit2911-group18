const pathParts = window.location.pathname.split("/");
const roomId = Number(pathParts[pathParts.length - 1]);

const pageTitle = document.getElementById("page-title");
const roomInfo = document.getElementById("room-info");
const bookingDate = document.getElementById("booking-date");
const timeSlot = document.getElementById("time-slot");
const bookingForm = document.getElementById("booking-form");
const message = document.getElementById("message");

async function loadRoom() {
  const response = await fetch(`/api/rooms/${roomId}`);

  if (!response.ok) {
    pageTitle.textContent = "Room Not Found";
    roomInfo.textContent = "The selected room does not exist.";
    bookingForm.style.display = "none";
    return;
  }

  const room = await response.json();

  pageTitle.textContent = `Book Room ${room.room_number}`;
  roomInfo.textContent = `${room.campus} - ${room.description}`;
}

async function loadAvailableSlots() {
  const date = bookingDate.value;

  const response = await fetch(`/api/rooms/${roomId}/available-slots?date=${date}`);
  const slots = await response.json();

  timeSlot.innerHTML = "";

  if (!response.ok) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "Could not load available times";
    timeSlot.appendChild(option);
    return;
  }

  if (slots.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No available slots";
    timeSlot.appendChild(option);
    return;
  }

  for (const slot of slots) {
    const option = document.createElement("option");

    option.value = JSON.stringify(slot);
    option.textContent = `${slot.start_time.slice(11, 16)} - ${slot.end_time.slice(11, 16)}`;

    timeSlot.appendChild(option);
  }
}

bookingForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  if (!timeSlot.value) {
    message.textContent = "Please choose a time slot.";
    return;
  }

  const selectedSlot = JSON.parse(timeSlot.value);

  const response = await fetch("/api/bookings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      room_id: roomId,
      start_time: selectedSlot.start_time,
      end_time: selectedSlot.end_time,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    message.textContent = result.error;
    return;
  }

  message.textContent = "Booking created successfully.";

  await loadAvailableSlots();
});

bookingDate.addEventListener("change", loadAvailableSlots);

loadRoom();
loadAvailableSlots();