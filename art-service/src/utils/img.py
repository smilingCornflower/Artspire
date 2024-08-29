import io
from typing import BinaryIO
from config import logger

from PIL import Image


async def convert_to_jpg(upload_file: BinaryIO) -> BinaryIO:
    logger.info("Started converting the image")
    img = Image.open(upload_file)
    img = img.convert('RGB')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr
