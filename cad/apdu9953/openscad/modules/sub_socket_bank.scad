// Three banks x (7 C13/C15 + 1 C19/C21). Pitch 28.5 mm.
// Mechanical spine per bank: rear carrier plate bolted to the chassis rear
// wall (4x M3), relay PCB on 4 threaded standoffs, busbars through insulator
// saddles on the carrier, fascia wrap-around flanges screwed to side-wall
// inserts (2 per side), socket housings snap-fitted into the fascia.
include <detail_common.scad>
EXPLODE_FACTOR = 0.0; // 0.0 = assembled, 1.0 = fully separated
use <sub_socket_c13_c15.scad>
use <sub_socket_c19_c21.scad>
$fn=36;
function bank_socket_z(i)=i<7 ? 104-i*28.5 : -99;
module bank_fascia(bank_id) {
    color("#1E222D") difference() {
        union() {
            // Plate widened to 57.4 so wrap-around side flanges cover the chassis skin.
            translate([0,-0.65,0]) cube([57.4,1.5,244],center=true);
            for(dir=[-1,1])
                translate([dir*28.75,3.75,0]) cube([1.5,4.5,244],center=true);
        }
        for(i=[0:7]) translate([0,0,bank_socket_z(i)])
            depth_profile(-1.5,1.7) rounded_profile(i==7 ? 40 : 30,i==7 ? 26 : 22,1.4);
        for(i=[0:7]) {
            z=bank_socket_z(i)+(i==7 ? 16.2 : 14.2);
            y_cylinder(1.8,-1.5,1.7,0,z);
            y_cylinder(0.85,-1.5,1.7,-3.5,z);
        }
        // Countersunk seats + clearance for the four side screws (axis X).
        for(dir=[-1,1], z=[-100,100])
            translate([dir>0?29.5+EPS:-29.5-EPS,3,z])
                rotate([0,dir>0?-90:90,0]) {
                    cylinder(d=3.4,h=2.5+2*EPS);
                    cylinder(d1=6.0,d2=3.4,h=1.2);
                }
        for(i=[0:7]) {
            s=bank_socket_z(i);
            edge=i==7 ? 12 : 10;
            translate([0,-0.65,s+edge+0.875]) cube([4,1.5+2*EPS,1.75],center=true);
            translate([0,-0.65,s-edge-0.875]) cube([4,1.5+2*EPS,1.75],center=true);
        }
    }
    // Guide stripes and prints sit on the plate outside the flanges.
    color("#F4F4F2") for(zc=[-48,66]) translate([-25,-1.45,zc]) cube([0.5,0.1,94],center=true);
    color("#F4F4F2") depth_profile(-1.5,0.1)
        translate([-25,115]) polygon([[-1.5,-2],[1.5,-2],[0,1.5]]);
    face_print(str("Bank ",bank_id),-24.5,-1.51,8,2.3,-90);
    for(i=[0:7]) face_print(str((bank_id-1)*8+i+1),i==7 ? -23.3 : -20.5,
        -1.51,bank_socket_z(i),i==7 ? 2.4 : 2.8,-90);
}
module bank_side_screws() {
    for(dir=[-1,1], z=[-100,100]) side_torx_screw(dir=dir,y=3,z=z);
}
module bank_busbars() {
    // Straight neutral and PE rails spanning all eight sockets.
    for(x=[-18,18]) {
        color(COL_COPPER) difference() {
            translate([x,26,2.5]) cube([4,1.8,225],center=true);
            for(i=[0:7]) y_cylinder(1.8,24.9,2.2,x,bank_socket_z(i));
        }
        for(i=[0:7]) color(COL_COPPER)
            translate([x>0 ? 9 : -12,24,bank_socket_z(i)+(x>0 ? -4.2 : 2)])
                cube([x>0 ? 18 : 12,0.8,1.3],center=true);
    }
    face_print("N",-18,24.98,112,2.5,0,COL_CREAM);
    face_print("PE",18,24.98,112,2.3,0,COL_CREAM);
}
// Exactly two continuous neutral/PE rails in the full PDU assembly.
// Standalone banks retain their local rail pair for backwards compatibility.
module pdu_busbars(bank_centers=[1159.5,669.5,329.5]) {
    low=min(bank_centers)-110;
    high=max(bank_centers)+115;
    for(x=[-24,24]) color(COL_COPPER)
        translate([x,26,(low+high)/2]) cube([3,1.8,high-low],center=true);
    for(zc=bank_centers,i=[0:7],side=[-1,1]) color(COL_COPPER)
        translate([side*16,24.9,zc+bank_socket_z(i)+(side>0 ? -4.2 : 2)])
            cube([17,0.8,1.3],center=true);
}
// Rear carrier plate: bolted to the chassis rear wall (4x M3 via
// bank_carrier_pts), front face carries the relay standoffs and the
// busbar saddle bosses. Fixed to the chassis in exploded views.
module bank_carrier_plate() {
    pts_carrier=bank_carrier_pts(0);
    pts_relay=bank_relay_pts(0);
    color("#4A5158") difference() {
        union() {
            translate([0,41,0]) cube([49,2,236],center=true);
            for(p=pts_relay) y_cylinder(5,35.4,4.6,p[0],p[1]);
            for(x=[-24,24]) y_cylinder(5,42,2.2,x,0);
        }
        for(p=pts_carrier) y_cylinder(2.4,39.9,2.2,p[0],p[1]);
        for(p=pts_relay) y_cylinder(2.2,35.3,4.8,p[0],p[1]);
        for(x=[-24,24]) y_cylinder(2.4,39.9,4.6,x,0);
    }
}
module bank_carrier_screws() {
    // M3 countersunk screws, rear insertion along +Y, threading the plate.
    for(p=bank_carrier_pts(0))
        translate([p[0],46.5,p[1]]) rotate([0,0,180])
            torx_screw_csk(head_d=6.0,shaft_d=2.8,length=4);
}
module bank_relay_screws() {
    for(p=bank_relay_pts(0))
        translate([p[0],35.1,p[1]]) torx_screw(head_d=4.2,shaft_d=2.4,length=5);
}
// Nylon insulator saddles clamping the two continuous busbars, each arm
// bolted to the carrier plate (M3 from the cavity side).
module bank_busbar_saddles() {
    for(dir=[-1,1]) {
        x=dir*24;
        color("#E5E0D2") difference() {
            union() {
                translate([dir*24.6,33.5,0]) cube([2.8,13,4],center=true);
                translate([x,26.5,0]) cube([6,4.2,6],center=true);
            }
            translate([x,26,0]) cube([3.4,2.0,7],center=true);
            y_cylinder(3.0,27,13,x,0);
        }
        translate([x,38.6,0]) torx_screw(head_d=5.4,shaft_d=2.8,length=4.5);
    }
}
module bank_relay_board(bank_id=1) {
    pts=bank_relay_pts(0);
    color(COL_PCB) difference() {
        translate([0,36.2,0]) cube([46,1.6,236],center=true);
        for(p=pts) y_cylinder(2.7,35.3,1.8,p[0],p[1]);
    }
    for(i=[0:7]) {
        z=bank_socket_z(i);
        color("#20252C") translate([0,30.5,z]) cube([16,10.2,14],center=true);
        face_print(str("K",i+1),0,25.38,z,2.2,0,COL_CREAM);
        color(COL_METAL) for(x=[-9,9],zz=[-4,4]) translate([x,34.7,z+zz]) cube([2,1.4,1],center=true);
        color("#243F67") y_cylinder(4,28,6,-16,z-6);
        color(COL_METAL) y_cylinder(3.2,27.95,0.15,-16,z-6);
    }
    color("#272C31") translate([10,30.5,116]) cube([18,7,5],center=true);
    color(COL_GOLD) for(x=[3:2:17]) y_cylinder(0.6,26,8,x,116);
    face_print(str("GSPE  SW8 / B",bank_id),0,35.37,-115,1.8,0,COL_CREAM);
}
module sub_socket_bank(bank_id=1,explode_factor=EXPLODE_FACTOR,show_housing=true,
                       show_fascia_external=true,show_internals=true,show_front_cover=true,
                       show_busbars=true) {
    assert(bank_id>=1 && bank_id<=3);
    e=explode_checked(explode_factor);
    if(show_housing && show_front_cover) translate([0,-12*e,0]) bank_fascia(bank_id);
    if(show_housing && show_front_cover) translate([0,-12*e,0]) bank_side_screws();
    for(i=[0:6]) translate([0,0,bank_socket_z(i)]) sub_socket_c13_c15((bank_id-1)*8+i+1,e,false,show_fascia_external,show_internals);
    translate([0,0,bank_socket_z(7)]) sub_socket_c19_c21(bank_id*8,e,false,show_fascia_external,show_internals);
    if(show_internals && show_busbars) translate([0,70*e,0]) bank_busbars();
    if(show_internals) bank_carrier_plate();
    if(show_internals) bank_carrier_screws();
    if(show_internals) bank_busbar_saddles();
    if(show_internals) translate([0,110*e,0]) bank_relay_board(bank_id);
    if(show_internals) translate([0,110*e,0]) bank_relay_screws();
}
sub_socket_bank(2);
