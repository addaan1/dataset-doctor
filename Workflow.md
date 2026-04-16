## Nama project

Saya sarankan nama ini:

**Dataset Doctor**

Tagline:
**“Turn messy CSV files into an instant data health report.”**

Alternatif nama lain:

* **CSV Doctor**
* **DataPulse**
* **Tabular Medic**
* **DataCard Lite**
* **TidyAudit**

Dari semuanya, **Dataset Doctor** paling enak karena:

* mudah diingat,
* terdengar berguna,
* cocok untuk open source,
* cukup “branding-friendly” untuk README dan social preview.

---

# Gambaran project

Kamu akan membuat tool Python open source yang:

* menerima file CSV,
* menganalisis kualitas data,
* memberi warning sederhana,
* lalu menghasilkan **laporan HTML + Markdown**.

Output minimal:

* jumlah baris dan kolom,
* tipe data,
* missing values,
* duplicate rows,
* unique values,
* kolom konstan,
* kolom dengan outlier sederhana,
* beberapa warning otomatis,
* ringkasan yang bisa dimasukkan ke README atau data card.

---

# Target hasil akhir 14 hari

Di akhir 14 hari, repo kamu sebaiknya sudah punya:

* kode Python yang berjalan
* command CLI seperti:
  `dataset-doctor data.csv`
* output:

  * `report.html`
  * `summary.md`
* README yang rapi
* 1 dataset demo
* screenshot / GIF demo
* license open source
* issues untuk kontribusi awal
* release v0.1.0

---

# Struktur project yang disarankan

```bash
dataset-doctor/
├─ dataset_doctor/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ analyzer.py
│  ├─ profiling.py
│  ├─ warnings.py
│  ├─ report.py
│  ├─ utils.py
│  └─ templates/
│     └─ report.html.j2
├─ examples/
│  └─ sample_dataset.csv
├─ outputs/
├─ tests/
│  ├─ test_analyzer.py
│  ├─ test_warnings.py
│  └─ test_report.py
├─ README.md
├─ LICENSE
├─ pyproject.toml
├─ .gitignore
└─ requirements.txt
```

---

# Roadmap 14 hari

## Hari 1 — Menentukan scope dan setup repo

Fokus hari ini: jangan coding terlalu banyak. Tentukan bentuk project dengan jelas.

Yang perlu dikerjakan:

* buat repo GitHub: `dataset-doctor`
* tulis deskripsi repo
* pilih lisensi, misalnya MIT
* buat struktur folder awal
* buat environment Python
* install library dasar:

  * pandas
  * jinja2
  * typer atau argparse
  * pytest
* tulis tujuan project dalam 1 paragraf

Output hari ini:

* repo sudah ada
* folder project sudah rapi
* file `README.md` awal sudah ada
* file `pyproject.toml` atau `requirements.txt` sudah dibuat

Checklist:

* project name final
* tagline final
* tujuan project jelas
* stack dipilih

---

## Hari 2 — Buat MVP definition

Fokus hari ini: tentukan fitur yang masuk versi pertama.

Yang perlu dikerjakan:

* tulis fitur **v1**
* tulis fitur **bukan v1**
* tentukan input dan output program
* buat daftar function utama

Fitur v1 yang saya sarankan:

* baca CSV
* tampilkan jumlah baris dan kolom
* tampilkan nama kolom
* tampilkan missing value count
* tampilkan duplicate row count
* tampilkan tipe data
* buat warning sederhana
* generate report HTML

Bukan v1:

* dashboard web
* drag-and-drop UI
* ML prediksi kualitas
* integrasi database
* GitHub Action otomatis

Function inti:

* `load_data()`
* `summarize_columns()`
* `check_missing_values()`
* `check_duplicates()`
* `detect_constant_columns()`
* `detect_high_cardinality()`
* `generate_warnings()`
* `render_html_report()`

Output hari ini:

* dokumen scope
* daftar fitur final v1
* pseudocode sederhana

---

## Hari 3 — Implementasi pembaca CSV dan summary dasar

Fokus hari ini: bikin tool benar-benar bisa jalan dari file CSV.

Yang perlu dikerjakan:

* buat `cli.py`
* buat command CLI dasar
* load CSV dengan pandas
* tampilkan summary dasar di terminal

Contoh:

```bash
python -m dataset_doctor.cli examples/sample_dataset.csv
```

Summary minimal:

* nama file
* jumlah baris
* jumlah kolom
* daftar nama kolom

Output hari ini:

* CSV bisa dibaca
* CLI awal berjalan
* tidak perlu report HTML dulu

---

## Hari 4 — Analisis missing values dan duplicates

Fokus hari ini: mulai masuk ke kualitas data.

Yang perlu dikerjakan:

* hitung missing value per kolom
* hitung persentase missing value
* hitung duplicate rows
* simpan hasil analisis dalam dictionary / object terstruktur

Misalnya hasil internal:

```python
{
  "row_count": 1000,
  "column_count": 12,
  "missing": {...},
  "duplicates": 45
}
```

Tambahan:

* urutkan kolom berdasarkan missing tertinggi
* tandai kolom yang missing lebih dari 30%

Output hari ini:

* data quality metrics awal sudah ada
* hasil bisa diprint rapi di terminal

---

## Hari 5 — Analisis tipe data dan struktur kolom

Fokus hari ini: pahami isi dataset.

Yang perlu dikerjakan:

* identifikasi kolom numerik, kategorikal, boolean, datetime sederhana
* hitung unique count per kolom
* deteksi kolom konstan
* deteksi high-cardinality columns

Aturan sederhana:

* konstan: unique hanya 1
* high-cardinality: unique ratio tinggi, misalnya > 0.8 untuk object/string

Output hari ini:

* dataset profile lebih lengkap
* bisa tahu kolom mana yang “mencurigakan”

---

## Hari 6 — Analisis distribusi sederhana dan outlier basic

Fokus hari ini: tambahkan sedikit “data science feel”.

Yang perlu dikerjakan:

* untuk kolom numerik, hitung:

  * min
  * max
  * mean
  * median
  * std
* deteksi outlier sederhana dengan IQR atau z-score
* jangan terlalu rumit, yang penting stabil

Saran:

* pakai **IQR** karena lebih mudah dijelaskan:

  * outlier < Q1 - 1.5*IQR
  * outlier > Q3 + 1.5*IQR

Output hari ini:

* statistik numerik tersedia
* outlier count per kolom tersedia

---

## Hari 7 — Sistem warning otomatis

Fokus hari ini: bikin project terasa pintar walau sebenarnya rule-based.

Yang perlu dikerjakan:

* buat file `warnings.py`
* definisikan rule warning sederhana

Contoh warning:

* “Kolom `email` punya 42% missing values.”
* “Dataset memiliki 12% baris duplikat.”
* “Kolom `user_id` terdeteksi high-cardinality.”
* “Kolom `status` konstan dan mungkin tidak informatif.”
* “Kolom `price` memiliki outlier tinggi.”

Buat output warning dengan level:

* info
* warning
* critical

Output hari ini:

* report kamu mulai terasa berguna, bukan cuma angka mentah

---

## Hari 8 — Generate Markdown summary

Fokus hari ini: hasil project harus mudah dibagikan.

Yang perlu dikerjakan:

* buat `summary.md`
* isi ringkasan otomatis:

  * dataset overview
  * top issues
  * recommended next steps

Contoh section:

* Overview
* Key Findings
* Problematic Columns
* Suggested Cleaning Actions

Contoh rekomendasi:

* drop duplicate rows
* imputasi missing values
* cek kembali kolom ID
* verifikasi outlier

Output hari ini:

* project sudah menghasilkan file yang enak dibaca manusia

---

## Hari 9 — Generate HTML report

Fokus hari ini: bikin hasilnya menarik secara visual.

Yang perlu dikerjakan:

