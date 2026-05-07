
fetch("/api/rooms")
  .then(response => response.json())
  .then(rooms => {
    const roomsList = document.getElementById("rooms-list");

    rooms.forEach(room => {
      fetch(`/api/rooms/${room.id}/available-slots`)
        .then(response => response.json())
        .then(slots => {
          let slotsHtml = "";

          slots.forEach(slot => {
            slotsHtml += `
              <li>
                ${slot.start_time.slice(11, 16)} -
                ${slot.end_time.slice(11, 16)}
              </li>
            `;
          });

          const card = document.createElement("article");
          card.className = "room-card";

          card.innerHTML = `
            <div class="room-image">
              <p>Study Room</p>
            </div>

            <div class="room-details">
              <h3>Room ${room.room_number}</h3>

              <p><strong>Campus:</strong> ${room.campus}</p>

              <p>${room.description}</p>

              <div class="slots">
                <strong>Available Times:</strong>
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
        });
    });
  });