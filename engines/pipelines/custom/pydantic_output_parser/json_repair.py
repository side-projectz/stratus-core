import json
from pydantic import ValidationError
from llama_index.core.output_parsers.pydantic import PydanticOutputParser


class JSONRepairPydanticOutputParser(PydanticOutputParser):
    def parse(self, text: str):
        try:
            return super().parse(text)
        except (ValidationError, json.JSONDecodeError):
            pass

        fixed_text = self._attempt_json_fix(text)
        try:
            return super().parse(fixed_text)
        except Exception as e:
            raise ValueError(
                f"Failed to fix JSON output.\n"
                f"Original text:\n{text}\n\nFixed text:\n{fixed_text}\nError: {e}"
            ) from e

    def _attempt_json_fix(self, raw_output: str) -> str:
        text = raw_output.strip()
        if text.startswith("```"):
            text = text.strip("`")

        text = text.replace(", ]", " ]")
        text = text.replace(", }", " }")

        open_brace_count = text.count("{")
        close_brace_count = text.count("}")
        if open_brace_count > close_brace_count:
            text += "}" * (open_brace_count - close_brace_count)
        elif close_brace_count > open_brace_count:
            text = text.rstrip("}")

        open_bracket_count = text.count("[")
        close_bracket_count = text.count("]")
        if open_bracket_count > close_bracket_count:
            text += "]" * (open_bracket_count - close_bracket_count)
        elif close_bracket_count > open_bracket_count:
            text = text.rstrip("]")

        return text
