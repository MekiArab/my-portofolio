from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_FILE = "database.db"


def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        print("Database baru dibuat: database.db")

profile = {
    "name": "Moh. Krisna Bramantio",
    "role": "Amatir",
    "about": "Seorang pemula di Dunia IT",
    "skills": ["Main Game", "Python,Html,CSS tipis-tipis", "Tidur", "Main Gaple"]
}

projects = [
    {"id": 1, "title": "Website Portofolio", "desc": "Website sederhana berbasis Flask.", "details": "Tau ah Capek, sakit kepala ajgg"},
#     {"id": 2, "title": "Inventory Dashboard", "desc": "Dashboard stok barang real-time.", "details": "Statistik visual dengan database SQLite."},
    # {"id": 3, "title": "Portfolio Website", "desc": "Portofolio modern tema aqua.", "details": "Desain responsif dan form kontak aktif."}
]

ADMIN_USER = "krisna2107"
ADMIN_PASS = "kucingbabi123"

@app.route('/')
def home():
    return render_template('index.html', profile=profile, projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return "Proyek tidak ditemukan", 404
    return render_template('project.html', profile=profile, project=project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Semua field wajib diisi!', 'error')
            return redirect(url_for('contact'))

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        flash('Pesan berhasil dikirim!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', profile=profile)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if user == ADMIN_USER and pw == ADMIN_PASS:
            session['admin_logged_in'] = True
            flash('Hello Krishhh!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Login dulu untuk mengakses dashboard.', 'error')
        return redirect(url_for('login'))

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC")
        messages = cur.fetchall()
        total = len(messages)

    return render_template('admin.html', profile=profile, messages=messages, total=total)

@app.route('/admin/delete/<int:msg_id>')
def delete_message(msg_id):
    if not session.get('admin_logged_in'):
        flash('Tidak diizinkan.', 'error')
        return redirect(url_for('login'))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM messages WHERE id=?", (msg_id,))
    flash('Pesan berhasil dihapus.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
