"""
แพลตฟอร์มจองค่ายในประเทศไทย
Camp Booking Platform for Thailand
"""

import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import qrcode
import json
import os
from datetime import datetime
from io import BytesIO

# ตั้งค่าธีมและสี
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Application state
root = None
camps = []
bookings = []
notifications = []
users_file = 'users.json'
users = {}
current_user = None


def load_data():
    global camps, bookings, notifications
    try:
        if os.path.exists('camps_data.json'):
            with open('camps_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                camps = data.get('camps', [])
                bookings = data.get('bookings', [])
                notifications = data.get('notifications', [])
    except Exception as e:
        print(f"Error loading data: {e}")


def save_data():
    global camps, bookings, notifications
    try:
        data = {'camps': camps, 'bookings': bookings, 'notifications': notifications}
        with open('camps_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")


def load_users():
    global users
    users = {}
    try:
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                # normalize user entries: support legacy string-password and new dict format
                for uname, val in raw.items():
                    if isinstance(val, dict):
                        users[uname] = val
                    else:
                        users[uname] = {
                            'password': val,
                            'fullname': '',
                            'phone': '',
                            'email': ''
                        }
    except Exception as e:
        print(f"Error loading users: {e}")


def save_users():
    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")


def show_login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    frame = ctk.CTkFrame(root)
    frame.pack(fill='both', expand=True, padx=40, pady=60)

    title = ctk.CTkLabel(frame, text='เข้าสู่ระบบ / ลงทะเบียน', font=ctk.CTkFont(size=28, weight='bold'))
    title.pack(pady=10)

    form = ctk.CTkFrame(frame)
    form.pack(pady=20)

    ctk.CTkLabel(form, text='ชื่อผู้ใช้:').grid(row=0, column=0, sticky='e', padx=6, pady=6)
    username_entry = ctk.CTkEntry(form, width=300)
    username_entry.grid(row=0, column=1, padx=6, pady=6)

    ctk.CTkLabel(form, text='รหัสผ่าน:').grid(row=1, column=0, sticky='e', padx=6, pady=6)
    password_entry = ctk.CTkEntry(form, width=300, show='*')
    password_entry.grid(row=1, column=1, padx=6, pady=6)

    btn_frame = ctk.CTkFrame(frame)
    btn_frame.pack(pady=16)

    login_btn = ctk.CTkButton(btn_frame, text='Login', width=120, command=lambda: attempt_login(username_entry.get().strip(), password_entry.get().strip()))
    login_btn.grid(row=0, column=0, padx=10)

    register_btn = ctk.CTkButton(btn_frame, text='Register', width=120, command=show_register_dialog)
    register_btn.grid(row=0, column=1, padx=10)



def attempt_login(username, password):
    global current_user
    if not username or not password:
        messagebox.showerror('Error', 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
        return
    stored = users.get(username)
    valid = False
    if stored:
        if isinstance(stored, dict):
            valid = stored.get('password') == password
        else:
            valid = stored == password

    if valid:
        current_user = username
        messagebox.showinfo('สำเร็จ', f'ยินดีต้อนรับ {username}')
        create_main_interface()
    else:
        messagebox.showerror('ล้มเหลว', 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')


def show_register_dialog():
    dialog = ctk.CTkToplevel(root)
    dialog.title('Register')
    dialog.geometry('420x260')
    dialog.grab_set()

    ctk.CTkLabel(dialog, text='สร้างบัญชีใหม่', font=ctk.CTkFont(size=18, weight='bold')).pack(pady=12)

    f = ctk.CTkFrame(dialog)
    f.pack(pady=8)
    ctk.CTkLabel(f, text='ชื่อผู้ใช้:').grid(row=0, column=0, sticky='e', padx=6, pady=6)
    u = ctk.CTkEntry(f, width=300)
    u.grid(row=0, column=1, padx=6, pady=6)
    ctk.CTkLabel(f, text='รหัสผ่าน:').grid(row=1, column=0, sticky='e', padx=6, pady=6)
    p = ctk.CTkEntry(f, width=300, show='*')
    p.grid(row=1, column=1, padx=6, pady=6)
    ctk.CTkLabel(f, text='ชื่อ-นามสกุล:').grid(row=2, column=0, sticky='e', padx=6, pady=6)
    fullname_entry = ctk.CTkEntry(f, width=300)
    fullname_entry.grid(row=2, column=1, padx=6, pady=6)
    ctk.CTkLabel(f, text='เบอร์โทร:').grid(row=3, column=0, sticky='e', padx=6, pady=6)
    phone_entry = ctk.CTkEntry(f, width=300)
    phone_entry.grid(row=3, column=1, padx=6, pady=6)
    ctk.CTkLabel(f, text='อีเมล:').grid(row=4, column=0, sticky='e', padx=6, pady=6)
    email_entry = ctk.CTkEntry(f, width=300)
    email_entry.grid(row=4, column=1, padx=6, pady=6)

    def do_register():
        username = u.get().strip()
        password = p.get().strip()
        if not username or not password:
            messagebox.showerror('Error', 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
            return
        if username in users:
            messagebox.showerror('Error', 'ชื่อผู้ใช้นี้มีอยู่แล้ว')
            return
        users[username] = {
            'password': password,
            'fullname': fullname_entry.get().strip(),
            'phone': phone_entry.get().strip(),
            'email': email_entry.get().strip()
        }
        save_users()
        messagebox.showinfo('สำเร็จ', 'สร้างบัญชีเรียบร้อย')
        dialog.destroy()

    ctk.CTkButton(dialog, text='สร้างบัญชี', command=do_register, width=200).pack(pady=12)


def create_main_interface():
    for widget in root.winfo_children():
        widget.destroy()

    title_frame = ctk.CTkFrame(root, fg_color="#2E7D32", height=100)
    title_frame.pack(fill="x", padx=0, pady=0)

    title_label = ctk.CTkLabel(title_frame, text="🏕️ แพลตฟอร์มจองค่ายในประเทศไทย", font=ctk.CTkFont(size=32, weight="bold"), text_color="white")
    title_label.pack(pady=25)

    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=30)

    user_btn = ctk.CTkButton(button_frame, text="👤 หน้าผู้ใช้ (จองค่าย)", command=show_user_interface, width=250, height=60, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#1976D2", hover_color="#1565C0")
    user_btn.grid(row=0, column=0, padx=20, pady=10)

    organizer_btn = ctk.CTkButton(button_frame, text="🏢 หน้าผู้จัดค่าย", command=show_organizer_interface, width=250, height=60, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#F57C00", hover_color="#EF6C00")
    organizer_btn.grid(row=0, column=1, padx=20, pady=10)

    notification_btn = ctk.CTkButton(button_frame, text=f"🔔 การแจ้งเตือน ", command=show_notifications, width=250, height=60, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#C62828", hover_color="#B71C1C")
    notification_btn.grid(row=1, column=0, padx=20, pady=10)

    bookings_btn = ctk.CTkButton(button_frame, text="📋 ดูรายการจองทั้งหมด", command=show_all_bookings, width=250, height=60, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#7B1FA2", hover_color="#6A1B9A")
    bookings_btn.grid(row=1, column=1, padx=20, pady=10)

    stats_frame = ctk.CTkFrame(root)
    stats_frame.pack(pady=20, padx=40, fill="x")

    stats_label = ctk.CTkLabel(stats_frame, text=f"📊 สถิติระบบ: ค่ายทั้งหมด {len(camps)} ค่าย | การจองทั้งหมด {len(bookings)} รายการ", font=ctk.CTkFont(size=16))
    stats_label.pack(pady=15)


def show_user_interface():
    for widget in root.winfo_children():
        widget.destroy()

    title_frame = ctk.CTkFrame(root, fg_color="#1976D2", height=80)
    title_frame.pack(fill="x")

    back_btn = ctk.CTkButton(title_frame, text="← กลับ", command=create_main_interface, width=100, fg_color="#0D47A1")
    back_btn.pack(side="left", padx=20, pady=20)

    title_label = ctk.CTkLabel(title_frame, text="👤 หน้าผู้ใช้ - เลือกค่ายที่ต้องการเข้าร่วม", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
    title_label.pack(side="left", padx=20, pady=20)

    scroll_frame = ctk.CTkScrollableFrame(root, width=1150, height=650)
    scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)

    if not camps:
        no_camps_label = ctk.CTkLabel(scroll_frame, text="ยังไม่มีค่ายในระบบ กรุณาติดต่อผู้จัดค่ายเพื่อเพิ่มข้อมูล", font=ctk.CTkFont(size=18))
        no_camps_label.pack(pady=50)
    else:
        for idx, camp in enumerate(camps):
            create_camp_card(scroll_frame, camp, idx)


def create_camp_card(parent, camp, idx):
    card_frame = ctk.CTkFrame(parent, corner_radius=15, border_width=2)
    card_frame.pack(pady=15, padx=10, fill="x")

    booked_count = sum(1 for b in bookings if b.get('camp_id') == idx)
    try:
        available_slots = int(camp.get('slots', '0')) - booked_count
    except Exception:
        available_slots = 0
    is_full = available_slots <= 0

    left_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
    left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    name_label = ctk.CTkLabel(left_frame, text=f"🏕️ {camp.get('name','')}", font=ctk.CTkFont(size=22, weight="bold"), anchor="w")
    name_label.pack(anchor="w", pady=(0, 10))

    creator = camp.get('creator', '')
    if creator:
        creator_label = ctk.CTkLabel(left_frame, text=f"เพิ่มค่ายโดย: {creator}", font=ctk.CTkFont(size=12), anchor="w", text_color="#616161")
        creator_label.pack(anchor="w", pady=(0, 8))

    details = [
        f"📅 วันเริ่มต้น: {camp.get('start_date','-')}",
        f"⏱️ จำนวนวัน: {camp.get('duration','-')} วัน",
        f"📍 สถานที่: {camp.get('location','-')}",
        f"🚌 การเดินทาง: {camp.get('transportation','-')}",
        f"🎁 สวัสดิการ: {camp.get('benefits','-')}",
        f"👥 รับสมัคร: {camp.get('slots','-')} คน (เหลือ {available_slots} ที่นั่ง)",
        f"📞 ติดต่อ: {camp.get('contact','-')}"
    ]

    for detail in details:
        detail_label = ctk.CTkLabel(left_frame, text=detail, font=ctk.CTkFont(size=14), anchor="w")
        detail_label.pack(anchor="w", pady=3)

    desc_label = ctk.CTkLabel(left_frame, text=f"📝 {camp.get('description','')}", font=ctk.CTkFont(size=13), anchor="w", wraplength=600)
    desc_label.pack(anchor="w", pady=(10, 0))

    right_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
    right_frame.pack(side="right", padx=20, pady=20)

    if is_full:
        status_label = ctk.CTkLabel(right_frame, text="❌ ผู้สมัครเต็มจำนวนแล้ว", font=ctk.CTkFont(size=16, weight="bold"), text_color="red")
        status_label.pack(pady=10)
    else:
        status_label = ctk.CTkLabel(right_frame, text=f"✅ เหลือที่นั่ง {available_slots} ที่", font=ctk.CTkFont(size=16, weight="bold"), text_color="green")
        status_label.pack(pady=10)

    is_creator = bool(creator and current_user and creator == current_user)
    if is_creator:
        info_label = ctk.CTkLabel(right_frame, text="คุณเป็นผู้สร้างค่ายนี้", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1976D2")
        info_label.pack(pady=10)
    else:
        book_btn = ctk.CTkButton(right_frame, text="📝 จองเลย!", command=lambda i=idx, n=camp.get('name',''): book_camp(i, n), width=150, height=40, font=ctk.CTkFont(size=16, weight="bold"), state="disabled" if is_full else "normal", fg_color="#4CAF50" if not is_full else "#BDBDBD")
        book_btn.pack(pady=5)

        # Show QR button only to the user who booked this camp
        user_is_booker = False
        if current_user:
            user_is_booker = any(b.get('camp_id') == idx and b.get('user') == current_user for b in bookings)
        if user_is_booker:
            qr_btn = ctk.CTkButton(right_frame, text="🔍 ดู QR Code", command=lambda c=camp: show_qr_code(c), width=150, height=40, font=ctk.CTkFont(size=14), fg_color="#2196F3")
            qr_btn.pack(pady=5)


def show_organizer_interface():
    for widget in root.winfo_children():
        widget.destroy()

    # Top title bar
    title_frame = ctk.CTkFrame(root, fg_color="#F57C00", height=80)
    title_frame.pack(fill="x")

    back_btn = ctk.CTkButton(title_frame, text="← กลับ", command=create_main_interface, width=120, fg_color="#EF6C00")
    back_btn.pack(side="left", padx=16, pady=16)

    title_label = ctk.CTkLabel(title_frame, text="📋 หน้าผู้จัดค่าย - จัดการค่ายของคุณ", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
    title_label.pack(side="left", padx=12)

    # Centered add button
    add_holder = ctk.CTkFrame(root, fg_color="transparent")
    add_holder.pack(fill="x", pady=(12,6))
    ctk.CTkButton(add_holder, text="➕ เพิ่มค่ายใหม่", command=show_add_camp_dialog, width=220, height=44, fg_color="#4CAF50", font=ctk.CTkFont(size=16, weight='bold')).pack(pady=6)

    # Scrollable list of camp cards
    list_frame = ctk.CTkScrollableFrame(root, width=1150, height=660)
    list_frame.pack(padx=20, pady=12, fill="both", expand=True)

    # only show camps created by the current user
    if not current_user:
        ctk.CTkLabel(list_frame, text="กรุณาเข้าสู่ระบบเพื่อดูค่ายของคุณ", font=ctk.CTkFont(size=18)).pack(pady=40)
        return

    my_camps = [(i, c) for i, c in enumerate(camps) if c.get('creator') == current_user]
    if not my_camps:
        ctk.CTkLabel(list_frame, text="คุณยังไม่มีค่ายที่สร้างไว้", font=ctk.CTkFont(size=18)).pack(pady=40)
    else:
        for idx, camp in my_camps:
            card = ctk.CTkFrame(list_frame, corner_radius=12, fg_color="#f3f3f3", border_width=1)
            card.pack(fill="x", pady=12, padx=12)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side='left', fill='both', expand=True, padx=16, pady=16)

            name_label = ctk.CTkLabel(left, text=f"{camp.get('name','')}", font=ctk.CTkFont(size=18, weight='bold'), anchor='w')
            name_label.pack(anchor='w')

            # status line (red) similar to screenshot
            booked_count = sum(1 for b in bookings if b.get('camp_id') == idx)
            try:
                available_slots = int(camp.get('slots', '0')) - booked_count
            except Exception:
                available_slots = 0
            status_text = f"สถิติ: จองแล้ว {booked_count}/{camp.get('slots','0')} | เหลือ {max(0, available_slots)} ที่นั่ง"
            status_label = ctk.CTkLabel(left, text=status_text, font=ctk.CTkFont(size=12), text_color='red')
            status_label.pack(anchor='w', pady=(6,8))

            details = [
                f"📅 วันเริ่มต้น: {camp.get('start_date','-')} | {camp.get('duration','-')} วัน",
                f"📍 สถานที่: {camp.get('location','-')}",
                f"🚌 การเดินทาง: {camp.get('transportation','-')}",
                f"🎁 สวัสดิการ: {camp.get('benefits','-')}",
                f"📞 ติดต่อ: {camp.get('contact','-')}",
            ]
            for d in details:
                ctk.CTkLabel(left, text=d, font=ctk.CTkFont(size=13), anchor='w').pack(anchor='w', pady=2)

            right = ctk.CTkFrame(card, fg_color='transparent')
            right.pack(side='right', padx=18, pady=18)

            # action buttons stacked vertically
            ctk.CTkButton(right, text=f"👥 ผู้จอง ({booked_count})", width=140, height=42, fg_color="#1976D2", command=lambda i=idx: view_participants(i)).pack(pady=(6,8))
            ctk.CTkButton(right, text="✏️ แก้ไข", width=140, height=42, fg_color="#FB8C00", command=lambda i=idx: show_edit_camp_dialog(i)).pack(pady=8)
            ctk.CTkButton(right, text="🗑️ ลบ", width=140, height=42, fg_color="#E53935", command=lambda i=idx: delete_camp(i)).pack(pady=8)


def show_add_camp_dialog():
    dialog = ctk.CTkToplevel(root)
    dialog.title('Add Camp')
    dialog.geometry('700x640')
    dialog.grab_set()

    f = ctk.CTkFrame(dialog)
    f.pack(padx=12, pady=12, fill='both', expand=True)

    labels = ['ชื่อค่าย', 'รายละเอียด', 'วันเริ่มต้น (YYYY-MM-DD)', 'จำนวนวัน', 'สถานที่', 'การเดินทาง', 'สวัสดิการ', 'จำนวนที่รับ', 'ติดต่อ']
    entries = []
    for i, lab in enumerate(labels):
        ctk.CTkLabel(f, text=lab).grid(row=i, column=0, sticky='e', padx=6, pady=6)
        if lab == 'รายละเอียด':
            t = scrolledtext.ScrolledText(f, width=50, height=6)
            t.grid(row=i, column=1, padx=6, pady=6)
            entries.append(t)
        else:
            e = ctk.CTkEntry(f, width=420)
            e.grid(row=i, column=1, padx=6, pady=6)
            entries.append(e)

    def do_add():
        try:
            name = entries[0].get().strip()
            description = entries[1].get('1.0', 'end').strip()
            start_date = entries[2].get().strip()
            duration = entries[3].get().strip()
            location = entries[4].get().strip()
            transport = entries[5].get().strip()
            benefits = entries[6].get().strip()
            slots = entries[7].get().strip()
            contact = entries[8].get().strip()

            if not name:
                messagebox.showerror('Error', 'กรุณากรอกชื่อค่าย')
                return

            camp = {
                'name': name,
                'description': description,
                'start_date': start_date,
                'duration': duration,
                'location': location,
                'transportation': transport,
                'benefits': benefits,
                'slots': slots,
                'contact': contact,
                'creator': current_user or ''
            }
            camps.append(camp)
            save_data()
            messagebox.showinfo('สำเร็จ', 'เพิ่มค่ายเรียบร้อย')
            dialog.destroy()
        except Exception as e:
            messagebox.showerror('Error', f'เกิดข้อผิดพลาด: {e}')

    ctk.CTkButton(dialog, text='บันทึกค่าย', command=do_add, width=200).pack(pady=12)


def delete_camp(idx):
    try:
        if messagebox.askyesno('ยืนยัน', 'คุณต้องการลบค่ายนี้หรือไม่?'):
            camps.pop(idx)
            save_data()
            show_organizer_interface()
    except Exception as e:
        messagebox.showerror('Error', f'ไม่สามารถลบได้: {e}')


def view_participants(idx):
    dialog = ctk.CTkToplevel(root)
    camp = camps[idx]
    dialog.title(f"รายการจองค่าย: {camp.get('name','')}")
    dialog.geometry('740x520')
    dialog.grab_set()

    parts = [b for b in bookings if b.get('camp_id') == idx]

    header = ctk.CTkLabel(dialog, text=f"รายการจองค่าย: {camp.get('name','')}", font=ctk.CTkFont(size=18, weight='bold'))
    header.pack(pady=(12,4))

    sub = ctk.CTkLabel(dialog, text=f"มีผู้จองทั้งหมด {len(parts)} คน", font=ctk.CTkFont(size=14))
    sub.pack(pady=(0,8))

    if not parts:
        ctk.CTkLabel(dialog, text='ยังไม่มีผู้สมัคร', font=ctk.CTkFont(size=14)).pack(pady=20)
        return

    scroll = ctk.CTkScrollableFrame(dialog, width=700, height=380)
    scroll.pack(padx=12, pady=8, fill='both', expand=True)

    for i, p in enumerate(parts, start=1):
        uname = p.get('user')
        userinfo = users.get(uname, {}) if users else {}
        if isinstance(userinfo, dict):
            fullname = userinfo.get('fullname') or uname
            phone = userinfo.get('phone') or '-'
            email = userinfo.get('email') or '-'
        else:
            fullname = uname
            phone = '-'
            email = '-'

        card = ctk.CTkFrame(scroll, corner_radius=8)
        card.pack(fill='x', pady=8, padx=8)

        top = ctk.CTkLabel(card, text=f"คนที่ {i} | จองเมื่อ: {p.get('time')}", font=ctk.CTkFont(size=12, weight='bold'))
        top.pack(anchor='w', padx=8, pady=(8,2))

        ctk.CTkLabel(card, text=f"ชื่อ: {fullname}", font=ctk.CTkFont(size=12)).pack(anchor='w', padx=8, pady=2)
        ctk.CTkLabel(card, text=f"เบอร์โทร: {phone}", font=ctk.CTkFont(size=12)).pack(anchor='w', padx=8, pady=2)
        ctk.CTkLabel(card, text=f"อีเมล: {email}", font=ctk.CTkFont(size=12)).pack(anchor='w', padx=8, pady=(2,8))


def show_edit_camp_dialog(idx):
    camp = camps[idx]
    dialog = ctk.CTkToplevel(root)
    dialog.title('Edit Camp')
    dialog.geometry('700x640')
    dialog.grab_set()

    f = ctk.CTkFrame(dialog)
    f.pack(padx=12, pady=12, fill='both', expand=True)

    labels = ['ชื่อค่าย', 'รายละเอียด', 'วันเริ่มต้น (YYYY-MM-DD)', 'จำนวนวัน', 'สถานที่', 'การเดินทาง', 'สวัสดิการ', 'จำนวนที่รับ', 'ติดต่อ']
    entries = []
    values = [camp.get('name',''), camp.get('description',''), camp.get('start_date',''), camp.get('duration',''), camp.get('location',''), camp.get('transportation',''), camp.get('benefits',''), camp.get('slots',''), camp.get('contact','')]
    for i, lab in enumerate(labels):
        ctk.CTkLabel(f, text=lab).grid(row=i, column=0, sticky='e', padx=6, pady=6)
        if lab == 'รายละเอียด':
            t = scrolledtext.ScrolledText(f, width=50, height=6)
            t.grid(row=i, column=1, padx=6, pady=6)
            t.insert('1.0', values[i])
            entries.append(t)
        else:
            e = ctk.CTkEntry(f, width=420)
            e.grid(row=i, column=1, padx=6, pady=6)
            e.insert(0, values[i])
            entries.append(e)

    def do_save():
        try:
            camp['name'] = entries[0].get().strip()
            camp['description'] = entries[1].get('1.0', 'end').strip()
            camp['start_date'] = entries[2].get().strip()
            camp['duration'] = entries[3].get().strip()
            camp['location'] = entries[4].get().strip()
            camp['transportation'] = entries[5].get().strip()
            camp['benefits'] = entries[6].get().strip()
            camp['slots'] = entries[7].get().strip()
            camp['contact'] = entries[8].get().strip()
            save_data()
            messagebox.showinfo('สำเร็จ', 'บันทึกเรียบร้อย')
            dialog.destroy()
            show_organizer_interface()
        except Exception as e:
            messagebox.showerror('Error', f'เกิดข้อผิดพลาด: {e}')

    ctk.CTkButton(dialog, text='บันทึก', command=do_save, width=200).pack(pady=12)


def show_notifications():
    dialog = ctk.CTkToplevel(root)
    dialog.title('การแจ้งเตือนทั้งหมด')
    dialog.geometry('760x560')
    dialog.grab_set()

    # Filter notifications that belong to current_user only
    if not current_user:
        messagebox.showerror('Error', 'กรุณา login เพื่อดูการแจ้งเตือน')
        return

    # determine matching notifications: prefer structured 'user' field, fallback to message contains username
    my_notifs = [n for n in notifications if (n.get('user') and n.get('user') == current_user) or (not n.get('user') and current_user in n.get('message',''))]

    header = ctk.CTkLabel(dialog, text=f"🔔 การแจ้งเตือนทั้งหมด ", font=ctk.CTkFont(size=18, weight='bold'))
    header.pack(pady=(12,6))

    def clear_my_notifications():
        if not my_notifs:
            return
        if not messagebox.askyesno('ยืนยัน', 'ต้องการลบการแจ้งเตือนทั้งหมดของคุณหรือไม่?'):
            return
        # remove notifications that match current_user
        new_list = [n for n in notifications if not ((n.get('user') and n.get('user') == current_user) or (not n.get('user') and current_user in n.get('message','')))]
        notifications.clear()
        notifications.extend(new_list)
        save_data()
        dialog.destroy()
        show_notifications()

    clear_btn = ctk.CTkButton(dialog, text='🗑️ ล้างการแจ้งเตือนทั้งหมด', fg_color='#E53935', command=clear_my_notifications, width=260, height=36)
    clear_btn.pack(pady=(0,8))

    if not my_notifs:
        ctk.CTkLabel(dialog, text='ยังไม่มีการแจ้งเตือนของคุณ', font=ctk.CTkFont(size=14)).pack(pady=20)
        return

    scroll = ctk.CTkScrollableFrame(dialog, width=720, height=420)
    scroll.pack(padx=12, pady=8, fill='both', expand=True)

    for n in my_notifs:
        card = ctk.CTkFrame(scroll, corner_radius=8, fg_color='#fafafa', border_width=2)
        card.pack(fill='x', pady=8, padx=8)

        time_label = ctk.CTkLabel(card, text=n.get('time',''), font=ctk.CTkFont(size=11))
        time_label.pack(anchor='w', padx=10, pady=(8,0))

        # compose detailed content when possible
        content_lines = []
        # if structured (has camp_id), show richer content including both the booking user and camp owner
        if n.get('camp_id') is not None:
            camp = camps[n.get('camp_id')] if 0 <= n.get('camp_id', -1) < len(camps) else None
            content_lines.append('มีการจองใหม่!')
            if camp:
                content_lines.append(f"ค่าย: {camp.get('name','-')}")

            # determine booking username (actor) and owner
            msg = n.get('message','') or ''
            owner = camp.get('creator') if camp else None

            # booking actor: prefer explicit 'actor' field, otherwise try 'user' field, otherwise try to parse message
            booking_uname = n.get('actor') if 'actor' in n else n.get('user')
            if booking_uname == owner or not booking_uname:
                if 'ผู้ใช้ ' in msg:
                    after = msg.split('ผู้ใช้ ', 1)[1]
                    booking_uname = after.split()[0].strip() if after else booking_uname

            # show booking user details
            if booking_uname:
                binfo = users.get(booking_uname, {}) if users else {}
                if isinstance(binfo, dict):
                    bfullname = binfo.get('fullname') or booking_uname
                    bphone = binfo.get('phone') or '-'
                    bemail = binfo.get('email') or '-'
                else:
                    bfullname = booking_uname
                    bphone = '-'
                    bemail = '-'
                content_lines.append(f"ผู้จอง: {bfullname}")
                content_lines.append(f"เบอร์: {bphone}")
                content_lines.append(f"อีเมล: {bemail}")
            else:
                # fallback to raw message if we couldn't determine booking user
                if msg:
                    content_lines.append(msg)

            # show camp owner details (if available and different)
            if owner:
                oinfo = users.get(owner, {}) if users else {}
                if isinstance(oinfo, dict):
                    ofull = oinfo.get('fullname') or owner
                    ophone = oinfo.get('phone') or '-'
                    oemail = oinfo.get('email') or '-'
                else:
                    ofull = owner
                    ophone = '-'
                    oemail = '-'
                content_lines.append('-----')
                content_lines.append(f"เจ้าของค่าย: {ofull}")
                content_lines.append(f"เบอร์: {ophone}")
                content_lines.append(f"อีเมล: {oemail}")
        else:
            # fallback to raw message
            content_lines.append(n.get('message',''))

        body = '\n'.join(content_lines)
        ctk.CTkLabel(card, text=body, font=ctk.CTkFont(size=13), wraplength=660, justify='left').pack(anchor='w', padx=10, pady=(6,10))


def show_all_bookings():
    dialog = ctk.CTkToplevel(root)
    dialog.title('รายการจองของฉัน')
    dialog.geometry('880x720')
    dialog.grab_set()

    if not current_user:
        messagebox.showerror('Error', 'กรุณา login เพื่อดูรายการจองของคุณ')
        dialog.destroy()
        return

    # If the current user created camps, show bookings for those camps (owner view).
    # Otherwise show personal bookings only.
    my_camp_ids = [i for i, c in enumerate(camps) if c.get('creator') == current_user]
    if my_camp_ids:
        # owner view: show all bookings for camps the user owns
        bookings_to_show = [b for b in bookings if b.get('camp_id') in my_camp_ids]
        header = ctk.CTkLabel(dialog, text=f"👥 รายชื่อผู้จองค่ายของคุณ ({len(bookings_to_show)} รายการ)", font=ctk.CTkFont(size=18, weight='bold'))
    else:
        # personal view: show only bookings made by the current user
        bookings_to_show = [b for b in bookings if b.get('user') == current_user]
        header = ctk.CTkLabel(dialog, text=f"📋 รายการจองของคุณ ({len(bookings_to_show)} รายการ)", font=ctk.CTkFont(size=18, weight='bold'))

    header.pack(pady=(12,8))

    if not bookings_to_show:
        empty_msg = 'ยังไม่มีการจองของคุณ' if not my_camp_ids else 'ยังไม่มีผู้จองในค่ายของคุณ'
        ctk.CTkLabel(dialog, text=empty_msg, font=ctk.CTkFont(size=14)).pack(pady=40)
        return

    # Scrollable area grouping bookings by camp
    scroll = ctk.CTkScrollableFrame(dialog, width=840, height=560)
    scroll.pack(padx=16, pady=8, fill='both', expand=True)

    # group bookings by camp_id
    grouped = {}
    for b in bookings_to_show:
        cid = b.get('camp_id')
        grouped.setdefault(cid, []).append(b)

    for cid, parts in grouped.items():
        camp = camps[cid] if 0 <= cid < len(camps) else {'name': 'Unknown'}

        camp_card = ctk.CTkFrame(scroll, corner_radius=10, fg_color='#f0f0f0', border_width=1)
        camp_card.pack(fill='x', pady=10, padx=8)

        title = ctk.CTkLabel(camp_card, text=f"👥  {camp.get('name','')} ({len(parts)} การจอง)", font=ctk.CTkFont(size=14, weight='bold'))
        title.pack(anchor='w', padx=10, pady=(8,6))

        inner = ctk.CTkFrame(camp_card, fg_color='transparent')
        inner.pack(fill='x', padx=8, pady=(0,10))

        for i, p in enumerate(parts, start=1):
            uname = p.get('user')
            uinfo = users.get(uname, {}) if users else {}
            if isinstance(uinfo, dict):
                fullname = uinfo.get('fullname') or uname
                phone = uinfo.get('phone') or '-'
                email = uinfo.get('email') or '-'
            else:
                fullname = uname
                phone = '-'
                email = '-'

            text = f"{i}. {fullname} | {phone} | {email} | จองเมื่อ: {p.get('time')}"
            row = ctk.CTkFrame(inner, fg_color='#ffffff', corner_radius=6)
            row.pack(fill='x', pady=6, padx=6)
            ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=12), anchor='w', wraplength=760).pack(side='left', padx=12, pady=8)



def book_camp(camp_id, camp_name):
    if not current_user:
        messagebox.showerror('Error', 'กรุณา login ก่อนทำการจอง')
        return
    try:
        already_booked = any(b.get('camp_id') == camp_id and b.get('user') == current_user for b in bookings)
        booked_count = sum(1 for b in bookings if b.get('camp_id') == camp_id)
        slots = int(camps[camp_id].get('slots', '0'))
        if booked_count >= slots:
            messagebox.showerror('เต็มแล้ว', 'ค่ายนี้รับครบแล้ว')
            return
        
        if already_booked:
            messagebox.showerror('จองแล้ว', 'คุณได้จองค่ายนี้แล้ว')
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = {'camp_id': camp_id, 'user': current_user, 'time': timestamp}
        bookings.append(entry)
        # create a structured notification so we can show richer info later
        notifications.append({
            'time': timestamp,
            'message': f'{current_user} จองค่าย {camp_name}',
            'camp_id': camp_id,
            'user': current_user
        })
        save_data()
        messagebox.showinfo('สำเร็จ', 'จองเรียบร้อย')
    except Exception as e:
        messagebox.showerror('Error', f'เกิดข้อผิดพลาด: {e}')


def show_qr_code(camp):
    # Generate QR for camp info
    info = f"Camp: {camp.get('name','')} | Start: {camp.get('start_date','')} | Contact: {camp.get('contact','')}"
    qr = qrcode.make(info)
    bio = BytesIO()
    qr.save(bio, format='PNG')
    bio.seek(0)
    img = Image.open(bio)
    img = img.resize((320, 320))

    dialog = ctk.CTkToplevel(root)
    dialog.title('QR Code')
    dialog.geometry('360x420')
    dialog.grab_set()

    photo = ImageTk.PhotoImage(img)
    label = ctk.CTkLabel(dialog, image=photo, text='')
    label.image = photo
    label.pack(pady=12)

    ctk.CTkLabel(dialog, text=info, wraplength=320).pack(pady=6)


def main():
    global root
    load_users()
    load_data()
    root = ctk.CTk()
    root.title('Camp Booking Platform')
    root.geometry('1280x820')
    show_login_screen()
    root.mainloop()


if __name__ == '__main__':
    main()