* buat template Jinja2
* render HTML report
* tampilkan:

  * overview card
  * tabel missing value
  * warning panel
  * statistik numerik
  * top suspicious columns

Tidak perlu terlalu cantik dulu. Yang penting:

* rapi
* mudah dibaca
* ada heading jelas
* ada tabel

Output hari ini:

* `report.html` berhasil dihasilkan

---

## Hari 10 — Percantik tampilan report

Fokus hari ini: visual yang cukup bagus buat screenshot README.

Yang perlu dikerjakan:

* perbaiki layout HTML
* tambahkan warna level warning
* tambahkan badge kecil:

  * Healthy
  * Needs Review
  * Critical
* tambahkan score sederhana, misalnya:

  * mulai dari 100
  * kurangi poin untuk missing, duplicate, constant columns, outliers ekstrem

Contoh:

* missing berat: -20
* duplicate tinggi: -15
* constant columns: -5
* outlier banyak: -10

Output hari ini:

* report lebih layak dipamerkan
* kamu bisa ambil screenshot untuk README

---

## Hari 11 — Testing dan edge cases

Fokus hari ini: bikin project lebih solid.

Yang perlu dikerjakan:

* buat unit test untuk:

  * missing values
  * duplicate detection
  * constant column detection
  * warning generation
* uji dengan beberapa CSV kecil
* uji edge cases:

  * file kosong
  * kolom semua null
  * satu baris saja
  * delimiter aneh kalau mau

Output hari ini:

* minimal beberapa test lulus
* project lebih meyakinkan untuk open source

---

## Hari 12 — README yang kuat

Fokus hari ini: ini sangat penting untuk peluang dilihat orang.

Isi README:

* judul project
* tagline
* screenshot hasil report
* masalah yang diselesaikan
* demo singkat
* instalasi
* cara pakai
* contoh output
* roadmap
* kontribusi
* lisensi

Struktur README yang saya sarankan:

1. What is Dataset Doctor
2. Why this project exists
3. Features
4. Installation
5. Usage
6. Example output
7. Roadmap
8. Contributing
9. License

Tambahkan juga:

* GIF singkat atau screenshot
* contoh command
* contoh hasil HTML

Output hari ini:

* README sudah “menjual”

---

## Hari 13 — Rapikan repo untuk open source launch

Fokus hari ini: buat repo ramah pengunjung dan calon kontributor.

Yang perlu dikerjakan:

* buat issue templates sederhana
* buat label:

  * good first issue
  * bug
  * enhancement
  * documentation
* buat `CONTRIBUTING.md`
* buat `CHANGELOG.md`
* rapikan `.gitignore`
* tambahkan contoh dataset kecil

Kalau sempat:

* buat logo sederhana teks
* buat social preview image untuk repo

Output hari ini:

* repo terasa serius dan siap dilihat publik

---

## Hari 14 — Launch day

Fokus hari ini: publish dengan cara yang rapi.

Yang perlu dikerjakan:

* final testing
* rapikan commit history kalau perlu
* buat release `v0.1.0`
* publish post singkat di:

  * GitHub
  * LinkedIn
  * X / Twitter kalau punya
  * komunitas Python / data science

Template post:

* masalah apa yang sering dialami
* solusi yang kamu buat
* demo 1 gambar
* ajakan coba dan kontribusi

Contoh angle posting:

> I built Dataset Doctor, a simple open-source tool that turns messy CSV files into instant data health reports. It helps spot missing values, duplicates, constant columns, and suspicious fields in seconds.

Output hari ini:

* repo live
* release live
* project siap dibagikan

---

# Langkah teknis yang perlu kamu lakukan

## 1. Setup environment

Buat virtual environment dan install dependencies.

