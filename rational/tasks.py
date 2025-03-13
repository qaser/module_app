import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def trigger_create_proposal_doc(proposal_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)('tasks', {
        'type': 'create_proposal_doc',
        'proposal_id': proposal_id,
    })

def trigger_send_notification(status_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)('tasks', {
        'type': 'send_notification',
        'status_id': status_id,
    })
