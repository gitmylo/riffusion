from enum import Enum


class WrapMode(Enum):
    SKIP = "SKIP"  # Ignore files smaller than split_width (around 5 seconds)
    FILL = "FILL"  # Fill the empty space with white (nothing)
    REPEAT = "REPEAT"  # Repeat the clip to the correct pixel count
