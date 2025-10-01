from enum import StrEnum


c_default_short_figsize = (6, 1.5)
"""Default short paper figure size"""
c_small_and_wide_figsize = (12*0.7,2*0.7)

class GraphName(StrEnum):
    """StrEnum for three letter graph names.

    Attributes:
        bar: "bar"
        scatter: "sca"
    """

    bar = "bar"
    scatter = "sca"
