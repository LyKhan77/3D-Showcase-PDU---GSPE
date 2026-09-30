// =====================================================================
// pdu_apdu9953_assembly.scad
// GSPE NetShelter 9000 Switched Rack PDU (APDU9953)
// 0U Vertical Slim Single-Column, 24 Outlets (21x C13/C15 + 3x C19/C21)
// 230V 32A 1-Phase, 2x Rocker Breaker 20A, NMC3 Controller, Whip Cord
// IEC 60309 32A 2P+E Biru, Rear Toolless Mounting (pitch 1680 mm)
//
// Master Assembly - MEREFLEKSIKAN REFERENSI RESMI:
// references/images/sketchfab_ns9000/annotation_1/3/4/6/7/8.png
//
// Sumbu: X = lebar muka (56), Y = kedalaman (46, muka = -Y),
//        Z = tinggi. Z = 0 dasar PDU, Z = 1829 puncak PDU.
// =====================================================================

use <modules/sub_chassis.scad>
use <modules/sub_socket_bank.scad>
use <modules/sub_nmc3_controller.scad>
use <modules/sub_breaker_box.scad>
use <modules/sub_top_whip_cord.scad>
use <modules/sub_mounting_pegs.scad>

include <modules/detail_common.scad>
EXPLODE_FACTOR = 0.0; // 0.0 = assembled, 1.0 = fully separated
$fn = 48;

// ==========================================
// KONTROL VISIBILITAS SHOWCASE (SHOW / HIDE)
// ==========================================
SHOW_HOUSING = true;         // Extrusion, caps, front covers and body fasteners
SHOW_MOUNTING = true;        // Dual pads, pegs and rear grounding stud
SHOW_POWER_ENTRY = true;     // Gland, cord, IEC plug and distribution block
SHOW_FASCIA_EXTERNAL = true; // Socket assemblies, rockers, NMC panel/LCD/ports
SHOW_INTERNALS = true;       // Contacts, two rails, relay PCBs, NMC PCB, breaker bodies
SHOW_FRONT_COVER = true;     // Housing subgroup; false opens the full front channel
VIEW_STAGE = "CUSTOM"; // [CUSTOM,STAGE1_HOUSING,STAGE2_MOUNTING,STAGE3_POWER,STAGE4_INTERNALS,STAGE5_CONTROLS,STAGE6_COMPLETE,STAGE7_EXPLODED]

// ---- Parameter Assembly ----
WHIP_LEN  = 500;        // stub preview; set 3000 untuk panjang nominal
SHOW_WHIP = true;

// ---- Konstanta Fisik (specs/apdu9953_ns9000_switched.yaml) ----
PDU_H   = 1829.0;
PDU_W   = 56.0;
PDU_D   = 46.0;
FRONT_Y = -PDU_D/2;     // -23.0 mm (bidang muka)
REAR_Y  =  PDU_D/2;     // +23.0 mm (bidang belakang)

// ---- Layout Vertikal (Z, bawah -> atas) ----
// Bawah kosong (label rating) -> Bank 3 -> Breaker 2 -> Bank 2 ->
// NMC3 (tengah) -> Bank 1 -> Breaker 1 -> leher kosong (branding) -> gland.
// Nilai berasal dari detail_common.scad (satu sumber untuk pola pemasangan).
BANK3_Z = LAYOUT_BANK_Z[2];   // Bank 3: outlet 17-24
BRK2_Z  = LAYOUT_BRK_Z[1];    // Breaker 2 (antara Bank 2 & Bank 3)
BANK2_Z = LAYOUT_BANK_Z[1];   // Bank 2: outlet 9-16
NMC_Z   = LAYOUT_NMC_Z;       // NMC3 controller (tengah unit)
BANK1_Z = LAYOUT_BANK_Z[0];   // Bank 1: outlet 1-8
BRK1_Z  = LAYOUT_BRK_Z[0];    // Breaker 1 (di atas Bank 1)

