// ================================
// PLAMOTO Sidebar Toggle Script
// ================================

document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("sidebarToggle");
  const toggleIcon = document.getElementById("toggleIcon");
  const sidebar = document.getElementById("sidebar");

  // Open the sidebar
  function openSidebar() {
    sidebar.classList.add("show");
    toggleIcon.classList.replace("bi-list", "bi-x");
  }

  // Close the sidebar
  function closeSidebar() {
    sidebar.classList.remove("show");
    toggleIcon.classList.replace("bi-x", "bi-list");
  }

  // Toggle sidebar state
  function toggleSidebar() {
    sidebar.classList.contains("show") ? closeSidebar() : openSidebar();
  }

  // Attach event listener
  if (toggleButton) {
    toggleButton.addEventListener("click", toggleSidebar);
  }

  // Close sidebar on link click (mobile only)
  document.querySelectorAll(".sidebar a").forEach(link => {
    link.addEventListener("click", () => {
      if (window.innerWidth < 768) closeSidebar();
    });
  });
});
