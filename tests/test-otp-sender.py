import uuid

import pytest

from tests.fakes import FakeOTPSender


@pytest.mark.asyncio
async def test_fake_otp_sender() -> None:
    sender = FakeOTPSender()
    user_id = uuid.uuid4()
    code = "123456"

    await sender.send_code(user_id, code)

    assert sender.sent_codes[user_id] == code
