import os
from PIL import Image

def images_to_pdf(image_dir, output_pdf_path):
    image_files = sorted(
        [f for f in os.listdir(image_dir) if f.lower().endswith(".png")]
    )

    if not image_files:
        print("❌ 画像ファイルが見つかりません")
        return

    image_paths = [os.path.join(image_dir, f) for f in image_files]
    images = [Image.open(p).convert("RGB") for p in image_paths]

    first, rest = images[0], images[1:]
    first.save(output_pdf_path, save_all=True, append_images=rest)
    print(f"✅ PDFを保存しました: {output_pdf_path}")
