import io
from typing import BinaryIO
from config import logger

from PIL import Image


async def convert_to_jpg(upload_file: BinaryIO) -> BinaryIO:
    logger.info("STARTED convert_to_jpg()")
    try:
        image = Image.open(upload_file)
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        output = io.BytesIO()
        image.save(output, format="JPEG")
        output.seek(0)
        return output

    except OSError as err:
        logger.critical("OSError occurred during image processing: %s", err)
        raise err
