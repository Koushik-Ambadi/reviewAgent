# src/repo_review/checks/naming/rules.py

import re
from typing import Any


DEFAULT_RULES = {

    # Function naming
    "function_name_pattern": r"^[A-Z][A-Za-z0-9]*(_[a-z0-9]+)+$",

    "excluded_function_patterns": [
        r"^look\d_",
        r"^plook_",
        r"^intrp",
        r"^binsearch_",
    ],

    # Macro naming
    "macro_name_pattern": r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$",

    "excluded_macro_patterns": [
        r"^{module}_IN_",
    ],

    "macro_value_type": "value",

    # Global naming
    "global_variable_template":
        "{data_type}{data_size}{module}_{unit}_{description}",

    "global_variable_fields": [
        "data_type",
        "data_size",
        "module",
        "unit",
        "description",
    ],

    "global_variable_name_max_length": 31,

    "global_variable_allowed_chars_pattern":
        r"^[A-Za-z0-9_]+$",

    "global_variable_description_pattern":
        r"^[a-z][A-Za-z0-9]*$",

    # Exclusions
    "excluded_global_type_patterns": [
        r"^B_.*_T$",
        r"^DW_.*_T$",
        r"^ConstP_.*_T$",
        r"^rt[A-Z].*$",
        r"^Tmp.*$",
    ],

    # Data types
    "global_variable_data_types": [
        "C",  # CAN signal
        "F",  # Fixed calibration
        "K",  # Calibration
        "N",  # NVM global
        "V",  # RAM global
        "L",  # Local
        "M",  # Struct member
    ],

    # Data sizes
    "global_variable_data_sizes": [
        "e",  # Element
        "a",  # Array
        "m",  # Matrix
        "s",  # Struct
        "t",  # Table
    ],

    # Modules
    "global_variable_modules": [
        "Adcmgr",
        "Atddrv",
        "Atdif",
        "Auxcon",
        "Balctl",
        "Battsm",
        "Calmgr",
        "Canstk",
        "Cantcv",
        "Cellmdl",
        "Cellmnt",
        "Chrg",
        "Conctl",
        "Coul",
        "Crcmgr",
        "Curlmt",
        "Cvtnsm",
        "Dcfc",
        "Dcmmgr",
        "Dchrg",
        "Didmgr",
        "Dtcmgr",
        "Hall",
        "Htrctl",
        "Hwio",
        "Hvil",
        "Inhibt",
        "Limctl",
        "Nmsm",
        "Nvmdrv",
        "Nvmmgr",
        "Ocp",
        "Otemp",
        "Ovuv",
        "Packsm",
        "Pchrg",
        "Pwrmnt",
        "Pyro",
        "Qrcode",
        "Rtcmgr",
        "Shunt",
        "Soc",
        "Soe",
        "Soh",
        "Sohc",
        "Sohr",
        "Sop",
        "Srs",
        "Sysmgr",
        "Syssm",
        "Therm",
        "Tmpmnt",
        "Udsstk",
        "Uepm",
        "VITDgn",
    ],

    # Units
    "global_variable_units": [
        "A",
        "mA",
        "kA",
        "V",
        "mV",
        "kV",
        "Ah",
        "kAh",
        "Wh",
        "kWh",
        "W",
        "kW",
        "degC",
        "degF",
        "us",
        "ms",
        "sec",
        "hrs",
        "day",
        "Hz",
        "kHz",
        "Ohm",
        "bi",
        "frc",
        "nu",
        "pct",
        "cnt",
        "ix",
        "tau",
    ],

    # Validation
    "enforce_module_required": True,
    "enforce_unit_required": True,
    "enforce_description_required": True,

    "case_sensitive_validation": True,
}


def merge_rules(
    rules: dict[str, Any] | None,
) -> dict[str, Any]:

    merged = dict(DEFAULT_RULES)

    if rules:
        merged.update(rules)

    return merged


def is_excluded_function(
    name: str,
    rules: dict[str, Any] | None = None,
) -> bool:

    merged = merge_rules(rules)

    return any(
        re.match(pattern, name)
        for pattern in merged["excluded_function_patterns"]
    )


def is_excluded_macro(
    name: str,
    module_name: str,
    rules: dict[str, Any] | None = None,
) -> bool:

    merged = merge_rules(rules)

    patterns = [
        pattern.format(module=module_name.lower())
        for pattern in merged["excluded_macro_patterns"]
    ]

    return any(
        re.match(pattern, name)
        for pattern in patterns
    )


def is_excluded_global(
    var_type: str,
    rules: dict[str, Any] | None = None,
) -> bool:

    merged = merge_rules(rules)

    return any(
        re.match(pattern, var_type)
        for pattern in merged["excluded_global_type_patterns"]
    )