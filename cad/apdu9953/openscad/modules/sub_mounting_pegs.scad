// Rear mounting, +Y outward. Origin halfway between peg centers.
// Reference: annotation_8.png / 05_embed_rear.png. Small dimensions inferred.
include <detail_common.scad>
EXPLODE_FACTOR = 0.0;
$fn = 48;
PAD_W = 42;
PAD_H = 42;
PAD_T = 6;
PAD_R = 2.5;
PAD_STEP = 52;
PEG_SPACING = 1680;
PEG_BASE_T = 2.5;
PEG_NECK_H = 17.5;
PEG_HEAD_T = 5;

module bevel_mounting_pad() {
    // R2.5 footprint; inset front face gives a real 0.9 mm perimeter bevel.
    hull() {
        depth_profile(0, PAD_T-0.9) rounded_profile(PAD_W,PAD_H,PAD_R);
        depth_profile(PAD_T-0.91,0.91) rounded_profile(PAD_W-1.8,PAD_H-1.8,PAD_R-0.9);
    }
}
module mounting_pad(primary=true, show_fasteners=true, explode_factor=0) {
    color("#1E222D") difference() {
        bevel_mounting_pad();
        if(primary) {
            // Peg bore plus a 2.58 mm deep flange seat (flange floats at Y 3.45..5.95).
            y_cylinder(6.4,-EPS,PAD_T+2*EPS);
            y_cylinder(16.4,PAD_T-2.58,2.58+EPS);
        }
    }
}
module toolless_peg() {
    // Stack: 3.9 mm pin through the pad bore, flange seated in the counterbore,
    // neck rising above the pad, mushroom head on top. Axis rearward (+Y).
    color(COL_METAL) rotate([-90,0,0]) difference() {
        union() {
            translate([0,0,-3.9]) cylinder(d=6,h=3.9+EPS);
            cylinder(d=16,h=PEG_BASE_T);
            translate([0,0,PEG_BASE_T-EPS]) cylinder(d=6,h=PEG_NECK_H+2*EPS);
            translate([0,0,PEG_BASE_T+PEG_NECK_H]) {
                cylinder(d1=10.6,d2=12,h=0.7);
                translate([0,0,0.7-EPS]) cylinder(d=12,h=PEG_HEAD_T-1.4+2*EPS);
                translate([0,0,PEG_HEAD_T-0.7]) cylinder(d1=12,d2=10.6,h=0.7);
            }
        }
        translate([0,0,PEG_BASE_T+PEG_NECK_H+PEG_HEAD_T-1.7])
            linear_extrude(height=1.7+EPS) torx_t15_profile();
    }
}
module ground_stud(explode_factor=0) {
    // M5 brass stud, washer and 8 mm AF hex nut, axis rearward.
    color(COL_GOLD) rotate([-90,0,0]) {
        cylinder(d=5,h=13);
        for(z=[1:0.8:12]) translate([0,0,z]) cylinder(d1=5.3,d2=5,h=0.35);
        translate([0,0,1+8*explode_factor]) difference() {
            cylinder(d=12,h=1.2);
            translate([0,0,-EPS]) cylinder(d=5.4,h=1.2+2*EPS);
        }
        translate([0,0,2.6+16*explode_factor]) difference() {
            cylinder(d=8/cos(30),h=4,$fn=6);
            translate([0,0,-EPS]) cylinder(d=5.4,h=4+2*EPS);
        }
    }
}
module ground_symbol() {
    color(COL_GOLD) depth_profile(-EPS,0.35+EPS) union() {
        translate([0,2]) square([0.8,5],center=true);
        for(i=[0:2]) translate([0,-i*2]) square([8-i*2,0.8],center=true);
    }
}
module sub_mounting_pegs(spacing=PEG_SPACING, explode_factor=EXPLODE_FACTOR,
                         show_mounting=true, show_pads=true, show_pegs=true,
                         show_ground=true, ground_z=-764.5) {
    e=explode_checked(explode_factor);
    if(show_mounting) {
        for(z=[-spacing/2,spacing/2]) translate([0,200*e,z]) {
            if(show_pads) translate([0,35*e,0]) {
                mounting_pad(explode_factor=e);
                translate([0,0,-PAD_STEP]) mounting_pad(primary=false);
            }
            if(show_pegs) translate([0,PAD_T-2.55+85*e,0]) toolless_peg();
        }
        if(show_ground) translate([0,200*e,ground_z]) {
            translate([10,25*e,0]) ground_stud(e);
            translate([-11,0,0]) ground_symbol();
        }
    }
}
sub_mounting_pegs();
