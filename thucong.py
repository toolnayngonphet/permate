import string
from random import choice, choices, shuffle, randint
from time import sleep
import tkinter as tk
from tkinter import messagebox
from requests import get, post

# Giả định rằng bạn có các file:
# ho_vietnam.txt, ten_vietnam.txt, mo_ta_ve_ban.txt, mo_ta_ads.txt,
# ref.txt, email.txt
# trong cùng thư mục với file script Python này.

# Đọc danh sách họ tên
try:
    with open("ho_vietnam.txt", "r", encoding="utf-8") as f:
        ds_ho = [line.strip() for line in f if line.strip()]
    with open("ten_vietnam.txt", "r", encoding="utf-8") as f:
        ds_ten = [line.strip() for line in f if line.strip()]
except FileNotFoundError as e:
    messagebox.showerror("Lỗi File", f"Không tìm thấy file cần thiết: {e.filename}\nVui lòng đảm bảo các file 'ho_vietnam.txt' và 'ten_vietnam.txt' tồn tại.")
    exit()


# Cấu hình CAPTCHA
API_KEY_2CAPTCHA = "66c35ed461013e2e864dc603c3322523" # Thay bằng API key của bạn
SITE_KEY = "6LffITgpAAAAAMdr7L8asMGE0qitwVuLgS3xHYQp"   # Sitekey của trang web mục tiêu

# Hàm giải captcha
def solve_captcha_2captcha(url_str):
    if not url_str:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập URL của trang web cần giải captcha.")
        return
    try:
        captcha_result.set("Đang gửi captcha...")
        root.update()

        res = post("http://2captcha.com/in.php", data={
            "key": API_KEY_2CAPTCHA,
            "method": "userrecaptcha",
            "googlekey": SITE_KEY,
            "pageurl": url_str,
            "json": 1
        }).json()

        if res["status"] != 1:
            raise Exception("Gửi captcha thất bại: " + res.get("request", ""))

        request_id = res["request"]
        captcha_result.set("Đang đợi kết quả từ 2Captcha...")
        root.update()

        for _ in range(24):
            sleep(5)
            check = get(f"http://2captcha.com/res.php?key={API_KEY_2CAPTCHA}&action=get&id={request_id}&json=1").json()
            if check["status"] == 1:
                token = check["request"]
                captcha_result.set(token)
                messagebox.showinfo("Captcha", "✅ Captcha đã giải xong")

# ================== SHOW CODE JS LÊN ĐỂ DÙNG DEVTOOLS =============================

#                 js_code = f"""
# // ✅ Dán đoạn này vào DevTools Console sau khi Captcha đã render
# const token_captcha = "{token}";
# document.getElementById("g-recaptcha-response").innerHTML = token_captcha;
# const recaptchaField = document.querySelector("#g-recaptcha-response");
# if (recaptchaField) {{
#     const event = new Event('input', {{ bubbles: true }});
#     recaptchaField.dispatchEvent(event);
#     console.log("✅ Token captcha đã được gán và sự kiện đã được dispatch");
# }} else {{
#     console.warn("❌ Không tìm thấy thẻ #g-recaptcha-response");
# }}"""
#                 show_code_window(js_code)

# ================== SHOW CODE JS LÊN ĐỂ DÙNG DEVTOOLS =============================

                page_url.set("")
                return
            captcha_result.set("...Đang đợi captcha...")
            root.update()

        captcha_result.set("❌ Hết thời gian chờ captcha")
    except Exception as e:
        captcha_result.set("❌ Lỗi: " + str(e))
        messagebox.showerror("Lỗi Captcha", str(e))


def show_code_window(code):
    popup = tk.Toplevel(root)
    popup.title("📋 JavaScript để dùng trong DevTools")
    popup.geometry("600x300")
    tk.Label(popup, text="Dán đoạn này vào DevTools Console:", font=("Arial", 10, "bold")).pack(pady=5)
    txt = tk.Text(popup, wrap="word", font=("Consolas", 10))
    txt.insert("1.0", code.strip())
    txt.pack(expand=True, fill="both", padx=10, pady=5)
    txt.config(state="normal")
    txt.focus_set()

