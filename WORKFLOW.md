# Data Center 3D CAD Modeling Workflow

Panduan standar untuk pemodelan 3D perangkat keras data center (Server Rack, PDU, WCDU, Server Chassis, Blanking Panel) menggunakan AI Agent (Kimi Code) dan arsitektur multi-MCP.

---

## 1. Arsitektur & Peran MCP

```text
       [ Input: Reference Image + Specs YAML ]
                         │
                         ▼
                Kimi Code / AI Agent
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
  OpenSCAD MCP      FreeCAD MCP       Blender MCP
 (CSG & Drafting) (B-Rep Engineering) (Visual & Digital Twin)
       │                 │                 │
 ├ Rapid blockout  ├ Sheet metal B-Rep├ PBR Materials
 ├ Spatial check   ├ Manifold & pipe  ├ Alpha texture mesh
 └ STL / 3MF       └ STEP / DXF export└ GLB / Photoreal Render
```

| Engine | Peran Utama | Format Output | Kapan Digunakan |
|---|---|---|---|
| **OpenSCAD MCP** | Rapid drafting, CSG math, spatial clearance, interference check | `.scad`, `.stl`, `.3mf` | Tahap eksplorasi awal, verifikasi ukuran dasar, cek tabrakan part. |
| **FreeCAD MCP** | Engineering solid modeling (B-Rep), sheet metal bending, piping | `.FCStd`, `.step`, `.dxf` | **Single source of truth manufaktur** (wajib untuk vendor pabrikasi). |
| **Blender MCP** | Visual rendering, material PBR (powder coat, LED, display), GLB web 3D | `.blend`, `.glb`, `.png` | Visualisasi arsitektural, katalog digital, presentasi, web dashboard. |

---

## 2. Struktur Direktori Project

```text
3D-Model-PDU/
├── WORKFLOW.md                 # Dokumentasi alur kerja (file ini)
├── .mcp.json                   # Konfigurasi MCP project
├── specs/                      # File spesifikasi parameter (YAML)
│   ├── blanking-panel-1u.yaml
│   ├── pdu-vertical-zero-u.yaml
│   ├── rack-42u.yaml
│   └── wcdu-4u.yaml
├── references/                 # Dokumen referensi & gambar
│   ├── datasheets/             # PDF atau dokumen spec pabrikan
│   └── images/                 # Foto produk nyata, diagram dimensi, layout port
├── libraries/                  # Standar konstanta (EIA-310, soket C13/C19, dll)
│   ├── eia_310.scad
│   └── eia_310.py
├── cad/
│   ├── openscad/               # Script source OpenSCAD (.scad)
│   └── freecad/                # Script otomasi Python FreeCAD
├── exports/
│   ├── step/                   # Model solid B-Rep untuk manufaktur
│   ├── stl/                    # Mesh solid
│   ├── dxf/                    # Gambar pola potong plat (flat pattern)
│   └── glb/                    # Model 3D web / visualisasi
└── previews/                   # Render gambar (PNG) untuk inspeksi cepat
```

---

## 3. Inisialisasi Project (Spec + Image Reference)

Bagi pemula, **selalu gunakan inisialisasi ganda**:

1. **Image Reference** (`references/images/`):
   - Memberikan konteks visual: letak tombol saklar, orientasi outlet PDU, engsel rack, layar status WCDU, dan detail estetika.
2. **Spec File YAML** (`specs/<nama-part>.yaml`):
   - Memberikan angka matematis presisi tanpa estimasi/halusinasi.

### Contoh Format Spec YAML (`specs/sample-pdu.yaml`)

```yaml
asset_id: pdu-01-vertical-basic
category: pdu
form_factor: 0U_vertical
units: mm

dimensions:
  length: 1200.0
  width: 56.0
  depth: 44.0
  sheet_thickness: 1.5

electrical_layout:
  total_outlets: 16
  outlet_type: IEC_C13
  bank_split: [8, 8]
  input_plug: IEC_60309_16A
  breaker_position: top

mounting:
  type: button_mount_brackets
  pitch_distance: 1150.0

references:
  image: references/images/pdu_sample.jpg
  standard: IEC_60320
```

---

## 4. Pipeline 5 Tahap Pemodelan

### Tahap 1: Ingestion & Spec Lock
- Letakkan gambar di `references/images/` dan datasheet di `references/datasheets/`.
- Agent membaca spec dan mengekstrak dimensi utama ke dalam `specs/<asset>.yaml`.
- Kunci dimensi kritis (panjang, lebar, tinggi, pitch lubang baut).

### Tahap 2: Rapid CSG Draft (OpenSCAD)
- Agent meng-generate file `.scad` di `cad/openscad/`.
- Import library standar `use <../../libraries/eia_310.scad>`.
- Jalankan tool `measure` dan `check` pada OpenSCAD MCP untuk memverifikasi bounding box dan volume.
- Render thumbnail cepat ke `previews/`.

