// =====================================================================
// sub_nmc_controller.scad
// GSPE NetShelter Rack PDU Advanced 100A
// Network Management Card 3 (NMC3) Cassette Controller
// REBRANDING: GSPE (Primary: #003674 Navy, Secondary: #FAFFD8 Cream)
//
// MEREFLEKSIKAN REFERENSI Schneider CAD ASLI DENGAN PRESISI TINGGI:
// - Screenshot 2026-09-28 at 15.28.49.png (USB Micro-B Console, USB-A Host, RJ45)
// - Screenshot 2026-09-28 at 15.29.14.png (Lensa Dome LED 3D, Tombol Menu/Chevron/Check)
// =====================================================================

$fn = 32;

// Dimensi Utama Modul Cassette
NMC_W = 54.0;
NMC_H = 150.0;
NMC_D = 45.0;           // kedalaman kaset masuk ke dalam chassis

// Palet Warna Resmi GSPE & Komponen CAD
COL_GSPE_PRI    = [0.000, 0.212, 0.455]; // #003674 Deep Corporate Navy
COL_GSPE_SEC    = [0.980, 1.000, 0.847]; // #FAFFD8 Soft Light Cream
COL_NMC_BODY    = [0.160, 0.165, 0.175]; // Matte dark chassis kaset
COL_BEZEL       = [0.110, 0.115, 0.120]; // Bezel luar
COL_SCREEN_BG   = [0.780, 0.860, 0.940]; // Biru-abu LCD grafis portrait
COL_TEXT_WHT    = [0.950, 0.950, 0.950]; // Putih cetak teks
COL_PORT_METAL  = [0.550, 0.570, 0.600]; // Logam shielding port
COL_PORT_DARK   = [0.080, 0.080, 0.090]; // Hitam rongga dalam port
COL_GOLD_PIN    = [0.880, 0.720, 0.240]; // Pin kontak emas 8P8C
COL_BTN_GREY    = [0.720, 0.740, 0.760]; // Abu-abu terang tombol navigasi

// Helper Profil 2D Cassette (dengan chamfer di kedua sudut atas)
module nmc_body_xz() {
    ch = 4.5;
    polygon([
        [-NMC_W/2 + ch,  NMC_H/2],
        [ NMC_W/2 - ch,  NMC_H/2],
        [ NMC_W/2,       NMC_H/2 - ch],
        [ NMC_W/2,      -NMC_H/2],
        [-NMC_W/2,      -NMC_H/2],
        [-NMC_W/2,       NMC_H/2 - ch]
    ]);
}

// Helper: Ikon Kunci Pas Vektor (Console)
module wrench_icon_2d() {
    rotate([0, 0, -45]) {
        difference() {
            union() {
                translate([0, -1.2]) square([0.7, 3.2], center = true);
                translate([0, 0.8]) circle(d = 2.4);
            }
            translate([0, 1.1]) square([1.0, 1.4], center = true);
        }
    }
}

// Helper: Ikon USB Trident Vektor
module usb_trident_icon_2d() {
    // Batang tengah
    translate([0, -0.4]) square([0.45, 3.5], center = true);
    // Panah atas
    translate([0, 1.6]) polygon([[-0.8, 0], [0.8, 0], [0, 1.1]]);
    // Cabang kiri + kotak
    translate([-1.0, 0.1]) square([0.35, 1.6], center = true);
    translate([-0.5, -0.6]) square([1.2, 0.35], center = true);
    translate([-1.0, 1.1]) square([0.8, 0.8], center = true);
    // Cabang kanan + lingkaran
    translate([1.0, 0.1]) square([0.35, 1.6], center = true);
    translate([0.5, -0.6]) square([1.2, 0.35], center = true);
    translate([1.0, 1.1]) circle(d = 0.85);
}

