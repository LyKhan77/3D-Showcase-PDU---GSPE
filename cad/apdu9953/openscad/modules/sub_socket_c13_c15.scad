// Reference: temp/ss/Screenshot 2026-09-29 at 12.03.49.png.
// Real through slots; top C15 key in front-facing XZ coordinates.
include <detail_common.scad>
EXPLODE_FACTOR = 0.0; // 0.0 = assembled, 1.0 = fully separated
$fn=48;
module socket_octagon(w=26,h=19,chamfer=4) {
    polygon([[-w/2+1,h/2],[w/2-1,h/2],[w/2,h/2-1],[w/2,-h/2+chamfer],
        [w/2-chamfer,-h/2],[-w/2+chamfer,-h/2],[-w/2,-h/2+chamfer],[-w/2,h/2-1]]);
}
module c13_c15_shroud_2d() {
    difference() {
        socket_octagon(23,17,4);
        translate([0,8.2]) square([4.2,3.2],center=true);
        translate([0,6.6]) circle(d=4.2); // circular notch relief
    }
}
module socket_contact_slots(y=-5,depth=24,large=false) {
    for(p=large ? [[-7.5,4],[7.5,4],[0,-5]] : [[-6,2],[6,2],[0,-4.2]])
        translate([p[0],y+depth/2,p[1]]) cube(large ? [6.2,depth,1.9] : [2.2,depth,5.5],center=true);
}
module socket_bezel(large=false) {
    color(COL_POLY) difference() {
        depth_profile(-4.9,3.5) rounded_profile(large ? 42 : 32,large ? 28 : 24,1.8);
        depth_profile(-5,3.8) socket_octagon(large ? 36 : 28,large ? 23 : 20,4);
    }
}
module socket_face(large=false) {
    color("#41454A") difference() {
        // 0.04 mm assembly clearance avoids coincident mating edges in STL.
        depth_profile(-4.25,2.76)
            if(large) difference() {
                socket_octagon(32,19,3.5);
                translate([0,8.8]) circle(d=5);
            } else c13_c15_shroud_2d();
        socket_contact_slots(-4.4,4.8,large);
    }
}
module socket_housing(large=false) {
    w=large ? 38 : 28; h=large ? 24 : 20; d=large ? 18 : 16;
    color("#1D222A") difference() {
        depth_profile(0.2,d) rounded_profile(w,h,1.3);
        depth_profile(0.1,d-2) socket_octagon(w-2,h-2,3);
        socket_contact_slots(0,d+1,large);
    }
    // Recessed moat floor; slots stay open, C15 relief reads as a dark keyway.
    color("#171C23") difference() {
        depth_profile(-1.45,1.85) socket_octagon(large ? 37 : 29,large ? 24 : 21,4);
        socket_contact_slots(-1.5,2.0,large);
    }
    color("#333944") for(x=[-1,1]) translate([x*(w/2+0.5),5,0]) cube([1.4,5,5],center=true);
    // Snap-fit latch arms (top + bottom) clicking into the fascia slots.
    color("#1D222A") for(sz=[-1,1]) hull() {
        translate([0,4.7,sz*(h/2-0.3)]) cube([3.2,1.4,1.0],center=true);
        translate([0,-0.44,sz*(h/2+1.25)]) cube([3.2,1.9,0.9],center=true);
    }
}
module socket_spring_contact() {
    // Folded phosphor-bronze spring cheeks and rear solder tail.
    color(COL_COPPER) {
        for(sx=[-1,1]) hull() {
            translate([sx*1.6,12,0]) cube([0.45,8,5],center=true);
            translate([sx*0.95,5,0]) cube([0.4,1.2,4.5],center=true);
        }
        translate([0,16,0]) cube([3.6,0.6,5],center=true);
        translate([0,20,0]) cube([1.4,8.2,0.7],center=true);
    }
}
module socket_contacts(large=false) {
    for(p=large ? [[-7.5,4],[7.5,4],[0,-5]] : [[-6,2],[6,2],[0,-4.2]])
        translate([p[0],0,p[1]]) rotate([0,large ? 90 : 0,0]) socket_spring_contact();
}
module socket_indicator(large=false) {
    z=large ? 16.2 : 14.2;
    color("#EBF2EE") translate([0,-1.52,z]) scale([1,0.72,1]) sphere(d=2.2);
    color("#080B0F") y_cylinder(0.85,-1.52,0.1,-3.5,z);
}
module socket_modular(large=false,explode_factor=EXPLODE_FACTOR,show_fascia_external=true,show_internals=true) {
    e=explode_checked(explode_factor);
    if(show_fascia_external) translate([0,-42*e,0]) socket_bezel(large);
    if(show_fascia_external) translate([0,-27*e,0]) socket_face(large);
    if(show_fascia_external) translate([0,8*e,0]) socket_housing(large);
    if(show_internals) translate([0,42*e,0]) socket_contacts(large);
    if(show_fascia_external) translate([0,-12*e,0]) socket_indicator(large);
}
module sub_socket_c13_c15(outlet_num=1,explode_factor=EXPLODE_FACTOR,show_number=true,show_fascia_external=true,show_internals=true) {
    socket_modular(false,explode_factor,show_fascia_external,show_internals);
    if(show_number && show_fascia_external) face_print(str(outlet_num),-20,-1.52-12*explode_factor,0,2.8,-90);
}
sub_socket_c13_c15(7);
