#coding: utf-8

import json
from enum import Enum

class State(Enum):
    OUT = 1
    JSON_INNER = 2
    JSON_INNER_STR_START = 3
    JSON_INNER_STR_END = 4


def skip_whitespace(cursor, content):
    content_len = len(content)
    while True:
        if cursor >= content_len:
            break

        c = content[cursor]

        if c.isspace():
            cursor = cursor + 1
        else:
            break;

        # cursor point to alpha or EOF
    return cursor

def advance(cursor,content):
    """
    forward cursor, point to next char,
    return next char cursor or None
    """
    return None if cursor >= (len(content)-1) else cursor-1

def prev_char(cursor, content):
    """
    return previous char or None
    """
    return None if cursor <= 0 else content[cursor-1]

def prev_backslash_count(cursor, content):
    """
    number of previous '\'
    """
    count = 0
    c = prev_char(cursor, content)
    cursor = cursor - 1

    while c == '\\':
        count = count + 1
        c = prev_char(cursor, content)
        cursor = cursor - 1

    return count


def pick_json(content):
    """
    Pick all json objects from content
    """
    result = []

    state = State.OUT
    cursor = 0
    content_len = len(content)

    json_start_index = -1
    json_end_index = -1

    while cursor < content_len:
        char = content[cursor]
        if state == State.OUT:
            # we search {, else ignore;
            # when meet {, change state to State.INNER
            if char == '{':
                state = State.JSON_INNER
                json_start_index = cursor

        elif state == State.JSON_INNER:
            if char == "\"":
                state = State.JSON_INNER_STR_START

            if char == "}":
                # pick json
                json_end_index = cursor

                json_str = content[json_start_index:json_end_index+1]
                print(f"{json_str=}")
                result.append(json.loads(json_str))
                state = State.OUT

        elif state == State.JSON_INNER_STR_START:
            if char == "\"":
                backslash_count = prev_backslash_count(cursor, content)

                if backslash_count % 2 == 0:
                    state = State.JSON_INNER_STR_END

        elif state == State.JSON_INNER_STR_END:
            state = State.JSON_INNER
            continue

        # advance cursor
        cursor = cursor + 1
        cursor = skip_whitespace(cursor, content)

    return result


if __name__ == "__main__":
    pass