// =====================================================================
// 1. DETAIL SOKET RJ-45 LAN (Sensor, Link, GbE) BERLUBANG NYATA
// =====================================================================
module rj45_socket_detailed(has_leds = false, led_left_col = [0.95, 0.85, 0.1], led_right_col = [0.1, 0.95, 0.2]) {
    w = 13.2;        // lebar kerah logam luar
    h = 11.4;        // tinggi kerah logam luar
    hole_w = 11.2;   // lebar bukaan rongga
    hole_h = 8.6;    // tinggi bukaan rongga
    depth = 8.5;     // kedalaman rongga masuk ke dalam (+Y)
    lip_fwd = 1.0;   // tonjolan bibir logam ke depan (-Y)

    // a. Kerah Logam Luar dengan Bevel Masuk
    color(COL_PORT_METAL) {
        difference() {
            translate([-w/2, -lip_fwd, -h/2])
                cube([w, lip_fwd + 0.1, h]);
            // Bukaan corong masuk
            translate([-hole_w/2, -lip_fwd - 0.5, -hole_h/2 - 0.2])
                cube([hole_w, lip_fwd + 1.0, hole_h]);
        }
    }

    // b. Dinding Dalam Plastik Hitam
    color([0.15, 0.15, 0.16]) {
        difference() {
            translate([-hole_w/2, 0, -hole_h/2 - 0.2])
                cube([hole_w, depth, hole_h]);
            // Rongga dalam tembus
            translate([-hole_w/2 + 0.7, -0.1, -hole_h/2 - 0.2 + 0.7])
                cube([hole_w - 1.4, depth + 0.2, hole_h - 1.4]);
        }
    }

    // c. Dasar Rongga Gelap Pekat
    color(COL_PORT_DARK)
        translate([-hole_w/2 + 0.7, depth - 0.4, -hole_h/2 - 0.2 + 0.7])
            cube([hole_w - 1.4, 0.5, hole_h - 1.4]);

    // d. 8 Pin Kontak Kawat Emas Miring Masuk ke Dalam (8P8C)
    color(COL_GOLD_PIN) {
        for (p = [0 : 7]) {
            translate([-hole_w/2 + 1.8 + p * 1.08, depth/2, hole_h/2 - 1.2])
                rotate([12, 0, 0])
                    cube([0.45, depth - 1.2, 0.4], center = true);
        }
    }

    // e. Latch Notch (Ceruk Pengait Plastik di Atas Rongga)
    color(COL_PORT_DARK)
        translate([0, depth/2, hole_h/2 + 0.3])
            cube([4.8, depth + 0.2, 1.2], center = true);

    // f. LED Indikator di Sudut Atas
    if (has_leds) {
        color(led_left_col)
            translate([-w/2 + 1.8, -lip_fwd - 0.1, h/2 - 1.1])
                cube([1.8, 0.4, 1.1], center = true);
        color(led_right_col)
            translate([ w/2 - 1.8, -lip_fwd - 0.1, h/2 - 1.1])
                cube([1.8, 0.4, 1.1], center = true);
    }
}

// =====================================================================
// 2. DETAIL PORT USB MICRO-B CONSOLE (PORT 11)
// Sesuai Screenshot 2026-09-28 at 15.28.49.png
// =====================================================================
module usb_micro_b_console() {
    w_pocket = 13.0;
    h_pocket = 9.0;
    depth = 7.0;

    // Bingkai & Rongga Persegi Luar
    color(COL_NMC_BODY)
        translate([-w_pocket/2, -0.6, -h_pocket/2])
            cube([w_pocket, 0.7, h_pocket]);

    // Plat Latar Belakang Aksen GSPE Primary (#003674)
    color(COL_GSPE_PRI)
        translate([-w_pocket/2 + 0.8, -0.2, -h_pocket/2 + 0.8])
            cube([w_pocket - 1.6, 0.4, h_pocket - 1.6]);

