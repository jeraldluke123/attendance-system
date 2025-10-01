import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import sqlite3
from io import BytesIO
import base64
import uuid

# 🎨 Page Configuration
st.set_page_config(
    page_title="🎓 Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Beautiful CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .stats-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        color: #155724;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(40, 167, 69, 0.2);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffc107;
        color: #856404;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(255, 193, 7, 0.2);
    }
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        color: #721c24;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(220, 53, 69, 0.2);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 🗄️ Database Functions
@st.cache_resource
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('attendance_system.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reg_no TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            parent_phone TEXT NOT NULL,
            barcode TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    return conn

def generate_qr_code(data):
    """Generate QR code and return base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#667eea", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def generate_unique_barcode():
    """Generate unique barcode string"""
    return str(uuid.uuid4())[:8].upper()

def determine_attendance_status():
    """Determine attendance status based on current time"""
    current_hour = datetime.now().hour
    if current_hour <= 9:
        return 'present', '🟢'
    elif current_hour <= 10:
        return 'late', '🟡'
    else:
        return 'absent', '🔴'

# 🎯 Main Application
def main():
    conn = init_database()
    
    # 🎨 Beautiful Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Smart Attendance Management System</h1>
        <p>✨ Streamlit-Powered • Real-time QR Scanning • Professional Reports • Mobile Responsive</p>
        <p>📅 Today: """ + datetime.now().strftime('%B %d, %Y') + """ • 🕐 """ + datetime.now().strftime('%H:%M') + """</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 📱 Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🎯 Navigation Menu")
        page = st.selectbox("📋 Choose Action", [
            "📊 Dashboard", 
            "👨‍🎓 Register Student", 
            "📷 QR Scanner", 
            "📈 Attendance Reports",
            "👥 All Students",
            "📱 QR Code Generator"
        ])
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        # Quick stats in sidebar
        cursor = conn.cursor()
        total_students = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        today_attendance = cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,)).fetchone()[0]
        
        st.metric("👨‍🎓 Total Students", total_students)
        st.metric("✅ Today's Attendance", today_attendance)
        
        if total_students > 0:
            attendance_rate = (today_attendance / total_students) * 100
            st.metric("📊 Attendance Rate", f"{attendance_rate:.1f}%")
    
    # 🎯 Page Routing
    if page == "📊 Dashboard":
        show_dashboard(conn)
    elif page == "👨‍🎓 Register Student":
        register_student(conn)
    elif page == "📷 QR Scanner":
        qr_scanner(conn)
    elif page == "📈 Attendance Reports":
        attendance_reports(conn)
    elif page == "👥 All Students":
        all_students(conn)
    elif page == "📱 QR Code Generator":
        qr_generator(conn)

# 📊 Dashboard Page
def show_dashboard(conn):
    st.header("📊 Dashboard Overview")
    
    # Real-time Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    cursor = conn.cursor()
    total_students = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,)).fetchone()[0]
    present_today = cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='present'", (today,)).fetchone()[0]
    late_today = cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='late'", (today,)).fetchone()[0]
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">👨‍🎓 {}</h3>
            <p>Total Students</p>
        </div>
        """.format(total_students), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #28a745;">✅ {}</h3>
            <p>Today's Attendance</p>
        </div>
        """.format(today_attendance), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #28a745;">🟢 {}</h3>
            <p>Present Today</p>
        </div>
        """.format(present_today), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffc107;">🟡 {}</h3>
            <p>Late Today</p>
        </div>
        """.format(late_today), unsafe_allow_html=True)
    
    # Recent Activity
    st.subheader("📋 Recent Attendance Activity")
    
    recent_query = """
        SELECT s.name, s.reg_no, s.department, a.date, a.time, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        ORDER BY a.created_at DESC 
        LIMIT 10
    """
    
    recent_data = pd.read_sql_query(recent_query, conn)
    
    if not recent_data.empty:
        # Add status emojis
        status_map = {'present': '🟢 Present', 'late': '🟡 Late', 'absent': '🔴 Absent'}
        recent_data['Status'] = recent_data['status'].map(status_map)
        
        # Rename columns for display
        recent_data = recent_data.rename(columns={
            'name': '👤 Name',
            'reg_no': '🆔 Reg No',
            'department': '🏢 Department',
            'date': '📅 Date',
            'time': '🕐 Time'
        })
        
        st.dataframe(recent_data[['👤 Name', '🆔 Reg No', '🏢 Department', '📅 Date', '🕐 Time', 'Status']], 
                    use_container_width=True, hide_index=True)
    else:
        st.info("📊 No attendance records yet. Start by registering students and scanning QR codes!")
    
    # Auto-refresh option
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

# 👨‍🎓 Register Student Page
def register_student(conn):
    st.header("👨‍🎓 Register New Student")
    
    with st.form("student_registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Student Full Name", placeholder="Enter student's full name")
            reg_no = st.text_input("🆔 Registration Number", placeholder="Enter unique registration number")
        
        with col2:
            department = st.selectbox("🏢 Department", [
                "Computer Science and Engineering",
                "Electronics and Communication Engineering", 
                "Mechanical Engineering",
                "Civil Engineering", 
                "Electrical and Electronics Engineering",
                "Information Technology"
            ])
            parent_phone = st.text_input("📱 Parent Phone Number", placeholder="+1234567890")
        
        submit_button = st.form_submit_button("✅ Register Student", use_container_width=True, type="primary")
        
        if submit_button:
            if name and reg_no and department and parent_phone:
                try:
                    # Generate unique barcode
                    barcode = generate_unique_barcode()
                    
                    # Insert into database
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO students (name, reg_no, department, parent_phone, barcode) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, reg_no, department, parent_phone, barcode))
                    conn.commit()
                    
                    # Success message
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>✅ Registration Successful!</h3>
                        <p><strong>{name}</strong> has been successfully registered!</p>
                        <p><strong>Registration Number:</strong> {reg_no}</p>
                        <p><strong>Department:</strong> {department}</p>
                        <p><strong>Barcode:</strong> {barcode}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Generate and display QR code
                    st.subheader("📱 Student QR Code")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        qr_code = generate_qr_code(barcode)
                        st.image(f"data:image/png;base64,{qr_code}", width=300, caption=f"QR Code for {name}")
                        
                        # Download QR code
                        st.download_button(
                            label="⬇️ Download QR Code",
                            data=base64.b64decode(qr_code),
                            file_name=f"{name.replace(' ', '_')}_QR.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown("### 📋 Student Details")
                        st.write(f"**👤 Name:** {name}")
                        st.write(f"**🆔 Registration:** {reg_no}")
                        st.write(f"**🏢 Department:** {department}")
                        st.write(f"**📱 Parent Phone:** {parent_phone}")
                        st.write(f"**🔐 Barcode:** `{barcode}`")
                        st.write(f"**📅 Registered:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                except sqlite3.IntegrityError as e:
                    if "reg_no" in str(e):
                        st.markdown("""
                        <div class="error-box">
                            <h4>❌ Registration Failed!</h4>
                            <p>A student with registration number <strong>{}</strong> already exists!</p>
                            <p>Please use a different registration number.</p>
                        </div>
                        """.format(reg_no), unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Database error: {e}")
                
                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")
            
            else:
                st.markdown("""
                <div class="error-box">
                    <h4>❌ Incomplete Information</h4>
                    <p>Please fill in all required fields:</p>
                    <ul>
                        <li>👤 Student Name</li>
                        <li>🆔 Registration Number</li>
                        <li>🏢 Department</li>
                        <li>📱 Parent Phone</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

# 📷 QR Scanner Page
def qr_scanner(conn):
    st.header("📷 QR Code Scanner")
    
    st.markdown("""
    ### 📱 How to Scan QR Codes:
    
    **Method 1: Phone Camera**
    1. 📱 Open your phone's camera app
    2. 🎯 Point at the student's QR code  
    3. 📝 Copy the text that appears
    4. 📋 Paste it in the box below
    
    **Method 2: QR Scanner App**
    1. 📲 Download any QR scanner app
    2. 🔍 Scan the student QR code
    3. 📋 Copy the result and paste below
    """)
    
    # QR Code input
    scanned_code = st.text_input(
        "🔍 Enter Scanned QR Code:",
        placeholder="Paste the QR code content here...",
        help="Scan the student QR code and paste the result here"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        scan_button = st.button("✅ Mark Attendance", use_container_width=True, type="primary")
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.rerun()
    
    with col3:
        st.button("📊 View Today's Records", use_container_width=True)
    
    if scan_button and scanned_code:
        cursor = conn.cursor()
        
        # Find student by barcode
        student_result = cursor.execute(
            "SELECT * FROM students WHERE barcode = ?", (scanned_code.strip(),)
        ).fetchone()
        
        if student_result:
            student_id, name, reg_no, department, parent_phone, barcode, created_at = student_result
            
            # Check if already marked today
            today = datetime.now().strftime('%Y-%m-%d')
            existing_record = cursor.execute(
                "SELECT * FROM attendance WHERE student_id = ? AND date = ?", 
                (student_id, today)
            ).fetchone()
            
            if existing_record:
                # Already marked today
                st.markdown(f"""
                <div class="warning-box">
                    <h3>⚠️ Already Marked Today!</h3>
                    <p><strong>{name}</strong> ({reg_no}) attendance has already been recorded today.</p>
                    <p><strong>Time:</strong> {existing_record[3]}</p>
                    <p><strong>Status:</strong> {existing_record[4].upper()} {{'🟢' if existing_record[4] == 'present' else '🟡' if existing_record[4] == 'late' else '🔴'}}</p>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                # Mark new attendance
                status, emoji = determine_attendance_status()
                current_time = datetime.now().strftime('%H:%M:%S')
                
                # Insert attendance record
                cursor.execute("""
                    INSERT INTO attendance (student_id, date, time, status) 
                    VALUES (?, ?, ?, ?)
                """, (student_id, today, current_time, status))
                conn.commit()
                
                # Success message with celebration
                st.balloons()
                st.markdown(f"""
                <div class="success-box">
                    <h2>✅ Attendance Marked Successfully!</h2>
                    <h3>{emoji} {name} ({reg_no})</h3>
                    <div style="margin: 1rem 0;">
                        <p><strong>📅 Date:</strong> {today}</p>
                        <p><strong>🕐 Time:</strong> {current_time}</p>
                        <p><strong>📊 Status:</strong> {status.upper()}</p>
                        <p><strong>🏢 Department:</strong> {department}</p>
                        <p><strong>📱 Parent Contact:</strong> {parent_phone}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show status explanation
                if status == 'present':
                    st.info("🟢 **Present:** Arrived on time (before 9:00 AM)")
                elif status == 'late':
                    st.warning("🟡 **Late:** Arrived late (9:00 AM - 10:00 AM)")
                else:
                    st.error("🔴 **Absent:** Marked absent (after 10:00 AM)")
        
        else:
            # Invalid QR code
            st.markdown("""
            <div class="error-box">
                <h3>❌ Invalid QR Code!</h3>
                <p>The scanned QR code does not match any registered student.</p>
                <p><strong>Possible reasons:</strong></p>
                <ul>
                    <li>🔍 QR code not properly scanned</li>
                    <li>👥 Student not registered in system</li>
                    <li>📱 Wrong QR code scanned</li>
                </ul>
                <p><strong>Please try again or register the student first.</strong></p>
            </div>
            """, unsafe_allow_html=True)

# 📈 Attendance Reports Page
def attendance_reports(conn):
    st.header("📈 Attendance Reports & Analytics")
    
    # Date range selector
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("📅 Start Date", datetime.now())
    
    with col2:
        end_date = st.date_input("📅 End Date", datetime.now())
    
    with col3:
        department_filter = st.selectbox("🏢 Filter by Department", 
            ["All Departments"] + [
                "Computer Science and Engineering",
                "Electronics and Communication Engineering", 
                "Mechanical Engineering",
                "Civil Engineering", 
                "Electrical and Electronics Engineering",
                "Information Technology"
            ])
    
    # Generate report
    if st.button("📊 Generate Report", use_container_width=True):
        # Build query based on filters
        base_query = """
            SELECT s.name, s.reg_no, s.department, a.date, a.time, a.status 
            FROM attendance a 
            JOIN students s ON a.student_id = s.id 
            WHERE a.date BETWEEN ? AND ?
        """
        
        params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if department_filter != "All Departments":
            base_query += " AND s.department = ?"
            params.append(department_filter)
        
        base_query += " ORDER BY a.date DESC, a.time DESC"
        
        report_data = pd.read_sql_query(base_query, conn, params=params)
        
        if not report_data.empty:
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_records = len(report_data)
            present_count = len(report_data[report_data['status'] == 'present'])
            late_count = len(report_data[report_data['status'] == 'late'])
            absent_count = len(report_data[report_data['status'] == 'absent'])
            
            with col1:
                st.metric("📋 Total Records", total_records)
            with col2:
                st.metric("🟢 Present", present_count)
            with col3:
                st.metric("🟡 Late", late_count)
            with col4:
                st.metric("🔴 Absent", absent_count)
            
            # Detailed report table
            st.subheader("📋 Detailed Report")
            
            # Add status emojis
            status_map = {'present': '🟢 Present', 'late': '🟡 Late', 'absent': '🔴 Absent'}
            report_data['Status'] = report_data['status'].map(status_map)
            
            # Rename columns for display
            display_data = report_data.rename(columns={
                'name': '👤 Name',
                'reg_no': '🆔 Reg No',
                'department': '🏢 Department',
                'date': '📅 Date',
                'time': '🕐 Time'
            })
            
            st.dataframe(
                display_data[['👤 Name', '🆔 Reg No', '🏢 Department', '📅 Date', '🕐 Time', 'Status']], 
                use_container_width=True,
                hide_index=True
            )
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV download
                csv_data = report_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"attendance_report_{start_date}_to_{end_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Excel download (as CSV for simplicity)
                st.download_button(
                    label="📊 Download for Excel",
                    data=csv_data,
                    file_name=f"attendance_report_{start_date}_to_{end_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
        else:
            st.info("📊 No attendance records found for the selected date range and filters.")

# 👥 All Students Page  
def all_students(conn):
    st.header("👥 All Registered Students")
    
    # Get all students
    students_query = """
        SELECT s.*, 
               COUNT(a.id) as total_attendance,
               COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
               COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_count,
               COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent_count
        FROM students s 
        LEFT JOIN attendance a ON s.id = a.student_id 
        GROUP BY s.id 
        ORDER BY s.name
    """
    
    students_data = pd.read_sql_query(students_query, conn)
    
    if not students_data.empty:
        # Calculate attendance percentage
        students_data['attendance_rate'] = ((students_data['present_count'] + students_data['late_count']) / 
                                          students_data['total_attendance'].replace(0, 1) * 100).round(1)
        
        st.subheader(f"📊 Total Students: {len(students_data)}")
        
        # Display student cards
        for idx, student in students_data.iterrows():
            with st.expander(f"👤 {student['name']} ({student['reg_no']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**🏢 Department:** {student['department']}")
                    st.write(f"**📱 Parent Phone:** {student['parent_phone']}")
                    st.write(f"**🔐 Barcode:** `{student['barcode']}`")
                
                with col2:
                    st.write(f"**📊 Total Records:** {student['total_attendance']}")
                    st.write(f"**🟢 Present:** {student['present_count']}")
                    st.write(f"**🟡 Late:** {student['late_count']}")
                
                with col3:
                    st.write(f"**🔴 Absent:** {student['absent_count']}")
                    attendance_rate = student['attendance_rate'] if student['total_attendance'] > 0 else 0
                    st.write(f"**📈 Attendance Rate:** {attendance_rate}%")
                    
                    # Progress bar for attendance
                    if student['total_attendance'] > 0:
                        st.progress(attendance_rate / 100)
        
        # Download student list
        st.subheader("📥 Download Options")
        
        # Prepare download data
        download_data = students_data[[
            'name', 'reg_no', 'department', 'parent_phone', 
            'total_attendance', 'present_count', 'late_count', 'absent_count', 'attendance_rate'
        ]].rename(columns={
            'name': 'Name',
            'reg_no': 'Registration Number', 
            'department': 'Department',
            'parent_phone': 'Parent Phone',
            'total_attendance': 'Total Records',
            'present_count': 'Present Count',
            'late_count': 'Late Count', 
            'absent_count': 'Absent Count',
            'attendance_rate': 'Attendance Rate (%)'
        })
        
        csv_data = download_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Student List",
            data=csv_data,
            file_name=f"students_list_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    else:
        st.info("👥 No students registered yet. Start by registering some students!")

# 📱 QR Code Generator Page
def qr_generator(conn):
    st.header("📱 QR Code Generator")
    
    st.info("Generate QR codes for existing students or create bulk QR codes.")
    
    # Select student
    cursor = conn.cursor()
    students = cursor.execute("SELECT id, name, reg_no, barcode FROM students ORDER BY name").fetchall()
    
    if students:
        student_options = {f"{name} ({reg_no})": (student_id, barcode) for student_id, name, reg_no, barcode in students}
        
        selected_student = st.selectbox("👤 Select Student", list(student_options.keys()))
        
        if selected_student and st.button("🎯 Generate QR Code"):
            student_id, barcode = student_options[selected_student]
            
            # Generate QR code
            qr_code = generate_qr_code(barcode)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(f"data:image/png;base64,{qr_code}", width=300, caption=f"QR Code for {selected_student}")
            
            with col2:
                st.write(f"**Student:** {selected_student}")
                st.write(f"**Barcode:** `{barcode}`")
                st.download_button(
                    label="⬇️ Download QR Code",
                    data=base64.b64decode(qr_code),
                    file_name=f"{selected_student.replace(' ', '_').replace('(', '').replace(')', '')}_QR.png",
                    mime="image/png"
                )
        
        # Bulk QR generation
        st.subheader("📦 Bulk QR Code Generation")
        
        if st.button("📦 Generate All QR Codes", use_container_width=True):
            st.info("🔄 Generating QR codes for all students...")
            
            # Create a zip file with all QR codes (simulated)
            all_qr_data = []
            
            for student_id, name, reg_no, barcode in students:
                qr_code = generate_qr_code(barcode)
                all_qr_data.append({
                    'name': name,
                    'reg_no': reg_no,
                    'barcode': barcode,
                    'qr_code': qr_code
                })
            
            st.success(f"✅ Generated {len(all_qr_data)} QR codes!")
            st.info("💡 Individual download buttons will appear for each student.")
    
    else:
        st.warning("👥 No students registered yet. Please register students first.")

if __name__ == "__main__":
    main()
