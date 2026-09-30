// =====================================================================
// sub_chassis.scad
// GSPE NetShelter 9000 Switched Rack PDU (APDU9953)
// Ekstrusi bodi 1829 x 56 x 46 mm, plat baja 1.5 mm, fillet sudut R2
// Sumbu: X = lebar muka (56), Y = kedalaman (46, muka = -Y),
//        Z = tinggi (0 = dasar, 1829 = puncak)
// =====================================================================

include <detail_common.scad>
EXPLODE_FACTOR = 0.0;
$fn = 48;

EPS = 0.01;              // overlap boolean anti z-fighting / mesh error

CHASSIS_H    = 1829.0;
CHASSIS_W    = 56.0;
CHASSIS_D    = 46.0;
CHASSIS_WALL = 1.5;
CHASSIS_R    = 2.0;
CAP_T        = 3.0;      // tebal end plate atas/bawah
GLAND_HOLE_DIA  = 23.0;  // lubang cable gland M25 di top cap (kabel Ø20)

// Palet GSPE
COL_BODY = [0.078, 0.090, 0.118];   // #14171E dark steel powder coat
COL_CAP  = [0.118, 0.133, 0.176];   // #1E222D module bezel graphite

// Zona cutout dinding muka: [z_center, tinggi, lebar]
// Selaras dengan layout pada pdu_apdu9953_assembly.scad
CHASSIS_FRONT_ZONES = [
    [1159.5, 241.0, 52.5],   // Bank 1 (outlet 1-8)
    [ 914.5, 211.0, 52.5],   // NMC3 Controller Cassette
    [ 669.5, 241.0, 52.5],   // Bank 2 (outlet 9-16)
    [ 329.5, 241.0, 52.5],
    [1329.5, 38.0, 37.0], // hydraulic breaker body clearance
    [ 499.5, 38.0, 37.0],   // Bank 3 (outlet 17-24)
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
                   front_zones = CHASSIS_FRONT_ZONES, explode_factor = EXPLODE_FACTOR,
                   show_housing = true, show_front_cover = true,
                   rear_pts = [ for(zc=LAYOUT_BANK_Z) each bank_carrier_pts(zc) ],
                   rear_pts_extra = [ for(zc=LAYOUT_BRK_Z) each brk_retainer_pts(zc) ],
                   tray_pts = [ each nmc_tray_pts(LAYOUT_NMC_Z) ],
                   side_pts = [ for(zc=concat(LAYOUT_BANK_Z,[LAYOUT_NMC_Z]))
                                    each fascia_side_z(zc) ],
                   cap_pts = terminal_bracket_pts()) {
    assert(explode_factor >= 0 && explode_factor <= 1);
    if(show_housing) translate([0,200*explode_factor,0]) {

    // ---- Badan ekstrusi (tabung persegi berongga) ----
    color(COL_BODY)
        difference() {
            linear_extrude(height = h)
                rounded_square_2d(w, d, r);
            translate([0, 0, -EPS])
                linear_extrude(height = h + 2*EPS)
                    rounded_square_2d(w - 2*wall, d - 2*wall,
                                      max(r - wall, 0.1));
            // Detachable face exposes the entire channel when hidden.
            if(!show_front_cover)
                translate([-w/2-EPS,-d/2-EPS,-EPS]) cube([w+2*EPS,wall+2*EPS,h+2*EPS]);
            for(x=[-19,19]) translate([x,d/2+EPS,h-7]) rotate([90,0,0]) {
                cylinder(d=3.2,h=wall+2*EPS);
                cylinder(d1=6.2,d2=3.2,h=1.3);
            }
            translate([10,d/2+EPS,150]) rotate([90,0,0]) cylinder(d=5.2,h=wall+2*EPS);
            for (zc = [1329.5,499.5], x = [-19,19], z = [-28.5,28.5])
                translate([x,-d/2+wall+EPS,zc+z]) rotate([90,0,0])
                    cylinder(d=3.1,h=wall+2*EPS);
            // Cutout zona muka (front = -Y)
            for (zone = front_zones)
                translate([-zone[2]/2, -d/2 - EPS, zone[0] - zone[1]/2])
                    cube([zone[2], wall + 2*EPS, zone[1]]);
            // Rear mounting holes: bank carrier plates, breaker retainers, NMC tray.
            for (p = concat(rear_pts, rear_pts_extra, tray_pts))
                translate([p[0], d/2+EPS, p[1]]) rotate([90,0,0]) {
                    cylinder(d=3.2, h=wall+2*EPS);
                    cylinder(d1=6.2, d2=3.2, h=1.3);
                }
            // Side-wall press holes for the fascia threaded inserts (axis X).
            for (z = side_pts, dir=[-1,1])
                translate([dir>0 ? (w/2-wall)-EPS : -(w/2-wall)+EPS, -20, z])
                    rotate([0, dir>0 ? 90 : -90, 0])
                        cylinder(d=5.05, h=wall+2*EPS);
        }

    // Pressed brass threaded inserts seated in the side-wall holes (housing group).
    for (z = side_pts, dir=[-1,1]) threaded_insert(dir=dir, y=-20, z=z);

    // ---- Bottom end plate (Z = 0); grounding is on the rear wall ----
    color(COL_CAP)
        difference() {
            linear_extrude(height = CAP_T)
                rounded_square_2d(w - 0.6, d - 0.6, max(r - 0.3, 0.1));

        }

    // Rear-facing end-cap return lip and two countersunk Torx screws.
    color(COL_CAP) translate([0,0,h-CAP_T]) difference() {
        translate([-23,d/2-wall-1.2,-7]) cube([46,1.2,7+EPS]);
        for(x=[-19,19]) translate([x,d/2,CAP_T-7]) rotate([90,0,0]) cylinder(d=3.2,h=5);
    }
    for(x=[-19,19]) translate([x,d/2+0.12+20*explode_factor,h-7])
        rotate([90,0,0]) color("#606770") difference() {
            union() {
                cylinder(d1=6,d2=3,h=1.3);
                translate([0,0,1.3-EPS]) cylinder(d=3,h=4);
            }
            translate([0,0,-EPS]) linear_extrude(height=0.85) torx_t15_profile();
        }

    // ---- Top end plate (Z = h), lubang cable gland + bracket terminal block ----
    color(COL_CAP)
        translate([0, 0, h - CAP_T])
            difference() {
                linear_extrude(height = CAP_T)
                    rounded_square_2d(w - 0.6, d - 0.6, max(r - 0.3, 0.1));
                translate([0, 0, -EPS])
                    cylinder(d = GLAND_HOLE_DIA, h = CAP_T + 2*EPS, $fn = 48);
                for (p = cap_pts)
                    translate([p[0], p[1], -EPS]) {
                        cylinder(d = 3.2, h = CAP_T + 2*EPS);
                        translate([0, 0, CAP_T - 1.3]) cylinder(d1 = 3.2, d2 = 6.2, h = 1.3);
                    }
            }
}

} // exploded chassis group

// Preview standalone
sub_chassis();
