// pod_alert_extension/background.js - Firefox Version
console.log("Background Script v5 (Auto-Search Enabled) Loaded for Firefox.");

let lastSniffedSwordfishEvent = {
    eventId: null,
    timestamp: 0,
    url: null // Store the URL for debugging
};

// Listener for the API call POD makes when an event's details are loaded (after a click)
browser.webRequest.onCompleted.addListener(
  (details) => {
    if (details.url.includes("swordfish-production.up.railway.app/events/")) {
      const match = details.url.match(/events\/(\d+)/); // Extracts digits after /events/
      if (match && match[1]) {
        const capturedEventId = match[1];
        const capturedTimestamp = details.timeStamp; // Timestamp of the request completion

        // Update if it's a different event or a newer timestamp for the same event
        if (capturedEventId !== lastSniffedSwordfishEvent.eventId || capturedTimestamp > lastSniffedSwordfishEvent.timestamp) {
            lastSniffedSwordfishEvent.eventId = capturedEventId;
            lastSniffedSwordfishEvent.timestamp = capturedTimestamp;
            lastSniffedSwordfishEvent.url = details.url; // For logging
            console.log(
              `[BG_WebRequest] CAPTURED/UPDATED Swordfish eventId: ${lastSniffedSwordfishEvent.eventId} from URL: ${details.url} at ${new Date(lastSniffedSwordfishEvent.timestamp).toISOString()}`
            );
        }
      }
    }
  },
  { urls: ["https://swordfish-production.up.railway.app/events/*"] }
);

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("[Background] Message received:", message.type);

    if (message.type === "getLatestSniffedEventDetails") {
        console.log(`[Background] Responding to 'getLatestSniffedEventDetails'. Current: ID=${lastSniffedSwordfishEvent.eventId}, TS=${lastSniffedSwordfishEvent.timestamp}`);
        return Promise.resolve({ 
            eventId: lastSniffedSwordfishEvent.eventId, 
            timestamp: lastSniffedSwordfishEvent.timestamp,
            url: lastSniffedSwordfishEvent.url 
        });

    } else if (message.type === "forwardToPython") {
        function getPythonServerUrl() {
          return browser.storage.sync.get({ backendPort: '5001' }).then(function(items) {
            const port = items.backendPort || '5001';
            return `http://localhost:${port}/pod_alert`;
          });
        }
        
        const payload = message.payload;

        if (!payload || !payload.eventId) {
            console.error("[Background] 'forwardToPython' called BUT payload is missing 'eventId'. Payload:", payload);
            return Promise.resolve({ status: "error", reason: "Missing eventId in payload for forwardToPython" });
        }
        
        console.log(`[Background] Forwarding to Python for eventId: ${payload.eventId}.`);
        
        return getPythonServerUrl().then(url => {
            return fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(response => {
                if (!response.ok) { throw new Error(`HTTP error! status: ${response.status}`); }
                return response.json();
            })
            .then(data => {
                console.log("[Background] Python server response:", data);
                return { status: data.status || "success", pythonResponse: data };
            })
            .catch(error => {
                console.error("[Background] Error POSTing to Python server:", error.message);
                return { status: "error", reason: `Python POST failed: ${error.message}` };
            });
        });

    } else if (message.type === "autoSearchBetBCK") {
        console.log(`[Background] Received auto-search request for term: "${message.searchTerm}"`);
        if (!message.searchTerm) {
            console.error("[Background] Auto-search failed: No search term provided.");
            return Promise.resolve({status: "error", reason: "No search term"});
        }

        // 1. Open a new tab for BetBCK, making it the active tab
        return browser.tabs.create({ url: "https://betbck.com/Qubic/StraightSportSelection.php", active: true }).then(newTab => {
            
            // 2. We need to wait for the tab to finish loading before we can send a message to its content script.
            const listener = (tabId, info) => {
                if (tabId === newTab.id && info.status === 'complete') {
                    // This listener is no longer needed, so we remove it to prevent it from firing again.
                    browser.tabs.onUpdated.removeListener(listener);
                    
                    // 3. Now we can send a message to the content script in the new tab
                    browser.tabs.sendMessage(newTab.id, {
                        type: "performAutoSearch",
                        searchTerm: message.searchTerm
                    }).then(response => {
                        console.log("[Background] Auto-search response:", response);
                        sendResponse(response);
                    }).catch(error => {
                        console.error("[Background] Error sending auto-search message:", error);
                        sendResponse({status: "error", reason: "Failed to send search message to tab"});
                    });
                }
            };
            
            browser.tabs.onUpdated.addListener(listener);
            
            // 4. Set a timeout in case the tab never loads
            setTimeout(() => {
                browser.tabs.onUpdated.removeListener(listener);
                console.warn("[Background] Auto-search timeout - tab may not have loaded properly");
                sendResponse({status: "warning", reason: "Tab load timeout"});
            }, 30000); // 30 second timeout
            
            return true; // Keep the message channel open for async response
        }).catch(error => {
            console.error("[Background] Error creating tab for auto-search:", error);
            return Promise.resolve({status: "error", reason: "Failed to create tab"});
        });
    }
    
    return false; // Synchronous response for other message types
}); 