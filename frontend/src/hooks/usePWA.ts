import { useState, useEffect } from 'react';

interface PWAState {
  isInstalled: boolean;
  canInstall: boolean;
  isOnline: boolean;
  hasNotifications: boolean;
  isServiceWorkerRegistered: boolean;
}

export const usePWA = () => {
  const [pwaState, setPwaState] = useState<PWAState>({
    isInstalled: false,
    canInstall: false,
    isOnline: navigator.onLine,
    hasNotifications: false,
    isServiceWorkerRegistered: false,
  });

  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  useEffect(() => {
    // Check if app is installed
    const checkInstallation = () => {
      if (window.matchMedia('(display-mode: standalone)').matches) {
        setPwaState(prev => ({ ...prev, isInstalled: true }));
      }
    };

    // Handle install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setPwaState(prev => ({ ...prev, canInstall: true }));
    };

    // Handle app installed
    const handleAppInstalled = () => {
      setPwaState(prev => ({ ...prev, isInstalled: true, canInstall: false }));
      setDeferredPrompt(null);
    };

    // Handle online/offline status
    const handleOnline = () => setPwaState(prev => ({ ...prev, isOnline: true }));
    const handleOffline = () => setPwaState(prev => ({ ...prev, isOnline: false }));

    // Register service worker - DISABLED to prevent screen flashing
    const registerServiceWorker = async () => {
      // Temporarily disabled to prevent screen flashing issues
      console.log('Service Worker registration disabled to prevent screen flashing');
      setPwaState(prev => ({ ...prev, isServiceWorkerRegistered: false }));
    };

    // Request notification permission
    const requestNotificationPermission = async () => {
      if ('Notification' in window) {
        const permission = await Notification.requestPermission();
        setPwaState(prev => ({ 
          ...prev, 
          hasNotifications: permission === 'granted' 
        }));
      }
    };

    // Event listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initialize
    checkInstallation();
    registerServiceWorker();
    requestNotificationPermission();

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Install app
  const installApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      setDeferredPrompt(null);
      setPwaState(prev => ({ ...prev, canInstall: false }));
    }
  };

  // Send push notification
  const sendNotification = (title: string, options?: NotificationOptions) => {
    if (pwaState.hasNotifications && 'serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.showNotification(title, {
          icon: '/logo192.png',
          badge: '/logo192.png',
          ...options,
        });
      });
    }
  };

  // Background sync for bet placement
  const syncBetPlacement = async (betData: any) => {
    // Simplified - just log for now to avoid TypeScript errors
    console.log('Bet data for background sync:', betData);
  };

  return {
    ...pwaState,
    installApp,
    sendNotification,
    syncBetPlacement,
  };
};
