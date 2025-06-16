import tkinter as tk
from PIL import ImageGrab, ImageTk

def select_region():
    # スクリーンショット取得
    screen = ImageGrab.grab()
    screen_width, screen_height = screen.size

    # Tkウィンドウ初期化
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.deiconify()

    # Canvas初期化（この段階でrootが完全に構成済）
    canvas = tk.Canvas(root, width=screen_width, height=screen_height, cursor="cross")
    canvas.pack()

    # 📌 PhotoImageは、Canvas作成の後・root初期化完了後に生成
    tk_image = ImageTk.PhotoImage(screen, master=root)
    canvas.create_image(0, 0, anchor="nw", image=tk_image)
    canvas.image = tk_image  # 参照保持

    # マウス操作の準備
    start_x = start_y = 0
    rect = None
    region = {}

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_mouse_move(event):
        if rect:
            canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        x1, y1 = start_x, start_y
        x2, y2 = event.x, event.y
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            region["box"] = None
        else:
            region["box"] = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        root.quit()

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    # 実行
    root.mainloop()
    root.destroy()
    return region.get("box")