# ===== HÀM SAO CHÉP ĐƯỢC NÂNG CẤP =====
def copy_to_clipboard(event):
    """Sao chép nội dung của widget được click vào clipboard."""
    widget = event.widget
    text_to_copy = widget.get()
    
    if text_to_copy and not text_to_copy.startswith("Lỗi:"):
        root.clipboard_clear()
        root.clipboard_append(text_to_copy)
        
        original_text = text_to_copy
        original_state = widget.cget('state') # Lưu trạng thái gốc ('normal' hoặc 'readonly')
        
        widget.config(state='normal')
        widget.delete(0, tk.END)
        widget.insert(0, "✅ Đã sao chép!")
        widget.config(state='readonly')
        
        # Lên lịch khôi phục, truyền cả trạng thái gốc vào
        root.after(1000, lambda: restore_text(widget, original_text, original_state))

def restore_text(widget, text, state):
    """Khôi phục lại văn bản và trạng thái gốc cho widget."""
    widget.config(state='normal')
    widget.delete(0, tk.END)
    widget.insert(0, text)
    widget.config(state=state) # Khôi phục lại trạng thái gốc
# ===============================================

# Các hàm sinh dữ liệu
def ho():
    return choice(ds_ho)

def ten():
    return choice(ds_ten)

def sdt():
    dau_so = [
        "32", "33", "34", "35", "36", "37", "38", "39",
        "70", "76", "77", "78", "79",
        "81", "82", "83", "84", "85",
    ]
    return choice(dau_so) + ''.join(choices("0123456789", k=7))

def password(length=None):
    """
    Tạo mật khẩu ngẫu nhiên, dài từ 8-16 ký tự.
    Ưu tiên chữ và số nhiều hơn ký tự đặc biệt.
    """
    if length is None:
        length = randint(8, 16)

    # 1. Định nghĩa các bộ ký tự
    lowercase_chars = string.ascii_lowercase
    uppercase_chars = string.ascii_uppercase
    digits_chars = string.digits
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    
    # 2. Đảm bảo có ít nhất một ký tự từ mỗi bộ
    guaranteed_chars = [
        choice(lowercase_chars),
        choice(uppercase_chars),
        choice(digits_chars),
        choice(special_chars)
    ]
    
    # 3. Tạo một bộ ký tự "ưu tiên" để lấp đầy phần còn lại
    #    Bằng cách lặp lại chữ và số, chúng sẽ có xác suất được chọn cao hơn.
    #    Ví dụ: Lặp lại 3 lần để tăng xác suất lên 3 lần.
    weighted_pool = (lowercase_chars + uppercase_chars + digits_chars) * 3 + special_chars
    
    # 4. Lấp đầy phần còn lại của mật khẩu từ bộ ký tự đã được ưu tiên
    remaining_length = length - len(guaranteed_chars)
    remaining_chars = choices(weighted_pool, k=remaining_length)
    
    # 5. Kết hợp và xáo trộn
    password_list = guaranteed_chars + remaining_chars
    shuffle(password_list)
    
    # 6. Trả về kết quả
    return "".join(password_list)

def visit():
    return choice(range(500, 10001, 10))

def username():
    try:
        data = get("https://tienichhay.net/ho-so-ngau-nhien.html").text
        return data.split("Username</td>\n\t\t\t\t<td><strong>")[1].split("</strong></td>")[0]
    except:
        return "Không thể lấy"

def address():
    try:
        data = get("https://tienichhay.net/ho-so-ngau-nhien.html").text
        return data.split("Địa chỉ đầy đủ</td>\n\t\t\t<td><strong>")[1].split("</strong></td>")[0]
    except:
        return "Không thể lấy"

