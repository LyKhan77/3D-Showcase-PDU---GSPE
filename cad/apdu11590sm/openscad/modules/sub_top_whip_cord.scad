// =====================================================================
// sub_top_whip_cord.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// Cable gland top entry, kabel fleksibel Ø28 mm, plug IEC 60309 100A
// 415V 3P+N+PE (merah). Origin: bidang top cap, sumbu +Z ke atas.
// =====================================================================

$fn = 32;

GLAND_HEX_AF = 36.0;    // gland nut hex across-flats
GLAND_H = 10.0;
BOOT_D_BOT = 36.0;      // strain-relief boot mengerucut 36 -> 28
BOOT_D_TOP = 28.0;
BOOT_H = 50.0;
CORD_DIA = 28.0;        // jacket 5-wire 100A 415V
CORD_LEN_NOMINAL = 1800.0;

// Plug IEC 60309 100A
PLUG_DIA = 80.0;        // diameter barrel
PLUG_LEN = 160.0;       // panjang badan
PLUG_RING_DIA = 88.0;   // locking ring pengunci putar
PLUG_RING_H = 18.0;
PLUG_PIN_DIA = 6.0;
PLUG_PIN_H = 15.0;
PLUG_PIN_R = 25.0;      // radius pola 5 pin (3P+N+PE)

RAL3001_RED = [0.65, 0.10, 0.12];

module sub_top_whip_cord(cord_len = 300) {
    // ---- Gland nut (hex) menumpang di top cap ----
    color([0.15, 0.15, 0.16])
        cylinder(d = GLAND_HEX_AF / cos(30), h = GLAND_H, $fn = 6);

    // ---- Rubber strain-relief boot (taper 36 -> 28) ----
    color([0.05, 0.05, 0.055])
        translate([0, 0, GLAND_H])
            cylinder(d1 = BOOT_D_BOT, d2 = BOOT_D_TOP, h = BOOT_H, $fn = 48);

    // ---- Kabel fleksibel Ø28 ----
    color([0.04, 0.04, 0.045])
        translate([0, 0, GLAND_H + BOOT_H])
            cylinder(d = CORD_DIA, h = cord_len, $fn = 48);

    z_plug = GLAND_H + BOOT_H + cord_len;

    // ---- Plug IEC 60309 100A (merah, 415V 3P+N+PE) ----
    translate([0, 0, z_plug]) {
        // badan barrel
        color(RAL3001_RED)
            cylinder(d = PLUG_DIA, h = PLUG_LEN, $fn = 64);
        // locking ring pengunci putar
        color([0.45, 0.07, 0.09])
            translate([0, 0, PLUG_LEN - PLUG_RING_H - 12])
                cylinder(d = PLUG_RING_DIA, h = PLUG_RING_H, $fn = 64);
        // kerah kabel di pangkal plug
        color([0.45, 0.07, 0.09])
            cylinder(d1 = CORD_DIA + 4, d2 = PLUG_DIA, h = 20, $fn = 48);
        // 5 round contact pins (3P+N+PE) di muka plug
        color([0.72, 0.72, 0.74])
            for (a = [90, 162, 234, 306, 18])
                translate([PLUG_PIN_R * cos(a), PLUG_PIN_R * sin(a), PLUG_LEN - 0.5])
                    cylinder(d = PLUG_PIN_DIA, h = PLUG_PIN_H, $fn = 24);
    }
}

// Preview standalone
sub_top_whip_cord();
