// EIA-310 Standard Dimensions (in millimeters)
// Reference standard for 19-inch Server Racks and Components

U_HEIGHT = 44.45;              // 1U = 1.75 inches
RACK_PANEL_WIDTH = 482.6;       // 19.0 inches
RACK_MOUNTING_PITCH = 465.1;    // Distance between rail hole centers
RACK_INTERNAL_CLEARANCE = 450.0;// Clearance between vertical rails

// EIA-310 vertical hole spacing within each 1U:
// Jarak dari batas bawah 1U ke titik pusat lubang:
// Hole 1: 6.35 mm (1/4 inch) dari tepi bawah U
// Hole 2: 6.35 + 15.875 = 22.225 mm (tengah U)
// Hole 3: 22.225 + 15.875 = 38.10 mm
// Sisa ke tepi atas: 44.45 - 38.10 = 6.35 mm
HOLE_OFFSET_1 = 6.35;
HOLE_OFFSET_2 = 22.225;
HOLE_OFFSET_3 = 38.10;

// Ukuran Lubang Standar
CAGE_NUT_HOLE = 9.5;           // 9.5mm x 9.5mm square cage nut hole
ROUND_HOLE_DIA = 6.0;          // Standard round mounting hole diameter (M6 clear)

// Fungsi helper untuk menghitung tinggi dari jumlah U
function u_to_mm(u) = u * U_HEIGHT;