Contoh:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas jinja2 typer pytest
```

---

## 2. Buat CLI sederhana

Tujuannya agar user cukup menjalankan:

```bash
dataset-doctor path/to/data.csv
```

Kalau belum packaging penuh, bisa mulai dari:

```bash
python -m dataset_doctor.cli path/to/data.csv
```

---

## 3. Simpan semua hasil analisis dalam satu struktur data

Jangan langsung campur logika analisis dengan HTML.

Contoh:

```python
report_data = {
    "overview": {...},
    "columns": [...],
    "warnings": [...],
    "score": 82
}
```

Ini penting supaya:

* mudah dites
* mudah dibuat HTML
* mudah dibuat Markdown juga

---

## 4. Pisahkan logic per file

Agar project kelihatan profesional:

* `analyzer.py` untuk hitung statistik
* `warnings.py` untuk rule warning
* `report.py` untuk render output
* `cli.py` untuk command line

---

## 5. Buat minimal 1 dataset contoh

Contoh dataset demo sebaiknya punya:

* missing values
* duplicate row
* 1 kolom konstan
* 1 kolom numerik dengan outlier
* 1 kolom high-cardinality

Jadi saat demo, semua fitur terlihat.

---

## 6. Fokus pada hasil yang “terlihat”

Project open source lebih mudah menarik perhatian kalau output-nya visual.

Prioritas:

* HTML report
* screenshot menarik
* README yang jelas

Jangan terlalu lama di bagian backend yang tidak terlihat.

---

## 7. Gunakan issue kecil untuk menjaga progres

Bikin issue seperti:

* add CSV loader
* add missing value detection
* add duplicate detection
* add HTML rendering
* add markdown summary
* add basic tests
* improve README

Ini membantu:

* progres terasa jelas
* repo terlihat aktif
* mudah buat label `good first issue`

---

# Prioritas fitur

## Wajib ada

* load CSV
* summary dataset
* missing values
* duplicates
* unique counts
* constant columns
* high-cardinality detection
* warning messages
* HTML output
* README bagus

## Bagus kalau sempat

* score kualitas dataset
* Markdown summary
* outlier detection
* badge status

## Jangan dulu

* dashboard web
* upload file lewat browser
* AI/LLM integration
* database support
* banyak format file selain CSV

---

# Jadwal harian singkat

Kalau mau versi super ringkas:

**Hari 1** setup repo
**Hari 2** tetapkan scope MVP
**Hari 3** load CSV + CLI
**Hari 4** missing + duplicates
**Hari 5** data types + unique + constant
**Hari 6** stats numerik + outlier
**Hari 7** warning engine
**Hari 8** Markdown summary
**Hari 9** HTML report
**Hari 10** percantik report + score
**Hari 11** testing
**Hari 12** README
**Hari 13** open source polish
**Hari 14** launch

---

# Definisi sukses project ini

Setelah 14 hari, project kamu dianggap berhasil kalau:

* orang bisa clone repo dan menjalankannya dalam < 5 menit
* README langsung menjelaskan manfaatnya
* screenshot output terlihat menarik
* demo dataset menunjukkan fitur utama
* kodenya cukup rapi untuk dikembangkan lagi

---

# Saran kerja harian

Agar tidak burnout:

* target kerja per hari: **1 output nyata**
* jangan mengejar semua fitur
* prioritaskan sesuatu yang bisa kamu screenshot
* commit tiap selesai 1 bagian kecil

Format kerja harian:

* 30 menit: rencana
* 90 menit: implementasi
* 30 menit: testing + commit + catatan besok

---

# Nama file issue awal yang bisa kamu buat

* `feat: add CSV loader`
* `feat: add dataset overview summary`
* `feat: add missing value analyzer`
* `feat: add duplicate row detection`
* `feat: add constant column detection`
* `feat: add high-cardinality detection`
* `feat: add warning engine`
* `feat: generate markdown summary`
* `feat: generate HTML report`
* `test: add analyzer unit tests`
* `docs: improve README with screenshots`

---

# Versi pitch singkat project

Kalau nanti ada yang tanya project kamu apa:

> Dataset Doctor adalah tool open source Python untuk mengecek kesehatan dataset CSV secara cepat. Tool ini membantu mendeteksi missing values, duplikasi, kolom konstan, outlier sederhana, dan menghasilkan report HTML yang mudah dibaca.

