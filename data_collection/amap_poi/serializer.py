import json


def dict_to_bytes(key_data: dict):
    return json.dumps(key_data).encode('utf-8')


def bytes_to_dict(byte_data: bytes):
    return json.loads(byte_data.decode('utf-8'))
