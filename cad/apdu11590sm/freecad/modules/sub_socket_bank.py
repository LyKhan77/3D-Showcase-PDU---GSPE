# =====================================================================
# sub_socket_bank.py — 1 modul bank (tinggi 68 mm):
# sisi kiri 2 baris pasangan soket (4 soket) di x=-13, z=+-17,
# sisi kanan plat breaker di x=+26.
# Konversi dari sub_socket_bank.scad.
# =====================================================================
from ._common import GSPE_NAVY, GSPE_CREAM
from .sub_socket_4in1 import build_socket_pair
from .sub_breaker_box import build_breaker_plate

ROW_PITCH = 34.0
BANK_H = 68.0
BANK_LEFT_X = -13.0
BANK_BRK_X = 26.0


# Fasa 3-phase bergantian: L1-N, L2-N, L3-N
def get_phase_str(bank_idx):
    return ("L1-N", "L2-N", "L3-N")[(bank_idx - 1) % 3]


def get_plate_col(bank_idx):
    return GSPE_NAVY if bank_idx % 2 == 1 else GSPE_CREAM


def get_text_col(bank_idx):
    return GSPE_CREAM if bank_idx % 2 == 1 else GSPE_NAVY


def build_socket_bank(parts, prefix, bank_num):
    base_outlet = (bank_num - 1) * 4

    # ---- SISI KIRI: baris atas (base+2, base+1) & bawah (base+4, base+3) ----
    build_socket_pair(parts, prefix + "_ROW1",
                      base_outlet + 2, base_outlet + 1,
                      offset=(BANK_LEFT_X, 0, ROW_PITCH / 2))
    build_socket_pair(parts, prefix + "_ROW2",
                      base_outlet + 4, base_outlet + 3,
                      offset=(BANK_LEFT_X, 0, -ROW_PITCH / 2))

    # ---- SISI KANAN: plat breaker ----
    build_breaker_plate(parts, prefix + "_BRK", bank_num,
                        get_phase_str(bank_num),
                        get_plate_col(bank_num), get_text_col(bank_num),
                        offset=(BANK_BRK_X, 0, 0))

    return parts
