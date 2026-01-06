// content_inject.js
(function () {
  if (window.__smartFocusInjected) return;
  window.__smartFocusInjected = true;

  function sendVideoMeta() {
    if (!location.href.includes("youtube.com/watch")) return;

    const title =
      document.querySelector("h1 yt-formatted-string")?.innerText || "";

    const channel =
      document.querySelector("#channel-name yt-formatted-string")?.innerText || "";

    const description =
      document.querySelector("#description")?.innerText || "";

    fetch("http://127.0.0.1:5000/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: location.href,
        title: title + " " + channel + " " + description
      })
    });
  }

  // Run on load
  setTimeout(sendVideoMeta, 3000);

  // Run when URL changes (SPA)
  let lastUrl = location.href;
  setInterval(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      setTimeout(sendVideoMeta, 3000);
    }
  }, 1000);
})();
