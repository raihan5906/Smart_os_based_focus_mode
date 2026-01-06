(async function() {
    function getMetadata() {
        return {
            url: window.location.href,
            title: document.title,
            channel: document.querySelector("#upload-info #channel-name")?.innerText || "",
            description: document.querySelector("#description-inner")?.innerText || ""
        };
    }

    async function checkTab() {
        try {
            const response = await fetch("http://127.0.0.1:5000/check", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(getMetadata())
            });
            const data = await response.json();

            if (data.action === "warn_then_close") {
                showOverlay(data.seconds, data.reason);
            }
        } catch (e) { /* Server might be offline */ }
    }

    function showOverlay(seconds, reason) {
        if (document.getElementById("focus-guard-overlay")) return;
        const div = document.createElement("div");
        div.id = "focus-guard-overlay";
        div.style = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:999999;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:sans-serif;";
        div.innerHTML = `<h1>Focus Alert</h1><p>${reason}</p><h2 id='fg-timer'>Closing in ${seconds}s</h2>`;
        document.body.appendChild(div);

        const int = setInterval(() => {
            seconds--;
            document.getElementById("fg-timer").innerText = `Closing in ${seconds}s`;
            if (seconds <= 0) {
                clearInterval(int);
                chrome.runtime.sendMessage({action: "close_tab"}); // Handled by background or self-close
                window.close();
            }
        }, 1000);
    }

    checkTab();
    // Re-check on YouTube page transitions
    window.addEventListener("yt-navigate-finish", checkTab);
})();