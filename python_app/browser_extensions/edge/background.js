const SERVER_URL = "http://127.0.0.1:5000/check";

async function checkTab(tab) {
  if (!tab || !tab.id || !tab.url) return;

  try {
    const res = await fetch(SERVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tabId: tab.id,
        url: tab.url,
        title: tab.title || "",
        browser: "chrome"
      })
    });

    if (!res.ok) return;

    const data = await res.json();

    if (data.action === "warn_then_close") {
      chrome.tabs.sendMessage(tab.id, {
        cmd: "show_countdown",
        keyword: data.keyword,
        seconds: data.seconds || 5
      });
    }

    if (data.action === "close") {
      chrome.tabs.remove(tab.id);
    }

  } catch (e) {
    console.error("Server error", e);
  }
}

chrome.tabs.onUpdated.addListener((tabId, info, tab) => {
  if (info.status === "complete") {
    checkTab(tab);
  }
});

chrome.tabs.onActivated.addListener(async info => {
  const tab = await chrome.tabs.get(info.tabId);
  checkTab(tab);
});

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg?.cmd === "close_tab_now" && sender.tab?.id) {
    chrome.tabs.remove(sender.tab.id);
  }
});
