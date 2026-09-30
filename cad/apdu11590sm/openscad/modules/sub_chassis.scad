// =====================================================================
// sub_chassis.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// Casing ekstrusi 2030 x 85 x 85 mm, plat 1.5 mm, fillet sudut R2
// Sumbu: X = lebar, Y = kedalaman (front face = -Y), Z = tinggi (0 = dasar)
// =====================================================================

$fn = 32;

CHASSIS_H = 2030.0;
CHASSIS_W = 85.0;
CHASSIS_D = 85.0;
CHASSIS_WALL = 1.5;
CHASSIS_R = 2.0;
CAP_T = 3.0;               // tebal end cap atas/bawah
GLAND_HOLE_DIA = 34.0;     // lubang cable gland di top cap
GROUND_HOLE_DIA = 6.5;     // lubang grounding stud M6 di bottom cap

// Zona cutout muka: [z_center, tinggi, lebar]
// Disesuaikan presisi dengan posisi modul pada assembly:
// - Bank Bawah: Z = 450 s/d 858 mm (tinggi 408 mm, lebar 78 mm)
// - NMC3 Cassette: Z = 1000 mm (tinggi 152 mm, lebar 56 mm)
// - Bank Atas: Z = 1250 s/d 1658 mm (tinggi 408 mm, lebar 78 mm)
CHASSIS_FRONT_ZONES = [
    [ 654.0, 410.0, 78.5],    // Bank Bawah (Soket 1-24 + Breakers B1-B6)
    [1000.0, 152.0, 56.5],    // NMC3 Controller Cassette
    [1454.0, 410.0, 78.5],    // Bank Atas (Soket 25-48 + Breakers B7-B12)
];

module rounded_square_2d(w, d, r) {
    hull()
        for (x = [-w/2 + r, w/2 - r])
            for (y = [-d/2 + r, d/2 - r])
                translate([x, y])
                    circle(r = r, $fn = 32);
}

module sub_chassis(h = CHASSIS_H, w = CHASSIS_W, d = CHASSIS_D,
                   wall = CHASSIS_WALL, r = CHASSIS_R,
                   front_zones = CHASSIS_FRONT_ZONES) {
    col_shell = [0.125, 0.125, 0.135];   // powder-coat matte black RAL 9005
    col_cap   = [0.09, 0.09, 0.10];

    // ---- Badan ekstrusi (tabung persegi berongga) ----
    color(col_shell)
        difference() {
            linear_extrude(height = h)
                rounded_square_2d(w, d, r);
            translate([0, 0, -0.5])
                linear_extrude(height = h + 1)
                    rounded_square_2d(w - 2*wall, d - 2*wall,
                                      max(r - wall, 0.1));
            // Cutout zona muka (front = -Y)
            for (zone = front_zones)
                translate([-zone[2]/2, -d/2 - 0.5, zone[0] - zone[1]/2])
                    cube([zone[2], wall + 1, zone[1]]);
        }

    // ---- Bottom cap (Z = 0), rata, lubang grounding M6 ----
    color(col_cap)
        difference() {
            linear_extrude(height = CAP_T)
                rounded_square_2d(w - 0.6, d - 0.6, max(r - 0.3, 0.1));
            translate([0, 20, -0.5])
                cylinder(d = GROUND_HOLE_DIA, h = CAP_T + 1, $fn = 24);
        }

    // ---- Top cap (Z = h), lubang cable gland Ø34 ----
    color(col_cap)
        translate([0, 0, h - CAP_T])
            difference() {
                linear_extrude(height = CAP_T)
                    rounded_square_2d(w - 0.6, d - 0.6, max(r - 0.3, 0.1));
                translate([0, 0, -0.5])
                    cylinder(d = GLAND_HOLE_DIA, h = CAP_T + 1, $fn = 48);
            }
}

// Preview standalone
sub_chassis();
