import json
import logging
import os
import tempfile

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files import File

from users.models import NotificationAppRoute

from .models import Proposal, ProposalDocument, Status
from .utils import create_doc

logger = logging.getLogger(__name__)

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('tasks', self.channel_name)
        logger.info(f"Connected to channel 'tasks' with channel_name={self.channel_name}")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('tasks', self.channel_name)
        logger.info(f"Disconnected from channel 'tasks' with channel_name={self.channel_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        task_type = data.get('task_type')

        if task_type == 'create_proposal_doc':
            proposal_id = data.get('proposal_id')
            await self.create_proposal_doc(proposal_id)
        elif task_type == 'send_notification':
            status_id = data.get('status_id')
            await self.send_notification(status_id)

    async def create_proposal_doc(self, proposal_id):
        proposal = await Proposal.objects.aget(id=proposal_id)
        equipment = proposal.equipment
        root_equipment = equipment
        while root_equipment.parent:
            root_equipment = root_equipment.parent
        app_user = await NotificationAppRoute.objects.filter(
            equipment=root_equipment,
            app_name='rational'
        ).afirst()
        proposal_doc_dict = {
            'department': root_equipment.name,
            'appuser': app_user.user.fio,
            'title': proposal.title,
            'equipment': equipment.name,
            'description': proposal.description,
            'author0': '',
            'direction0': '',
            'jobposition0': '',
            'author1': '',
            'direction1': '',
            'jobposition1': '',
            'author2': '',
            'direction2': '',
            'jobposition2': '',
            'author3': '',
            'direction3': '',
            'jobposition3': '',
            'role0': '',
            'role1': '',
            'role2': '',
            'role3': '',
        }
        for id, author in enumerate(proposal.authors.all()):
            proposal_doc_dict[f'author{id}'] = author.fio
            proposal_doc_dict[f'direction{id}'] = author.equipment.name
            proposal_doc_dict[f'jobposition{id}'] = author.job_position
            proposal_doc_dict[f'role{id}'] = 'Автор идеи'
        doc = create_doc(proposal_doc_dict)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            doc.save(tmp_file)
            tmp_file_path = tmp_file.name
        reg_date = proposal.reg_date.strftime('%d.%m.%Y')
        file_name = f'Заявление РП №{proposal.reg_num}.docx'
        with open(tmp_file_path, 'rb') as file:
            proposal_doc = ProposalDocument(
                name=file_name,
                proposal=proposal
            )
            proposal_doc.doc.save(file_name, File(file))
            await proposal_doc.asave()
        os.remove(tmp_file_path)

    async def send_notification(self, status_id):
        print('!!!!')
        status = await Status.objects.aget(id=status_id)
        recipients = []
        if status.status in [status.StatusChoices.REG, status.StatusChoices.RECHECK]:
            root_equipment = status.proposal.equipment
            while root_equipment.parent:
                root_equipment = root_equipment.parent
            app_route = await NotificationAppRoute.objects.filter(app_name='rational', equipment=root_equipment).afirst()
            if app_route and app_route.user:
                recipients.append(app_route.user.email)
        if status.status in [
            status.StatusChoices.REWORK,
            status.StatusChoices.ACCEPT,
            status.StatusChoices.REJECT,
            status.StatusChoices.APPLY
        ]:
            recipients += list(status.proposal.authors.values_list('email', flat=True))
        if recipients:
            subject = f'Изменение статуса РП №{status.proposal.reg_num}'
            message = (
                f'Статус рационализаторского предложения №{status.proposal.reg_num} изменен.\n'
                f'Новый статус: {status.get_status_display()}\n'
                f"Дата изменения: {status.date_changed.strftime('%d.%m.%Y, %H:%M')}\n"
                f"Примечание: {status.note or 'Без примечаний'}"
            )
            print(status.status, recipients)
            # send_email(self.owner.email, subject, message)
