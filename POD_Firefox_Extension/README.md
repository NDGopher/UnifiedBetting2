# POD Firefox Extension

This is the Firefox version of the POD (PickTheOdds) Chrome Extension. It monitors POD for alerts and forwards them to your Python backend.

## Key Differences from Chrome Version

1. **Manifest Version**: Uses Manifest V2 (Firefox requirement)
2. **API Calls**: Uses `browser.*` instead of `chrome.*` APIs
3. **Background Script**: Uses regular background script instead of service worker
4. **Permissions**: Host permissions are included in the main permissions array
5. **Google Sheets**: OAuth integration is not available in Firefox version

## Installation Instructions

### Method 1: Temporary Installation (Development)

1. **Open Firefox** and navigate to `about:debugging`
2. **Click "This Firefox"** in the left sidebar
3. **Click "Load Temporary Add-on"**
4. **Select the `manifest.json` file** from this folder
5. The extension will be installed temporarily and will be removed when you restart Firefox

### Method 2: Permanent Installation (Recommended)

1. **Create a ZIP file** containing all the extension files:
   - Select all files in this folder
   - Right-click and create a ZIP archive
   - Name it `pod-firefox-extension.zip`

2. **Open Firefox** and navigate to `about:addons`
3. **Click the gear icon** (⚙️) in the top right
4. **Select "Install Add-on From File"**
5. **Choose your ZIP file**
6. The extension will be installed permanently

### Method 3: Developer Installation

1. **Open Firefox** and navigate to `about:debugging`
2. **Click "This Firefox"** in the left sidebar
3. **Click "Load Temporary Add-on"**
4. **Select the `manifest.json` file** from this folder
5. **Click "Inspect"** to open the developer tools
6. The extension will reload automatically when you make changes

## Configuration

1. **Click the extension icon** in your Firefox toolbar
2. **Click "Options"** to open the settings page
3. **Set your backend port** (default: 5001)
4. **Click "Save"**

## Usage

1. **Navigate to** https://picktheodds.app
2. **Log in** to your POD account
3. **Go to the terminal page** (if not already there)
4. **The extension will automatically**:
   - Monitor for new alerts
   - Capture event IDs when you click on alerts
   - Forward alert data to your Python backend
   - Auto-refresh the page periodically

## Troubleshooting

### Extension Not Working

1. **Check the browser console** for error messages
2. **Verify your backend is running** on the correct port
3. **Check the extension permissions** in `about:addons`
4. **Try reloading the extension** in `about:debugging`

### Common Issues

- **"Extension not compatible"**: Make sure you're using Firefox 57 or later
- **"Permission denied"**: Check that the extension has the required permissions
- **"Backend connection failed"**: Verify your Python backend is running on localhost:5001

### Debug Mode

1. **Open `about:debugging`**
2. **Click "This Firefox"**
3. **Find your extension** and click "Inspect"
4. **Check the console** for detailed logs

## File Structure

```
POD_Firefox_Extension/
├── manifest.json          # Extension manifest (Firefox V2)
├── background.js          # Background script (Firefox API)
├── content.js            # Content script (Firefox API)
├── popup.html            # Extension popup
├── popup.js              # Popup script (Firefox API)
├── popup.css             # Popup styles
├── options.html          # Options page
├── options.js            # Options script (Firefox API)
├── betbck_auto_search.js # Auto-search functionality
├── icon16.png            # Extension icon (16px)
├── icon32.png            # Extension icon (32px)
├── icon48.png            # Extension icon (48px)
└── README.md             # This file
```

## API Compatibility

| Feature | Chrome | Firefox | Status |
|---------|--------|---------|--------|
| WebRequest API | ✅ | ✅ | Working |
| Tabs API | ✅ | ✅ | Working |
| Storage API | ✅ | ✅ | Working |
| Runtime Messaging | ✅ | ✅ | Working |
| Identity API | ✅ | ❌ | Not available |
| Service Workers | ✅ | ❌ | Not used |

## Development

To modify the extension:

1. **Make your changes** to the source files
2. **Reload the extension** in `about:debugging`
3. **Test your changes** on the POD website
4. **Check the console** for any errors

## Support

If you encounter issues:

1. **Check the browser console** for error messages
2. **Verify your backend is running** and accessible
3. **Test with the Chrome version** to isolate Firefox-specific issues
4. **Check Firefox's extension documentation** for API changes

## Notes

- The Firefox version uses Manifest V2, which is the current standard for Firefox extensions
- Google Sheets integration is not available due to Firefox's OAuth limitations
- All other functionality should work identically to the Chrome version
- The extension is designed to be compatible with Firefox 57+ 