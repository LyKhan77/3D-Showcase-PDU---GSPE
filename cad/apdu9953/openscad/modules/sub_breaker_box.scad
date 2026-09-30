// Reference: temp/ss/Screenshot 2026-09-29 at 12.01.00.png.
// Envelope 48 x 70; guard reaches -12; bakelite body extends +35.
include <detail_common.scad>
EXPLODE_FACTOR = 0.0; // 0.0 = assembled, 1.0 = fully separated
$fn=48;
module breaker_fascia() {
    color(COL_BLACK) difference() {
        depth_profile(-2.8,2.8) rounded_profile(48,70,1.5);
        translate([-7,0,0]) depth_profile(-3,3.2) rounded_profile(22,38,1.5);
        for(x=[-19,19],z=[-28.5,28.5]) {
            y_cylinder(3.1,-3,3.3,x,z);
            y_cylinder(6,-2.82,1.55,x,z);
        }
    }
}
module breaker_guard() {
    color("#292D32") {
        for(x=[-18,4]) hull() {
            translate([x,-4.1,0]) cube([2.8,2.6,38],center=true);
            for(z=[-15,15]) translate([x-1.4,-8,z]) rotate([0,90,0]) cylinder(r=4,h=2.8);
        }
        for(z=[-18,18]) translate([-7,-4.2,z]) cube([23,2.8,2],center=true);
    }
}
module breaker_rocker_solid() {
    // Cylindrical face and concave finger scoop, with a separate lower flat step.
    color("#373B40") union() {
        difference() {
            intersection() {
                translate([-7,9.5,1]) rotate([0,90,0]) cylinder(r=19,h=17,center=true,$fn=144);
                translate([-7,-4.5,1]) cube([17,12,30],center=true);
            }
            translate([-7,-20,7]) rotate([0,90,0]) cylinder(r=13,h=18,center=true,$fn=144);
        }
        translate([-7,-6,-12]) cube([17,7,5],center=true);
    }
}
module breaker_rocker() {
    breaker_rocker_solid();
    face_print("20",-7,-9.51,-12,3.2);
    // Conformal ink follows the cylindrical finger scoop, without buried letters.
    color("#F4F4F2") render(convexity=10) intersection() {
        difference() {
            translate([0,-0.10,0]) breaker_rocker_solid();
            translate([0,0.02,0]) breaker_rocker_solid();
        }
        depth_profile(-12,10) translate([-7,0]) {
            translate([0,2]) text("ON",size=1.6,font="Helvetica:style=Bold",halign="center",valign="center");
            translate([0,10]) text("OFF",size=1.45,font="Helvetica:style=Bold",halign="center",valign="center");
        }
    }
}
module breaker_bakelite_body() {
    // Body extended rearward (Y 0.2..37) to seat against the retainer plate.
    color("#111419") difference() {
        translate([-7,18.6,0]) cube([20,36.8,35],center=true);
        for(z=[-10,10]) translate([-7,35.4,z]) cube([9.5,4.5,9.5],center=true);
    }
    color("#111419") translate([-7,0.5,0]) cube([22,1,38],center=true);
    color("#30343B") for(y=[6,15,24]) translate([-7,y,0]) cube([20.6,0.8,34],center=true);
}
// Rear retainer plate clamping the breaker body, screwed to the chassis
// rear wall (single source: brk_retainer_pts). Travels with the body.
module breaker_retainer_plate() {
    color("#3A4149") difference() {
        translate([-7,38,0]) cube([22,2,38],center=true);
        for(z=[-10,10]) translate([-7,38,z]) cube([9.5,2.6,9.5],center=true);
    }
}
module breaker_retainer_screws() {
    for(p=brk_retainer_pts(0))
        translate([p[0],46.5,p[1]]) rotate([0,0,180])
            torx_screw_csk(head_d=6.0,shaft_d=2.8,length=7);
}
module breaker_terminal_lug(z=10) {
    color(COL_COPPER) difference() {
        translate([-7,36.3,z]) cube([8,3,7],center=true);
        y_cylinder(2.8,34.5,4,-7,z);
    }
    // Vertical clamp screw pressing the conductor into the lug bore.
    translate([-7,36.3,13.5]) rotate([-90,0,0]) torx_screw(4.5,2.4,3);
}
module sub_breaker_box(bank_label="Bank 1",explode_factor=EXPLODE_FACTOR,
                       show_housing=true,show_fascia_external=true,show_internals=true,show_front_cover=true) {
    e=explode_checked(explode_factor);
    if(show_housing && show_front_cover) translate([0,-12*e,0]) {
        breaker_fascia();
        face_print(bank_label,16.8,-2.81,0,4.5,-90,COL_CREAM);
    }
    if(show_fascia_external) translate([0,-24*e,0]) breaker_guard();
    if(show_fascia_external) translate([0,-43*e,0]) breaker_rocker();
    if(show_housing && show_front_cover) for(x=[-19,19],z=[-28.5,28.5]) translate([x,-2.6-65*e,z]) torx_screw();
    if(show_internals) translate([0,15*e,0]) {
        breaker_bakelite_body();
        breaker_retainer_plate();
        breaker_retainer_screws();
    }
    if(show_internals) for(z=[-10,10]) translate([0,60*e,0]) breaker_terminal_lug(z);
}
sub_breaker_box("Bank 2");
