const today = new Date().toISOString().split("T")[0];

const roomsList = document.getElementById("rooms-list");
const roomSearch = document.getElementById("room-search");
const campusFilter = document.getElementById("campus-filter");

let allRooms = [];

async function getAvailableSlots(roomId) {
  const response = await fetch(`/api/rooms/${roomId}/available-slots?date=${today}`);
  return await response.json();
}

function roomMatchesFilters(room) {
  const searchValue = roomSearch.value.toLowerCase();
  const campusValue = campusFilter.value;

  const matchesSearch =
    room.room_number.toLowerCase().includes(searchValue) ||
    room.campus.toLowerCase().includes(searchValue) ||
    room.capacity.toLowerCase().includes(searchValue) ||
    room.features.toLowerCase().includes(searchValue) ||
    room.description.toLowerCase().includes(searchValue);

  const matchesCampus =
    campusValue === "all" ||
    room.campus.toLowerCase().includes(campusValue.toLowerCase());

  return matchesSearch && matchesCampus;
}

async function renderRooms() {
  roomsList.innerHTML = "";

  const filteredRooms = allRooms.filter(roomMatchesFilters);

  if (filteredRooms.length === 0) {
    roomsList.innerHTML = `
      <section class="no-rooms">
        <h3>No rooms found</h3>
        <p>Try changing your search or campus filter.</p>
      </section>
    `;
    return;
  }

  for (const room of filteredRooms) {
    const slots = await getAvailableSlots(room.id);

    let slotsHtml = "";

    slots.forEach(slot => {
      slotsHtml += `
        <li>
          ${slot.start_time.slice(11, 16)} -
          ${slot.end_time.slice(11, 16)}
        </li>
      `;
    });

    if (slots.length === 0) {
      slotsHtml = "<li>No available times today</li>";
    }

    const card = document.createElement("article");
    card.className = "room-card";

    card.innerHTML = `
      <div class="room-image">
        <p>Study Room</p>
      </div>

      <div class="room-details">
        <h3>Room ${room.room_number}</h3>

        <p><strong>Campus:</strong> ${room.campus}</p>
        <p><strong>Capacity:</strong> ${room.capacity}</p>
        <p><strong>Features:</strong> ${room.features}</p>

        <p>${room.description}</p>

        <div class="slots">
          <strong>Available Times Today:</strong>
          <ul>
            ${slotsHtml}
          </ul>
        </div>

        <a href="/new-booking/${room.id}" class="top-button">
          Book Room
        </a>
      </div>
    `;

    roomsList.appendChild(card);
  }
}

async function loadRooms() {
  const response = await fetch("/api/rooms");
  allRooms = await response.json();

  renderRooms();
}

roomSearch.addEventListener("input", renderRooms);
campusFilter.addEventListener("change", renderRooms);

loadRooms();