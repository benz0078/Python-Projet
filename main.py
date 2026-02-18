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
import base64

# ตั้งค่าธีมและสี
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class CampBookingPlatform:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("แพลตฟอร์มจองค่าย - Camp Booking Platform")
        self.root.geometry("1200x800")
        
        # ข้อมูลค่ายทั้งหมด
        self.camps = []
        self.bookings = []
        self.notifications = []
        
        # โหลดข้อมูลที่บันทึกไว้
        self.load_data()
        # โหลดผู้ใช้
        self.load_users()
        
        # แสดงหน้าเข้าสู่ระบบก่อนเข้าแอปหลัก
        self.show_login_screen()
        
    def load_data(self):
        """โหลดข้อมูลจากไฟล์"""
        try:
            if os.path.exists('camps_data.json'):
                with open('camps_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.camps = data.get('camps', [])
                    self.bookings = data.get('bookings', [])
                    self.notifications = data.get('notifications', [])
        except Exception as e:
            print(f"Error loading data: {e}")
            
    def save_data(self):
        """บันทึกข้อมูลลงไฟล์"""
        try:
            data = {
                'camps': self.camps,
                'bookings': self.bookings,
                'notifications': self.notifications
            }
            with open('camps_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    # ---------- user persistence for simple auth (no hashing as requested) ----------
    def load_users(self):
        self.users_file = 'users.json'
        self.users = {}
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")

    def save_users(self):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")

    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.root)
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

        login_btn = ctk.CTkButton(btn_frame, text='Login', width=120,
                                   command=lambda: self.attempt_login(username_entry.get().strip(), password_entry.get().strip()))
        login_btn.grid(row=0, column=0, padx=10)

        register_btn = ctk.CTkButton(btn_frame, text='Register', width=120,
                                      command=lambda: self.show_register_dialog())
        register_btn.grid(row=0, column=1, padx=10)

        hint = ctk.CTkLabel(frame, text='(รหัสผ่านจะถูกเก็บแบบ plain text ตามที่ร้องขอ — ห้ามใช้ใน production)', font=ctk.CTkFont(size=10))
        hint.pack(pady=6)

    def attempt_login(self, username, password):
        if not username or not password:
            messagebox.showerror('Error', 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
            return
        stored = self.users.get(username)
        if stored and stored == password:
            self.current_user = username
            messagebox.showinfo('สำเร็จ', f'ยินดีต้อนรับ {username}')
            self.create_main_interface()
        else:
            messagebox.showerror('ล้มเหลว', 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')

    def show_register_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
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
            if username in self.users:
                messagebox.showerror('Error', 'ชื่อผู้ใช้นี้มีอยู่แล้ว')
                return
            self.users[username] = password
            self.save_users()
            messagebox.showinfo('สำเร็จ', 'สร้างบัญชีเรียบร้อย')
            dialog.destroy()

        ctk.CTkButton(dialog, text='สร้างบัญชี', command=do_register, width=200).pack(pady=12)
    
    def create_main_interface(self):
        """สร้างหน้าต่างหลัก"""
        # ล้างหน้าจอ
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # หัวข้อ
        title_frame = ctk.CTkFrame(self.root, fg_color="#2E7D32", height=100)
        title_frame.pack(fill="x", padx=0, pady=0)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🏕️ แพลตฟอร์มจองค่ายในประเทศไทย",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=25)
        
        # ปุ่มเมนูหลัก
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=30)
        
        user_btn = ctk.CTkButton(
            button_frame,
            text="👤 หน้าผู้ใช้ (จองค่าย)",
            command=self.show_user_interface,
            width=250,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        user_btn.grid(row=0, column=0, padx=20, pady=10)
        
        organizer_btn = ctk.CTkButton(
            button_frame,
            text="🏢 หน้าผู้จัดค่าย",
            command=self.show_organizer_interface,
            width=250,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#F57C00",
            hover_color="#EF6C00"
        )
        organizer_btn.grid(row=0, column=1, padx=20, pady=10)
        
        notification_btn = ctk.CTkButton(
            button_frame,
            text=f"🔔 การแจ้งเตือน ({len(self.notifications)})",
            command=self.show_notifications,
            width=250,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#C62828",
            hover_color="#B71C1C"
        )
        notification_btn.grid(row=1, column=0, padx=20, pady=10)
        
        bookings_btn = ctk.CTkButton(
            button_frame,
            text="📋 ดูรายการจองทั้งหมด",
            command=self.show_all_bookings,
            width=250,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        bookings_btn.grid(row=1, column=1, padx=20, pady=10)
        
        # แสดงสถิติ
        stats_frame = ctk.CTkFrame(self.root)
        stats_frame.pack(pady=20, padx=40, fill="x")
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=f"📊 สถิติระบบ: ค่ายทั้งหมด {len(self.camps)} ค่าย | การจองทั้งหมด {len(self.bookings)} รายการ",
            font=ctk.CTkFont(size=16)
        )
        stats_label.pack(pady=15)
    
    def show_user_interface(self):
        """แสดงหน้าต่างผู้ใช้"""
        # ล้างหน้าจอ
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # หัวข้อ
        title_frame = ctk.CTkFrame(self.root, fg_color="#1976D2", height=80)
        title_frame.pack(fill="x")
        
        back_btn = ctk.CTkButton(
            title_frame,
            text="← กลับ",
            command=self.create_main_interface,
            width=100,
            fg_color="#0D47A1"
        )
        back_btn.pack(side="left", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="👤 หน้าผู้ใช้ - เลือกค่ายที่ต้องการเข้าร่วม",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # สร้าง Scrollable Frame
        scroll_frame = ctk.CTkScrollableFrame(self.root, width=1150, height=650)
        scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        if not self.camps:
            no_camps_label = ctk.CTkLabel(
                scroll_frame,
                text="ยังไม่มีค่ายในระบบ กรุณาติดต่อผู้จัดค่ายเพื่อเพิ่มข้อมูล",
                font=ctk.CTkFont(size=18)
            )
            no_camps_label.pack(pady=50)
        else:
            # แสดงค่ายทั้งหมด
            for idx, camp in enumerate(self.camps):
                self.create_camp_card(scroll_frame, camp, idx)
    
    def create_camp_card(self, parent, camp, idx):
        """สร้างการ์ดแสดงข้อมูลค่าย"""
        card_frame = ctk.CTkFrame(parent, corner_radius=15, border_width=2)
        card_frame.pack(pady=15, padx=10, fill="x")
        
        # คำนวณจำนวนที่จองแล้ว
        booked_count = sum(1 for b in self.bookings if b['camp_id'] == idx)
        available_slots = int(camp['slots']) - booked_count
        is_full = available_slots <= 0
        
        # ส่วนซ้าย - ข้อมูลหลัก
        left_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # ชื่อค่าย
        name_label = ctk.CTkLabel(
            left_frame,
            text=f"🏕️ {camp['name']}",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w", pady=(0, 10))
        # ผู้สร้างค่าย
        creator = camp.get('creator', '')
        if creator:
            creator_label = ctk.CTkLabel(
                left_frame,
                text=f"เพิ่มค่ายโดย: {creator}",
                font=ctk.CTkFont(size=12),
                anchor="w",
                text_color="#616161"
            )
            creator_label.pack(anchor="w", pady=(0, 8))
        
        # รายละเอียด
        details = [
            f"📅 วันเริ่มต้น: {camp['start_date']}",
            f"⏱️ จำนวนวัน: {camp['duration']} วัน",
            f"📍 สถานที่: {camp['location']}",
            f"🚌 การเดินทาง: {camp['transportation']}",
            f"🎁 สวัสดิการ: {camp['benefits']}",
            f"👥 รับสมัคร: {camp['slots']} คน (เหลือ {available_slots} ที่นั่ง)",
            f"📞 ติดต่อ: {camp['contact']}"
        ]
        
        for detail in details:
            detail_label = ctk.CTkLabel(
                left_frame,
                text=detail,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            detail_label.pack(anchor="w", pady=3)
        
        # รายละเอียดเพิ่มเติม
        desc_label = ctk.CTkLabel(
            left_frame,
            text=f"📝 {camp['description']}",
            font=ctk.CTkFont(size=13),
            anchor="w",
            wraplength=600
        )
        desc_label.pack(anchor="w", pady=(10, 0))
        
        # ส่วนขวา - ปุ่มและ QR Code
        right_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=20)
        
        # สถานะ
        if is_full:
            status_label = ctk.CTkLabel(
                right_frame,
                text="❌ ผู้สมัครเต็มจำนวนแล้ว",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="red"
            )
            status_label.pack(pady=10)
        else:
            status_label = ctk.CTkLabel(
                right_frame,
                text=f"✅ เหลือที่นั่ง {available_slots} ที่",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="green"
            )
            status_label.pack(pady=10)
        
        # ปุ่มจอง
        # ถ้าผู้ใช้งานปัจจุบันเป็นผู้สร้างค่าย ให้ไม่แสดงปุ่มจองและ QR Code
        current_user = getattr(self, 'current_user', None)
        is_creator = bool(creator and current_user and creator == current_user)

        if is_creator:
            info_label = ctk.CTkLabel(
                right_frame,
                text="คุณเป็นผู้สร้างค่ายนี้",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#1976D2"
            )
            info_label.pack(pady=10)
        else:
            book_btn = ctk.CTkButton(
                right_frame,
                text="📝 จองเลย!",
                command=lambda: self.book_camp(idx, camp['name']),
                width=150,
                height=40,
                font=ctk.CTkFont(size=16, weight="bold"),
                state="disabled" if is_full else "normal",
                fg_color="#4CAF50" if not is_full else "#BDBDBD"
            )
            book_btn.pack(pady=5)

            # ปุ่มดู QR Code
            qr_btn = ctk.CTkButton(
                right_frame,
                text="🔍 ดู QR Code",
                command=lambda: self.show_qr_code(camp),
                width=150,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="#2196F3"
            )
            qr_btn.pack(pady=5)
    
    def show_organizer_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Header
        title_frame = ctk.CTkFrame(self.root, fg_color="#F57C00", height=80)
        title_frame.pack(fill="x")
        back_btn = ctk.CTkButton(title_frame, text="← กลับ", command=self.create_main_interface, width=100, fg_color="#EF6C00")
        back_btn.pack(side="left", padx=12, pady=16)
        title_label = ctk.CTkLabel(title_frame, text="📋 หน้าผู้จัดค่าย - จัดการค่ายของคุณ", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        title_label.pack(side="left", padx=8)

        # Add button centered
        add_holder = ctk.CTkFrame(self.root)
        add_holder.pack(fill="x", padx=20, pady=12)
        add_btn = ctk.CTkButton(add_holder, text="+ เพิ่มค่ายใหม่", width=180, fg_color="#4CAF50", hover_color="#43A047", command=self.show_add_camp_dialog)
        add_btn.pack(anchor="n")

        # List area
        list_frame = ctk.CTkScrollableFrame(self.root, width=1150, height=560)
        list_frame.pack(padx=20, pady=10, fill="both", expand=True)

        if not self.camps:
            ctk.CTkLabel(list_frame, text="ยังไม่มีค่ายในระบบ", font=ctk.CTkFont(size=16)).pack(pady=30)
            return

        for idx, camp in enumerate(self.camps):
            # Card
            card = ctk.CTkFrame(list_frame, fg_color="#f2f2f2", corner_radius=8, border_width=1)
            card.pack(fill="x", padx=8, pady=10)

            # Left: details
            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=12, pady=12)

            # Header row: name and status
            booked_count = sum(1 for b in self.bookings if b.get('camp_id') == idx)
            slots = int(camp.get('slots', '0')) if str(camp.get('slots','0')).isdigit() else 0
            remaining = slots - booked_count
            status_text = f"สถานะ: จองแล้ว {booked_count}/{slots} | เหลือ {max(0, remaining)} ที่ | " + ("ผู้สมัครเต็มแล้ว" if remaining<=0 else "รับได้")
            name_lbl = ctk.CTkLabel(left, text=camp.get('name','(no name)'), font=ctk.CTkFont(size=16, weight="bold"))
            name_lbl.pack(anchor="w")
            status_lbl = ctk.CTkLabel(left, text=status_text, font=ctk.CTkFont(size=11), text_color=("#C62828" if remaining<=0 else "#388E3C"))
            status_lbl.pack(anchor="w", pady=(6,10))
            # creator
            creator = camp.get('creator', '')
            if creator:
                ctk.CTkLabel(left, text=f"เพิ่มค่ายโดย: {creator}", font=ctk.CTkFont(size=12), text_color="#616161").pack(anchor="w")

            # Details rows
            details = [
                f"📅 วันที่เริ่ม: {camp.get('start_date','-')} | ⏱️ {camp.get('duration','-')} วัน",
                f"📍 สถานที่: {camp.get('location','-')}",
                f"🚌 การเดินทาง: {camp.get('transportation','-')}",
                f"🎁 สวัสดิการ: {camp.get('benefits','-')}",
                f"📞 ติดต่อ: {camp.get('contact','-')}"
            ]
            for d in details:
                ctk.CTkLabel(left, text=d, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)

            # Right: action buttons
            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=12, pady=12)
            # participants (blue)
            part_btn = ctk.CTkButton(right, text=f"👥 ผู้สมัคร ({booked_count})", width=120, fg_color="#2196F3", hover_color="#1976D2", command=lambda i=idx: self.view_participants(i))
            part_btn.pack(pady=6)
            # edit (orange)
            edit_btn = ctk.CTkButton(right, text="✏️ แก้ไข", width=120, fg_color="#FFA726", hover_color="#FB8C00", command=lambda i=idx: self.show_edit_camp_dialog(i))
            edit_btn.pack(pady=6)
            # delete (red)
            del_btn = ctk.CTkButton(right, text="🗑️ ลบ", width=120, fg_color="#E53935", hover_color="#D32F2F", command=lambda i=idx: self.delete_camp(i))
            del_btn.pack(pady=6)

    def show_add_camp_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title('เพิ่มค่ายใหม่')
        dialog.geometry('700x600')
        dialog.grab_set()

        canvas = ctk.CTkFrame(dialog)
        canvas.pack(fill='both', expand=True, padx=12, pady=12)

        labels = ['ชื่อค่าย', 'วันเริ่มต้น (YYYY-MM-DD)', 'จำนวนวัน', 'สถานที่', 'การเดินทาง', 'สวัสดิการ', 'จำนวนที่รับ (slots)', 'ติดต่อ', 'รายละเอียด']
        entries = {}

        for i, lbl in enumerate(labels[:-1]):
            ctk.CTkLabel(canvas, text=lbl + ':').grid(row=i, column=0, sticky='e', padx=6, pady=6)
            e = ctk.CTkEntry(canvas, width=420)
            e.grid(row=i, column=1, padx=6, pady=6)
            entries[lbl] = e

        # description as scrolledtext
        ctk.CTkLabel(canvas, text=labels[-1] + ':').grid(row=len(labels)-1, column=0, sticky='ne', padx=6, pady=6)
        desc = scrolledtext.ScrolledText(canvas, width=50, height=6)
        desc.grid(row=len(labels)-1, column=1, padx=6, pady=6)
        entries['รายละเอียด'] = desc

        def do_add():
            name = entries['ชื่อค่าย'].get().strip()
            start_date = entries['วันเริ่มต้น (YYYY-MM-DD)'].get().strip()
            duration = entries['จำนวนวัน'].get().strip()
            location = entries['สถานที่'].get().strip()
            transportation = entries['การเดินทาง'].get().strip()
            benefits = entries['สวัสดิการ'].get().strip()
            slots = entries['จำนวนที่รับ (slots)'].get().strip()
            contact = entries['ติดต่อ'].get().strip()
            description = entries['รายละเอียด'].get('1.0', 'end').strip()

            if not name or not start_date or not slots:
                messagebox.showerror('Error', 'กรุณากรอกชื่อค่าย วันเริ่มต้น และจำนวนที่รับ')
                return
            try:
                int(slots)
            except Exception:
                messagebox.showerror('Error', 'จำนวนที่รับต้องเป็นตัวเลข')
                return

            camp = {
                'name': name,
                'start_date': start_date,
                'duration': duration or '1',
                'location': location,
                'transportation': transportation,
                'benefits': benefits,
                'slots': str(slots),
                'contact': contact,
                'description': description,
                'creator': getattr(self, 'current_user', '')
            }
            self.camps.append(camp)
            self.save_data()
            messagebox.showinfo('สำเร็จ', 'เพิ่มค่ายเรียบร้อยแล้ว')
            dialog.destroy()
            self.show_organizer_interface()

        ctk.CTkButton(dialog, text='เพิ่มค่าย', command=do_add, width=180).pack(pady=12)

    def delete_camp(self, index):
        if index < 0 or index >= len(self.camps):
            return
        if not messagebox.askyesno('ยืนยัน', f'แน่ใจหรือไม่ที่จะลบค่าย "{self.camps[index].get("name")}" ?'):
            return
        self.camps.pop(index)
        self.save_data()
        messagebox.showinfo('สำเร็จ', 'ลบค่ายเรียบร้อยแล้ว')
        self.show_organizer_interface()

    def view_participants(self, index):
        # placeholder: show simple dialog listing bookings for this camp
        participants = [b for b in self.bookings if b.get('camp_id') == index]
        dialog = ctk.CTkToplevel(self.root)
        dialog.title('ผู้สมัคร')
        dialog.geometry('480x360')
        dialog.grab_set()
        if not participants:
            ctk.CTkLabel(dialog, text='ยังไม่มีผู้สมัครสำหรับค่ายนี้', font=ctk.CTkFont(size=14)).pack(pady=20)
            return
        frame = ctk.CTkScrollableFrame(dialog, width=440, height=300)
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        for p in participants:
            text = f"{p.get('name','-')} | เบอร์: {p.get('phone','-')} | วันที่: {p.get('date','-')}"
            ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=12), anchor='w').pack(fill='x', pady=6, padx=6)

    def show_edit_camp_dialog(self, index):
        if index < 0 or index >= len(self.camps):
            return
        camp = self.camps[index]
        dialog = ctk.CTkToplevel(self.root)
        dialog.title('แก้ไขค่าย')
        dialog.geometry('700x600')
        dialog.grab_set()

        canvas = ctk.CTkFrame(dialog)
        canvas.pack(fill='both', expand=True, padx=12, pady=12)

        labels = ['ชื่อค่าย', 'วันเริ่มต้น (YYYY-MM-DD)', 'จำนวนวัน', 'สถานที่', 'การเดินทาง', 'สวัสดิการ', 'จำนวนที่รับ (slots)', 'ติดต่อ', 'รายละเอียด']
        entries = {}

        vals = [camp.get('name',''), camp.get('start_date',''), camp.get('duration',''), camp.get('location',''), camp.get('transportation',''), camp.get('benefits',''), camp.get('slots',''), camp.get('contact',''), camp.get('description','')]

        for i, lbl in enumerate(labels[:-1]):
            ctk.CTkLabel(canvas, text=lbl + ':').grid(row=i, column=0, sticky='e', padx=6, pady=6)
            e = ctk.CTkEntry(canvas, width=420)
            e.insert(0, vals[i])
            e.grid(row=i, column=1, padx=6, pady=6)
            entries[lbl] = e

        ctk.CTkLabel(canvas, text=labels[-1] + ':').grid(row=len(labels)-1, column=0, sticky='ne', padx=6, pady=6)
        desc = scrolledtext.ScrolledText(canvas, width=50, height=6)
        desc.insert('1.0', vals[-1])
        desc.grid(row=len(labels)-1, column=1, padx=6, pady=6)
        entries['รายละเอียด'] = desc

        def do_save():
            camp['name'] = entries['ชื่อค่าย'].get().strip()
            camp['start_date'] = entries['วันเริ่มต้น (YYYY-MM-DD)'].get().strip()
            camp['duration'] = entries['จำนวนวัน'].get().strip()
            camp['location'] = entries['สถานที่'].get().strip()
            camp['transportation'] = entries['การเดินทาง'].get().strip()
            camp['benefits'] = entries['สวัสดิการ'].get().strip()
            camp['slots'] = entries['จำนวนที่รับ (slots)'].get().strip()
            camp['contact'] = entries['ติดต่อ'].get().strip()
            camp['description'] = entries['รายละเอียด'].get('1.0', 'end').strip()
            self.save_data()
            messagebox.showinfo('สำเร็จ', 'บันทึกการแก้ไขเรียบร้อย')
            dialog.destroy()
            self.show_organizer_interface()

        ctk.CTkButton(dialog, text='บันทึกการแก้ไข', command=do_save, width=180).pack(pady=12)

    def show_notifications(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        title_frame = ctk.CTkFrame(self.root, fg_color="#C62828", height=80)
        title_frame.pack(fill="x")
        back_btn = ctk.CTkButton(title_frame, text="← กลับ", command=self.create_main_interface, width=100, fg_color="#B71C1C")
        back_btn.pack(side="left", padx=20, pady=20)
        title_label = ctk.CTkLabel(title_frame, text="🔔 การแจ้งเตือน", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        title_label.pack(side="left", padx=20)
        frame = ctk.CTkScrollableFrame(self.root, width=1150, height=650)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        if not self.notifications:
            ctk.CTkLabel(frame, text="ยังไม่มีการแจ้งเตือน", font=ctk.CTkFont(size=16)).pack(pady=20)
        else:
            for n in self.notifications:
                ctk.CTkLabel(frame, text=n, font=ctk.CTkFont(size=14), anchor="w").pack(fill="x", pady=5, padx=10)

    def show_all_bookings(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        title_frame = ctk.CTkFrame(self.root, fg_color="#7B1FA2", height=80)
        title_frame.pack(fill="x")
        back_btn = ctk.CTkButton(title_frame, text="← กลับ", command=self.create_main_interface, width=100, fg_color="#6A1B9A")
        back_btn.pack(side="left", padx=20, pady=20)
        title_label = ctk.CTkLabel(title_frame, text="📋 รายการการจองทั้งหมด", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        title_label.pack(side="left", padx=20)
        frame = ctk.CTkScrollableFrame(self.root, width=1150, height=650)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        if not self.bookings:
            ctk.CTkLabel(frame, text="ยังไม่มีรายการการจอง", font=ctk.CTkFont(size=16)).pack(pady=20)
        else:
            for b in self.bookings:
                text = f"ค่าย ID: {b.get('camp_id')} | ชื่อ: {b.get('name')} | วันที่: {b.get('date')}"
                ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=14), anchor="w").pack(fill="x", pady=5, padx=10)
    
    def book_camp(self, camp_id, camp_name):
        """จองค่าย"""
        # ป๊อปอัพกรอกข้อมูล
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("กรอกข้อมูลการจอง")
        dialog.geometry("400x350")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text=f"จองค่าย: {camp_name}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # ฟอร์มกรอกข้อมูล
        ctk.CTkLabel(dialog, text="ชื่อ-นามสกุล:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        # (form fields and submission buttons would follow here)


def main():
    app = CampBookingPlatform()
    try:
        app.root.lift()
        app.root.attributes("-topmost", True)
        app.root.after(500, lambda: app.root.attributes("-topmost", False))
    except Exception:
        pass
    app.root.mainloop()


if __name__ == "__main__":
    main()