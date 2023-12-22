from translation_god.helpers import diff_dict

def test_diff_dict():
    result = diff_dict({ "a": 1 }, {})
    assert result.get("a") == 1

    result = diff_dict({ "a": 1, "b": 2 }, {"b": 3 })
    assert result.get("a") == 1
    assert result.get("b") is None
