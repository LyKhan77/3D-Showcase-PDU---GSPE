// C19/C21: separable bezel, housing and three spring contacts.
include <detail_common.scad>
EXPLODE_FACTOR = 0.0; // 0.0 = assembled, 1.0 = fully separated
use <sub_socket_c13_c15.scad>
module sub_socket_c19_c21(outlet_num=8,explode_factor=EXPLODE_FACTOR,show_number=true,show_fascia_external=true,show_internals=true) {
    socket_modular(true,explode_factor,show_fascia_external,show_internals);
    if(show_number && show_fascia_external) face_print(str(outlet_num),-23.5,-1.52-12*explode_factor,0,2.6,-90);
}
sub_socket_c19_c21(8);
