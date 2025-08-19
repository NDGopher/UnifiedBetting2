// Firefox-compatible options page
document.addEventListener('DOMContentLoaded', function() {
    // Load saved settings
    browser.storage.sync.get({
        backendPort: '5001'
    }, function(items) {
        document.getElementById('backendPort').value = items.backendPort;
    });

    // Save settings when form is submitted
    document.getElementById('settingsForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const backendPort = document.getElementById('backendPort').value;
        
        browser.storage.sync.set({
            backendPort: backendPort
        }, function() {
            // Show saved message
            const status = document.getElementById('status');
            status.textContent = 'Settings saved!';
            setTimeout(function() {
                status.textContent = '';
            }, 2000);
        });
    });
}); 