const API_BASE_URL = "YOUR_API_BASE_URL"; // Replace with your actual API base URL

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

async function loadEvents() {
  const container = document.getElementById("events");
  const status = document.getElementById("status");

  try {
    const events = await apiRequest("/api/events");
    status.textContent = "";

    if (events.length === 0) {
      status.textContent = "No events available.";
      return;
    }

    for (const event of events) {
      const card = document.createElement("article");
      card.className = "event-card";

      const title = document.createElement("h3");
      title.textContent = event.title;

      const date = document.createElement("p");
      date.textContent = `Date: ${event.event_date}`;

      const location = document.createElement("p");
      location.textContent = `Location: ${event.location}`;

      const link = document.createElement("a");
      link.className = "button";
      link.textContent = "Register";
      link.href = `register.html?event_id=${event.id}`;

      card.append(title, date, location, link);
      container.appendChild(card);
    }
  } catch (error) {
    status.textContent = `Unable to load events: ${error.message}`;
  }
}

async function loadRegistration() {
  const form = document.getElementById("registration-form");
  const status = document.getElementById("status");
  const title = document.getElementById("event-title");

  const params = new URLSearchParams(window.location.search);
  const eventId = Number(params.get("event_id"));

  if (!Number.isSafeInteger(eventId) || eventId < 1) {
    title.textContent = "Invalid event";
    return;
  }

  try {
    const event = await apiRequest(`/api/events/${eventId}`);
    title.textContent = `Register for ${event.title}`;
    form.hidden = false;
  } catch (error) {
    title.textContent = "Event unavailable";
    status.textContent = error.message;
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const button = form.querySelector("button");
    button.disabled = true;
    status.textContent = "Submitting registration...";

    const registration = {
      event_id: eventId,
      name: form.elements.name.value.trim(),
      email: form.elements.email.value.trim()
    };

    try {
      const result = await apiRequest("/api/registrations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registration)
      });

      status.textContent = result.message;
      form.reset();
    } catch (error) {
      status.textContent = `Registration failed: ${error.message}`;
    } finally {
      button.disabled = false;
    }
  });
}

if (document.getElementById("events")) {
  loadEvents();
}

if (document.getElementById("registration-form")) {
  loadRegistration();
}
