// =====================================================================
// sub_top_whip_cord.scad
// GSPE NetShelter 9000 Switched Rack PDU (APDU9953)
// Top-entry hex cable gland nut + kabel karet Ø20 mm + steker industri
// IEC 60309 32A 2P+E (Biru 230V)
// MEREFLEKSIKAN REFERENSI: annotation_7.png
// Origin: bidang top cap (Z = 0), sumbu +Z ke atas.
// =====================================================================

include <detail_common.scad>
EXPLODE_FACTOR = 0.0;
$fn = 32;

EPS = 0.01;

// Cable gland M25 (kabel Ø20)
GLAND_COLLAR_D = 26.0;
GLAND_COLLAR_H = 4.0;
GLAND_HEX_AF   = 32.0;    // across-flats hex nut
GLAND_HEX_H    = 12.0;
BOOT_D_BOT     = 24.0;    // strain-relief boot mengerucut 24 -> 20
BOOT_D_TOP     = 20.0;
BOOT_H         = 22.0;
CORD_DIA       = 20.0;    // jacket karet 3x6 mm² (spec: cord_diameter 20)
CORD_LEN_NOMINAL = 3000.0;

// Steker IEC 60309 32A 2P+E (biru)
PLUG_DIA      = 56.0;
PLUG_LEN      = 90.0;
PLUG_RING_DIA = 62.0;
PLUG_RING_H   = 14.0;
PLUG_PIN_LN_D = 5.0;      // pin daya L/N
PLUG_PIN_PE_D = 6.0;      // pin earth lebih besar
PLUG_PIN_R    = 17.0;     // radius pola pin

COL_GLAND = [0.118, 0.133, 0.176];   // #1E222D graphite
COL_CORD  = [0.045, 0.050, 0.058];   // karet hitam
COL_BLUE  = [0.133, 0.443, 0.702];   // biru IEC 60309 230V (RAL 5015)
COL_PIN   = [0.773, 0.608, 0.153];   // #C59B27 kuningan

module power_terminal_block() {
    // Three screw-clamp ways L/N/PE below the gland, within the 56 x 46 body.
    color("#252D35") difference() {
        translate([0,0,-54]) cube([40,24,30],center=true);
        for(x=[-13,0,13]) translate([x,-12.1,-54]) rotate([-90,0,0]) cylinder(d=7,h=13);
    }
    for(x=[-13,0,13]) {
        color("#C59B27") translate([x,-2,-54]) cube([8,3,20],center=true);
        translate([x,-13,-47]) torx_screw(5.4,2.8,9);
        color(x<0 ? "#76533A" : x==0 ? "#2177AC" : "#5D9438")
            translate([x,0,-37]) cylinder(d=4.5,h=30);
    }
    face_print("L",-13,-12.05,-63,2.8);
    face_print("N",0,-12.05,-63,2.8);
    face_print("PE",13,-12.05,-63,2.8);
}
// Mounting bracket for the terminal block: plate on the block, four standoffs
// to the top cap (single source: terminal_bracket_pts), four vertical M3
// screws, plus a wire saddle clamping the internal L/N/PE conductors.
module power_terminal_bracket() {
    color("#3A4149") difference() {
        union() {
            translate([0,0,-38]) cube([44,26,3],center=true);
            for(p=terminal_bracket_pts())
                translate([p[0],p[1],-19.5]) cylinder(d=6,h=33,center=true);
            for(x=[-12,12])
                translate([x,0,-31]) cylinder(d=4,h=10,center=true);
        }
        for(p=terminal_bracket_pts())
            translate([p[0],p[1],-8]) cylinder(d=2.2,h=11,center=true);
        // Passages for the internal L/N/PE conductors into the block.
        for(x=[-13,0,13]) translate([x,0,-38]) cylinder(d=5,h=3+2*EPS,center=true);
    }
    // Wire saddle with three conductor passages.
    color("#252D35") difference() {
        translate([0,0,-23]) cube([30,16,6],center=true);
        for(x=[-13,0,13]) translate([x,0,-23]) cylinder(d=5.2,h=6+2*EPS,center=true);
    }
    for(p=terminal_bracket_pts())
        translate([p[0],p[1],0]) rotate([-90,0,0])
            torx_screw_csk(head_d=5.4,shaft_d=2.8,length=4);
}
module sub_top_whip_cord(cord_len = 500, explode_factor = EXPLODE_FACTOR,
                         show_power_entry=true,show_whip=true) {
    assert(explode_factor >= 0 && explode_factor <= 1);
    if(show_power_entry) {
    translate([0,110*explode_factor,0]) {
        power_terminal_block();
        power_terminal_bracket();
    }
    if(show_whip) translate([0,200*explode_factor,0]) {
    // ---- Kerah dasar gland ----
    color(COL_GLAND)
        cylinder(d = GLAND_COLLAR_D, h = GLAND_COLLAR_H);

    // ---- Hex gland nut berulir (3 cincin ulir antara kerah & nut) ----
    color(COL_GLAND) {
        // cincin ulir
        for (i = [0 : 2])
            translate([0, 0, GLAND_COLLAR_H + i * 1.4])
                cylinder(d = GLAND_COLLAR_D + 1.0, h = 0.9);
        // hex nut
        translate([0, 0, GLAND_COLLAR_H + 4.6])
            cylinder(d = GLAND_HEX_AF / cos(30), h = GLAND_HEX_H, $fn = 6);
    }

    z_boot = GLAND_COLLAR_H + 4.6 + GLAND_HEX_H;

    // ---- Strain-relief boot karet (taper) ----
    color(COL_CORD)
        translate([0, 0, z_boot - EPS])
            cylinder(d1 = BOOT_D_BOT, d2 = BOOT_D_TOP, h = BOOT_H + EPS);

    // ---- Kabel karet lentur Ø20 ----
    color(COL_CORD)
        translate([0, 0, z_boot + BOOT_H - EPS])
            cylinder(d = CORD_DIA, h = cord_len + EPS);

    z_plug = z_boot + BOOT_H + cord_len;

    // ---- Steker IEC 60309 32A 2P+E (biru) ----
    translate([0, 0, z_plug - EPS]) {
        // kerah kabel pangkal plug
        color(COL_BLUE)
            cylinder(d1 = CORD_DIA + 3, d2 = PLUG_DIA, h = 16);
        // badan barrel
        color(COL_BLUE)
            translate([0, 0, 16 - EPS])
                cylinder(d = PLUG_DIA, h = PLUG_LEN - PLUG_RING_H - 16 + EPS);
        // locking ring
        color([0.10, 0.35, 0.58])
            translate([0, 0, PLUG_LEN - PLUG_RING_H])
                cylinder(d = PLUG_RING_DIA, h = PLUG_RING_H);
        // muka plug
        color([0.10, 0.35, 0.58])
            translate([0, 0, PLUG_LEN - EPS])
                cylinder(d = PLUG_DIA - 6, h = 4 + EPS);
        // 3 pin (2P+E): earth lebih panjang di posisi 6 jam
        color(COL_PIN) {
            // Earth (PE)
            translate([0, -PLUG_PIN_R, PLUG_LEN + 4 - EPS])
                cylinder(d = PLUG_PIN_PE_D, h = 18);
            // L & N
            for (a = [60, 300])
                translate([PLUG_PIN_R * cos(a), PLUG_PIN_R * sin(a),
                           PLUG_LEN + 4 - EPS])
                    cylinder(d = PLUG_PIN_LN_D, h = 14);
        }
    }
}

}
} // exploded chassis attachment

// Preview standalone (stub 500 mm; nominal 3000 mm)
sub_top_whip_cord();