### Tahap 3: Engineering B-Rep Modeling (FreeCAD)
- Model dikonversi/dibuat ulang dalam bentuk B-Rep solid menggunakan FreeCAD Python script di `cad/freecad/`.
- Tambahkan detail sheet metal (flange, bend radius 1.5–2.0 mm, countersink hole).
- Ekspor geometri solid ke `exports/step/<asset>.step` untuk kebutuhan engineering & vendor manufaktur.

### Tahap 4: Material, Detail & Visual (Blender)
- Import model STL / STEP-mesh ke Blender via Blender MCP.
- Terapkan material PBR:
  - *Black powder-coated steel* (Roughness ~0.6, Metallic 0.0).
  - *Brushed aluminum* untuk rail atau panel aksen.
  - *LED status indicators* (Emission shader: Green/Amber).
- Terapkan **Alpha Perforation Mask** untuk pintu sarang lebah / perforated door.
- Ekspor ke `exports/glb/<asset>.glb` untuk web viewer.

### Tahap 5: Verification & Delivery Manifest
- Agent memastikan:
  - Toleransi & clearance telah divalidasi.
  - File STEP dan GLB tersedia.
  - Manifest tercatat di `manifests/<asset>.json`.

### Tahap 6: Web Delivery (`showcase/`)
- GLB di `exports/` adalah **master** dan tidak diubah. `showcase/` memakai salinan Draco yang jauh lebih kecil.
- Jalankan dari folder `scripts/`:

```bash
npm install            # sekali saja
npm run build:web      # exports/ -> showcase/*.glb (Draco, posisi 16-bit, normal 12-bit)
npm run verify:web     # gagal jika jumlah segitiga, nama mesh/material, atau bbox menyimpang dari master
npm run posters        # poster JPEG di showcase/assets/posters/
npm run test:web       # smoke test viewer: ganti Assembled/Exploded, stage, tip hotspot (desktop + ponsel)
npm run audit:web      # cek link, meta, aksesibilitas (axe), overflow, ukuran unduhan
BASE_URL=https://showcase3dpdu-gspe.vercel.app/ npm run test:web   # jalankan tes/audit terhadap situs yang sudah live
```

- Situs tidak memuat apa pun dari origin lain: font Plex, model-viewer, dan decoder Draco disalin ke `showcase/assets/vendor/` (`npm run vendor`, versi dan lisensi ada di `vendor/README.md`). `showcase/vercel.json` memberlakukan Content-Security-Policy yang memblokir sumber luar. Tambah CDN baru = ubah CSP di file itu.
- Halaman memuat model hanya setelah pengunjung menekan **Load interactive 3D model** (`reveal="manual"`). Model exploded baru diunduh saat diminta.
- Jalankan ulang ketiga langkah setiap kali GLB master di `exports/` berubah.

---

## 5. Aturan Baku Data Center (Golden Rules)

### A. Standar EIA-310-D (19-Inch Rack)
* **1 Rack Unit (1U)** = `44.45 mm` (1.75 inci).
* Pola 3 lubang vertikal per 1U memiliki jarak **tidak seragam**:
  - `6.35 mm` dari batas bawah U ke lubang 1.
  - `15.875 mm` dari lubang 1 ke lubang 2 (tengah).
  - `15.875 mm` dari lubang 2 ke lubang 3.
  - `6.35 mm` dari lubang 3 ke batas atas U.
* Jarak horizontal antar lubang baut rail: **`465.1 mm`**.
* Lebar panel depan standar: **`482.6 mm`**.
* Selalu gunakan konstanta dari `libraries/eia_310.scad` / `libraries/eia_310.py`.

### B. Perforated Door Trap (Pintu Sarang Lebah)
* Pintu rack memiliki 63%–80% area terbuka dengan ribuan lubang heksagonal kecil.
* **JANGAN** lakukan ribuan boolean cutouts di CAD kernel (akan crash/freeze).
* **Solusi**:
  - Di CAD: Modelkan pelat pintu solid dengan catatan spesifikasi perforasi manufaktur pada 2D drawing.
  - Di Blender / GLB: Gunakan tekstur heksagonal transparan (*alpha channel mask*).

### C. Komponen WCDU (Liquid Cooling Distribution Unit)
* Pisahkan komponen WCDU ke dalam 3 sub-rakitan:
  1. **Chassis & Enclosure**: Rangka sheet metal 1U–4U atau standalone cabinet.
  2. **Hydraulic Manifold**: Pipa supply/return stainless steel/tembaga dengan port OCP UQD (Universal Quick Disconnect).
  3. **Control & Pump Module**: Blok pompa redundant, heat exchanger, sensor flow/temp, dan front display LCD.

---

## 6. Panduan Menjalankan Perintah via Kimi Code

1. **Jalankan OpenSCAD MCP**: Berjalan otomatis via background CLI.
2. **Jalankan FreeCAD MCP**: Buka aplikasi FreeCAD → Workbench **MCP Addon** → Klik **Start RPC Server**.
3. **Jalankan Blender MCP**: Buka aplikasi Blender → Tekan `N` → Tab **MCP for Blender** → Klik **Start MCP Server**.
