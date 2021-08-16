
class LoliconAPIError(Exception):
    pass
class PixivError(Exception):
    pass
class PixivNoSizeError(PixivError):
    pass

class LoliconAPIEmptyError(LoliconAPIError):
    pass

