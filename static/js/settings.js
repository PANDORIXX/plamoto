document.addEventListener("DOMContentLoaded", () => {
  const droidcamRadio = document.getElementById("droidcam");
  const picamRadio = document.getElementById("picam");
  const droidcamSettings = document.getElementById("droidcam-settings");
  const picamSettings = document.getElementById("picam-settings");

  function toggleSettings() {
    droidcamSettings.classList.toggle("hidden", !droidcamRadio.checked);
    picamSettings.classList.toggle("hidden", !picamRadio.checked);
  }

  // Initialize visibility
  toggleSettings();

  // Listen for changes
  droidcamRadio.addEventListener("change", toggleSettings);
  picamRadio.addEventListener("change", toggleSettings);
});
