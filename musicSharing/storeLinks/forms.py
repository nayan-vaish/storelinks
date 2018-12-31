from django.forms import ModelForm, TextInput

from .models import SharedMusicLink


class SharedMusicLinkForm(ModelForm):
    class Meta:
        model = SharedMusicLink
        fields = ('link_name', 'link', 'artist_name',
                  'link_source', 'link_type', 'shared_by')
