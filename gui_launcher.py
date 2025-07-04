import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import re
from datetime import datetime
import time
from PIL import ImageGrab, Image
import pyautogui

from region_selector import select_region

# ===== スクショ保存・PDF作成 =====

def sanitize_filename(filename):
    # ファイル名に使えない文字を除去
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

def get_zero_padding(n):
    return len(str(n))

def make_output_folder():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = os.path.join("output", timestamp)
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    return output_dir, images_dir, timestamp

def take_screenshots(region, total_pages, delay, countdown, outdir, page_key):
    print(f"📦 出力先: {outdir}")
    pad_len = get_zero_padding(total_pages)

    print(f"⏳ カウントダウン（{countdown}秒）...")
    for i in reversed(range(1, countdown + 1)):
        print(f"{i}...")
        time.sleep(1)

    for i in range(1, total_pages + 1):
        time.sleep(delay)
        screenshot = ImageGrab.grab(bbox=region)
        filename = f"page_{str(i).zfill(pad_len)}.png"
        screenshot.save(os.path.join(outdir, filename))
        print(f"📸 Saved: {filename}")
        if i != total_pages:
            pyautogui.press(page_key)  # ページ送りキーを押す

def images_to_pdf(image_dir, output_pdf_path):
    try:
        image_files = sorted(f for f in os.listdir(image_dir) if f.lower().endswith(".png"))
        image_paths = [os.path.join(image_dir, f) for f in image_files]
        images = [Image.open(p).convert("RGB") for p in image_paths]
        if not images:
            raise ValueError("画像がありません。")
        first, rest = images[0], images[1:]
        first.save(output_pdf_path, save_all=True, append_images=rest)
        print(f"📕 PDF作成完了: {output_pdf_path}")
    except Exception as e:
        raise RuntimeError(f"PDF作成中にエラー: {e}")
# ===== GUI本体 =====

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Kindle Screenshot GUI")
        self.region = None

        # 入力フォーム
        # ページ数
        tk.Label(root, text="ページ数:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.page_entry = tk.Entry(root)
        self.page_entry.grid(row=0, column=1, sticky="we", padx=5, pady=2)

        # ディレイ
        tk.Label(root, text="ディレイ（秒）:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.delay_entry = tk.Entry(root)
        self.delay_entry.grid(row=1, column=1, sticky="we", padx=5, pady=2)

        # カウントダウン
        tk.Label(root, text="カウントダウン:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.countdown_scale = tk.Scale(root, from_=1, to=10, orient="horizontal")
        self.countdown_scale.set(3)
        self.countdown_scale.grid(row=2, column=1, sticky="we", padx=5, pady=2)

        # 範囲ラベル（右側に並べる）
        self.range_label = tk.Label(root, text="未選択")
        self.range_label.grid(row=2, column=2, rowspan=2, sticky="w", padx=5)

        # PDFファイル名
        tk.Label(root, text="PDFファイル名:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.pdf_name_entry = tk.Entry(root)
        self.pdf_name_entry.grid(row=3, column=1, sticky="we", padx=5, pady=2)

        # ページ送りキー入力欄
        tk.Label(root, text="ページ送りキー\n（例: Right, PageDown, Space）").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.page_key_entry = tk.Entry(root)
        self.page_key_entry.insert(0, "Right")  # デフォルトは右キー
        self.page_key_entry.grid(row=4, column=1, sticky="we", padx=5, pady=2)

        # 範囲選択ボタン（右）
        tk.Button(root, text="範囲を選ぶ", command=self.choose_region).grid(row=4, column=2, padx=5, pady=2)

        # 📂 PDF作成後にフォルダを開くチェックボックス
        self.open_folder_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="PDF作成後にフォルダを開く", variable=self.open_folder_var).grid(
            row=5, column=0, sticky="w", padx=5, pady=10
        )

        # 開始ボタン（青くしないなら普通のボタン）
        tk.Button(root, text="開始", command=self.start_capture).grid(
            row=5, column=1, sticky="e", padx=5, pady=10
        )

        # 閉じるボタン
        tk.Button(root, text="閉じる", command=root.destroy).grid(
            row=5, column=2, sticky="w", padx=5, pady=10
        )
        # 列拡張設定
        root.grid_columnconfigure(1, weight=1)

    def choose_region(self):
        self.region = select_region()
        self.range_label.config(text=f"範囲: {self.region}" if self.region else "未選択")

    def start_capture(self):
        try:
            total_pages = int(self.page_entry.get())
            delay = float(self.delay_entry.get())
            countdown = int(self.countdown_scale.get())
        except ValueError:
            messagebox.showerror("入力エラー", "数値の入力に誤りがあります。")
            return

        if not self.region:
            messagebox.showerror("範囲未選択", "スクショ範囲を指定してください。")
            return

        pdfname = self.pdf_name_entry.get().strip()
        output_dir, image_dir, timestamp = make_output_folder()
        if not pdfname:
            pdfname = timestamp
        pdfname = sanitize_filename(pdfname)
        if not pdfname.lower().endswith(".pdf"):
            pdfname += ".pdf"

        # ページ送りキーの取得
        page_key = self.page_key_entry.get().strip() or "Right"

        try:
            take_screenshots(self.region, total_pages, delay, countdown, image_dir, page_key)
            images_to_pdf(image_dir, os.path.join(output_dir, pdfname))
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            return

        if self.open_folder_var.get():
            try:
                subprocess.run(["open", output_dir])
            except Exception as e:
                print("フォルダを開けませんでした:", e)

        self.root.destroy()
# ===== 実行 =====
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
