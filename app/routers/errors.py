from fastapi.responses import JSONResponse

class ErrorResponse(JSONResponse):
    def __init__(self, code: str, message: str, status_code=400):
        super().__init__(
            status_code=status_code,
            content={"error": {"code": code, "message": message}}
        )