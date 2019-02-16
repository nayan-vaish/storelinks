from django.db import models


class SharedMusicLink(models.Model):
    TRACK = 'TRACK'
    ALBUM = 'ALBUM'
    SET = 'SET'
    EP = 'EP'
    DEMO = 'Demo'
    LINK_TYPE_CHOICES = (
        (DEMO, 'Demo'),
        (TRACK, 'Track'),
        (EP, 'EP'),
        (ALBUM, 'Album'),
        (SET, 'Set')
    )

    TO_LISTEN = 1
    DONE = 2
    STATUS_CHOICES = (
        (TO_LISTEN, 'To_Listen'),
        (DONE, 'Done')
    )
    user_name = models.CharField(db_index=True, max_length=100)
    link_name = models.CharField(max_length=100)
    link = models.URLField(max_length=400)
    artist_name = models.CharField(db_index=True, max_length=100)
    link_source = models.CharField(db_index=True, max_length=100)
    link_type = models.CharField(db_index=True,
                                 max_length=5,
                                 choices=LINK_TYPE_CHOICES,
                                 default=TRACK)
    shared_by = models.CharField(max_length=100)
    shared_date = models.DateTimeField('date shared',
                                       auto_now_add=True,
                                       blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=TO_LISTEN)

    def __str__(self):
        return self.link_name
