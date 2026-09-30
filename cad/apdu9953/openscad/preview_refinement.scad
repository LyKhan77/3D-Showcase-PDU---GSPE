// All close-ups use the actual assembly, preserving adjacent chassis context.
// Select via -D 'PREVIEW_PART="breaker"'; render_refinement.py sets cameras.
use <pdu_apdu9953_assembly.scad>
PREVIEW_PART="breaker";
EXPLODE_FACTOR=0.0;
$fn=48;
if(PREVIEW_PART=="breaker") translate([0,23,-499.5]) pdu_apdu9953_assembly(EXPLODE_FACTOR);
else if(PREVIEW_PART=="sockets") translate([0,23,-669.5]) pdu_apdu9953_assembly(EXPLODE_FACTOR);
else if(PREVIEW_PART=="controller") translate([0,23,-914.5]) pdu_apdu9953_assembly(EXPLODE_FACTOR);
else if(PREVIEW_PART=="ports") translate([0,23,-914.5]) pdu_apdu9953_assembly(EXPLODE_FACTOR);
else if(PREVIEW_PART=="exploded") pdu_apdu9953_assembly(EXPLODE_FACTOR);
// Mounting-audit showcase views: internals with housing and fascia hidden so
// the carrier plates, standoffs, saddles and screw lines are visible.
else if(PREVIEW_PART=="sidefast") translate([0,0,-669.5])
    pdu_apdu9953_assembly(EXPLODE_FACTOR,true,true,true,true,true,"CUSTOM",true,false);
else if(PREVIEW_PART=="intmount") translate([0,0,-669.5])
    pdu_apdu9953_assembly(EXPLODE_FACTOR,false,true,true,false,true,"CUSTOM",true,false);
else if(PREVIEW_PART=="ctrmount") translate([0,0,-914.5])
    pdu_apdu9953_assembly(EXPLODE_FACTOR,false,true,true,false,true,"CUSTOM",true,false);
else if(PREVIEW_PART=="intmountexpl") translate([0,0,-669.5])
    pdu_apdu9953_assembly(EXPLODE_FACTOR,false,true,true,false,true,"CUSTOM",true,false);
else assert(false,"Unknown PREVIEW_PART");
