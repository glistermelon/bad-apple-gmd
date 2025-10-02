from copy import deepcopy

class GameObject:

    def __init__(self, id : int, x : float = None, y : float = None):
        self.id = id
        self.x = x
        self.y = y
        self.red = None
        self.green = None
        self.blue = None
        self.duration = None
        self.touch_triggered = False
        self.color_channel = None
        self.target_color_channel = None
        self.z_layer = None
        self.offset_x = None
        self.offset_y = None
        self.easing = None
        self.scale = None
        self.opacity = None
        self.primary_hsv_enabled = None
        self.primary_hsv = None
        self.secondary_hsv = None
        self.pulse_fade_in = None
        self.pulse_hold_duration = None
        self.pulse_fade_out = None
        self.target_id = None
        self.pulse_target_type_group = False
        self.activate_group = False
        self.groups = []
        self.spawn_triggered = False
        self.dont_fade = False
        self.dont_enter = False
        self.secondary_gid = None
        self.exclusive = False
        self.scale_x = None
        self.scale_y = None
        self.hide = False
        self.disable_legacy_hsv = None
        self.zoom_factor = None
        self.control_id = None
        self.use_control_id = False

        self.hardcoded = {}

    def serialize(self):

        if len(self.groups) > 10:
            raise RuntimeError('object had more than 10 groups')
        
        # if self.groups != sorted(self.groups):
        #     print(f'warning: object has unsorted groups: {self.groups}')

        self.groups = sorted(self.groups)

        data = deepcopy(self.hardcoded)
        if self.id:
            data[1] = self.id
        if self.x:
            data[2] = self.x
        if self.y:
            data[3] = self.y
        if self.red is not None:
            data[7] = self.red
        if self.green is not None:
            data[8] = self.green
        if self.blue is not None:
            data[9] = self.blue
        if self.duration is not None:
            data[10] = self.duration
        if self.touch_triggered:
            data[11] = self.touch_triggered
        if self.color_channel is not None:
            data[21] = self.color_channel
        if self.target_color_channel is not None:
            data[23] = self.target_color_channel
        if self.z_layer is not None:
            data[24] = self.z_layer
        if self.offset_x is not None:
            data[28] = self.offset_x
        if self.offset_y is not None:
            data[29] = self.offset_y
        if self.easing is not None:
            data[30] = self.easing
        if self.scale is not None:
            data[32] = self.scale
        if self.opacity is not None:
            data[35] = self.opacity
        if self.primary_hsv_enabled:
            data[41] = 1
        if self.primary_hsv is not None:
            data[43] = self.primary_hsv
        if self.secondary_hsv is not None:
            data[44] = self.secondary_hsv
        if self.pulse_fade_in is not None:
            data[45] = self.pulse_fade_in
        if self.pulse_hold_duration is not None:
            data[46] = self.pulse_hold_duration
        if self.pulse_fade_out is not None:
            data[47] = self.pulse_fade_out
        if self.target_id is not None:
            data[51] = self.target_id
        if self.pulse_target_type_group:
            data[52] = 1
        if self.activate_group:
            data[56] = 1
        if self.groups:
            data[57] = '.'.join(str(g) for g in self.groups)
        if self.spawn_triggered:
            data[62] = 1
        if self.dont_fade:
            data[64] = 1
        if self.dont_enter:
            data[67] = 1
        if self.secondary_gid is not None:
            data[71] = self.secondary_gid
        if self.exclusive:
            data[86] = 1
        if self.scale_x is not None:
            data[128] = self.scale_x
        if self.scale_y is not None:
            data[129] = self.scale_y
        if self.hide:
            data[135] = 1
        if self.disable_legacy_hsv:
            data[210] = 1
        if self.zoom_factor is not None:
            data[371] = self.zoom_factor
        if self.control_id is not None:
            data[534] = self.control_id
        if self.use_control_id:
            data[535] = 1
        
        return ','.join(f'{k},{v}' for k, v in data.items())

class PulseTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None):
        super().__init__(1006, x, y)
        self.disable_legacy_hsv = True

class AlphaTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None, opacity = None):
        super().__init__(1007, x, y)
        self.opacity = opacity

class SpawnTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None, gid = None):
        super().__init__(1268, x, y)
        self.target_id = gid

class ToggleTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None, gid = None, activate_group = False):
        super().__init__(1268, x, y)
        self.target_id = gid
        self.activate_group = activate_group

class StopTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None):
        super().__init__(1616, x, y)

class ZoomCameraTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None, zoom_factor = None):
        super().__init__(1913, x, y)
        self.zoom_factor = zoom_factor

class StaticCameraTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None, center_gid = None):
        super().__init__(1914, x, y)
        self.secondary_gid = center_gid

class MoveTrigger(GameObject):
    def __init__(self, x : float = None, y : float = None):
        super().__init__(901, x, y)