// =====================================================================
// sub_breaker_box.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// MEREFLEKSIKAN REFERENSI Schneider CAD ASLI (socket.png)
//
// Koordinat:
// X = lebar (kiri-kanan)
// Y = kedalaman (muka depan = 0, menonjol = -Y)
// Z = tinggi vertikal
// =====================================================================

$fn = 24;

BRK_W = 24.0;           // Lebar plat breaker
BRK_H = 68.0;           // Tinggi plat breaker (mencakup 2 baris soket)

module sub_breaker_plate(bank_id = 3, phase_str = "L3-N", plate_color = [0.45, 0.46, 0.48], text_color = [0.95, 0.95, 0.95]) {
    // Plat dasar breaker
    color(plate_color)
        difference() {
            translate([-BRK_W/2, -1.0, -BRK_H/2])
                cube([BRK_W, 2.0, BRK_H]);

            // Lubang cutout untuk switch rocker tengah
            translate([-7.5, -2.0, -16.0])
                cube([15.0, 4.0, 32.0]);
        }

    // Baut Phillips hitam atas
    color([0.1, 0.1, 0.1])
        translate([0, -1.2, BRK_H/2 - 6.0])
            rotate([90, 0, 0]) {
                cylinder(d = 4.5, h = 1.0);
                translate([-1.5, -0.4, 0.8]) cube([3.0, 0.8, 0.5]);
                translate([-0.4, -1.5, 0.8]) cube([0.8, 3.0, 0.5]);
            }

    // Baut Phillips hitam bawah
    color([0.1, 0.1, 0.1])
        translate([0, -1.2, -BRK_H/2 + 20.0])
            rotate([90, 0, 0]) {
                cylinder(d = 4.5, h = 1.0);
                translate([-1.5, -0.4, 0.8]) cube([3.0, 0.8, 0.5]);
                translate([-0.4, -1.5, 0.8]) cube([0.8, 3.0, 0.5]);
            }

    // Bezel frame switch rocker tengah
    color([0.15, 0.15, 0.16])
        translate([-7.0, -2.0, -15.0])
            cube([14.0, 2.0, 30.0]);

    // Tombol rocker 20A hitam (posisi ON agak miring)
    color([0.10, 0.10, 0.11])
        translate([-5.5, -3.2, -13.5])
            rotate([-5, 0, 0])
                cube([11.0, 2.5, 27.0]);

    // Tulisan putih pada saklar ("ON 20" dan "| OFF")
    color([0.9, 0.9, 0.9]) {
        translate([0, -3.5, 4.0])
            rotate([90, 0, 0])
                linear_extrude(height = 0.3) {
                    text("ON", size = 2.4, font = "Helvetica:style=Bold", halign = "center");
                    translate([0, -3.2, 0]) text("20", size = 2.0, font = "Helvetica", halign = "center");
                }
        translate([0, -3.5, -8.0])
            rotate([90, 0, 0])
                linear_extrude(height = 0.3) {
                    text("|", size = 2.4, font = "Helvetica:style=Bold", halign = "center");
                    translate([0, -3.2, 0]) text("OFF", size = 2.0, font = "Helvetica", halign = "center");
                }
    }

    // Label Bank & Fasa di bawah saklar (misal "B3" dan "L3-N")
    // Sesuai referensi CAD: teks diputar vertikal 90 derajat (B3 di kanan, fasa di kiri)
    color(text_color) {
        translate([3.5, -1.5, -BRK_H/2 + 7.5])
            rotate([90, 0, 0])
                linear_extrude(height = 0.4)
                    rotate([0, 0, 90])
                        text(str("B", bank_id), size = 3.6, font = "Helvetica:style=Bold", halign = "center", valign = "center");
        translate([-3.5, -1.5, -BRK_H/2 + 7.5])
            rotate([90, 0, 0])
                linear_extrude(height = 0.4)
                    rotate([0, 0, 90])
                        text(phase_str, size = 2.6, font = "Helvetica:style=Bold", halign = "center", valign = "center");
    }
}

// Standalone preview
sub_breaker_plate(3, "L3-N", [0.45, 0.46, 0.48], [0.95, 0.95, 0.95]);
