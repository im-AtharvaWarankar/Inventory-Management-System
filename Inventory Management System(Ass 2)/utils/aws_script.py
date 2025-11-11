from django.conf import settings
import uuid
import boto3
import os
from PIL import Image
from pillow_heif import register_heif_opener
import io
register_heif_opener()

s3 = boto3.client("s3", region_name=settings.REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


def upload_image(file, folder=None):
    image_id = str(uuid.uuid4())
    file_bytes = file.open()
    if folder is not None and folder != "":
        aws_path = os.path.join(folder, "images", f"{image_id}.jpg")
    else:
        aws_path = os.path.join("images", f"{image_id}.jpg")
    try:
        s3.upload_fileobj(
            file_bytes,
            settings.S3_BUCKET,
            aws_path,
            ExtraArgs={'ACL': 'public-read'})
        url = f"{settings.AWS_URL}/{aws_path}"
        return url
    except Exception:
        return None


def crop_and_upload_image(file, folder=None, width=512, height=512):
    image_id = str(uuid.uuid4())
    file_bytes = file.open()
    image = Image.open(file_bytes)
    format = image.format
    image = image.resize((width, height))
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format=format)
    in_mem_file.seek(0)
    if folder is not None and folder != "":
        aws_path = os.path.join(folder, "images", f"{image_id}.jpg")
    else:
        aws_path = os.path.join("images", f"{image_id}.jpg")
    try:
        s3.upload_fileobj(
            in_mem_file, settings.S3_BUCKET, aws_path, ExtraArgs={"ACL": "public-read"}
        )
        url = f"{settings.AWS_URL}/{aws_path}"
        return url
    except Exception:
        return None


def upload_file(file, folder=None, file_format=None, extraArgsUser=None):
    file_id = str(uuid.uuid4())
    if folder is not None and folder != "":
        aws_path = os.path.join(folder, f"{file_id}")
    else:
        raise ValueError("No folder specified")
    file_bytes = file.open()
    if file_format:
        file_id = f"{file_id}.{file_format}"
    try:
        extraArgs = {'ACL': 'public-read'}
        if extraArgsUser is not None:
            extraArgsUser = dict(extraArgsUser)
            extraArgs.update(extraArgsUser)

        s3.upload_fileobj(
            file_bytes,
            settings.S3_BUCKET,
            aws_path,
            ExtraArgs=extraArgs)
        url = f"{settings.AWS_URL}/{aws_path}"
        return url
    except Exception:
        return None


def compress_image(file, folder=None, extraArgsUser=None):
    if folder is None:
        folder = 'extras'
    try:
        # open the file
        image = Image.open(file)
        # Create a BytesIO object to store the compressed image
        output = io.BytesIO()
        # Compress the image and save it to the BytesIO object
        size = 1440, 1440
        image.thumbnail(size)
        image = image.convert('RGB')
        image.save(output, "JPEG")
        # Seek to the beginning of the stream
        output.seek(0)
        # AWS PATH and Extra Args configuration
        aws_file_name = str(uuid.uuid4()) + ".jpg"
        aws_path = os.path.join(folder, aws_file_name)
        extraArgs = {'ACL': 'public-read', 'ContentType': 'image/jpeg'}
        if extraArgsUser is not None:
            extraArgsUser = dict(extraArgsUser)
            extraArgs.update(extraArgsUser)
        # Upload file
        s3.upload_fileobj(
            output,
            settings.S3_BUCKET,
            aws_path,
            ExtraArgs=extraArgs
        )
        # Construct the URL for the uploaded image
        url = f"{settings.AWS_URL}/{aws_path}"
        return url
    except Exception as e:
        print("Error While Uploading File:", e, flush=True)
        return None
