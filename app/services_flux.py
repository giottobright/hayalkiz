import asyncio
import base64
import json
from typing import List, Optional, Tuple, Dict, Any, Callable

import aiohttp

from .config import get_settings


class FluxService:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.flux_api_key or ""
        # Allows overriding via FLUX_API_URL, otherwise keeps placeholder
        self.endpoint = settings.flux_api_url or "https://api.flux-kontext-pro.example/generate"

    def _is_bfl(self) -> bool:
        return isinstance(self.endpoint, str) and "api.bfl.ai" in self.endpoint

    def _is_bfl_ultra(self) -> bool:
        return self._is_bfl() and self.endpoint.rstrip("/").endswith("/v1/flux-pro-1.1-ultra")

    def _is_bfl_kontext(self) -> bool:
        return self._is_bfl() and self.endpoint.rstrip("/").endswith("/v1/flux-kontext-pro")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "accept": "application/json"}
        if not self.api_key:
            return headers
        if self._is_bfl():
            headers["x-key"] = self.api_key
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _post_generate(self, session: aiohttp.ClientSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with session.post(self.endpoint, headers=self._headers(), json=payload, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            if resp.status >= 400:
                text = await resp.text()
                print(f"Flux POST error {resp.status}: {text}")
                resp.raise_for_status()
            # Try JSON; if not JSON, try to interpret as raw image
            ctype = resp.headers.get("Content-Type", "")
            if "application/json" in ctype:
                return await resp.json()
            content = await resp.read()
            # When raw image bytes are returned directly, wrap into JSON-like structure
            b64 = base64.b64encode(content).decode("utf-8")
            return {"images": [b64], "encoding": "base64"}

    async def _get(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        async with session.get(url, headers=self._headers(), timeout=aiohttp.ClientTimeout(total=120)) as resp:
            if resp.status >= 400:
                text = await resp.text()
                print(f"Flux GET error {resp.status}: {text}")
                resp.raise_for_status()
            return await resp.json()

    async def _download(self, session: aiohttp.ClientSession, url: str) -> bytes:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            resp.raise_for_status()
            return await resp.read()

    def _infer_status_url(self, task_id: str) -> Optional[str]:
        # Best-effort heuristic: replace trailing path with record-info
        # e.g., https://host/generate -> https://host/record-info/{task_id}
        if not self.endpoint:
            return None
        try:
            base = self.endpoint.rsplit("/", 1)[0]
            return f"{base}/record-info/{task_id}"
        except Exception:
            return None

    def _extract_image_bytes_from_response(self, data: Dict[str, Any]) -> List[bytes]:
        images: List[bytes] = []
        # Common patterns
        # 1) { images: [base64, ...] }
        if isinstance(data.get("images"), list) and data.get("encoding") == "base64":
            for b64 in data["images"]:
                try:
                    images.append(base64.b64decode(b64))
                except Exception:
                    pass
            return images
        # 2) { image: base64 }
        if isinstance(data.get("image"), str) and data.get("encoding") == "base64":
            try:
                images.append(base64.b64decode(data["image"]))
                return images
            except Exception:
                return []
        # 3) { images: [{ url: ..}, ...] }
        # This branch is handled by caller to download URLs
        return []

    async def generate_photo(self, prompt: str, *, model: Optional[str] = None, size: Optional[str] = None, aspect_ratio: Optional[str] = None, raw: Optional[bool] = None) -> Optional[bytes]:
        images = await self.generate_photos(prompt, count=1, model=model, size=size, aspect_ratio=aspect_ratio, raw=raw)
        return images[0] if images else None

    async def generate_photos(self, prompt: str, *, count: int = 1, model: Optional[str] = None, size: Optional[str] = None, aspect_ratio: Optional[str] = None, raw: Optional[bool] = None) -> List[bytes]:
        async with aiohttp.ClientSession() as session:
            if self._is_bfl():
                # BFL API: Kontext or Ultra
                async def one_image() -> Optional[bytes]:
                    payload: Dict[str, Any] = {"prompt": prompt}
                    # Ultra supports width/height and raw; Kontext uses aspect_ratio only
                    if self._is_bfl_ultra():
                        if size and "x" in size:
                            try:
                                w_s, h_s = size.lower().split("x", 1)
                                payload["width"], payload["height"] = int(w_s), int(h_s)
                            except Exception:
                                pass
                        if raw is not None:
                            payload["raw"] = bool(raw)
                    if aspect_ratio:
                        payload["aspect_ratio"] = aspect_ratio  # e.g., "3:4"
                    # Prefer png by default to avoid jpeg artifacts
                    payload["output_format"] = "png"

                    try:
                        start_resp = await self._post_generate(session, payload)
                    except Exception:
                        return None

                    polling_url = start_resp.get("polling_url")
                    task_id = start_resp.get("id")
                    # Poll using provided URL; fallback to heuristic if not present
                    status_url = polling_url or self._infer_status_url(str(task_id)) if task_id else None
                    if not status_url:
                        # Some providers may return direct URL or base64 even for BFL-like flow
                        direct = self._extract_image_bytes_from_response(start_resp)
                        if direct:
                            return direct[0]
                        url = start_resp.get("imageUrl") or start_resp.get("result", {}).get("sample")
                        if isinstance(url, str):
                            try:
                                return await self._download(session, url)
                            except Exception:
                                return None
                        return None

                    # Poll loop
                    for _ in range(120):  # up to ~60s at 0.5s or 120s at 1s
                        try:
                            info = await self._get(session, status_url)
                        except Exception:
                            await asyncio.sleep(0.5)
                            continue
                        status = (info.get("status") or info.get("state") or "").lower()
                        # BFL: Ready / Error / Failed
                        if status in {"ready", "completed", "succeeded", "success", "done"}:
                            # BFL result.sample
                            url = info.get("result", {}).get("sample")
                            if isinstance(url, str):
                                try:
                                    return await self._download(session, url)
                                except Exception:
                                    return None
                            # Fallbacks
                            if isinstance(info.get("imageUrl"), str):
                                try:
                                    return await self._download(session, info["imageUrl"])
                                except Exception:
                                    return None
                            decoded = self._extract_image_bytes_from_response(info)
                            if decoded:
                                return decoded[0]
                            return None
                        if status in {"failed", "error"}:
                            return None
                        await asyncio.sleep(0.5)
                    return None

                results = await asyncio.gather(*[one_image() for _ in range(max(1, count))])
                return [r for r in results if r]

            # Generic providers (previous behavior)
            model_name = model or "flux.1-kontext-max"
            request_payload = {
                "prompt": prompt,
                "model": model_name,
                "num_images": count,
            }
            if size:
                request_payload["size"] = size  # e.g., "1024x1024"
            if aspect_ratio:
                request_payload["aspect_ratio"] = aspect_ratio
            if raw is not None:
                request_payload["raw"] = bool(raw)

            try:
                data = await self._post_generate(session, request_payload)
            except Exception:
                return []

            # Direct base64 images
            direct_images = self._extract_image_bytes_from_response(data)
            if direct_images:
                return direct_images[:count]

            # Task-based API: look for taskId/id
            task_id = data.get("taskId") or data.get("id") or data.get("data", {}).get("id")
            polling_url = data.get("polling_url")
            if task_id or polling_url:
                status_url = polling_url or self._infer_status_url(str(task_id))
                if not status_url:
                    return []
                # Poll until completed or failed
                for _ in range(120):  # up to ~60s at 0.5s
                    try:
                        info = await self._get(session, status_url)
                    except Exception:
                        await asyncio.sleep(0.5)
                        continue
                    status = (info.get("status") or info.get("state") or "").lower()
                    if status in {"ready", "completed", "succeeded", "success", "done"}:
                        # Try URLs first
                        image_bytes: List[bytes] = []
                        # Possible shapes: BFL result.sample, { imageUrl: str } or { images: [{url: str}, ...] }
                        url = info.get("result", {}).get("sample")
                        if isinstance(url, str):
                            try:
                                image_bytes.append(await self._download(session, url))
                            except Exception:
                                pass
                        if isinstance(info.get("imageUrl"), str):
                            try:
                                image_bytes.append(await self._download(session, info["imageUrl"]))
                            except Exception:
                                pass
                        if isinstance(info.get("images"), list):
                            for item in info["images"]:
                                url = item.get("url") if isinstance(item, dict) else None
                                if url:
                                    try:
                                        image_bytes.append(await self._download(session, url))
                                    except Exception:
                                        pass
                        if image_bytes:
                            return image_bytes[:count]
                        # Or maybe base64 provided upon completion
                        decoded = self._extract_image_bytes_from_response(info)
                        if decoded:
                            return decoded[:count]
                        return []
                    if status in {"failed", "error"}:
                        return []
                    await asyncio.sleep(0.5)
                return []

            # URL-based immediate response
            if isinstance(data.get("imageUrl"), str):
                try:
                    content = await self._download(session, data["imageUrl"])
                    return [content]
                except Exception:
                    return []
            if isinstance(data.get("images"), list):
                image_bytes: List[bytes] = []
                for item in data["images"]:
                    url = item.get("url") if isinstance(item, dict) else None
                    if url:
                        try:
                            image_bytes.append(await self._download(session, url))
                        except Exception:
                            pass
                if image_bytes:
                    return image_bytes[:count]
            return []

    async def generate_photo_data_uri(self, prompt: str) -> Optional[str]:
        content = await self.generate_photo(prompt)
        if not content:
            return None
        b64 = base64.b64encode(content).decode("utf-8")
        return f"data:image/png;base64,{b64}"
