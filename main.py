# main.py
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import whisper

# Trích xuất âm thanh từ video
def extract_audio(video_path, audio_path):
    status_var.set("Đang tách âm thanh từ video...")
    root.update_idletasks()
    subprocess.run([
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Chọn file input
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Media files", "*.mp4 *.mp3 *.wav")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

# Tạo subtitle và văn bản
def generate_files():
    input_path = entry_file.get()
    
    if not input_path:
        messagebox.showerror("Lỗi", "Vui lòng chọn file!")
        return
    
    try:
        whisper_model = whisper.load_model("base")
        audio_path = "temp_audio.wav"
        base_path = os.path.splitext(input_path)[0]
        srt_path = base_path + ".srt"
        txt_path = base_path + ".txt"
        
        # Cập nhật trạng thái
        status_var.set("Đang chuẩn bị xử lý...")
        root.update_idletasks()
        
        if input_path.endswith(('.mp4', '.mkv', '.avi')):
            status_var.set("Đang tách âm thanh từ video...")
            root.update_idletasks()
            extract_audio(input_path, audio_path)
        else:
            audio_path = input_path
        
        # Xử lý với Whisper
        status_var.set("Đang xử lý file âm thanh với Whisper...")
        root.update_idletasks()
        result = whisper_model.transcribe(audio_path)
        
        # Xuất file SRT
        status_var.set("Đang tạo file subtitle (SRT)...")
        root.update_idletasks()
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments']):
                start = segment['start']
                end = segment['end']
                text = segment['text']
                
                f.write(f"{i+1}\n")
                f.write(f"{format_time(start)} --> {format_time(end)}\n")
                f.write(f"{text}\n\n")
        
        # Xuất file TXT
        status_var.set("Đang tạo file văn bản (TXT)...")
        root.update_idletasks()
        with open(txt_path, 'w', encoding='utf-8') as f:
            for segment in result['segments']:
                text = segment['text']
                f.write(f"{text}\n")
        
        messagebox.showinfo("Thành công", f"Subtitle đã được lưu tại:\n{srt_path}\nVăn bản đã được lưu tại:\n{txt_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
    finally:
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
        status_var.set("Hoàn tất.")
        root.update_idletasks()

# Định dạng thời gian cho file .srt
def format_time(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

# GUI
root = tk.Tk()
root.title("Subtitle & Text Generator")

tk.Label(root, text="Chọn file âm thanh/video:").pack(pady=5)
entry_file = tk.Entry(root, width=50)
entry_file.pack(pady=5)
tk.Button(root, text="Chọn File", command=select_file).pack(pady=5)

tk.Button(root, text="Tạo Subtitle & Văn Bản", command=generate_files, bg="green", fg="white").pack(pady=20)

# Thanh trạng thái
status_var = tk.StringVar(value="Sẵn sàng")
status_label = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor='w')
status_label.pack(fill='x', pady=5, padx=5)

root.mainloop()
