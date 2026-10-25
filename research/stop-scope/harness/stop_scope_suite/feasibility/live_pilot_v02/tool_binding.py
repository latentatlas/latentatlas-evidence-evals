"""Resolve omitted arguments from the actual offered schema, never guesses."""

from copy import deepcopy
from jsonschema import Draft202012Validator


def normalized_arguments(name, arguments, schemas):
    matches = [s["function"] for s in schemas if s.get("type") == "function" and s["function"]["name"] == name]
    if len(matches) != 1 or name not in {"read_file", "write_file"}:
        raise ValueError("No unique offered tool schema")
    schema = matches[0]["parameters"]
    Draft202012Validator(schema).validate(arguments)
    if not set(arguments) <= set(schema["properties"]):
        raise ValueError("Unrecognized argument")
    result = deepcopy(arguments)
    for key, field in schema["properties"].items():
        if key not in result:
            if "default" not in field:
                raise ValueError("Missing argument without a declared default: " + key)
            result[key] = deepcopy(field["default"])
    Draft202012Validator(schema).validate(result)
    return result
