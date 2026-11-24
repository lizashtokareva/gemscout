import hashlib
import json


def calculate_request_hash(data: dict) -> str:
    serialized_data = json.dumps(data, sort_keys=True)
    request_hash = hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()

    return request_hash
