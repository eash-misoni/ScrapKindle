import os
import time
import datetime
import pyautogui
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageGrab

# GUIでスクリーンショット範囲を選ぶ
def select_area():
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showinfo("範囲選択", "スクショ範囲をドラッグしてください")
    bbox = pyautogui.screenshot().getbbox()  # デフォルトの全画面
    rect = pyautogui.selectRegion()  # 任意のGUIで選ぶなら別途実装必要
    return rect if rect else bbox

# ゼロ埋め桁数を決める関数
def get_zero_padding(n):
    return len(str(n))

# タイムスタンプ付きの出力先フォルダ作成
def make_output_folder():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = os.path.join("output", timestamp, "images")
    os.makedirs(path, exist_ok=True)
    return path

# スクリーンショットを撮って保存
def take_screenshots(region, total_pages, delay, outdir):
    pad_len = get_zero_padding(total_pages)
    for i in range(1, total_pages + 1):
        time.sleep(delay)
        screenshot = ImageGrab.grab(bbox=region)
        filename = f"page_{str(i).zfill(pad_len)}.png"
        screenshot.save(os.path.join(outdir, filename))
        print(f"Saved: {filename}")

# main処理
def main():
    # GUI入力
    root = tk.Tk()
    root.withdraw()
    total_pages = simpledialog.askinteger("ページ数", "何ページ分キャプチャしますか？")
    delay = simpledialog.askfloat("ディレイ", "1ページごとの待機秒数は？")

    # 矩形選択（仮）※要実装 or 代替
    region = pyautogui.selectRegion()  # 実際には未実装。暫定的な選択手法に置き換えてください

    # 保存処理
    outdir = make_output_folder()
    take_screenshots(region, total_pages, delay, outdir)

if __name__ == "__main__":
    main()
