"""JSON response module."""

from typing import Any
from fastapi.responses import JSONResponse


class CustomJSONResponse(JSONResponse):
    """Custom JSON response."""

    def render(self, content: Any) -> bytes:
        """Render response content."""
        if isinstance(content, dict) and not content.get("error"):
            content = {"data": content}
        return super().render(content)
