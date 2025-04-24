function getDevices() {
  console.log("Fetching devices...");
  const statusElement = document.getElementById("status");
  statusElement.textContent = "Status: Fetching devices...";

  fetch("/devices")
    .then((response) => {
      console.log("yoyo");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log(response);
      return response.json();
    })
    .then((devices) => {
      console.log(devices);
      const select = document.getElementById("camera");
      select.innerHTML = ""; // Clear existing list

      if (!devices || devices.length === 0) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No devices found";
        select.appendChild(option);
        statusElement.textContent = "Status: No cameras found";
        return;
      }

      devices.forEach((device) => {
        const option = document.createElement("option");
        option.value = device.id;
        option.textContent = device.name || `Camera ${device.id.slice(0, 8)}`;
        select.appendChild(option);
      });

      statusElement.textContent = "Status: Devices loaded successfully";
    })
    .catch((error) => {
      console.error("Error fetching devices:", error);
      statusElement.textContent = "Status: Error fetching devices";
    });
}

function startStream() {
  document.getElementById("status").textContent = "Status: Starting stream...";
  const source = document.getElementById("camera").value;
  const fps = document.getElementById("fps").value;
  const blur = document.getElementById("blur").value;
  const background = document.getElementById("background").value;

  fetch(
    `/start?source=${source}&fps=${fps}&blur=${blur}&background=${background}`
  );
}

function stopStream() {
  document.getElementById("status").textContent = "Status: Stopping stream...";
  fetch("/stop")
    .then((response = response.json()))
    .then((data) => {
      document.getElementById("status").textContent = "Status: Stream stopped";
    });
}
