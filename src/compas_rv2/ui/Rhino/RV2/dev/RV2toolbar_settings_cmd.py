from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rv2.rhino import get_scene

import RV2settings_cmd


__commandname__ = "RV2toolbar_settings"


def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    RV2settings_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
