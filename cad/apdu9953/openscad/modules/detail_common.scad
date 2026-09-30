// Millimetres. X = width, -Y = viewer, Z = up.
EPS = 0.02;
COL_NAVY = "#003674";
COL_CREAM = "#FAFFD8";
COL_POLY = "#2A2E39";
COL_BLACK = "#14171E";
COL_METAL = "#939BA4";
COL_COPPER = "#C58B49";
COL_GOLD = "#D7B553";
COL_PCB = "#176443";
function explode_checked(e) = assert(e >= 0 && e <= 1,"EXPLODE_FACTOR must be in [0, 1]") e;
// XZ profile, extruded towards +Y, preserving Z orientation.
module depth_profile(y_front, depth) {
    translate([0,y_front+depth,0]) rotate([90,0,0]) linear_extrude(height=depth) children();
}
module rounded_profile(w,h,r=1.8) {
    offset(r=r) square([w-2*r,h-2*r],center=true);
}
module face_print(s,x,y,z,size=2.4,angle=0,ink="#F4F4F2") {
    color(ink) translate([x,y,z]) rotate([90,0,0]) linear_extrude(height=0.10)
        rotate(angle) text(s,size=size,font="Helvetica:style=Bold",halign="center",valign="center");
}
module y_cylinder(d,y,depth,x=0,z=0) {
    translate([x,y+depth,z]) rotate([90,0,0]) cylinder(d=d,h=depth,$fn=40);
}
// Six rounded lobes; nominal T15 visual drive envelope 3.27 mm.
module torx_t15_profile() {
    difference() {
        circle(d=3.27,$fn=72);
        for(a=[0:60:300]) rotate(a) translate([1.88,0]) circle(r=0.75,$fn=24);
    }
}
module torx_screw(head_d=5.4,shaft_d=2.8,length=6) {
    color("#606770") difference() {
        union() { y_cylinder(head_d,0,1.25); y_cylinder(shaft_d,1.20,length); }
        depth_profile(-EPS,0.75) torx_t15_profile();
    }
    color("#20252B") depth_profile(0.70,0.03) scale(0.98) torx_t15_profile();
}
// Countersunk variant: conical seat from head_d to shaft_d over 1.2 mm, then shaft.
// Origin sits at the cone base (outer seating face); screw points along +Y.
module torx_screw_csk(head_d=6.0,shaft_d=2.8,length=6) {
    color("#606770") difference() {
        union() {
            translate([0,1.2,0]) rotate([90,0,0]) cylinder(d1=shaft_d,d2=head_d,h=1.2);
            y_cylinder(shaft_d,1.15,length);
        }
        depth_profile(-EPS,0.75) torx_t15_profile();
    }
    color("#20252B") depth_profile(0.70,0.03) scale(0.98) torx_t15_profile();
}
// Side-axis (X) countersunk Torx screw for the wrap-around fascia flanges.
// dir=+1: head at +X pointing -X; dir=-1 mirrored. Origin argument places the
// cone base (seating face) at the flange outer face, shaft reaches the insert.
module side_torx_screw(dir=1,length=4.5,head_d=5.4,shaft_d=2.8,y=0,z=0) {
    translate([dir*29.5,y,z]) rotate([0,0,dir>0?90:-90])
        torx_screw_csk(head_d=head_d,shaft_d=shaft_d,length=length);
}
// Brass press-in threaded insert for the 1.5 mm side wall; plain tube runs
// the wall thickness and protrudes 2 mm into the cavity. The fascia flange
// carries the countersunk seat; the screw shaft threads into this tube.
module threaded_insert(dir=1,y=0,z=0) {
    translate([dir>0?24.5:-24.5,y,z]) rotate([0,0,dir>0?-90:90]) {
        color("#C59B27") difference() {
            y_cylinder(5,0,3.5);
            y_cylinder(2.4,-EPS,3.5+2*EPS);
        }
    }
}
module wire_between(a,b,d=0.32) {
    hull() { translate(a) sphere(d=d,$fn=10); translate(b) sphere(d=d,$fn=10); }
}
module pcb_chip(x,z,w,h,y=31,depth=2) {
    color("#242930") translate([x,y,z]) cube([w,depth,h],center=true);
    color(COL_METAL) for(sx=[-1,1],zz=[-h/2+1:1.5:h/2-1])
        translate([x+sx*(w/2+0.45),y+0.4,z+zz]) cube([1,0.45,0.55],center=true);
}

// =====================================================================
// SINGLE SOURCE OF TRUTH — layout vertikal & pola titik pemasangan.
// Satu fungsi = satu pola; dipakai bersama oleh chassis (lubang), modul
// komponen (dudukan/baut), dan audit. Jangan menduplikasi angka di modul.
// =====================================================================
LAYOUT_H    = 1829.0;
LAYOUT_BANK_Z = [1159.5, 669.5, 329.5];   // bank 1,2,3 (tengah zona)
LAYOUT_BRK_Z  = [1329.5, 499.5];          // breaker 1,2
LAYOUT_NMC_Z  = 914.5;                    // controller cassette
LAYOUT_FRONT_Y = -23.0;
LAYOUT_REAR_Y  =  23.0;

// Plat carrier bank -> dinding belakang chassis (4 sekrup, sumbu Y).
function bank_carrier_pts(zc) =
    [ for(x=[-19,19], dz=[-110,110]) [x, zc+dz] ];
// Standoff carrier -> PCB relay; HARUS identik dengan lubang PCB (4 titik).
function bank_relay_pts(zc) =
    [ for(x=[-20,20], dz=[-113,113]) [x, zc+dz] ];
// Plat retainer breaker -> dinding belakang chassis (2 sekrup, sumbu Y).
function brk_retainer_pts(zc) =
    [ for(dz=[-14,14]) [-7, zc+dz] ];
// Tray shielding NMC -> dinding belakang chassis (4 sekrup, sumbu Y).
function nmc_tray_pts(zc) =
    [ for(x=[-21,21], dz=[-101,101]) [x, zc+dz] ];
// Boss standoff tray -> main PCB NMC; HARUS identik dengan lubang PCB (4 titik).
function nmc_pcb_pts(zc) =
    [ for(x=[-21,21], dz=[-96,96]) [x, zc+dz] ];
// Stasiun sekrup samping fascia (offset Z relatif tengah komponen, sumbu X,
// insert dinding samping di Y global -20 / lokal 3 dari bidang muka).
function fascia_side_z(zc) = [zc-100, zc+100];
// Bracket terminal block -> top cap (4 sekrup vertikal, sumbu Z).
function terminal_bracket_pts() =
    [ for(x=[-14,14], y=[-9,9]) [x, y] ];
