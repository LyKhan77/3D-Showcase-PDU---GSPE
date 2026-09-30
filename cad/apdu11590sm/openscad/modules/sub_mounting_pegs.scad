// =====================================================================
// sub_mounting_pegs.scad
// APC NetShelter Rack PDU Advanced 100A (APDU11590SM)
// 2x toolless round mounting button (rear side, pitch 1832.0 mm)
// Origin: bidang muka belakang chassis (Y=0), sumbu peg ke +Y,
//         Z=0 di tengah jarak kedua peg.
// =====================================================================

$fn = 32;

PEG_SPACING = 1832.0;    // jarak center-to-center vertikal
PEG_HEAD_DIA = 12.0;     // kepala jamur
PEG_HEAD_T = 3.0;
PEG_NECK_DIA = 6.0;
PEG_NECK_H = 5.0;
PEG_BASE_DIA = 10.0;
PEG_BASE_T = 2.0;

module mounting_peg() {
    col = [0.55, 0.56, 0.58];   // baja seng
    color(col)
        rotate([-90, 0, 0]) {   // sumbu silinder -> +Y
            // basis
            cylinder(d = PEG_BASE_DIA, h = PEG_BASE_T);
            // leher
            translate([0, 0, PEG_BASE_T])
                cylinder(d = PEG_NECK_DIA, h = PEG_NECK_H);
            // kepala jamur dengan chamfer atas
            translate([0, 0, PEG_BASE_T + PEG_NECK_H]) {
                cylinder(d = PEG_HEAD_DIA, h = PEG_HEAD_T - 1.2);
                translate([0, 0, PEG_HEAD_T - 1.2])
                    cylinder(d1 = PEG_HEAD_DIA, d2 = PEG_HEAD_DIA - 3,
                             h = 1.2, $fn = 32);
            }
        }
}

module sub_mounting_pegs(spacing = PEG_SPACING) {
    for (z = [-spacing/2, spacing/2])
        translate([0, 0, z])
            mounting_peg();
}

// Preview standalone
sub_mounting_pegs();
