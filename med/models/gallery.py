from freenit.db import db
from peewee import ForeignKeyField, TextField

Model = db.Model


class GalleryAlbum(Model):
    name = TextField(index=True)


class GalleryFile(Model):
    album = ForeignKeyField(GalleryAlbum, backref='files')
    filename = TextField(index=True)

    def url(self, prefix=''):
        name = self.album.name
        return f'{prefix}/{name}/{self.filename}'
