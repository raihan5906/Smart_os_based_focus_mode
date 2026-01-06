(function () {
  if (window.__SMART_FOCUS_POPUP__) return;
  window.__SMART_FOCUS_POPUP__ = true;

  let popup = null;
  let timerId = null;

  function removePopup() {
    if (popup) popup.remove();
    popup = null;
    if (timerId) clearInterval(timerId);
    timerId = null;
  }

  function showCountdown(site, seconds) {
    removePopup();

    popup = document.createElement("div");
    popup.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 460px;
      background: white;
      color: black;
      border: 1px solid #d0d0d0;
      border-radius: 6px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.25);
      padding: 18px;
      font-family: Segoe UI, Arial, sans-serif;
      z-index: 2147483647;
      text-align: left;
    `;

    const title = document.createElement("div");
    title.style.fontWeight = "600";
    title.style.marginBottom = "8px";
    title.textContent = site;

    const counter = document.createElement("div");
    counter.style.fontSize = "14px";

    popup.append(title, counter);
    document.body.appendChild(popup);

    let remaining = seconds;
    counter.textContent =
      `closing by Smart OS-Based Focus Manager in ${remaining} seconds`;

    timerId = setInterval(() => {
      remaining--;
      if (remaining <= 0) {
        clearInterval(timerId);
        chrome.runtime.sendMessage({ cmd: "close_tab_now" });
        removePopup();
      } else {
        counter.textContent =
          `closing by Smart OS-Based Focus Manager in ${remaining} seconds`;
      }
    }, 1000);
  }

  chrome.runtime.onMessage.addListener((msg) => {
    if (msg?.cmd === "show_countdown") {
      const siteName =
        msg.keyword ||
        (location.hostname ? location.hostname.replace("www.", "") : "This site");

      showCountdown(siteName, msg.seconds || 5);
    }
  });
})();
