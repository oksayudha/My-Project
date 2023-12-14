from flask import Flask, render_template, session,\
    request, redirect, url_for
import mysql.connector
from models import User

application = Flask(__name__)
application.config['SECRET_KEY'] = '1234567890987654321'
application.config['DB_USER'] = 'root'
application.config['DB_PASSWORD'] = 'root'
application.config['DB_NAME'] = 'keripikdb'
application.config['DB_HOST'] = 'localhost'
conn = cursor = None


def openDb():
    global conn, cursor
    conn = mysql.connector.connect(
        user=application.config['DB_USER'],
        password=application.config['DB_PASSWORD'],
        database=application.config['DB_NAME'],
        host=application.config['DB_HOST'],
    )
    cursor = conn.cursor()


def closeDb():
    global conn, cursor
    cursor.close()
    conn.close()

# --------------------- Modul Login dan Home --------------------


@application.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, password)
        if user.authenticate():
            session['username'] = username
            return redirect(url_for('dashboard'))
        pesan = 'gagal'
        return render_template('login.html', pesan=pesan)
    pesan = 'belum_login'
    return render_template('login.html', pesan=pesan)


@application.route('/logout')
def logout():
    session.pop('username', None)
    pesan = 'logout'
    return render_template('login.html', pesan=pesan)


@application.route('/dashboard')
def dashboard():
    return render_template('index.html')


# -------------------- Modul Pelanggan -------------------------


@application.route('/masterpelanggan')
def masterpelanggan():
    openDb()
    cursor.execute('SELECT * FROM pelanggan')
    container = []
    for pelanggan_id, pelanggan_nama, pelanggan_tlp, pelanggan_alamat in cursor.fetchall():
        container.append((pelanggan_id, pelanggan_nama,
                         pelanggan_tlp, pelanggan_alamat))
    closeDb()
    return render_template('masterpelanggan.html', container=container, menu='master', submenu='pengguna')


@application.route('/tambah_pelanggan', methods=['GET', 'POST'])
def tambah_pelanggan():
    if request.method == 'POST':
        nama = request.form['nama']
        telp = request.form['telp']
        alamat = request.form['alamat']
        data = (nama, telp, alamat)
        openDb()
        cursor.execute('''
        INSERT INTO pelanggan (pelanggan_nama,pelanggan_tlp,pelanggan_alamat)
        VALUES('%s','%s','%s')''' % data)
        conn.commit()
        closeDb()
        return redirect(url_for('masterpelanggan'))
    else:
        return render_template('tambah_form_pelanggan.html')


@application.route('/ubah_pelanggan/<id>', methods=['GET', 'POST'])
def pelanggan_ubah(id):
    openDb()
    cursor.execute("SELECT * FROM pelanggan WHERE pelanggan_id='%s'" % id)
    data = cursor.fetchone()
    if request.method == 'POST':
        id = request.form['id']
        nama = request.form['nama']
        telp = request.form['telp']
        alamat = request.form['alamat']
        cursor.execute('''
        UPDATE pelanggan SET pelanggan_nama='%s', pelanggan_tlp='%s',
pelanggan_alamat='%s'
        WHERE pelanggan_id='%s'
    ''' % (nama, telp, alamat, id))
        conn.commit()
        closeDb()
        return redirect(url_for('masterpelanggan'))
    else:
        closeDb()
        return render_template('ubah_form_pelanggan.html', data=data)


@application.route('/hapus_pelanggan/<id>', methods=['GET', 'POST'])
def pelanggan_hapus(id):
    openDb()
    cursor.execute("DELETE FROM pelanggan WHERE pelanggan_id='%s'" % id)
    conn.commit()
    closeDb()
    return redirect(url_for('masterpelanggan'))

@application.route('/get_pelanggan_count')
def get_pelanggan_count():
    openDb()
    cursor.execute("SELECT COUNT(*) FROM pelanggan")
    pelanggan_count = cursor.fetchone()[0]
    closeDb()

    return str(pelanggan_count)

# ------------------- Modul Pemesanan --------------------------


@application.route('/masterpemesanan')
def masterpemesanan():
    openDb()
    cursor.execute('SELECT * FROM pemesanan')
    container = []
    for pesanan_id, pesanan_pelanggan, pesanan_jml, pesanan_harga, pesanan_tgl in cursor.fetchall():
        container.append((pesanan_id, pesanan_pelanggan,
                          pesanan_jml, pesanan_harga, pesanan_tgl))
    closeDb()
    return render_template('masterpemesanan.html', menu='master', submenu='pemesanan', container=container)


@application.route('/tambah_pemesanan', methods=['GET', 'POST'])
def tambah_pemesanan():
    openDb()
    cursor.execute("SELECT pelanggan_nama FROM pelanggan")
    pelanggan = cursor.fetchall()
    cursor.execute("SELECT harga_per_item FROM harga")
    harga_per_item = cursor.fetchone()[0]
    closeDb()

    if request.method == 'POST':
        pesanan_plgn = request.form['pesanan_plgn']
        pesanan_jml = int(request.form['pesanan_jml'])
        pesanan_hrg = pesanan_jml *  harga_per_item
        pesanan_tanggal = request.form['pesanan_tanggal']
        data = (pesanan_plgn, pesanan_jml, pesanan_hrg, pesanan_tanggal)

        openDb()
        transaksi_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO pemesanan (pesanan_pelanggan, pesanan_jml, pesanan_harga, pesanan_tgl) VALUES (%s, %s, %s, %s)", data)
        conn.commit()
        closeDb()

        return redirect(url_for('masterpemesanan', transaksi_id=transaksi_id))
    else:
        return render_template('tambah_form_pemesanan.html', pelanggan=pelanggan, harga_per_item=harga_per_item)



@application.route('/ubah_pemesanan/<id>', methods=['GET', 'POST'])
def pesanan_ubah(id):
    openDb()
    cursor.execute("SELECT * FROM pemesanan WHERE pesanan_id='%s'" % id)
    data = cursor.fetchone()
    if request.method == 'POST':
        pesanan_pelanggan = request.form['pesanan_pelanggan']
        pesanan_jml = request.form['pesanan_jml']
        pesanan_hrg = request.form['pesanan_hrg']
        pesanan_tanggal = request.form['pesanan_tanggal']
        cursor.execute('''
        UPDATE pemesanan SET pesanan_pelanggan='%s', pesanan_jml='%s', pesanan_harga='%s', pesanan_tgl='%s'
        WHERE pesanan_id='%s'
        ''' % (pesanan_pelanggan, pesanan_jml, pesanan_hrg, pesanan_tanggal, id))
        conn.commit()
        closeDb()
        return redirect(url_for('masterpemesanan'))
    else:
        closeDb()
        return render_template('ubah_form_pemesanan.html', data=data)


@application.route('/hapus_pesanan/<id>', methods=['GET', 'POST'])
def hapus_pesanan(id):
    openDb()
    cursor.execute("DELETE FROM pemesanan WHERE pesanan_id='%s'" % id)
    conn.commit()
    closeDb()
    return redirect(url_for('masterpemesanan'))

@application.route('/get_pesanan_count')
def get_pesanan_count():
    openDb()
    cursor.execute("SELECT COUNT(*) FROM pemesanan")
    pesanan_count = cursor.fetchone()[0]
    closeDb()

    return str(pesanan_count)

if __name__ == '__main__':
    application.run(debug=True)
