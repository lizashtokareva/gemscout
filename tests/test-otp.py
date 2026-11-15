import uuid

from auth_service.security.otp import generate_otp, hash_otp, verify_otp


def test_generate_otp() -> None:
    code = generate_otp()
    assert len(code) == 6
    assert code.isdigit()


def test_verify_correct_otp() -> None:
    challenge_id = uuid.uuid4()
    code = "123456"

    code_hash = hash_otp(code, challenge_id)

    assert verify_otp(code, challenge_id, code_hash)


def test_verify_wrong_otp() -> None:
    challenge_id = uuid.uuid4()
    correct_code = "123456"
    wrong_code = "654321"

    code_hash = hash_otp(correct_code, challenge_id)

    assert verify_otp(wrong_code, challenge_id, code_hash) is False


def test_otp_with_wrong_challenge_id() -> None:
    challenge_id_1 = uuid.uuid4()
    challenge_id_2 = uuid.uuid4()

    code = "123456"
    code_hash = hash_otp(code, challenge_id_1)
    assert verify_otp(code, challenge_id_2, code_hash) is False
