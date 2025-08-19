let fetchedData = [];

document.getElementById('fetchButton').addEventListener('click', () => {
    document.getElementById('results').innerHTML = 'Fetching event IDs...';
    console.log('Popup: Fetching event IDs...');

    browser.tabs.query({ active: true, currentWindow: true }).then(tabs => {
        const activeTab = tabs[0];
        if (!activeTab) {
            document.getElementById('results').innerHTML = 'No active tab found.';
            console.error('Popup: No active tab found.');
            return;
        }

        browser.tabs.sendMessage(activeTab.id, { action: 'getEventIds' }).then(response => {
            if (response.success) {
                const eventIds = response.eventIds;
                console.log('Popup: Extracted event IDs:', eventIds);

                if (eventIds.length === 0) {
                    document.getElementById('results').innerHTML = 'No alerts found.';
                    console.log('Popup: No alerts found.');
                    return;
                }

                document.getElementById('results').innerHTML = 'Fetching odds...';
                console.log('Popup: Fetching odds for event IDs:', eventIds);

                browser.runtime.sendMessage({ action: 'fetchOdds', eventIds }).then(response => {
                    const resultsDiv = document.getElementById('results');
                    if (response.success) {
                        console.log('Popup: Successfully fetched odds:', response.data);
                        if (response.data.length === 0) {
                            resultsDiv.innerHTML = 'No data found.';
                            console.log('Popup: No data found from API.');
                            return;
                        }

                        fetchedData = response.data;

                        let html = '<table border="1"><tr><th>Event ID</th><th>Match</th><th>Market</th><th>Outcome</th><th>Current Odds</th><th>Previous Odds</th><th>Opener Odds</th><th>No-Vig Price</th></tr>';
                        response.data.forEach(row => {
                            html += `<tr>
                                <td>${row.eventId}</td>
                                <td>${row.matchDetails}</td>
                                <td>${row.market}</td>
                                <td>${row.outcome}</td>
                                <td>${row.currentOdds}</td>
                                <td>${row.previousOdds}</td>
                                <td>${row.openerOdds}</td>
                                <td>${row.noVigPrice}</td>
                            </tr>`;
                        });
                        html += '</table>';
                        html += '<button id="saveButton">Save to Google Sheets</button>';
                        resultsDiv.innerHTML = html;

                        document.getElementById('saveButton').addEventListener('click', saveToGoogleSheets);
                    } else {
                        resultsDiv.innerHTML = `Error: ${response.error}`;
                        console.error('Popup: Error fetching odds:', response.error);
                    }
                }).catch(error => {
                    document.getElementById('results').innerHTML = `Error: ${error.message}`;
                    console.error('Popup: Error sending message to background:', error);
                });
            } else {
                document.getElementById('results').innerHTML = `Error fetching event IDs: ${response.error}`;
                console.error('Popup: Error fetching event IDs:', response.error);
            }
        }).catch(error => {
            document.getElementById('results').innerHTML = `Error: ${error.message}`;
            console.error('Popup: Error sending message to content script:', error);
        });
    });
});

function saveToGoogleSheets() {
    console.log('Popup: Attempting to save to Google Sheets...');
    // Note: Firefox doesn't support chrome.identity API directly
    // You would need to implement OAuth flow differently for Firefox
    document.getElementById('results').innerHTML += '<p>Google Sheets integration not available in Firefox version.</p>';
    console.log('Popup: Google Sheets integration not implemented for Firefox');
}

// Firefox-compatible message handling
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Popup: Message received:', message);
    
    if (message.type === 'updateStatus') {
        document.getElementById('status').textContent = message.status;
    }
    
    return false; // Synchronous response
});