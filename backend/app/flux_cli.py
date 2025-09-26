import argparse
import asyncio
import os
from datetime import datetime
from typing import List

from .services_flux import FluxService


async def generate_and_save(prompt: str, *, count: int, output_dir: str, model: str | None, size: str | None, aspect: str | None, raw: bool | None) -> List[str]:
    service = FluxService()
    images = await service.generate_photos(prompt, count=count, model=model, size=size, aspect_ratio=aspect, raw=raw)
    if not images:
        return []

    os.makedirs(output_dir, exist_ok=True)
    saved_paths: List[str] = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for idx, content in enumerate(images, start=1):
        filename = f"flux_{timestamp}_{idx:02d}.png"
        path = os.path.join(output_dir, filename)
        with open(path, "wb") as f:
            f.write(content)
        saved_paths.append(path)
    return saved_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate images via Flux.1 Kontext and save to folder")
    parser.add_argument("prompt", type=str, help="Text prompt")
    parser.add_argument("--count", type=int, default=1, help="Number of images to generate")
    parser.add_argument("--out", type=str, default=os.path.join("data", "images"), help="Output directory")
    parser.add_argument("--model", type=str, default=None, help="Model name, e.g., flux.1-kontext-max")
    parser.add_argument("--size", type=str, default=None, help="Image size, e.g., 1024x1024")
    parser.add_argument("--aspect", type=str, default=None, help="Aspect ratio, e.g., 3:4 or 16:9")
    parser.add_argument("--raw", action="store_true", help="Enable RAW mode (BFL)")

    args = parser.parse_args()

    saved = asyncio.run(generate_and_save(args.prompt, count=args.count, output_dir=args.out, model=args.model, size=args.size, aspect=args.aspect, raw=args.raw))
    if not saved:
        print("No images generated.")
        raise SystemExit(1)
    print("Saved:")
    for p in saved:
        print(p)


if __name__ == "__main__":
    main()