    // Selubung Logam Micro-B (Bentuk Trapesium Khas Micro-USB)
    color(COL_PORT_METAL) {
        difference() {
            // Badan luar kerah trapesium
            translate([0, 1.0, 0])
                rotate([90, 0, 0])
                    linear_extrude(height = 3.0)
                        polygon([
                            [-3.8,  1.6],
                            [ 3.8,  1.6],
                            [ 3.8, -0.6],
                            [ 2.8, -1.6], // chamfer sudut bawah
                            [-2.8, -1.6], // chamfer sudut bawah
                            [-3.8, -0.6]
                        ]);
            // Rongga dalam colokan
            translate([0, 2.0, 0])
                rotate([90, 0, 0])
                    linear_extrude(height = 5.0)
                        polygon([
                            [-3.2,  1.1],
                            [ 3.2,  1.1],
                            [ 3.2, -0.4],
                            [ 2.3, -1.1],
                            [-2.3, -1.1],
                            [-3.2, -0.4]
                        ]);
        }
    }

    // Lidah Plastik Hitam Pin Kontak di Dalam Micro-B
    color(COL_PORT_DARK)
        translate([0, 2.5, 0.1])
            cube([5.0, 4.0, 0.6], center = true);

    // Pin Emas Halus di Atas Lidah
    color(COL_GOLD_PIN)
        for (p = [-2 : 2])
            translate([p * 0.9, 2.5, 0.45])
                cube([0.3, 3.5, 0.2], center = true);
}

// =====================================================================
// 3. DETAIL PORT USB-A HOST (PORT 10)
// Sesuai Screenshot 2026-09-28 at 15.28.49.png
// =====================================================================
module usb_a_host_port() {
    w_pocket = 16.0;
    h_pocket = 10.0;
    depth = 9.0;

    // Bezel Frame Hitam Masuk ke Dalam (Chamfered Pocket)
    color(COL_BEZEL)
        difference() {
            translate([-w_pocket/2, -0.6, -h_pocket/2])
                cube([w_pocket, 1.2, h_pocket]);
            translate([-13.0/2, -1.0, -7.0/2])
                cube([13.0, 2.0, 7.0]);
        }

    // Selubung Logam Persegi Panjang USB Type-A Receptacle
    color(COL_PORT_METAL) {
        difference() {
            translate([-12.5/2, 0, -6.5/2])
                cube([12.5, depth, 6.5]);
            // Rongga dalam colokan
            translate([-11.3/2, -0.1, -5.3/2])
                cube([11.3, depth + 0.2, 5.3]);
        }
        // Lidah Klip Pegas Retensi di Bagian Atas Logam
        translate([0, 2.0, 6.5/2])
            cube([6.0, 2.5, 0.5], center = true);
    }

    // Dasar Rongga Gelap
    color(COL_PORT_DARK)
        translate([0, depth - 0.5, 0])
            cube([11.3, 1.0, 5.3], center = true);

    // Lidah Isolator Putih Pin USB di Bagian Bawah Rongga
    color(COL_GSPE_SEC)
        translate([0, depth/2 + 0.5, -5.3/2 + 1.2])
            cube([10.5, depth - 1.0, 1.4], center = true);

    // 4 Pin Kontak Emas di Permukaan Lidah
    color(COL_GOLD_PIN) {
        for (i = [-3, -1, 1, 3])
            translate([i * 1.2, depth/2 + 0.5, -5.3/2 + 2.0])
                cube([0.6, depth - 2.0, 0.3], center = true);
    }
}

// =====================================================================
// 4. DETAIL TOMBOL NAVIGASI BULAT (MENU, DOWN CHEVRON, CHECKMARK)
// Sesuai Screenshot 2026-09-28 at 15.29.14.png
// =====================================================================
module nav_button_base(d = 9.2, h = 1.4) {
    // Tombol bulat dengan tepi atas membulat halus
    color(COL_BTN_GREY)
        rotate([90, 0, 0])
            cylinder(d1 = d, d2 = d - 0.8, h = h);
}

// Tombol 1: Menu Icon (4 Baris Horizontal)
module nav_button_menu() {
    nav_button_base();
    color([0.28, 0.30, 0.32])
        for (i = [-3, -1, 1, 3])
            translate([0, -1.45, i * 0.9])
                cube([5.0, 0.3, 0.55], center = true);
}

