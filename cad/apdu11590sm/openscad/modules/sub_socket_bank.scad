// =====================================================================
// sub_socket_bank.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// MEREFLEKSIKAN REFERENSI Schneider CAD ASLI (socket.png)
//
// Struktur 1 Modul Bank (Tinggi = 68.0 mm):
// - Sisi KIRI: 2 baris pasangan soket (ROW_PITCH = 34.0 mm, total 4 soket per modul)
//   - Tiap baris: 1x Combo 4-in-1 (kiri) + 1x C13/C15 (kanan) + locking latches + LEDs
// - Sisi KANAN: 1x Modul Circuit Breaker 20A (BRK_H = 68.0 mm)
//   - Pasangan tinggi presisi 1:1 (2 x 34.0 mm = 68.0 mm)
// =====================================================================

use <sub_socket_4in1.scad>
use <sub_breaker_box.scad>

$fn = 24;

ROW_PITCH = 34.0;       // Jarak vertikal antar baris pasangan soket
BANK_ROWS = 2;          // 2 baris x 2 soket = 4 soket per blok breaker
BANK_H = BANK_ROWS * ROW_PITCH; // 68.0 mm

module sub_socket_bank(bank_num = 3, phase_str = "L3-N", plate_color = [0.45, 0.46, 0.48], text_color = [0.95, 0.95, 0.95]) {
    // Nomor awal outlet untuk bank ini
    // Bank 3: baris 1 = (8, 7), baris 2 = (10, 9)
    base_outlet = (bank_num - 1) * 4;

    // ---- SISI KIRI: 2 Baris Pasangan Soket ----
    translate([-13.0, 0, 0]) {
        // Baris atas (misal 8 & 7)
        translate([0, 0, ROW_PITCH / 2])
            sub_socket_pair(base_outlet + 2, base_outlet + 1);

        // Baris bawah (misal 10 & 9)
        translate([0, 0, -ROW_PITCH / 2])
            sub_socket_pair(base_outlet + 4, base_outlet + 3);
    }

    // ---- SISI KANAN: Plat Breaker Bank ----
    translate([26.0, 0, 0])
        sub_breaker_plate(bank_num, phase_str, plate_color, text_color);
}

// Standalone preview: Bank 3 (GSPE Navy #003674) dan Bank 4 (GSPE Cream #FAFFD8)
module preview_two_banks() {
    COL_GSPE_PRI = [0.000, 0.212, 0.455];
    COL_GSPE_SEC = [0.980, 1.000, 0.847];
    translate([0, 0, BANK_H / 2])
        sub_socket_bank(3, "L3-N", COL_GSPE_PRI, COL_GSPE_SEC);
    translate([0, 0, -BANK_H / 2])
        sub_socket_bank(4, "L1-N", COL_GSPE_SEC, COL_GSPE_PRI);
}

preview_two_banks();