// Warna Brand GSPE
COL_GSPE_PRI = [0.000, 0.212, 0.455];   // #003674 Deep Navy
COL_GSPE_SEC = [0.980, 1.000, 0.847];   // #FAFFD8 Pale Cream

// =====================================================================
// ASSEMBLY RACK PDU
// =====================================================================

// Presets are cumulative. Stages 1-4 keep front covers open for inspection.
function showcase_stage(stage) =
    stage=="CUSTOM" ? 0 : stage=="STAGE1_HOUSING" ? 1 :
    stage=="STAGE2_MOUNTING" ? 2 : stage=="STAGE3_POWER" ? 3 :
    stage=="STAGE4_INTERNALS" ? 4 : stage=="STAGE5_CONTROLS" ? 5 :
    stage=="STAGE6_COMPLETE" ? 6 : stage=="STAGE7_EXPLODED" ? 7 :
    assert(false,str("Unknown VIEW_STAGE: ",stage)) 0;

module pdu_apdu9953_assembly(explode_factor=EXPLODE_FACTOR,
    show_housing=SHOW_HOUSING, show_mounting=SHOW_MOUNTING,
    show_power_entry=SHOW_POWER_ENTRY, show_fascia_external=SHOW_FASCIA_EXTERNAL,
    show_internals=SHOW_INTERNALS, view_stage=VIEW_STAGE,
    show_front_cover=SHOW_FRONT_COVER, show_whip=SHOW_WHIP) {
    stage=showcase_stage(view_stage);
    e=explode_checked(stage==0 ? explode_factor : stage==7 ? 0.6 : 0);
    housing=stage==0 ? show_housing : true;
    mounting=stage==0 ? show_mounting : stage>=2;
    power=stage==0 ? show_power_entry : stage>=3;
    external=stage==0 ? show_fascia_external : stage>=5;
    internals=stage==0 ? show_internals : stage>=4;
    cover=stage==0 ? show_front_cover : stage>=5;
    whip=stage==0 ? show_whip : true;

    sub_chassis(explode_factor=e,show_housing=housing,show_front_cover=cover);
    for(bank=[[1,BANK1_Z],[2,BANK2_Z],[3,BANK3_Z]])
        translate([0,FRONT_Y,bank[1]])
            sub_socket_bank(bank_id=bank[0],explode_factor=e,show_housing=housing,
                show_fascia_external=external,show_internals=internals,
                show_front_cover=cover,show_busbars=false);
    if(internals) translate([0,FRONT_Y+70*e,0])
        pdu_busbars([BANK1_Z,BANK2_Z,BANK3_Z]);

    translate([0,FRONT_Y,NMC_Z]) sub_nmc3_controller(e,external,internals);
    for(brk=[["Bank 1",BRK1_Z],["Bank 2",BRK2_Z]])
        translate([0,FRONT_Y,brk[1]])
            sub_breaker_box(brk[0],e,housing,external,internals,cover);
    translate([0,REAR_Y,PDU_H/2])
        sub_mounting_pegs(explode_factor=e,show_mounting=mounting);
    translate([0,0,PDU_H])
        sub_top_whip_cord(cord_len=WHIP_LEN,explode_factor=e,
                         show_power_entry=power,show_whip=whip);

// 7. Plat branding GSPE di leher kosong atas (navy + cream)
if(housing && cover) translate([0, FRONT_Y - 0.8 - 12*e, 1560]) {
    // Plat dasar navy
    color(COL_GSPE_PRI)
        cube([44.0, 0.8, 120.0], center = true);

    // Border bevel tipis cream
    color(COL_GSPE_SEC)
        translate([0, -0.42, 0])
            rotate([90, 0, 0])
                linear_extrude(height = 0.25)
                    difference() {
                        square([42.0, 118.0], center = true);
                        square([40.4, 116.4], center = true);
                    };

    // Teks branding horizontal rapi (membaca normal kiri-ke-kanan, tanpa overlap)
    color(COL_GSPE_SEC)
        translate([0, -0.45, 0])
            rotate([90, 0, 0])
                linear_extrude(height = 0.35) {
                    // Logo GSPE
                    translate([0, 42])
                        text("GSPE", size = 8.5, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");

                    // Garis pemisah atas
                    translate([0, 32])
                        square([32.0, 0.8], center = true);

                    // Model SKU
                    translate([0, 22])
                        text("APDU9953", size = 4.2, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");

                    // Seri produk
                    translate([0, 10])
                        text("NETSHELTER", size = 3.0, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");
                    translate([0, 3])
                        text("9000 SERIES", size = 3.0, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");
                    translate([0, -5])
                        text("SWITCHED PDU", size = 2.6, font = "Helvetica",
                             halign = "center", valign = "center");

                    // Garis pemisah tengah
                    translate([0, -15])
                        square([28.0, 0.6], center = true);

                    // Rating elektrikal
                    translate([0, -24])
                        text("230 V  ·  32 A", size = 3.2, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");
                    translate([0, -32])
                        text("50/60 Hz  1-PHASE", size = 2.2, font = "Helvetica",
                             halign = "center", valign = "center");
                    translate([0, -42])
                        text("7.36 kW CAPACITY", size = 2.5, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");
                }
}

// 8. Label rating di dasar bodi (horizontal, teratur, presisi)
if(housing && cover) translate([0, FRONT_Y - 0.8 - 12*e, 110]) {
    // Plat dasar navy
    color(COL_GSPE_PRI)
        cube([44.0, 0.8, 68.0], center = true);

    // Border frame label
    color(COL_GSPE_SEC)
        translate([0, -0.42, 0])
            rotate([90, 0, 0])
                linear_extrude(height = 0.25)
                    difference() {
                        square([41.6, 65.6], center = true);
                        square([40.2, 64.2], center = true);
                    };

    // Teks spesifikasi rating elektrikal horizontal
    color(COL_GSPE_SEC)
        translate([0, -0.45, 0])
            rotate([90, 0, 0])
                linear_extrude(height = 0.35) {
                    translate([0, 24])
                        text("GSPE RACK PDU", size = 3.2, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");
                    translate([0, 17])
                        text("MODEL: APDU9953", size = 2.4, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");

                    translate([0, 12])
                        square([36.0, 0.5], center = true);

                    translate([0, 6])
                        text("INPUT: 200-240V ~ 32A", size = 2.2, font = "Helvetica",
                             halign = "center", valign = "center");
                    translate([0, 0])
                        text("OUTPUT: 24 OUTLETS", size = 2.2, font = "Helvetica",
                             halign = "center", valign = "center");
                    translate([0, -6])
                        text("21x C13/C15  ·  3x C19/C21", size = 1.9, font = "Helvetica",
                             halign = "center", valign = "center");
                    translate([0, -12])
                        text("PLUG: IEC 60309 32A 2P+E", size = 1.9, font = "Helvetica",
                             halign = "center", valign = "center");

                    translate([0, -17])
                        square([36.0, 0.5], center = true);

                    translate([0, -23])
                        text("CE  ·  RoHS  ·  IP20", size = 2.2, font = "Helvetica:style=Bold",
                             halign = "center", valign = "center");
                }
}

} // module pdu_apdu9953_assembly

// Instansiasi default saat file dibuka langsung
pdu_apdu9953_assembly();

// ---- Info Log ----
echo(str("APDU9953 Assembly: 3 Bank x 8 Outlet = 24 (21x C13/C15 + 3x C19/C21)"));
echo(str("Breakers: 2x 20A low-profile rocker | NMC3: LCD + 3 btn + 3 LED + 6 port"));
echo(str("Mounting: toolless pegs pitch 1680.0 mm | Whip cord stub: ", WHIP_LEN, " mm (nominal 3000)"));
