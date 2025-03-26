import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from maker import make_watermark

save_path = ''
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        image_listbox.delete(0, tk.END)
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_listbox.insert(tk.END, os.path.join(folder_path, filename))

def preview_image(event):
    selected_index = image_listbox.curselection()
    if selected_index:
        image_path = image_listbox.get(selected_index)
        try:
            img = Image.open(image_path)
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            preview_label.config(image=photo)
            preview_label.image = photo
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片: {e}")

def export_image():
    selected_index = image_listbox.curselection()
    if selected_index:
        image_path = image_listbox.get(selected_index)
        try:
            img = Image.open(image_path)
            output_image_path = make_watermark(image_path)
            result_img = Image.open(output_image_path)
            default_name = os.path.basename(output_image_path)
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                         filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")],
                                         initialfile=default_name)
            if save_path:
                result_img.save(save_path)
                # 删除文件
                os.remove(output_image_path)

                if save_path:
                    img2 = Image.open(save_path)
                    img2.thumbnail((400, 400))
                    photo = ImageTk.PhotoImage(img2)
                    preview_label2.config(image=photo)
                    preview_label2.image = photo
        except Exception as e:
            messagebox.showerror("错误", f"导出图片时出错: {e}")


root = tk.Tk()
root.geometry("1200x900")
root.title("相机边框水印")

# 选择文件夹按钮
select_folder_button = tk.Button(root, text="选择文件夹", command=select_folder)
select_folder_button.pack(pady=10)

# 图片列表框
image_listbox = tk.Listbox(root, width=50)
image_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
image_listbox.bind("<<ListboxSelect>>", preview_image)

# 预览图片标签
preview_label = tk.Label(root)
preview_label.pack(anchor=tk.NE, padx=10, pady=10)

preview_label2 = tk.Label(root)
preview_label2.pack(anchor=tk.NE, padx=10, pady=10)

# 导出按钮
export_button = tk.Button(root, text="导出", command=export_image)
export_button.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