// Tombol 2: Down Chevron (Tebal Huruf V)
module nav_button_chevron() {
    nav_button_base();
    color([0.28, 0.30, 0.32])
        translate([0, -1.45, 0.2])
            rotate([90, 0, 0])
                linear_extrude(height = 0.3)
                    polygon([
                        [-3.0,  1.6],
                        [ 0.0, -1.4],
                        [ 3.0,  1.6],
                        [ 2.2,  2.2],
                        [ 0.0,  0.0],
                        [-2.2,  2.2]
                    ]);
}

// Tombol 3: Checkmark (Centang Tebal ✓)
module nav_button_check() {
    nav_button_base();
    color([0.28, 0.30, 0.32])
        translate([0, -1.45, 0.2])
            rotate([90, 0, 0])
                linear_extrude(height = 0.3)
                    polygon([
                        [-2.8, -0.4],
                        [-1.0, -2.2],
                        [ 3.0,  1.8],
                        [ 2.2,  2.4],
                        [-1.0, -0.8],
                        [-2.0,  0.2]
                    ]);
}

// =====================================================================
// MODUL UTAMA NMC CONTROLLER LENGKAP REBRANDING "GSPE"
// =====================================================================
module sub_nmc_controller() {
    // 1. Casing Utama Cassette dengan Lubang-Lubang Port Tembus
    color(COL_NMC_BODY) {
        difference() {
            // Tubuh solid kaset
            rotate([90, 0, 0])
                linear_extrude(height = NMC_D)
                    nmc_body_xz();

            // Lubang Tembus Port USB Console & Host
            translate([-NMC_W/2 + 15.0, -NMC_D + 4.0, NMC_H/2 - 84.0])
                cube([13.5, 9.0, 9.5], center = true);
            translate([NMC_W/2 - 15.0, -NMC_D + 4.0, NMC_H/2 - 84.0])
                cube([16.5, 9.0, 10.5], center = true);

            // Lubang Tembus 2x Sensor RJ45
            translate([-13.0, -NMC_D + 4.0, NMC_H/2 - 97.0])
                cube([13.4, 9.0, 11.6], center = true);
            translate([ 13.0, -NMC_D + 4.0, NMC_H/2 - 97.0])
                cube([13.4, 9.0, 11.6], center = true);

            // Lubang Tembus 2x Link RJ45
            translate([-13.0, -NMC_D + 4.0, NMC_H/2 - 111.0])
                cube([13.4, 9.0, 11.6], center = true);
            translate([ 13.0, -NMC_D + 4.0, NMC_H/2 - 111.0])
                cube([13.4, 9.0, 11.6], center = true);

            // Lubang Tembus 1x GbE Network RJ45
            translate([7.0, -NMC_D + 4.0, NMC_H/2 - 128.0])
                cube([13.4, 9.0, 11.6], center = true);
        }
    }

    // 2. Bezel Tepi Luar Kaset
    color(COL_BEZEL)
        translate([0, -NMC_D, 0])
            rotate([90, 0, 0])
                difference() {
                    linear_extrude(height = 0.6) nmc_body_xz();
                    translate([-NMC_W/2 + 1.0, -NMC_H/2 + 1.0, -0.5])
                        cube([NMC_W - 2.0, NMC_H - 2.0, 2]);
                }

    // -----------------------------------------------------------------
    // BAGIAN ATAS: REBRANDING "GSPE" & STATUS LEDS 3D
    // -----------------------------------------------------------------
    // Logo "GSPE" Tebal & Modern
    color(COL_GSPE_SEC)
        translate([0, -NMC_D - 0.2, NMC_H/2 - 11.5])
            rotate([90, 0, 0])
                linear_extrude(height = 0.5)
                    text("GSPE", size = 7.0, font = "Helvetica:style=Bold", halign = "center", valign = "center");

    // Lensa Dome LED Status Daya 3D (Kubah Setengah Bola Hijau Menyala)
    // Sesuai Screenshot 2026-09-28 at 15.29.14.png di bawah logo
    color([0.15, 0.95, 0.30])
        translate([0, -NMC_D - 0.2, NMC_H/2 - 17.0])
            rotate([90, 0, 0])
                sphere(d = 3.6);

