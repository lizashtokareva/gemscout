import uuid


class FakeOTPSender:
    def __init__(self) -> None:
        self.sent_codes = {}

    async def send_code(self, user_id: uuid.UUID, code: str) -> None:
        self.sent_codes[user_id] = code
