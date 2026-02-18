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
                users = json.load(f)
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

    hint = ctk.CTkLabel(frame, text='(รหัสผ่านจะถูกเก็บแบบ plain text ตามที่ร้องขอ — ห้ามใช้ใน production)', font=ctk.CTkFont(size=10))
    hint.pack(pady=6)


def attempt_login(username, password):
    global current_user
    if not username or not password:
        messagebox.showerror('Error', 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
        return
    stored = users.get(username)
    if stored and stored == password:
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

    def do_register():
        username = u.get().strip()
        password = p.get().strip()
        if not username or not password:
            messagebox.showerror('Error', 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
            return
        if username in users:
            messagebox.showerror('Error', 'ชื่อผู้ใช้นี้มีอยู่แล้ว')
            return
        users[username] = password
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

    notification_btn = ctk.CTkButton(button_frame, text=f"🔔 การแจ้งเตือน ({len(notifications)})", command=show_notifications, width=250, height=60, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#C62828", hover_color="#B71C1C")
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

        qr_btn = ctk.CTkButton(right_frame, text="🔍 ดู QR Code", command=lambda c=camp: show_qr_code(c), width=150, height=40, font=ctk.CTkFont(size=14), fg_color="#2196F3")
        qr_btn.pack(pady=5)


def show_organizer_interface():
    for widget in root.winfo_children():
        widget.destroy()

    title_frame = ctk.CTkFrame(root, fg_color="#F57C00", height=80)
    title_frame.pack(fill="x")

    back_btn = ctk.CTkButton(title_frame, text="← กลับ", command=create_main_interface, width=100, fg_color="#EF6C00")
    back_btn.pack(side="left", padx=12, pady=16)

    title_label = ctk.CTkLabel(title_frame, text="📋 หน้าผู้จัดค่าย - จัดการค่ายของคุณ", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
    title_label.pack(side="left", padx=8)

    add_holder = ctk.CTkFrame(root)
    add_holder.pack(fill="x", padx=20, pady=12)
    left = ctk.CTkFrame(add_holder)
    left.pack(side="left", padx=12)

    ctk.CTkButton(left, text="➕ เพิ่มค่ายใหม่", command=show_add_camp_dialog, width=180, fg_color="#388E3C").pack(padx=8, pady=8)

    list_frame = ctk.CTkScrollableFrame(root, width=1150, height=650)
    list_frame.pack(padx=20, pady=12, fill="both", expand=True)

    if not camps:
        ctk.CTkLabel(list_frame, text="ยังไม่มีค่ายในระบบ", font=ctk.CTkFont(size=18)).pack(pady=40)
    else:
        for idx, camp in enumerate(camps):
            cf = ctk.CTkFrame(list_frame, corner_radius=8)
            cf.pack(fill="x", pady=8, padx=8)

            ctk.CTkLabel(cf, text=f"{idx+1}. {camp.get('name','')}", font=ctk.CTkFont(size=16, weight='bold')).pack(side='left', padx=12, pady=12)
            btn_frame = ctk.CTkFrame(cf)
            btn_frame.pack(side='right', padx=12)

            ctk.CTkButton(btn_frame, text="✏️ แก้ไข", width=100, command=lambda i=idx: show_edit_camp_dialog(i)).pack(side='left', padx=6)
            ctk.CTkButton(btn_frame, text="🗑️ ลบ", width=100, command=lambda i=idx: delete_camp(i)).pack(side='left', padx=6)
            ctk.CTkButton(btn_frame, text="👥 ผู้สมัคร", width=120, command=lambda i=idx: view_participants(i)).pack(side='left', padx=6)


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
    dialog.title('Participants')
    dialog.geometry('600x500')
    dialog.grab_set()

    listbox = scrolledtext.ScrolledText(dialog, width=70, height=30)
    listbox.pack(padx=12, pady=12)
    parts = [b for b in bookings if b.get('camp_id') == idx]
    if not parts:
        listbox.insert('end', 'ยังไม่มีผู้สมัคร')
    else:
        for p in parts:
            listbox.insert('end', f"- {p.get('user')} เวลา {p.get('time')}\n")


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
    dialog.title('Notifications')
    dialog.geometry('700x520')
    dialog.grab_set()

    t = scrolledtext.ScrolledText(dialog, width=80, height=30)
    t.pack(padx=12, pady=12)
    if not notifications:
        t.insert('end', 'ยังไม่มีการแจ้งเตือน')
    else:
        for n in notifications:
            t.insert('end', f"- {n.get('time','')} : {n.get('message','')}\n")


def show_all_bookings():
    dialog = ctk.CTkToplevel(root)
    dialog.title('All Bookings')
    dialog.geometry('800x600')
    dialog.grab_set()

    t = scrolledtext.ScrolledText(dialog, width=100, height=40)
    t.pack(padx=12, pady=12)
    if not bookings:
        t.insert('end', 'ยังไม่มีการจอง')
    else:
        for b in bookings:
            camp_info = camps[b.get('camp_id')] if 0 <= b.get('camp_id', -1) < len(camps) else {'name': 'Unknown'}
            t.insert('end', f"- {b.get('user')} จอง {camp_info.get('name')} เวลา {b.get('time')}\n")


def book_camp(camp_id, camp_name):
    if not current_user:
        messagebox.showerror('Error', 'กรุณา login ก่อนทำการจอง')
        return
    try:
        booked_count = sum(1 for b in bookings if b.get('camp_id') == camp_id)
        slots = int(camps[camp_id].get('slots', '0'))
        if booked_count >= slots:
            messagebox.showerror('เต็มแล้ว', 'ค่ายนี้รับครบแล้ว')
            return
        entry = {'camp_id': camp_id, 'user': current_user, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        bookings.append(entry)
        notifications.append({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'message': f'{current_user} จองค่าย {camp_name}'})
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