    // Dudukan Cincin Hitam Lensa Dome
    color([0.10, 0.10, 0.11])
        translate([0, -NMC_D - 0.1, NMC_H/2 - 17.0])
            rotate([90, 0, 0])
                cylinder(d = 4.6, h = 0.4, center = true);

    // 3 Status LED Vertikal (Okay, Warning, Overload)
    translate([-1.0, -NMC_D - 0.2, NMC_H/2 - 22.5]) {
        // Okay LED (hijau terang)
        color([0.15, 0.95, 0.25]) translate([0, 0, 2.8]) rotate([90, 0, 0]) sphere(d = 1.8);
        color(COL_TEXT_WHT) translate([-2.5, 0, 2.8]) rotate([90, 0, 0]) linear_extrude(0.3) text("Okay", size = 1.5, halign = "right", valign = "center");

        // Warning LED (kuning-amber)
        color([0.98, 0.82, 0.10]) translate([0, 0, 0]) rotate([90, 0, 0]) sphere(d = 1.8);
        color(COL_TEXT_WHT) translate([-2.5, 0, 0]) rotate([90, 0, 0]) linear_extrude(0.3) text("Warning", size = 1.5, halign = "right", valign = "center");

        // Overload LED (merah cerah)
        color([0.95, 0.15, 0.12]) translate([0, 0, -2.8]) rotate([90, 0, 0]) sphere(d = 1.8);
        color(COL_TEXT_WHT) translate([-2.5, 0, -2.8]) rotate([90, 0, 0]) linear_extrude(0.3) text("Overload", size = 1.5, halign = "right", valign = "center");
    }

    // -----------------------------------------------------------------
    // BAGIAN TENGAH-ATAS: LAYAR LCD GRAFIS PORTRAIT GSPE
    // -----------------------------------------------------------------
    // Frame Layar Hitam
    color([0.10, 0.10, 0.11])
        translate([-NMC_W/2 + 6.0, -NMC_D - 0.1, NMC_H/2 - 76.0])
            cube([31.0, 0.6, 48.0]);

    // Layar LCD Portrait Aktif (Background Biru Lembut)
    color(COL_SCREEN_BG)
        translate([-NMC_W/2 + 7.0, -NMC_D - 0.7, NMC_H/2 - 75.0])
            cube([29.0, 0.3, 46.0]);

    // Header Bar GSPE Navy (#003674) di Atas Layar
    color(COL_GSPE_PRI)
        translate([-NMC_W/2 + 7.0, -NMC_D - 0.9, NMC_H/2 - 36.0])
            cube([29.0, 0.25, 6.5]);

    // Teks Header Warna Cream (#FAFFD8) "Phase Info"
    color(COL_GSPE_SEC)
        translate([-NMC_W/2 + 21.5, -NMC_D - 1.15, NMC_H/2 - 33.0])
            rotate([90, 0, 0])
                linear_extrude(0.25)
                    text("Phase Info", size = 2.4, font = "Helvetica:style=Bold", halign = "center", valign = "center");

    // Teks Menu di Layar (Warna Corporate Navy Gelap)
    color(COL_GSPE_PRI) {
        translate([-NMC_W/2 + 21.5, -NMC_D - 0.9, NMC_H/2 - 42.0]) rotate([90,0,0]) linear_extrude(0.2) text("Bank Info", size = 2.2, halign = "center", valign = "center");
        translate([-NMC_W/2 + 21.5, -NMC_D - 0.9, NMC_H/2 - 48.0]) rotate([90,0,0]) linear_extrude(0.2) text("Outlet Current", size = 2.2, halign = "center", valign = "center");
        translate([-NMC_W/2 + 21.5, -NMC_D - 0.9, NMC_H/2 - 54.0]) rotate([90,0,0]) linear_extrude(0.2) text("Alarm Status", size = 2.2, halign = "center", valign = "center");
        translate([-NMC_W/2 + 21.5, -NMC_D - 0.9, NMC_H/2 - 60.0]) rotate([90,0,0]) linear_extrude(0.2) text("Network", size = 2.2, halign = "center", valign = "center");
        translate([-NMC_W/2 + 21.5, -NMC_D - 0.9, NMC_H/2 - 66.0]) rotate([90,0,0]) linear_extrude(0.2) text("Software Info", size = 2.2, halign = "center", valign = "center");
    }

