from enum import Enum


class WrapMode(Enum):
    SKIP: str = "SKIP"  # Ignore files smaller than split_width (around 5 seconds)
    FILL: str = "FILL"  # Fill the empty space with white (nothing)
    REPEAT: str = "REPEAT"  # Repeat the clip to the correct pixel count
