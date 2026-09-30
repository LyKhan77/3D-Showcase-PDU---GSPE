// =====================================================================
// sub_socket_4in1.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// MEREFLEKSIKAN REFERENSI RESMI Schneider CAD (socket.png)
//
// Standar: IEC 60320 Sheet F (C13/C15 Receptacle) & Hybrid 4-in-1 Combo
//
// Arsitektur CSG Bersih (Zero Overlap, Bebas Z-Fighting):
// - Baseplate dengan bukaan jendela terpotong bersih
// - Rongga dasar well gelap berada di kedalaman Y = 3.5 mm
// - Muka soket abu-abu terang berada di kedalaman Y = 0.5 s/d 2.5 mm
// - Slot pin tembus langsung ke dasar well
// =====================================================================

$fn = 32;

// ---- Palet Warna Referensi Schneider CAD ----
COL_BASE_PLATE  = [0.42, 0.44, 0.46];   // Abu-abu casing bank (RAL 7037)
COL_WELL_BG     = [0.16, 0.17, 0.18];   // Dasar rongga gelap steker
COL_SOCKET_FACE = [0.60, 0.62, 0.65];   // Abu-abu terang muka reseptakel soket
COL_PIN_SLOT    = [0.04, 0.04, 0.05];   // Hitam pekat lubang kontak terminal
COL_LATCH_CLEAR = [0.85, 0.90, 0.95, 0.70]; // Polikarbonat bening klip pengunci
COL_LATCH_FRAME = [0.12, 0.12, 0.13];   // Rangka hitam dudukan engsel klip
COL_LED_GREEN   = [0.0,  0.95, 0.35];   // Hijau menyala LED status
COL_TEXT_WHITE  = [0.95, 0.95, 0.95];   // Teks cetak putih nomor outlet
COL_SCREW_BLACK = [0.10, 0.10, 0.10];   // Baut hitam Phillips

// Dimensi Modul Pasangan Soket
PAIR_W = 50.0;
PAIR_H = 34.0;

// =====================================================================
// HELPER: Profil 2D Muka Soket Kanan C13/C15 (Chamfer Kiri, Notch U Kanan)
// =====================================================================
module c13_face_profile_2d() {
    w = 15.0;
    h = 21.0;
    ch = 3.8;
    
    difference() {
        polygon([
            // Sisi kiri chamfer atas & bawah
            [-w/2 + ch,  h/2],
            [-w/2,       h/2 - ch],
            [-w/2,      -h/2 + ch],
            [-w/2 + ch, -h/2],
            // Sisi kanan rounded
            [ w/2 - 1.5, -h/2],
            [ w/2,       -h/2 + 1.5],
            [ w/2,        h/2 - 1.5],
            [ w/2 - 1.5,  h/2]
        ]);
        
        // Notch U sisi kanan (C13)
        translate([w/2, 0])
            resize([6.0, 5.0])
                circle(d = 5.0);
    }
}

// =====================================================================
// HELPER: Profil 2D Muka Soket Kiri Combo 4-in-1 (Notch U Kiri, Chamfer Kanan)
// =====================================================================
module combo_face_profile_2d() {
    w = 18.0;
    h = 22.0;
    ch = 4.0;
    
    difference() {
        polygon([
            // Sisi kiri rounded
            [-w/2 + 1.5,  h/2],
            [-w/2,        h/2 - 1.5],
            [-w/2,       -h/2 + 1.5],
            [-w/2 + 1.5, -h/2],
            // Sisi kanan chamfer atas & bawah
            [ w/2 - ch,  -h/2],
            [ w/2,       -h/2 + ch],
            [ w/2,        h/2 - ch],
            [ w/2 - ch,   h/2]
        ]);
        
        // Notch U sisi kiri (Combo)
        translate([-w/2, 0])
            resize([6.0, 5.2])
                circle(d = 5.2);
    }
}

