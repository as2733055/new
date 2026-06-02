/**
 * Network Detection Service for React Frontend
 * Monitors internet connectivity and switches between online/offline modes
 */

class NetworkDetectionService {
  constructor(serverUrl = 'http://localhost:8000', checkInterval = 10000) {
    this.serverUrl = serverUrl;
    this.checkInterval = checkInterval;
    this.isOnline = true;
    this.modeChangeCallbacks = [];
    this.statusChangeCallbacks = [];
    this.monitoringInterval = null;
  }

  /**
   * Register callback for when mode changes
   */
  onModeChange(callback) {
    this.modeChangeCallbacks.push(callback);
    return () => {
      this.modeChangeCallbacks = this.modeChangeCallbacks.filter(cb => cb !== callback);
    };
  }

  /**
   * Register callback for status updates
   */
  onStatusChange(callback) {
    this.statusChangeCallbacks.push(callback);
    return () => {
      this.statusChangeCallbacks = this.statusChangeCallbacks.filter(cb => cb !== callback);
    };
  }

  /**
   * Start monitoring network connectivity
   */
  startMonitoring() {
    console.log('[NetworkDetection] Starting monitoring...');
    
    // Initial check
    this._performCheck();
    
    // Periodic checks
    this.monitoringInterval = setInterval(
      () => this._performCheck(),
      this.checkInterval
    );

    // Listen to online/offline events
    window.addEventListener('online', () => this._handleOnline());
    window.addEventListener('offline', () => this._handleOffline());
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    window.removeEventListener('online', () => this._handleOnline());
    window.removeEventListener('offline', () => this._handleOffline());
    console.log('[NetworkDetection] Monitoring stopped');
  }

  /**
   * Perform connectivity check
   */
  async _performCheck() {
    const wasOnline = this.isOnline;
    
    // Multi-level check
    const hasConnection = await this._checkConnectivity();
    this.isOnline = hasConnection;

    // Notify listeners if status changed
    if (wasOnline !== this.isOnline) {
      console.log(`[NetworkDetection] Mode changed: ${this.isOnline ? 'ONLINE' : 'OFFLINE'}`);
      this._notifyModeChange(this.isOnline);
    }

    this._notifyStatusChange();
  }

  /**
   * Check connectivity through multiple methods
   */
  async _checkConnectivity() {
    // First, try to reach the server
    if (await this._checkServer()) {
      return true;
    }

    // Then try general internet
    if (await this._checkInternet()) {
      return true;
    }

    return false;
  }

  /**
   * Check if server is reachable
   */
  async _checkServer() {
    try {
      const response = await fetch(`${this.serverUrl}/health`, {
        timeout: 5000,
        method: 'GET',
        cache: 'no-cache'
      });
      return response.ok;
    } catch (error) {
      console.debug('[NetworkDetection] Server check failed:', error.message);
      return false;
    }
  }

  /**
   * Check general internet connectivity
   */
  async _checkInternet() {
    const testUrls = [
      'https://www.google.com/favicon.ico',
      'https://cloudflare.com/favicon.ico',
      'https://www.github.com/favicon.ico'
    ];

    for (const url of testUrls) {
      try {
        const response = await fetch(url, {
          timeout: 3000,
          method: 'HEAD',
          cache: 'no-cache'
        });
        if (response.ok) {
          return true;
        }
      } catch (error) {
        // Continue to next URL
      }
    }

    return false;
  }

  /**
   * Handle online event
   */
  _handleOnline() {
    console.log('[NetworkDetection] Browser online event');
    if (!this.isOnline) {
      this.isOnline = true;
      this._notifyModeChange(true);
    }
  }

  /**
   * Handle offline event
   */
  _handleOffline() {
    console.log('[NetworkDetection] Browser offline event');
    if (this.isOnline) {
      this.isOnline = false;
      this._notifyModeChange(false);
    }
  }

  /**
   * Notify listeners of mode change
   */
  _notifyModeChange(isOnline) {
    this.modeChangeCallbacks.forEach(callback => {
      try {
        callback(isOnline);
      } catch (error) {
        console.error('[NetworkDetection] Error in mode change callback:', error);
      }
    });
  }

  /**
   * Notify listeners of status change
   */
  _notifyStatusChange() {
    const status = this.getStatus();
    this.statusChangeCallbacks.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('[NetworkDetection] Error in status change callback:', error);
      }
    });
  }

  /**
   * Get current status
   */
  getStatus() {
    return {
      isOnline: this.isOnline,
      isOffline: !this.isOnline,
      mode: this.isOnline ? 'ONLINE' : 'OFFLINE_LOCAL',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get mode string for display
   */
  getModeString() {
    if (this.isOnline) {
      return '🟢 Online - Connected to Server';
    } else {
      return '🟡 Offline - Local Network Only';
    }
  }

  /**
   * Get connection indicator for UI
   */
  getConnectionIndicator() {
    return this.isOnline ? '🟢' : '🟡';
  }
}

export default NetworkDetectionService;

/**
 * Usage in React Component:
 * 
 * import NetworkDetectionService from './services/NetworkDetectionService';
 * 
 * function ChatApp() {
 *   const [mode, setMode] = useState('ONLINE');
 *   
 *   useEffect(() => {
 *     const detector = new NetworkDetectionService();
 *     
 *     // Listen for mode changes
 *     detector.onModeChange((isOnline) => {
 *       setMode(isOnline ? 'ONLINE' : 'OFFLINE_LOCAL');
 *     });
 *     
 *     detector.startMonitoring();
 *     
 *     return () => {
 *       detector.stopMonitoring();
 *     };
 *   }, []);
 *   
 *   return (
 *     <div>
 *       <div>{detector.getModeString()}</div>
 *     </div>
 *   );
 * }
 */
