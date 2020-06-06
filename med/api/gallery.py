import os
import shutil

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_optional
from flask_smorest import Blueprint, abort
from freenit.schemas.paging import PageInSchema, paginate
from werkzeug.utils import secure_filename

from ..models.gallery import GalleryAlbum, GalleryFile
from ..models.user import User
from ..schemas.gallery import (GalleryAlbumPageOutSchema, GalleryAlbumSchema,
                               GalleryUploadSchema,
                               ResumableGalleryUploadSchema)

blueprint = Blueprint('gallery', 'gallery')


@blueprint.route('', endpoint='albums')
class GalleryAlbumListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(GalleryAlbumPageOutSchema)
    def get(self, pagination, year=None):
        """Get list of albums"""
        return paginate(GalleryAlbum.select(), pagination)

    @blueprint.arguments(GalleryAlbumSchema)
    @blueprint.response(GalleryAlbumSchema)
    def post(self, args):
        """Create album post"""
        try:
            album = GalleryAlbum.get(name=args['name'])
            abort(409, message='Album with the same name already exists')
        except GalleryAlbum.DoesNotExist:
            album = GalleryAlbum(**args)
            album.save()
        return album


@blueprint.route('/album/<name>', endpoint='album')
class GalleryAlbumAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(GalleryAlbumSchema)
    def get(self, pagination, name, year=None):
        """Get album details"""
        try:
            album = GalleryAlbum.get(name=name)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        album.files = paginate(
            album.files.order_by(GalleryFile.filename),
            pagination,
        )
        prefix = current_app.config.get('MEDIA_URL', None)
        if prefix is None:
            abort(409, message='Backend misconfiguration, no MEDIAL_URL')
        album.prefix = prefix
        return album

    @jwt_optional
    @blueprint.arguments(GalleryUploadSchema, location='files')
    @blueprint.arguments(ResumableGalleryUploadSchema, location='form')
    @blueprint.response(ResumableGalleryUploadSchema)
    def post(self, fileargs, formargs, name, year=None):
        """Upload picture to album"""
        try:
            album = GalleryAlbum.get(name=name)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        user_id = get_jwt_identity()
        if user_id is None:
            abort(401, message='Must be logged in to upload!')
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='No such user')
        if not user.admin and album.name != 'avatars':
            abort(403, message='Only avatar uploads are allowed!')
        prefix = current_app.config.get('MEDIA_URL', None)
        if prefix is None:
            abort(409, message='Backend misconfiguration, no MEDIAL_URL')
        uploadFile = fileargs['file']
        chunkNumber = formargs['resumableChunkNumber']
        chunkSize = formargs['resumableChunkSize']
        total = formargs['resumableTotalChunks']
        identifier = formargs['resumableIdentifier']
        media_path = os.path.abspath(
            current_app.config.get(
                'MEDIA_PATH',
                None,
            ), )
        filePath = f'/tmp/{identifier}'
        with open(filePath, 'ab') as tempfile:
            offset = (chunkNumber - 1) * chunkSize
            tempfile.seek(offset)
            tempfile.write(uploadFile.read())
        if chunkNumber == total:
            if album.name == 'avatars':
                category = formargs['resumableType'][:5]
                if category != 'image':
                    abort(409, message='Only image type allowed')
                imgtype = formargs['resumableType'][6:]
                filename = f'{user.id}.{imgtype}'
            else:
                filename = secure_filename(uploadFile.filename)
            try:
                finalFile = GalleryFile.get(album=album, filename=filename)
            except GalleryFile.DoesNotExist:
                finalFile = GalleryFile(
                    album=album,
                    filename=secure_filename(filename),
                )
            print(finalFile.filename)
            formargs['resumableFilename'] = finalFile.filename
            file_dir = f'{media_path}/{album.name}'
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            finalPath = finalFile.url(prefix=media_path)
            shutil.move(filePath, finalPath)
            os.chmod(finalPath, 0o644)
            finalFile.save()
            if album.name == 'avatars':
                user.avatar = finalFile.url(prefix=prefix)
                user.save()
        return formargs
