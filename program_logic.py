import json
import os
from datetime import datetime

# ==========================================
# 1. ตัวแปรสถานะระบบ (State)
# ==========================================
camps = []
bookings = []
notifications = []
users = {}
current_user = None
users_file = 'users.json'
data_file = 'camps_data.json'

# ==========================================
# 2. ระบบจัดการไฟล์ข้อมูล
# ==========================================
def load_data():
    global camps, bookings, notifications
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                camps = data.get('camps', [])
                bookings = data.get('bookings', [])
                notifications = data.get('notifications', [])
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

def save_data():
    try:
        data = {'camps': camps, 'bookings': bookings, 'notifications': notifications}
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")

def load_users():
    global users
    users = {}
    try:
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการโหลดผู้ใช้: {e}")

def save_users():
    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกผู้ใช้: {e}")

# ==========================================
# 3. เมนูการทำงาน (Command Line Interface)
# ==========================================
def menu_login():
    global current_user
    while not current_user:
        print("\n" + "="*40)
        print("🏕️ ยินดีต้อนรับสู่แพลตฟอร์มจองค่าย")
        print("="*40)
        print("1. เข้าสู่ระบบ")
        print("2. สมัครสมาชิก")
        print("3. ออกจากโปรแกรม")
        
        choice = input("เลือกเมนู (1-3): ").strip()
        
        if choice == '1':
            u = input("ชื่อผู้ใช้: ").strip()
            p = input("รหัสผ่าน: ").strip()
            if users.get(u) == p:
                current_user = u
                print(f"\n✅ เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ {u}")
            else:
                print("\n❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                
        elif choice == '2':
            u = input("ตั้งชื่อผู้ใช้: ").strip()
            p = input("ตั้งรหัสผ่าน: ").strip()
            if not u or not p:
                print("\n❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            elif u in users:
                print("\n❌ ชื่อผู้ใช้นี้มีคนใช้แล้ว")
            else:
                users[u] = p
                save_users()
                print("\n✅ สมัครสมาชิกสำเร็จ! คุณสามารถเข้าสู่ระบบได้เลย")
                
        elif choice == '3':
            print("\nลาก่อนครับ!")
            return False
        else:
            print("\n❌ กรุณาเลือกเมนู 1-3")
    return True

def menu_view_camps():
    print("\n" + "-"*40)
    print("📋 รายชื่อค่ายทั้งหมด")
    print("-"*40)
    
    if not camps:
        print("ยังไม่มีค่ายในระบบ")
        return

    for idx, camp in enumerate(camps):
        booked = sum(1 for b in bookings if b.get('camp_id') == idx)
        slots = int(camp.get('slots', 0))
        available = max(0, slots - booked)
        
        print(f"[{idx}] 🏕️ {camp.get('name', '')} (เพิ่มโดย: {camp.get('creator', '')})")
        print(f"    วันที่: {camp.get('start_date', '')} | จำนวนวัน: {camp.get('duration', '')} วัน")
        print(f"    สถานที่: {camp.get('location', '')}")
        print(f"    รับสมัคร: {slots} คน | ว่าง: {available} ที่นั่ง")
        print(f"    รายละเอียด: {camp.get('description', '')}")
        print("-" * 20)
        
    print("\nตัวเลือก:")
    print("พิมพ์ตัวเลข ID ค่าย (เช่น 0, 1) เพื่อทำการจอง")
    print("พิมพ์ 'b' เพื่อกลับไปเมนูหลัก")
    
    choice = input("เลือก: ").strip()
    if choice.lower() == 'b':
        return
        
    try:
        camp_id = int(choice)
        if 0 <= camp_id < len(camps):
            book_camp(camp_id)
        else:
            print("❌ ไม่พบ ID ค่ายนี้")
    except ValueError:
        print("❌ ข้อมูลไม่ถูกต้อง")

def book_camp(camp_id):
    camp = camps[camp_id]
    booked = sum(1 for b in bookings if b.get('camp_id') == camp_id)
    slots = int(camp.get('slots', 0))
    already_booked = any(b.get('camp_id') == camp_id and b.get('user') == current_user for b in bookings)
    
    if camp.get('creator') == current_user:
        print("\n❌ คุณเป็นผู้สร้างค่ายนี้ ไม่สามารถจองเองได้")
        return
        
    if already_booked:
        print("\n❌ คุณได้จองค่ายนี้แล้ว")
        return
    
    if booked >= slots:
        print("\n❌ ค่ายนี้ที่นั่งเต็มแล้ว")
        return
        
    confirm = input(f"\nยืนยันการจองค่าย '{camp['name']}' หรือไม่? (y/n): ").strip().lower()
    if confirm == 'y':
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        bookings.append({
            'camp_id': camp_id,
            'user': current_user,
            'time': timestamp
        })
        notifications.append({
            'time': timestamp,
            'message': f"{current_user} จองค่าย {camp['name']}"
        })
        save_data()
        print("\n✅ จองค่ายสำเร็จ!")

def menu_manage_camps():
    print("\n" + "-"*40)
    print("🏢 จัดการค่ายของคุณ (ผู้จัดค่าย)")
    print("-"*40)
    print("1. เพิ่มค่ายใหม่")
    print("2. ดูผู้สมัครค่ายของฉัน")
    print("3. กลับเมนูหลัก")
    
    choice = input("เลือกเมนู (1-3): ").strip()
    
    if choice == '1':
        print("\n-- กรอกข้อมูลค่ายใหม่ --")
        name = input("ชื่อค่าย: ").strip()
        desc = input("รายละเอียด: ").strip()
        start_date = input("วันเริ่มต้น (YYYY-MM-DD): ").strip()
        duration = input("จำนวนวัน: ").strip()
        location = input("สถานที่: ").strip()
        transport = input("การเดินทาง: ").strip()
        benefits = input("สวัสดิการ: ").strip()
        slots = input("จำนวนที่รับสมัคร: ").strip()
        contact = input("ติดต่อ: ").strip()
        
        if not name or not slots.isdigit():
            print("\n❌ ข้อมูลไม่ถูกต้อง (ชื่อค่ายห้ามว่าง และจำนวนที่รับต้องเป็นตัวเลข)")
            return
            
        camps.append({
            'name': name, 'description': desc, 'start_date': start_date,
            'duration': duration, 'location': location, 'transportation': transport,
            'benefits': benefits, 'slots': slots, 'contact': contact,
            'creator': current_user
        })
        save_data()
        print("\n✅ เพิ่มค่ายใหม่สำเร็จ!")
        
    elif choice == '2':
        my_camps = [(i, c) for i, c in enumerate(camps) if c.get('creator') == current_user]
        if not my_camps:
            print("\nคุณยังไม่ได้สร้างค่ายใดๆ")
            return
            
        for idx, camp in my_camps:
            print(f"\nค่าย: {camp['name']} (ID: {idx})")
            parts = [b for b in bookings if b.get('camp_id') == idx]
            if not parts:
                print("  - ยังไม่มีผู้สมัคร")
            else:
                for p in parts:
                    print(f"  - ผู้สมัคร: {p['user']} (เวลาจอง: {p['time']})")

def menu_main():
    global current_user
    while current_user:
        print("\n" + "="*40)
        print(f"🏠 เมนูหลัก (เข้าสู่ระบบโดย: {current_user})")
        print("="*40)
        print("1. ดูค่ายทั้งหมดและจองค่าย")
        print("2. จัดการค่ายของฉัน (เพิ่มค่าย/ดูผู้สมัคร)")
        print("3. ดูการแจ้งเตือน")
        print("4. ออกจากระบบ")
        
        choice = input("เลือกเมนู (1-4): ").strip()
        
        if choice == '1':
            menu_view_camps()
        elif choice == '2':
            menu_manage_camps()
        elif choice == '3':
            print("\n🔔 การแจ้งเตือน:")
            if not notifications:
                print("- ไม่มีแจ้งเตือน -")
            else:
                for n in reversed(notifications[-10:]): # ดู 10 รายการล่าสุด
                    print(f"[{n['time']}] {n['message']}")
        elif choice == '4':
            print(f"\n👋 ออกจากระบบสำเร็จ ลาก่อน {current_user}!")
            current_user = None
        else:
            print("\n❌ กรุณาเลือกเมนู 1-4")

# ==========================================
# 4. จุดเริ่มต้นโปรแกรม
# ==========================================
def main():
    load_users()
    load_data()
    
    # วนลูปโปรแกรมจนกว่าผู้ใช้จะเลือก "ออกจากโปรแกรม" ในหน้าล็อกอิน
    while True:
        if not menu_login():
            break
        menu_main()

# เริ่มการทำงานเมื่อรันเซลล์
main()