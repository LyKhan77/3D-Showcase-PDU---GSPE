"""Presentation identities independent of color and geometry implementation."""
LAYERS = {
    "housing": "Chassis housing", "mounting": "Mounting system",
    "power": "Power whip cord", "breakers": "Circuit breakers",
    "outlet_banks": "24-outlet banks", "nmc3": "NMC3 controller",
    "internal": "Internal busbars & PCB",
}
GROUP_LAYERS = dict(zip(
    ("GRP_HOUSING", "GRP_MOUNTING", "GRP_POWER_ENTRY", "GRP_BREAKERS", "GRP_SOCKET_BANKS", "GRP_NMC3_CONTROLLER"),
    ("housing", "mounting", "power", "breakers", "outlet_banks", "nmc3")))
BANK_INTERNAL = {
    "Busbars", "SilkBusbarN", "SilkBusbarPE", "CarrierPlate", "CarrierTorxScrews",
    "BusbarSaddles", "SaddleTorxScrews", "RelayPCB", "PowerRelays", "FilterCapacitors",
    "CapacitorTops", "RelayPins", "RibbonConnector", "RibbonGoldPins", "SilkPCBSW8", "RelayTorxScrews",
    *(f"SilkK{i}" for i in range(1, 9)),
}
NMC_INTERNAL = {
    "ShieldTray", "TrayTorxScrews", "MainPCB", "SoC_Chip", "RAM_Chip", "LAN_Transformer",
    "CrystalOscillator", "FPC_Connector", "FPC_Ribbon", "ElectrolyticCaps", "SilkSoC",
    "SilkRAM", "SilkLAN", "SilkCrystal", "SilkNMC3PCB", "PCBTorxScrews",
}

def classify(part):
    owner = GROUP_LAYERS[part["group"]]
    name = part["name"]
    suffix = name.split("_", 1)[1]
    layer, role = owner, "main"
    if owner == "housing":
        role = "front" if ("FrontCover" in suffix or "BrandingPlate" in suffix or "RatingPlate" in suffix) else "shell"
    if owner == "outlet_banks":
        if suffix in BANK_INTERNAL or suffix.endswith("_SpringClips"):
            layer, role = "internal", "bank"
        elif suffix in {"Fascia", "GuideStripes", "SilkBankLabel", "SideTorxScrews"}:
            role = "front"
        else:
            role = "outlets"
    if owner == "breakers":
        role = "front" if suffix in {"Fascia", "FasciaTorxScrews", "SilkBankLabel", "Guard", "Rocker", "Silk20", "SilkON", "SilkOFF"} else "body"
    if owner == "nmc3":
        if suffix in NMC_INTERNAL:
            layer = "internal"
            role = "nmc3_tray" if suffix in {"ShieldTray", "TrayTorxScrews"} else "nmc3_pcb"
        elif suffix.startswith("Port_"):
            role = "nmc3_" + suffix.split("_")[1].lower()
        elif suffix.startswith("Display"):
            role = "nmc3_display"
        elif suffix.startswith(("Nav", "Reset")):
            role = "nmc3_controls"
        else:
            role = "front"
    return dict(layer=layer, role=role, owner=owner)