// =====================================================================
// 1. SOKET KANAN: STANDAR IEC 60320 SHEET F (C13 / C15)
// =====================================================================
module socket_c13_unit() {
    // a. Dasar Rongga Gelap (Well Cavity Background) di Y = 3.5 mm
    color(COL_WELL_BG)
        translate([0, 3.5, 0])
            cube([20.0, 1.0, 25.0], center = true);

    // b. Pulau Muka Soket C13 Abu-Abu Terang (Y = 0.5 sampai 2.5 mm)
    color(COL_SOCKET_FACE) {
        difference() {
            rotate([90, 0, 0])
                translate([0, 0, -2.5])
                    linear_extrude(height = 2.0)
                        c13_face_profile_2d();

            // 3 Slot Pin Horizontal C13 tembus
            translate([-3.0, 1.5, 0])
                cube([4.6, 3.0, 1.8], center = true);
            translate([ 3.0, 1.5, 5.2])
                cube([4.6, 3.0, 1.8], center = true);
            translate([ 3.0, 1.5, -5.2])
                cube([4.6, 3.0, 1.8], center = true);
        }
    }

    // c. Lubang Terminal Hitam Pekat di Dasar Slot
    color(COL_PIN_SLOT) {
        translate([-3.0, 3.0, 0])
            cube([4.6, 1.2, 1.8], center = true);
        translate([ 3.0, 3.0, 5.2])
            cube([4.6, 1.2, 1.8], center = true);
        translate([ 3.0, 3.0, -5.2])
            cube([4.6, 1.2, 1.8], center = true);
    }
}

// =====================================================================
// 2. SOKET KIRI: HYBRID 4-in-1 COMBO (C13 / C15 / C19 / C21)
// =====================================================================
module socket_combo_unit() {
    // a. Dasar Rongga Gelap (Well Cavity Background) di Y = 3.5 mm
    color(COL_WELL_BG)
        translate([0, 3.5, 0])
            cube([22.0, 1.0, 25.0], center = true);

    // b. Pulau Muka Soket Combo Abu-Abu Terang (Y = 0.5 sampai 2.5 mm)
    color(COL_SOCKET_FACE) {
        difference() {
            rotate([90, 0, 0])
                translate([0, 0, -2.5])
                    linear_extrude(height = 2.0)
                        combo_face_profile_2d();

            // T-Slot Earth (kanan tengah)
            translate([ 2.8, 1.5, 0]) {
                cube([5.0, 3.0, 2.0], center = true);
                translate([-1.0, 0, 0])
                    cube([2.0, 3.0, 4.6], center = true);
            }

            // T-Slot Line (kiri atas)
            translate([-3.0, 1.5, 5.2]) {
                cube([4.8, 3.0, 2.0], center = true);
                translate([-0.8, 0, 0])
                    cube([2.0, 3.0, 4.6], center = true);
            }

            // T-Slot Neutral (kiri bawah)
            translate([-3.0, 1.5, -5.2]) {
                cube([4.8, 3.0, 2.0], center = true);
                translate([-0.8, 0, 0])
                    cube([2.0, 3.0, 4.6], center = true);
            }
        }
    }

    // c. Lubang Terminal Hitam Pekat di Dasar Slot
    color(COL_PIN_SLOT) {
        translate([ 2.8, 3.0, 0]) {
            cube([5.0, 1.2, 2.0], center = true);
            translate([-1.0, 0, 0]) cube([2.0, 1.2, 4.6], center = true);
        }
        translate([-3.0, 3.0, 5.2]) {
            cube([4.8, 1.2, 2.0], center = true);
            translate([-0.8, 0, 0]) cube([2.0, 1.2, 4.6], center = true);
        }
        translate([-3.0, 3.0, -5.2]) {
            cube([4.8, 1.2, 2.0], center = true);
            translate([-0.8, 0, 0]) cube([2.0, 1.2, 4.6], center = true);
        }
    }
}

// =====================================================================
// 3. LOCKING LATCH KLIP PENGUNCI TRANSPARAN (DI ATAS SOKET)
// =====================================================================
module socket_locking_latch() {
    // Dudukan engsel hitam
    color(COL_LATCH_FRAME)
        translate([-7.5, -2.5, -2.0])
            cube([15.0, 3.5, 3.5]);

