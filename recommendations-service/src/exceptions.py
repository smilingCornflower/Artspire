class ArtNotFoundException(Exception):
    def __init__(self, art_id: int | None = None, message: str = "Art not found"):
        self.art_id = art_id
        if art_id is not None:
            self.message = f"{message}: {art_id}"
        else:
            self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