    // -----------------------------------------------------------------
    // KANAN LAYAR: RESET PINHOLE & 3 TOMBOL BESAR PERSIS REFERENSI
    // -----------------------------------------------------------------
    // Reset Pinhole (R)
    color([0.15, 0.75, 0.35])
        translate([NMC_W/2 - 7.0, -NMC_D - 0.2, NMC_H/2 - 33.0])
            rotate([90, 0, 0]) {
                cylinder(d = 2.4, h = 0.5);
                translate([2.6, 0, 0]) linear_extrude(0.2) text("R", size = 1.8, font = "Helvetica:style=Bold", valign = "center");
            }

    // Tombol 1: Menu Icon (4 Baris)
    translate([NMC_W/2 - 7.0, -NMC_D, NMC_H/2 - 43.5])
        nav_button_menu();

    // Tombol 2: Down Chevron (Tebal Huruf V)
    translate([NMC_W/2 - 7.0, -NMC_D, NMC_H/2 - 54.0])
        nav_button_chevron();

    // Tombol 3: Checkmark (Centang Tebal ✓)
    translate([NMC_W/2 - 7.0, -NMC_D, NMC_H/2 - 64.5])
        nav_button_check();

    // Ikon USB Trident Vektor di bawah tombol centang mengarah ke port host
    color([0.65, 0.67, 0.70])
        translate([NMC_W/2 - 14.0, -NMC_D - 0.2, NMC_H/2 - 75.5])
            rotate([90, 0, 0])
                linear_extrude(0.2)
                    usb_trident_icon_2d();

    // -----------------------------------------------------------------
    // BAGIAN BAWAH: PORT USB & RJ-45 LENGKAP SESUAI SCREENSHOT
    // -----------------------------------------------------------------
    // Row 1: USB Ports
    // Port 11: USB Micro-B Console (kiri)
    translate([-NMC_W/2 + 15.0, -NMC_D, NMC_H/2 - 84.0])
        usb_micro_b_console();

    // Ikon Kunci Pas Vektor & Teks Label "Console"
    color(COL_TEXT_WHT) {
        translate([-NMC_W/2 + 4.5, -NMC_D - 0.2, NMC_H/2 - 80.5])
            rotate([90, 0, 0])
                linear_extrude(0.2)
                    wrench_icon_2d();
        translate([-NMC_W/2 + 4.5, -NMC_D - 0.2, NMC_H/2 - 84.5])
            rotate([90, 0, 0])
                linear_extrude(0.2) text("Console", size = 1.3, font = "Helvetica:style=Bold", halign = "center");
    }

    // Port 10: USB-A Host Port (kanan)
    translate([NMC_W/2 - 15.0, -NMC_D, NMC_H/2 - 84.0])
        usb_a_host_port();

    // Row 2 & 3: 2x2 Grid Port RJ-45 (Sensor & Link)
    // Sensor 2 (kiri atas) & Sensor 1 (kanan atas) - Tanpa LED
    translate([-13.0, -NMC_D, NMC_H/2 - 97.0]) rj45_socket_detailed(has_leds = false);
    translate([ 13.0, -NMC_D, NMC_H/2 - 97.0]) rj45_socket_detailed(has_leds = false);

    // Label "Sensor" dan Garis Pembatas "—"
    color(COL_TEXT_WHT) {
        translate([0, -NMC_D - 0.2, NMC_H/2 - 97.0])
            rotate([90, 0, 0])
                linear_extrude(0.2) text("Sensor", size = 1.6, font = "Helvetica:style=Bold", halign = "center", valign = "center");
        translate([0, -NMC_D - 0.2, NMC_H/2 - 104.0])
            rotate([90, 0, 0])
                linear_extrude(0.2) text("—", size = 2.0, font = "Helvetica:style=Bold", halign = "center", valign = "center");
    }