    // Klip polikarbonat transparan menjulur ke depan menutupi bibir atas soket
    color(COL_LATCH_CLEAR)
        translate([-7.0, -2.7, 0.5])
            rotate([-25, 0, 0])
                difference() {
                    cube([14.0, 2.2, 8.5]);
                    for (i = [1:3])
                        translate([-0.5, 1.1, i * 2.2])
                            cube([15.0, 1.4, 0.9]);
                }
}

// =====================================================================
// 4. PASANGAN SOKET LENGKAP (1 BARIS = 2 SOKET + LATCH + LED + BAUT)
// =====================================================================
module sub_socket_pair(num_left = 10, num_right = 9) {
    // Plat dasar abu-abu dengan jendela terpotong rapi (bebas overlap)
    color(COL_BASE_PLATE)
        difference() {
            translate([-PAIR_W/2, -0.2, -PAIR_H/2])
                cube([PAIR_W, 1.2, PAIR_H]);

            // Jendela soket kiri
            translate([-PAIR_W/4 - 0.5, 0.4, -1.0])
                cube([22.2, 2.0, 25.2], center = true);

            // Jendela soket kanan
            translate([PAIR_W/4 + 0.5, 0.4, -1.0])
                cube([20.2, 2.0, 25.2], center = true);
        }

    // Baut Phillips hitam di tengah atas antara 2 klip pengunci
    color(COL_SCREW_BLACK)
        translate([0, -0.6, PAIR_H/2 - 4.0])
            rotate([90, 0, 0]) {
                cylinder(d = 3.5, h = 1.0);
                translate([-1.2, -0.3, 0.8]) cube([2.4, 0.6, 0.5]);
                translate([-0.3, -1.2, 0.8]) cube([0.6, 2.4, 0.5]);
            }

    // ---- SOKET KIRI: Combo 4-in-1 ----
    translate([-PAIR_W/4 - 0.5, 0, -1.0]) {
        socket_combo_unit();
        translate([0, 0, 14.0])
            socket_locking_latch();
    }

    // ---- SOKET KANAN: Standar IEC 60320 Sheet F (C13 / C15) ----
    translate([PAIR_W/4 + 0.5, 0, -1.0]) {
        socket_c13_unit();
        translate([0, 0, 14.0])
            socket_locking_latch();
    }

    // ---- STRIP BAWAH: LED & NOMOR OUTLET ----
    // Bar hitam di bawah soket
    color([0.15, 0.15, 0.16])
        translate([-PAIR_W/2 + 2.0, -0.8, -PAIR_H/2 + 1.0])
            cube([PAIR_W - 4.0, 1.2, 3.8]);

    // LED Hijau Kiri (untuk soket combo)
    color(COL_LED_GREEN)
        translate([-PAIR_W/2 + 4.5, -1.2, -PAIR_H/2 + 2.9])
            cube([3.2, 0.6, 1.8], center = true);

    // LED Hijau Kanan (untuk soket C13)
    color(COL_LED_GREEN)
        translate([PAIR_W/2 - 4.5, -1.2, -PAIR_H/2 + 2.9])
            cube([3.2, 0.6, 1.8], center = true);

    // Nomor Outlet Cetak Putih (diputar 90 derajat counter-clockwise sesuai referensi)
    color(COL_TEXT_WHITE) {
        translate([-PAIR_W/4 - 0.5, -1.2, -PAIR_H/2 + 2.9])
            rotate([90, 0, 0])
                linear_extrude(height = 0.4)
                    rotate([0, 0, 90])
                        text(str(num_left), size = 2.4, font = "Helvetica:style=Bold", halign = "center", valign = "center");
        translate([ PAIR_W/4 + 0.5, -1.2, -PAIR_H/2 + 2.9])
            rotate([90, 0, 0])
                linear_extrude(height = 0.4)
                    rotate([0, 0, 90])
                        text(str(num_right), size = 2.4, font = "Helvetica:style=Bold", halign = "center", valign = "center");
    }
}

// Standalone preview
sub_socket_pair(10, 9);
