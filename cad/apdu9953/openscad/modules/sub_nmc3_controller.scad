// NMC3 reference: references/images/sketchfab_ns9000/annotation_1.png.
// Internals are a visual reconstruction, not a reverse-engineered circuit board.
include <detail_common.scad>
EXPLODE_FACTOR = 0.0; // 0.0 = assembled, 1.0 = fully separated
$fn=48;
module face_text(s,size=2.4,halign="center",bold=true) {
    rotate([90,0,0]) linear_extrude(height=0.1)
        text(s,size=size,font=bold ? "Helvetica:style=Bold" : "Helvetica",halign=halign,valign="center");
}
module face_text_vert(s,size=2.4) { rotate([0,90,0]) face_text(s,size); }
// Measured visual proportions from the live Sketchfab connector close-up.
// Network/Link A/Link B: contacts below, latch above; Universal I/O is inverted.
NMC_PORT_X=12;
NMC_PORT_Z=[10,-18,-46];
module rj45_aperture() {
    union() {
        translate([0,2]) square([13.4,10],center=true);
        translate([0,7.6]) square([6.4,2.0],center=true);
        translate([0,8.8]) square([3.5,1.5],center=true);
    }
}
module rj45_contact_comb() {
    // Source viewer renders the metallic contacts with a pale green reflection.
    color("#8ACB9C") for(i=[0:7]) {
        x=-3.57+i*1.02;
        wire_between([x,-3.05,-2.85],[x,-2.75,-2.35],0.40);
        wire_between([x,-2.75,-2.35],[x,5.4,-1.75],0.40);
        wire_between([x,5.4,-1.75],[x,7.8,-1.75],0.40);
    }
    // Ramp stays below the springs: a rectangular support would hide their middles.
    color("#222B29") hull() {
        translate([0,-2,-3.5]) cube([10.2,0.4,0.4],center=true);
        translate([0,8,-2.3]) cube([10.2,0.4,0.4],center=true);
    }
}
module nmc_rj45(leds=false,inverted=false,light_pipes=true) {
    // Dark, tall front housing; substantial solid skirt BELOW the LAN mouth.
    // Only Universal I/O flips the aperture and contact comb, not the LED lenses.
    flip=inverted ? 180 : 0;
    color("#3E4448") render(convexity=12) difference() {
        hull() {
            depth_profile(-3.95,0.15) rounded_profile(19.2,21.6,0.35);
            depth_profile(-3.25,0.15) rounded_profile(20,22.4,0.6);
        }
        rotate([0,flip,0]) depth_profile(-4.1,1.2) offset(delta=0.18) rj45_aperture();
        if(light_pipes) for(x=[-5.9,5.9])
            translate([x,-3.5,9.05]) cube([3.2,1.5,1.9],center=true);
    }
    // Folded metal shell is darkened; thin precision edges remain visible.
    color("#42494E") render(convexity=12) difference() {
        depth_profile(-3.15,17.4) rounded_profile(19.6,22,0.4);
        depth_profile(-3.3,17.7) rounded_profile(18.5,20.9,0.25);
        for(x=[-9.6,9.6]) translate([x,4,0]) cube([1,3,5],center=true);
    }
    rotate([0,flip,0]) {
        color("#171C20") render(convexity=12) difference() {
            depth_profile(-3.14,17.7) rounded_profile(18.4,20.8,0.3);
            depth_profile(-3.3,15.7) rj45_aperture();
        }
        rj45_contact_comb();
        // Recessed side ledges and latch bearing surfaces, behind the mouth.
        color("#343A3E") for(sx=[-1,1]) {
            translate([sx*6.3,4,0.2]) cube([0.65,11.5,0.65],center=true);
            translate([sx*2.4,1.5,7.8]) cube([0.5,8.0,1.1],center=true);
        }
    }
    color("#525B61") for(sx=[-1,1]) {
        translate([sx*9.1,5.3,-5.2]) rotate([0,0,sx*10]) cube([0.45,4.3,2.4],center=true);
        // Diagonal folded seam at the two lower front corners.
        wire_between([sx*8.3,-3.32,-10.6],[sx*9.6,-2.9,-8.8],0.18);
    }
    if(light_pipes) for(sx=[-1,1]) {
        color("#707B80") translate([sx*5.9,-3.72,9.05]) cube([3.1,0.35,1.8],center=true);
        color("#E2F1EE") translate([sx*5.9,-4.02,9.05]) cube([2.6,0.30,1.35],center=true);
        // Actual green/amber emitters sit behind the white light-pipe lenses.
        if(leds) color(sx<0 ? "#00E676" : "#FFB300")
            translate([sx*5.9,-2.8,9.05]) cube([1.7,0.3,0.9],center=true);
    }
}
module nmc_network_legend() {
    for(i=[0:2]) face_print(["1000","100","10"][i],12+i*3.4,-1.43,-30,
        2.15,-90,i==0 ? "#A8DF4B" : "#E4AC4C");
    color("#AAE845") y_cylinder(2.25,-1.66,0.24,3,-30);
    color("#FFC44D") y_cylinder(2.25,-1.66,0.24,6.7,-30);
    face_print("x",6.7,-1.68,-30,1.35,0,"#434A39");
    color("#435B2F") depth_profile(-1.69,0.06) translate([3,-30])
        polygon([[-0.3,0.75],[0.35,0.75],[0.05,0.05],[0.4,0.05],[-0.3,-0.75],[-0.05,-0.05],[-0.4,-0.05]]);
}
module nmc_usb_a_host() {
    color(COL_METAL) render(convexity=10) difference() {
        depth_profile(-2.5,12.8) rounded_profile(14.4,7.4,0.6);
        depth_profile(-2.6,13.0) rounded_profile(13.2,6.2,0.25);
        for(x=[-4,4]) translate([x,2,3.6]) cube([2,2.7,1],center=true);
    }
    // Folded retention detents along both sides of the shell.
    color(COL_METAL) for(sx=[-1,1]) translate([sx*6.5,0.8,0])
        rotate([0,0,sx*12]) cube([0.45,3,1.6],center=true);
    color(COL_CREAM) translate([0,4,-1.4]) cube([11.7,10,1.2],center=true);
    color(COL_GOLD) for(x=[-3.75,-1.25,1.25,3.75])
        translate([x,2,-0.72]) cube([0.7,5.8,0.18],center=true);
    color(COL_BLACK) translate([0,10.5,0]) cube([13,1,6],center=true);
}
module nmc_usb_micro_b() {
    color(COL_METAL) render(convexity=10) difference() {
        depth_profile(-2.3,6.5) polygon([[-4,1.65],[4,1.65],[4,-0.7],[3,-1.65],[-3,-1.65],[-4,-0.7]]);
        depth_profile(-2.4,6.7) polygon([[-3.45,1.1],[3.45,1.1],[3.45,-0.45],[2.7,-1.1],[-2.7,-1.1],[-3.45,-0.45]]);
    }
    color("#22272D") translate([0,1,-0.4]) cube([5.7,5,0.6],center=true);
    color(COL_GOLD) for(i=[-2:2]) translate([i*0.85,0.6,-0.05]) cube([0.32,3.8,0.16],center=true);
}
module nmc_nav_button() {
    color("#454D57") difference() { y_cylinder(8,-0.1,0.8); y_cylinder(6.9,-0.2,1); }
    color("#BBC1C6") intersection() {
        translate([0,0.35,0]) scale([1,0.52,1]) sphere(d=7);
        translate([0,-1.1,0]) cube([8,2.4,8],center=true);
    }
}
module nmc_faceplate() {
    color("#1E222D") difference() {
        union() {
            depth_profile(-1.4,1.5) rounded_profile(57.4,212,1.8);
            // Wrap-around side flanges screwed to the chassis side-wall inserts.
            for(dir=[-1,1])
                translate([dir*28.75,3.75,0]) cube([1.5,4.5,212],center=true);
        }
        translate([-6,0,63]) depth_profile(-1.5,1.7) rounded_profile(30,32,0.6);
        for(p=[[-NMC_PORT_X,NMC_PORT_Z[0]],[-NMC_PORT_X,NMC_PORT_Z[1]],[-NMC_PORT_X,NMC_PORT_Z[2]],[NMC_PORT_X,NMC_PORT_Z[2]]])
            translate([p[0],0,p[1]]) depth_profile(-1.5,1.7) rounded_profile(19.7,22.1,0.4);
        translate([NMC_PORT_X,-0.65,NMC_PORT_Z[0]]) cube([9,1.7,4.6],center=true);
        translate([NMC_PORT_X,-0.65,NMC_PORT_Z[1]]) cube([14.8,1.7,7.8],center=true);
        for(x=[-11,0,11]) y_cylinder(7.2,-1.5,1.7,x,32);
        y_cylinder(1.4,-1.5,1.7,-3,24);
        // Countersunk seats + clearance for the four side screws (axis X).
        for(dir=[-1,1],z=[-100,100])
            translate([dir>0?29.5+EPS:-29.5-EPS,3,z])
                rotate([0,dir>0?-90:90,0]) {
                    cylinder(d=3.4,h=2.5+2*EPS);
                    cylinder(d1=6.0,d2=3.4,h=1.2);
                }
    }
    face_print("GSPE",0,-1.42,94,6.5,0,COL_CREAM);
    face_print("NETSHELTER 9000 SWITCHED",0,-1.42,87.5,1.8);
    for(p=[[-24,10,"Universal I/O"],[-24,-18,"Link A"],[-24,-46,"Link B"],
           [24,10,"Console"],[24,-18,"USB"],[24,-46,"Network"]])
        face_print(p[2],p[0],-1.42,p[1],2,-90);
    nmc_network_legend();
    face_print("R",-7,-1.42,24,2.1);
    face_print("Main",-11,-1.42,26.4,1.8);
    face_print("v",0,-1.42,26.4,1.8);
    face_print("Select",11,-1.42,26.4,1.8);
    color(COL_NAVY) translate([0,-1.51,-78]) cube([50,0.2,6],center=true);
    face_print("APDU9953 / 230 V 32 A",0,-1.42,-86,2.3,0,COL_CREAM);
    for(i=[0:2]) {
        z=72-i*8;
        color(["#00E676","#FFB300","#E53935"][i]) y_cylinder(2.2,-2,0.6,21.5,z);
        face_print(["Ok","Warning","Overload"][i],15,-1.42,z,1.5);
    }
}
module nmc_display(explode_factor=0) {
    e=explode_factor;
    color("#121A22") difference() {
        translate([-6,-1.45,63]) cube([31,1.2,33],center=true);
        translate([-6,-1.5,63]) cube([28.6,1.4,28.6],center=true);
    }
    color("#0A1721") translate([-6,-0.5,63]) cube([28,0.6,28],center=true);
    color("#00CF69") translate([-6,-0.86,74]) cube([27.7,0.12,4.8],center=true);
    face_print("Phase Info",-6,-0.94,74,2.2,0,COL_NAVY);
    for(i=[0:4]) face_print(["Network","Software Info","SKU/Serial #","Display Settings","Log to Flash"][i],
        -6,-0.94,69.5-i*3.45,1.8,0,COL_CREAM);
    color(COL_CREAM) translate([-6,-0.86,50.9]) cube([27.7,0.12,3.3],center=true);
    face_print("Main    v    Select",-6,-0.94,50.9,1.6,0,COL_NAVY);
    // Thin optical cover floats separately in the exploded stack.
    color([0.70,0.85,0.90,0.16]) translate([-6,-1.25-12*e,63]) cube([28.4,0.16,28.4],center=true);
}
module nmc_shield_enclosure() {
    // Open-front folded sheet-metal tray, 0.8 mm walls; no solid cassette block.
    color(COL_METAL) render(convexity=10) difference() {
        translate([0,24,0]) cube([50,28,208],center=true);
        translate([0,23.1,0]) cube([48.4,28.2,206.4],center=true);
        for(z=[-90:10:-60],x=[-15,0,15]) translate([x,37.7,z]) cube([7,1.4,2],center=true);
    }
    // Threaded standoff bosses bridging tray rear wall -> main PCB; positions
    // are exactly the PCB mounting holes (single source: nmc_pcb_pts).
    color(COL_METAL) for(p=nmc_pcb_pts(0)) difference() {
        y_cylinder(5.5,23.6,13.8,p[0],p[1]);
        y_cylinder(2.2,23.4,14.2,p[0],p[1]);
    }
}
// Rear-wall screws holding the tray to the chassis (single source: nmc_tray_pts).
module nmc_tray_screws() {
    for(p=nmc_tray_pts(0))
        translate([p[0],46.5,p[1]]) rotate([0,0,180])
            torx_screw_csk(head_d=6.0,shaft_d=2.8,length=8);
}
// Main-PCB screws into the tray standoffs (single source: nmc_pcb_pts).
module nmc_pcb_screws() {
    for(p=nmc_pcb_pts(0))
        translate([p[0],21.9,p[1]]) torx_screw(head_d=4.2,shaft_d=2.4,length=9);
}
module nmc_side_screws() {
    for(dir=[-1,1],z=[-100,100]) side_torx_screw(dir=dir,y=3,z=z);
}
module nmc_main_pcb() {
    color(COL_PCB) difference() {
        translate([0,23,0]) cube([46,1.6,200],center=true);
        for(p=nmc_pcb_pts(0)) y_cylinder(2.7,22,2,p[0],p[1]);
    }
    pcb_chip(-6,38,16,16,19.5,4.2); // SoC
    face_print("SoC",-6,17.35,38,2.4,0,COL_CREAM);
    pcb_chip(12,37,7,13,20.8,2.6); // RAM
    face_print("RAM",12,19.45,37,1.5,0,COL_CREAM);
    pcb_chip(11,-70,12,10,19,6); // LAN pulse transformer
    face_print("LAN",11,15.95,-70,1.8,0,COL_CREAM);
    color(COL_METAL) translate([-12,20.5,20]) cube([8,3.2,4],center=true); // crystal
    face_print("25 MHz",-12,18.85,20,1.2);
    color(COL_CREAM) translate([-6,20.5,80]) cube([18,3.2,4.8],center=true); // FPC
    color(COL_GOLD) for(x=[-14:1.2:2]) translate([x,18.8,80]) cube([0.45,0.35,3.6],center=true);
    color("#B47D35") translate([-6,13,81]) cube([15,12,0.25],center=true); // FPC ribbon
    color("#23436A") for(z=[-88,-77,0]) y_cylinder(5,16.5,5.6,-15,z);
    for(z=[-42,-31,-20]) pcb_chip(9,z,5,3,21,1.8);
    face_print("GSPE NMC3",0,22.17,92,2.6,0,COL_CREAM);
}
module sub_nmc3_controller(explode_factor=EXPLODE_FACTOR,show_fascia_external=true,show_internals=true) {
    e=explode_checked(explode_factor);
    if(show_fascia_external) translate([0,-12*e,0]) nmc_faceplate();
    if(show_fascia_external) translate([0,-12*e,0]) nmc_side_screws();
    if(show_fascia_external) translate([0,-26*e,0]) nmc_display(e);
    if(show_fascia_external) for(x=[-11,0,11]) translate([x,-1.4-43*e,32]) nmc_nav_button();
    if(show_fascia_external) translate([0,8*e,0]) {
        translate([-NMC_PORT_X,0,NMC_PORT_Z[0]]) nmc_rj45(inverted=true,light_pipes=false);
        for(z=[NMC_PORT_Z[1],NMC_PORT_Z[2]]) translate([-NMC_PORT_X,0,z]) nmc_rj45();
        translate([NMC_PORT_X,0,NMC_PORT_Z[0]]) nmc_usb_micro_b();
        translate([NMC_PORT_X,0,NMC_PORT_Z[1]]) nmc_usb_a_host();
        translate([NMC_PORT_X,0,NMC_PORT_Z[2]]) nmc_rj45(leds=true);
        color(COL_BLACK) y_cylinder(1.1,0.5,1.8,-3,24); // reset switch behind the pinhole
    }
    if(show_internals) translate([0,55*e,0]) nmc_main_pcb();
    if(show_internals) translate([0,55*e,0]) nmc_pcb_screws();
    if(show_internals) translate([0,105*e,0]) nmc_shield_enclosure();
    if(show_internals) translate([0,105*e,0]) nmc_tray_screws();
}
sub_nmc3_controller();
