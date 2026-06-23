from errors import internal_server_error


def test_internal_server_error_handler():
    body, code = internal_server_error(Exception("boom"))
    assert code == 500
    assert body == {"error": "Internal Server Error"}
