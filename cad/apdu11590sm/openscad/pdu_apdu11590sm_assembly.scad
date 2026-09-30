// =====================================================================
// pdu_apdu11590sm_assembly.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// Master Assembly - MEREFLEKSIKAN REFERENSI Schneider CAD ASLI
// (references/images/socket.png & references/images/display.png)
//
// Sumbu: X = lebar (85), Y = kedalaman (85, front = -Y), Z = tinggi.
// Z = 0 dasar PDU, Z = 2030 puncak PDU.
// =====================================================================

use <modules/sub_chassis.scad>
use <modules/sub_socket_bank.scad>
use <modules/sub_nmc_controller.scad>
use <modules/sub_top_whip_cord.scad>
use <modules/sub_mounting_pegs.scad>

$fn = 24;

// ---- Parameter Assembly ----
WHIP_CORD_LEN = 300;        // stub preview; set 1800 untuk panjang nominal
SHOW_WHIP = true;

// ---- Konstanta Fisik ----
PDU_H = 2030.0;
PDU_W = 85.0;
PDU_D = 85.0;
FRONT_Y = -PDU_D/2;         // -42.5 mm
REAR_Y  =  PDU_D/2;         // +42.5 mm

// Warna Brand GSPE (Corporate Palette)
COL_GSPE_PRI = [0.000, 0.212, 0.455]; // #003674 Deep Corporate Navy
COL_GSPE_SEC = [0.980, 1.000, 0.847]; // #FAFFD8 Soft Light Cream

// Fasa 3-phase bergantian: L1-N, L2-N, L3-N
function get_phase_str(bank_idx) = 
    ((bank_idx - 1) % 3 == 0) ? "L1-N" :
    ((bank_idx - 1) % 3 == 1) ? "L2-N" : "L3-N";

// Plat fasa bergantian GSPE Navy dan GSPE Cream
function get_plate_col(bank_idx) = 
    (bank_idx % 2 == 1) ? COL_GSPE_PRI : COL_GSPE_SEC;

function get_text_col(bank_idx) = 
    (bank_idx % 2 == 1) ? COL_GSPE_SEC : COL_GSPE_PRI;

// =====================================================================
// ASSEMBLY RACK PDU
// =====================================================================

// 1. Badan Casing Ekstrusi + End Caps (85 x 85 x 2030 mm)
sub_chassis();

// 2. Modul NMC3 Controller (Cassette di tengah Z = 1000 mm, flush dengan muka PDU)
// Mencakup LCD grafis portrait, 3 tombol navigasi, USB, 2x2 RJ45 + GbE berlubang nyata
translate([0, FRONT_Y + 45.0 - 0.8, 1000])
    sub_nmc_controller();

// 3. Bank Soket Bawah (Bank 1-6: 6 modul x 68mm = 408mm, total 24 soket)
// Dimulai dari Z = 450 mm sampai Z = 858 mm
LOWER_Z_START = 450.0;
for (b = [1 : 6]) {
    translate([0, FRONT_Y, LOWER_Z_START + (b - 1) * 68.0 + 34.0])
        sub_socket_bank(b, get_phase_str(b), get_plate_col(b), get_text_col(b));
}

// 4. Bank Soket Atas (Bank 7-12: 6 modul x 68mm = 408mm, total 24 soket)
// Dimulai dari Z = 1250 mm sampai Z = 1658 mm
UPPER_Z_START = 1250.0;
for (b = [7 : 12]) {
    translate([0, FRONT_Y, UPPER_Z_START + (b - 7) * 68.0 + 34.0])
        sub_socket_bank(b, get_phase_str(b), get_plate_col(b), get_text_col(b));
}

// 5. Baut Toolless Mounting Belakang (Pitch 1832 mm, terpusat di belakang)
translate([0, REAR_Y, PDU_H/2])
    sub_mounting_pegs();

// 6. Power Cord Whip + Industrial Plug IEC 60309 100A Merah
if (SHOW_WHIP)
    translate([0, 0, PDU_H])
        sub_top_whip_cord(cord_len = WHIP_CORD_LEN);

// ---- Info Log ----
echo(str("Assembly GSPE-PDU-100A: 12 Bank Modul = 48 Soket (24 Combo 4-in-1 + 24 Standard C13/C15)"));
echo(str("Circuit Breakers: 12x 20A plates with GSPE Navy #003674 and Cream #FAFFD8 phase branding"));
echo(str("NMC3: GSPE Controller, Graphic LCD, 3 Nav Buttons, USB Console/Host, 4x RJ45 + GbE"));
