import django_tables2 as tables

from users.models import Role

from .models import Order, Protocol, Document, Event


class DocumentTable(tables.Table):
    class Meta:
        model = Document
        fields = [
            'date_doc',
            'num_doc',
            'title',
            'subject',
            'is_complete',
        ]
        attrs = {'class': 'table table_plans'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        # order_by = '-date_doc'
        template_name = 'module_app/table/new_table.html'


class ProtocolTable(tables.Table):

    class Meta:
        model = Protocol
        fields = [
            'num_protocol',
            'date_protocol',
            'title',
            'subject',
            'is_complete',
        ]
        attrs = {'class': 'table table_plans'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        order_by = '-date_protocol'
        template_name = 'module_app/table/new_table.html'


class OrderTable(tables.Table):

    class Meta:
        model = Order
        fields = [
            'num_order',
            'date_order',
            'title',
            'subject',
            'is_complete',
        ]
        attrs = {'class': 'table table_plans'}
        row_attrs = {'id': lambda record: record.id}
        orderable = False
        order_by = '-date_order'
        template_name = 'module_app/table/new_table.html'
