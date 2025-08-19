# Chrome vs Firefox Extension Comparison

## Overview

Both extensions provide the same core functionality but are adapted for their respective browser APIs.

## Key Differences

### 1. Manifest File

**Chrome (Manifest V3):**
```json
{
  "manifest_version": 3,
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html"
  }
}
```

**Firefox (Manifest V2):**
```json
{
  "manifest_version": 2,
  "background": {
    "scripts": ["background.js"]
  },
  "browser_action": {
    "default_popup": "popup.html"
  },
  "applications": {
    "gecko": {
      "id": "odds-dropper@unifiedbetting.com"
    }
  }
}
```

### 2. API Calls

| Feature | Chrome | Firefox |
|---------|--------|---------|
| Background Script | `chrome.runtime.sendMessage()` | `browser.runtime.sendMessage()` |
| Tabs API | `chrome.tabs.query()` | `browser.tabs.query()` |
| Storage API | `chrome.storage.sync.get()` | `browser.storage.sync.get()` |
| WebRequest | `chrome.webRequest.onCompleted` | `browser.webRequest.onCompleted` |

### 3. Message Handling

**Chrome:**
```javascript
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    // Handle message
    sendResponse({ status: "success" });
    return true; // Keep message channel open
});
```

**Firefox:**
```javascript
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    // Handle message
    return Promise.resolve({ status: "success" });
});
```

### 4. Async Operations

**Chrome:**
```javascript
chrome.tabs.query({ active: true }, (tabs) => {
    // Handle tabs
});
```

**Firefox:**
```javascript
browser.tabs.query({ active: true }).then((tabs) => {
    // Handle tabs
});
```

## Feature Comparison

| Feature | Chrome | Firefox | Notes |
|---------|--------|---------|-------|
| POD Monitoring | ✅ | ✅ | Identical functionality |
| Event ID Capture | ✅ | ✅ | Identical functionality |
| Backend Communication | ✅ | ✅ | Identical functionality |
| Auto-Search | ✅ | ✅ | Identical functionality |
| Google Sheets | ✅ | ❌ | OAuth not available in Firefox |
| Options Page | ✅ | ✅ | Identical functionality |
| Popup Interface | ✅ | ✅ | Identical functionality |
| Background Script | ✅ | ✅ | Different API, same functionality |
| Content Script | ✅ | ✅ | Identical functionality |

## Installation Differences

### Chrome Installation
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select extension folder

### Firefox Installation
1. Go to `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select `manifest.json`

## Development Workflow

### Chrome Development
- Edit files
- Go to `chrome://extensions/`
- Click "Reload" button
- Test changes

### Firefox Development
- Edit files
- Go to `about:debugging`
- Click "Reload" button
- Test changes

## Debugging

### Chrome Debugging
- Right-click extension icon → "Inspect popup"
- Go to `chrome://extensions/` → "background page"
- Check console for errors

### Firefox Debugging
- Go to `about:debugging` → "This Firefox"
- Click "Inspect" next to extension
- Check console for errors

## Performance

Both extensions should perform identically for the core functionality. The main differences are:

- **Chrome**: Uses service workers (more modern)
- **Firefox**: Uses regular background scripts (more compatible)

## Compatibility

- **Chrome**: Requires Chrome 88+ for Manifest V3
- **Firefox**: Requires Firefox 57+ for WebExtensions

## Maintenance

When updating the extension:

1. **Make changes** to both versions
2. **Test in Chrome** first
3. **Adapt for Firefox** API differences
4. **Test in Firefox**
5. **Update both versions** simultaneously

## Recommendations

1. **Use Chrome version** for full functionality (including Google Sheets)
2. **Use Firefox version** if you prefer Firefox or need cross-browser compatibility
3. **Both versions** work identically for core POD monitoring functionality
4. **Keep both versions** updated for maximum compatibility 