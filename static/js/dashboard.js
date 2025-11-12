document.addEventListener("DOMContentLoaded", () => {
  const toggleSwitch = document.getElementById("backgroundCaptureSwitch");
  const progressBar = document.getElementById("background_capture_progress");
  const progressText = document.getElementById("background_capture_text");
  const latestImg = document.getElementById("latest-image");

  let countdown = 0;
  let intervalTotal = 0;

  const updateLatestImage = () => {
    fetch('/latest_image')
      .then(res => res.json())
      .then(data => {
        if (data.url && latestImg.src !== data.url) {
          latestImg.src = data.url + '?t=' + new Date().getTime();
        }
      })
      .catch(err => console.error('Error fetching latest image:', err));
  };

  const updateStatus = () => {
    fetch("/background_capture_status")
      .then(res => res.json())
      .then(data => {
        toggleSwitch.checked = !!data.active;
        if (data.active) {
          intervalTotal = data.next_in * 60;
          countdown = 0;
          progressBar.classList.replace("bg-custom-inactive", "bg-custom-active");
        } else {
          intervalTotal = 0;
          countdown = 0;
          progressBar.classList.replace("bg-custom-active", "bg-custom-inactive");
          progressBar.style.width = "0%";
          progressText.innerText = "";
        }
      })
      .catch(err => console.error("Failed to fetch background capture status:", err));
  };

  const updateProgress = () => {
    if (intervalTotal > 0) {
      countdown++;
      const pct = Math.min((countdown / intervalTotal) * 100, 100);
      progressBar.style.width = pct + "%";

      const remainingSeconds = Math.max(intervalTotal - countdown, 0);
      const remainingMinutes = Math.ceil(remainingSeconds / 60);
      progressText.innerText = `${remainingMinutes} min verbleiben`;
    } else {
      progressBar.style.width = "0%";
      progressText.innerText = "";
    }
  };

  toggleSwitch.addEventListener("change", () => {
    const isActive = toggleSwitch.checked;

    fetch("/toggle_background_capture", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        toggleSwitch.checked = !!data.active;
        intervalTotal = data.next_in ? data.next_in * 60 : 0;
        countdown = 0;
        progressBar.classList.toggle("bg-custom-active", data.active);
        progressBar.classList.toggle("bg-custom-inactive", !data.active);
      })
      .catch(err => {
        console.error("Error toggling background capture:", err);
        toggleSwitch.checked = !isActive;
      });
  });

  updateStatus();
  updateLatestImage();

  setInterval(updateStatus, 60000);
  setInterval(updateLatestImage, 5000);
  setInterval(updateProgress, 1000);
});
