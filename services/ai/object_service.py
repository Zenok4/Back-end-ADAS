import httpx
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode
from config import AI_SERVER_URL, async_client


class ObjectService:
    def __init__(self):
        self.ai_server_url = f"{AI_SERVER_URL.rstrip('/')}/object/predict"

    async def predict_object(
        self,
        image_base64: str,
        session_id: str | None = None,
        ego_state: dict | None = None,
        camera: dict | None = None,
    ):
        payload = {
            "image_base64": image_base64
        }

        if session_id is not None:
            payload["session_id"] = session_id

        if ego_state is not None:
            payload["ego_state"] = ego_state

        if camera is not None:
            payload["camera"] = camera

        try:
            resp = await async_client.post(
                self.ai_server_url,
                json=payload,
                timeout=5.0
            )

            if resp.status_code != 200:
                return response_error(
                    code=HttpCode.bad_request,
                    message="AI server returned error"
                )

            data = resp.json()

            return response_success(
                data=data,
                key="data",
                message="Analyze object success",
                code=HttpCode.success
            )

        except httpx.RequestError as e:
            return {
                "error": f"Failed to connect to AI server: {str(e)}",
                "url": self.ai_server_url
            }
