import io
from typing import BinaryIO
from config import logger

from PIL import Image


async def convert_to_jpg(upload_file: BinaryIO) -> BinaryIO:
    logger.info("Started converting the image")
    try:
        image = Image.open(upload_file)
        output = io.BytesIO()
        image.save(output, format="JPEG")
        output.seek(0)
        return output
    except OSError as err:
        logger.error("OSError occurred during image processing")
        raise err
