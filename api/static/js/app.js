if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("static/js/serviceWorker.js")
      .then((res) => console.log("service worker registered"))
      .catch((err) => console.log("service worker not registered", err));
  });
}

// This script toggles the active class and aria-current attribute on the nav links
document.addEventListener("DOMContentLoaded", function () {
  const navLinks = document.querySelectorAll(".nav-link");
  const currentUrl = window.location.pathname;

  navLinks.forEach((link) => {
    const linkUrl = link.getAttribute("href");
    if (linkUrl === currentUrl) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    } else {
      link.classList.remove("active");
      link.removeAttribute("aria-current");
    }
  });
});

function showOverlay(developer, note, code) {
  // Populate the overlay with content
  document.getElementById(
    "overlayTitle"
  ).textContent = `Developer: ${developer}`;
  document.getElementById(
    "overlayNote"
  ).innerHTML = `<strong>Note:</strong> ${note}`;
  document.getElementById(
    "overlayCode"
  ).innerHTML = `<strong>Code Snippet:</strong> <br>${code}`;

  // Show the overlay
  document.getElementById("diaryOverlay").style.display = "flex";
}
