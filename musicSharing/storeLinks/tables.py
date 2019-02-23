import django_tables2 as tables
from django_tables2 import TemplateColumn
from django.utils.html import format_html
from .models import SharedMusicLink


class LinkNameColumn(tables.Column):
    def render(self, record):
        return format_html('<a href="{}">{}</a>', record.link, record.link_name.title())


class LinkSourceColum(tables.Column):
    def render(self, value):
        return value.upper()


class TitleColum(tables.Column):
    def render(self, value):
        return value.title()


class SharedLinksTable(tables.Table):
    link_name = LinkNameColumn()
    artist_name = TitleColum()
    link_source = LinkSourceColum()
    shared_by = TitleColum()

    class Meta:
        model = SharedMusicLink
        fields = ('link_name', 'artist_name', 'link_type', 'link_source', 'shared_by', 'shared_date', 'edit', 'delete', 'share', 'move')
        template_name = 'django_tables2/bootstrap4.html'

    move = TemplateColumn(template_name='storeLinks/moveStatus.html', orderable=False)
    edit = TemplateColumn(template_name='storeLinks/editButton.html', orderable=False)
    share = TemplateColumn(template_name='storeLinks/shareButton.html', orderable=False)
    delete = TemplateColumn(template_name='storeLinks/deleteButton.html', orderable=False)
