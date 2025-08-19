# Mobile PWA Setup Guide

## Overview
The Unified Betting System has been converted to a Progressive Web App (PWA) that can be installed on mobile devices and used like a native app.

## Features
- **Mobile-Optimized UI**: Responsive design that works on all screen sizes
- **Installable**: Add to home screen on iOS and Android
- **Offline Support**: Works even when internet connection is lost
- **Push Notifications**: Get alerts for betting opportunities
- **Background Sync**: Automatic bet placement when connection is restored
- **Touch-Friendly**: Optimized for mobile touch interactions

## Setup Instructions

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Create Logo Files
You need to create two logo files in the `public` folder:
- `logo192.png` - 192x192 pixels
- `logo512.png` - 512x512 pixels

These should be PNG images representing your betting system (e.g., green betting chip, chart icon).

### 3. Start Development Server
```bash
npm start
```

### 4. Install on Mobile Device

#### Android (Chrome):
1. Open the app in Chrome
2. Tap the three-dot menu
3. Select "Add to Home screen"
4. Choose "Add" to install

#### iOS (Safari):
1. Open the app in Safari
2. Tap the share button (square with arrow)
3. Select "Add to Home Screen"
4. Tap "Add" to install

## Mobile Features

### Navigation
- **Hamburger Menu**: Tap the menu icon for navigation
- **Speed Dial**: Floating action button for quick access
- **Swipe Gestures**: Swipe between sections

### Notifications
- **Permission Request**: App will ask for notification permission
- **Bet Alerts**: Get notified of high EV opportunities
- **Auto Betting**: Receive confirmations for automatic bets

### Offline Mode
- **Cached Resources**: App works offline with cached data
- **Background Sync**: Queues actions when offline
- **Data Persistence**: Strategies and settings saved locally

## Automatic Bet Placement

### Strategy Configuration
1. **Min EV Threshold**: Set minimum expected value percentage
2. **Max Bet Amount**: Define maximum bet size
3. **Sports Selection**: Choose which sports to monitor
4. **Bookmaker Selection**: Select preferred betting sites

### Auto Betting Modes
- **Manual Confirmation**: Review each bet before placement
- **Fully Automatic**: Place bets automatically based on criteria
- **Notification Only**: Get alerts without automatic placement

### Safety Features
- **Bet Limits**: Maximum bet amounts per strategy
- **Daily Limits**: Total daily betting limits
- **Confirmation Required**: Manual approval for large bets

## Technical Details

### Service Worker
- **Offline Caching**: Stores app resources locally
- **Background Sync**: Handles bet placement when offline
- **Push Notifications**: Manages notification delivery

### PWA Manifest
- **App Name**: "Unified Betting System"
- **Theme Color**: Green (#43a047)
- **Display Mode**: Standalone (app-like experience)
- **Orientation**: Portrait primary

### Mobile Optimizations
- **Touch Targets**: Minimum 44px for touch interactions
- **Responsive Grid**: Adapts to different screen sizes
- **Mobile Navigation**: Drawer menu and speed dial
- **Status Indicators**: Online/offline, notifications, install prompts

## Troubleshooting

### Common Issues
1. **App Won't Install**: Check if HTTPS is enabled
2. **Notifications Not Working**: Verify permission is granted
3. **Offline Mode Issues**: Clear cache and reinstall
4. **Performance Problems**: Check device compatibility

### Debug Mode
- Open browser developer tools
- Check Console for error messages
- Verify Service Worker registration
- Test offline functionality

## Security Considerations

### Data Protection
- **Local Storage**: Strategies stored locally on device
- **No Server Storage**: Betting data stays private
- **Encrypted Communication**: HTTPS for all API calls

### Betting Safety
- **Confirmation Required**: Large bets need approval
- **Strategy Limits**: Prevents excessive betting
- **Audit Trail**: Logs all automatic actions

## Future Enhancements

### Planned Features
- **Biometric Authentication**: Fingerprint/Face ID login
- **Advanced Analytics**: Detailed betting performance tracking
- **Social Features**: Share strategies with other users
- **AI Integration**: Machine learning for bet optimization

### API Integration
- **Real-time Odds**: Live betting line updates
- **Account Management**: Direct bookmaker integration
- **Payment Processing**: Automated deposit/withdrawal
- **Risk Management**: Advanced portfolio analysis

## Support

For technical support or feature requests:
- Check the console for error messages
- Verify all dependencies are installed
- Ensure mobile device compatibility
- Test with different browsers and devices

## License
This mobile PWA is part of the Unified Betting System and follows the same licensing terms.
