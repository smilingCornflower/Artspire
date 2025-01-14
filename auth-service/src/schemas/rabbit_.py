from .base_ import CustomBaseModel


class S3AddResponse(CustomBaseModel):
    status: int
    blob_name: str


class S3AddSchema(CustomBaseModel):
    img_base64: str  # base64 encoded an image file
    img_type: str
    blob_name: str


class S3GetSchema(CustomBaseModel):
    blob_name: str


class S3GetResponse(CustomBaseModel):
    status: int
    img_url: str
