export default class PollingClient {
  constructor(options = {}) {
    this.pollingInterval = options.pollingInterval || 600000; // 60 секунд
    this.endpoint = options.endpoint || '/api/notifications/';
    this.messageHandlers = new Set();
    this.isRunning = false;
    this.pollingTimer = null;
    this.lastCheck = null;
  }

  start() {
    if (this.isRunning) return;

    this.isRunning = true;
    this.poll();
    console.log('[Polling] Notification polling started');
  }

  stop() {
    this.isRunning = false;
    if (this.pollingTimer) {
      clearTimeout(this.pollingTimer);
    }
    console.log('[Polling] Notification polling stopped');
  }

  poll() {
    if (!this.isRunning) return;

    fetch(`${this.endpoint}?last_check=${this.lastCheck || ''}`)
      .then(response => response.json())
      .then(data => {
        if (data.length > 0) {
          this.lastCheck = new Date().toISOString();
          data.forEach(message => this.notifyMessage(message));
        }
      })
      .catch(error => {
        console.error('[Polling] Error:', error);
      })
      .finally(() => {
        if (this.isRunning) {
          this.pollingTimer = setTimeout(() => this.poll(), this.pollingInterval);
        }
      });
  }

  addMessageHandler(handler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  notifyMessage(message) {
    this.messageHandlers.forEach(handler => handler(message));
  }
}