def bio():
    try:
        with open("mo_ta_ve_ban.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            return choice(lines).strip().split(". ", 1)[1]
    except FileNotFoundError:
        return "Lỗi: Không tìm thấy file 'mo_ta_ve_ban.txt'"
    except Exception as e:
        return f"Lỗi khi đọc file: {e}"

def ads_desc():
    try:
        with open("mo_ta_ads.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            return choice(lines).strip().split(". ", 1)[1]
    except FileNotFoundError:
        return "Lỗi: Không tìm thấy file 'mo_ta_ads.txt'"
    except Exception as e:
        if isinstance(e, IndexError):
            with open("mo_ta_ads.txt", "r", encoding="utf-8") as f:
                 return choice(f.readlines()).strip()
        return f"Lỗi khi đọc file: {e}"

def read_ref():
    try:
        with open("ref.txt", "r", encoding="utf-8") as f:
            return f.readline().strip()
    except FileNotFoundError:
        return "Lỗi: Không tìm thấy file 'ref.txt'"
    except Exception as e:
        return f"Lỗi đọc file: {e}"

def read_email():
    try:
        with open("email.txt", "r", encoding="utf-8") as f:
            return f.readline().strip()
    except FileNotFoundError:
        return "Lỗi: Không tìm thấy file 'email.txt'"
    except Exception as e:
        return f"Lỗi đọc file: {e}"

# Giao diện Tkinter
root = tk.Tk()
root.title("Trình tạo dữ liệu & giải Captcha")
root.geometry("550x800")
root.resizable(False, False)

# --- Phần tạo dữ liệu ngẫu nhiên ---
fields = [
    ("Tên", "ten"),
    ("Họ", "ho"),
    ("SĐT", "sdt"),
    ("Mật khẩu", "password"),
    ("Địa chỉ", "address"),
    ("Giới thiệu", "bio"),
    ("Username", "username"),
    ("Lượt truy cập", "visit"),
    ("Mô tả ads", "ads_desc"),
]

vars = {}
# ===== CẬP NHẬT VÒNG LẶP ĐỂ GÁN SỰ KIỆN CHO TẤT CẢ CÁC Ô =====
for idx, (label, key) in enumerate(fields):
    tk.Label(root, text=label + ":").grid(row=idx, column=0, sticky="e", padx=10, pady=5)
    var = tk.StringVar()
    
    # Tạo widget Entry
    if key in ["bio", "ads_desc"]:
        entry_widget = tk.Entry(root, textvariable=var, width=60)
        entry_widget.grid(row=idx, column=1, pady=5, ipady=10)
    else:
        entry_widget = tk.Entry(root, textvariable=var, width=60)
        entry_widget.grid(row=idx, column=1, pady=5)
    
    # Gán sự kiện click-to-copy cho widget vừa tạo
    entry_widget.bind("<Button-1>", copy_to_clipboard)
    
    vars[key] = var
# =============================================================

def tao_du_lieu():
    try:
        vars["ten"].set(ten())
        vars["ho"].set(ho())
        vars["sdt"].set(sdt())
        vars["password"].set(password())
        vars["address"].set(address())
        vars["bio"].set(bio())
        vars["username"].set(username())
        vars["visit"].set(visit())
        vars["ads_desc"].set(ads_desc())
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

current_row = len(fields)
tk.Button(root, text="Tạo dữ liệu ngẫu nhiên", command=tao_du_lieu, bg="#4CAF50", fg="white", width=25)\
    .grid(row=current_row, column=0, columnspan=2, pady=15)

# --- Phần giải captcha ---
current_row += 1
tk.Label(root, text="URL Trang cần giải Captcha:").grid(row=current_row, column=0, sticky="e", padx=10, pady=5)
page_url = tk.StringVar()
tk.Entry(root, textvariable=page_url, width=60).grid(row=current_row, column=1, pady=5)

current_row += 1
tk.Button(root, text="Giải Captcha", bg="#2196F3", fg="white", width=25,
          command=lambda: solve_captcha_2captcha(page_url.get()))\
    .grid(row=current_row, column=0, columnspan=2, pady=10)

current_row += 1
tk.Label(root, text="Kết quả Captcha (token):").grid(row=current_row, column=0, sticky="e", padx=10, pady=5)
captcha_result = tk.StringVar()
captcha_entry = tk.Entry(root, textvariable=captcha_result, width=60, state='readonly')
captcha_entry.grid(row=current_row, column=1, pady=5)
captcha_entry.bind("<Button-1>", copy_to_clipboard)

# ===== HIỂN THỊ DỮ LIỆU VÀ GÁN SỰ KIỆN CLICK-TO-COPY =====
# Dòng ngăn cách
current_row += 1
tk.Frame(height=2, bd=1, relief=tk.SUNKEN).grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=10)

# Trường REF
current_row += 1
tk.Label(root, text="REF:").grid(row=current_row, column=0, sticky="e", padx=10, pady=5)
ref_var = tk.StringVar()
ref_var.set(read_ref())
ref_entry = tk.Entry(root, textvariable=ref_var, width=60, state='readonly', relief=tk.FLAT)
ref_entry.grid(row=current_row, column=1, pady=5)
ref_entry.bind("<Button-1>", copy_to_clipboard)

# Trường EMAIL
current_row += 1
tk.Label(root, text="EMAIL:").grid(row=current_row, column=0, sticky="e", padx=10, pady=5)
email_var = tk.StringVar()
email_var.set(read_email())
email_entry = tk.Entry(root, textvariable=email_var, width=60, state='readonly', relief=tk.FLAT)
email_entry.grid(row=current_row, column=1, pady=5)
email_entry.bind("<Button-1>", copy_to_clipboard)
# ===============================================

root.mainloop()