    // Link 2 (kiri bawah) & Link 1 (kanan bawah) - Dengan LED Kuning/Hijau
    translate([-13.0, -NMC_D, NMC_H/2 - 111.0]) rj45_socket_detailed(has_leds = true);
    translate([ 13.0, -NMC_D, NMC_H/2 - 111.0]) rj45_socket_detailed(has_leds = true);

    color(COL_TEXT_WHT)
        translate([0, -NMC_D - 0.2, NMC_H/2 - 111.0])
            rotate([90, 0, 0])
                linear_extrude(0.2) text("Link", size = 1.6, font = "Helvetica:style=Bold", halign = "center", valign = "center");

    // Nomor Port "2" (kiri) dan "1" (kanan)
    color(COL_TEXT_WHT) {
        translate([-NMC_W/2 + 4.5, -NMC_D - 0.2, NMC_H/2 - 120.0])
            rotate([90, 0, 0]) linear_extrude(0.2) text("2", size = 1.8, font = "Helvetica:style=Bold", halign = "center");
        translate([ NMC_W/2 - 4.5, -NMC_D - 0.2, NMC_H/2 - 120.0])
            rotate([90, 0, 0]) linear_extrude(0.2) text("1", size = 1.8, font = "Helvetica:style=Bold", halign = "center");
    }

    // Row 4: Port 14 Gigabit Ethernet RJ-45 (Tengah-Kanan)
    translate([7.0, -NMC_D, NMC_H/2 - 128.0])
        rj45_socket_detailed(has_leds = true, led_left_col = [0.95, 0.95, 0.95], led_right_col = [0.95, 0.95, 0.95]);

    // Ikon Jaringan Tree (3 Node) & Indikator Kecepatan (10 / 100 / 1000)
    translate([-12.0, -NMC_D - 0.2, NMC_H/2 - 125.0]) {
        // Ikon Tree Jaringan Putih
        color(COL_TEXT_WHT)
            rotate([90, 0, 0]) {
                translate([0, 4.0, 0]) cube([2.0, 2.0, 0.3], center = true);
                translate([-2.5, 0.5, 0]) cube([2.0, 2.0, 0.3], center = true);
                translate([ 2.5, 0.5, 0]) cube([2.0, 2.0, 0.3], center = true);
                // Garis koneksi
                translate([0, 2.5, 0]) cube([0.5, 2.0, 0.3], center = true);
                translate([0, 1.5, 0]) cube([5.0, 0.5, 0.3], center = true);
            }
        // Angka Kecepatan Bertingkat
        translate([0, 0, -4.5])
            rotate([90, 0, 0]) {
                color([0.2, 0.9, 0.3])  text("10", size = 1.4, font = "Helvetica:style=Bold", halign = "center");
                color([0.98, 0.65, 0.1]) translate([0, -2.2, 0]) text("100", size = 1.4, font = "Helvetica:style=Bold", halign = "center");
                color([0.2, 0.9, 0.3])  translate([0, -4.4, 0]) text("1000", size = 1.4, font = "Helvetica:style=Bold", halign = "center");
            }
    }

    // Logo Rebranding "GSPE" di Kanan Bawah
    color(COL_GSPE_SEC)
        translate([NMC_W/2 - 3.5, -NMC_D - 0.2, -NMC_H/2 + 7.5])
            rotate([90, 0, 0])
                linear_extrude(0.35)
                    text("GSPE", size = 3.8, font = "Helvetica:style=Bold", halign = "right");

    // -----------------------------------------------------------------
    // PULL TAB / EJECTION LEVER KASTET (BAWAH)
    // -----------------------------------------------------------------
    color([0.10, 0.10, 0.11])
        translate([-8.0, -NMC_D + 1.0, -NMC_H/2 - 4.0])
            cube([16.0, 3.5, 5.0]);
}

// Standalone preview
sub_nmc_controller();
