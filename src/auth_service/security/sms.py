import uuid
from typing import Protocol


class OTPSender(Protocol):
    async def send_code(
        self,
        user_id: uuid.UUID,
        code: str,
    ) -> None: ...
