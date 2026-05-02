import os
from supabase import create_client, Client


URL = os.environ.get("S3_URL")
KEY = os.environ.get("S3_KEY")
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

supabase: Client = create_client(URL, KEY)

storage = supabase.storage.from_('stickers_aibo')

def get_s3_storage():
    return storage