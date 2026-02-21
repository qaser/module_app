import PollingClient from '../../api/PollingClient.js';


const pollingClient = new PollingClient({
  endpoint: '/api/notifications/unread/'
});


pollingClient.start();
