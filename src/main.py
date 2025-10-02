import base64
import gzip
from copy import deepcopy
from collections import defaultdict
from sortedcontainers import SortedList
import xml.etree.ElementTree as XmlElementTree

import video
from gd import *


VIDEO_FILEPATH = '../resources/bad apple.mp4'
TEMPLATE_FILEPATH = '../resources/template.gmd'
OUTPUT_FILEPATH = '../bad apple.gmd'

RES_X = 512
RES_Y = 384
FPS = 10
TONES = 16

SPEED_ADJUSTMENT = 1.08
FPS_REDUCTION = 30 / FPS
FRAME_DURATION = 1 / FPS
FRAME_GAP_X = 2.4 * 4 * FPS_REDUCTION * SPEED_ADJUSTMENT

OPAQUE_CHANNEL = None
BLENDING_CHANNEL = 2
PIXEL_SIZE = 7.5
PIXEL_SCALE = 0.27
PIXEL_SIZE *= PIXEL_SCALE
CANVAS_OFFSET_X = 30 * 200
CANVAS_OFFSET_Y = 30 * 10
ANIM_START_X = 25.6

GID_COUNT = 10000
RESERVED_GID_COUNT = 1
STATIC_CAM_GID = 1

BATCH_CAPACITY = 16000


class LevelBuilder:

    def __init__(self):
        self.level_str_chunks = []
        self.free_groups = SortedList(range(RESERVED_GID_COUNT + 1, GID_COUNT))
        self.claimed_groups = set()

        self.free_move_groups = SortedList()
        self.claimed_move_groups = set()
        self.move_counter = defaultdict(int)

        self.pulse_cid = 1

    def free_all_groups(self):
        self.free_groups.update(self.claimed_groups)
        self.claimed_groups.clear()

        self.free_move_groups.update(self.claimed_move_groups)
        self.claimed_move_groups.clear()

    def commit(self, object : GameObject | list[GameObject]):
        chunk = None
        if isinstance(object, GameObject):
            chunk = object.serialize()
        else:
            chunk = ';'.join(obj.serialize() for obj in object)
        self.level_str_chunks.append(chunk)

    def get_objects_string(self):
        return ';'.join(self.level_str_chunks)
    
    def get_gmd(self):

        level_str = None
        xml_root = XmlElementTree.parse(TEMPLATE_FILEPATH).getroot()
        xml_dict = xml_root.findall('.//dict')[0]
        level_str_node = None
        for i, node in enumerate(xml_dict):
            if node.tag == 'k' and node.text == 'k4':
                level_str_node = xml_dict[i + 1]
                level_str = level_str_node.text.strip()
                break

        level_str = gzip.decompress(base64.urlsafe_b64decode(level_str)).decode()
        level_str = level_str.split(';')[0]
        level_str += ';' + self.get_objects_string()
        level_str = base64.urlsafe_b64encode(gzip.compress(level_str.encode())).decode()

        level_str_node.text = level_str

        return XmlElementTree.tostring(xml_root).decode()
    
    def get_group(self):
        if not self.free_groups:
            raise RuntimeError('ran out of free groups')
        return self.free_groups.pop(0)
    
    def stop_pulses(self, pulses, curr_frame_idx = None):

        for pulse in pulses:
            pulse.pulse_hold_duration = 100 # (curr_frame_idx - pulse.entry_frame_idx) * FRAME_DURATION
            if curr_frame_idx is not None:
                pulse.control_id = self.pulse_cid 
            self.commit(pulse)

        if curr_frame_idx is not None:
            stop = StopTrigger(ANIM_START_X + FRAME_GAP_X * curr_frame_idx, 50)
            stop.target_id = self.pulse_cid
            stop.use_control_id = True
            self.commit(stop)
            self.pulse_cid += 1


level_builder = LevelBuilder()


batch_size = 0
z_layer = 11
pixels = [[None for x in range(RES_X)] for y in range(RES_Y)]

def create_pixel(x, y):

    pixel = GameObject(
        917,
        CANVAS_OFFSET_X + PIXEL_SIZE / 2 + PIXEL_SIZE * x,
        CANVAS_OFFSET_Y + PIXEL_SIZE / 2 + PIXEL_SIZE * y
    )
    
    pixel.dont_fade = True
    pixel.dont_enter = True
    pixel.scale_x = PIXEL_SCALE * 1.05
    pixel.scale_y = pixel.scale_x

    pixel.base_x = pixel.x
    pixel.base_y = pixel.y
    pixel.entry_frame_idx = 0

    return pixel

major_y = 0
while major_y < RES_Y:

    for major_x in range(0, RES_X, 2):

        for minor_x in range(0, 2):
            for minor_y in range(0, 2 if major_y + 1 != RES_Y else 1):

                x = major_x + minor_x
                y = major_y + minor_y

                pixel = create_pixel(x, y)
                pixel.color_channel = BLENDING_CHANNEL if minor_x == minor_y else OPAQUE_CHANNEL
                pixel.z_layer = z_layer

                pixels[y][x] = pixel

    batch_size += RES_X

    if batch_size + RES_X > BATCH_CAPACITY:

        for x in range(0, RES_X):
            pixel = create_pixel(x, major_y)
            pixel.color_channel = OPAQUE_CHANNEL
            pixel.z_layer = z_layer
            pixels[major_y][x] = pixel
        major_y += 1

        batch_size = 0
        z_layer -= 2

    else:

        major_y += 2

pixels = list(reversed(pixels))


static_cam_trigger = StaticCameraTrigger(
    CANVAS_OFFSET_X + PIXEL_SIZE / 2 + PIXEL_SIZE * (RES_X - 1) / 2,
    CANVAS_OFFSET_Y + PIXEL_SIZE / 2 + PIXEL_SIZE * (RES_Y - 1) / 2,
    STATIC_CAM_GID
)
static_cam_trigger.spawn_triggered = True
static_cam_trigger.groups.append(STATIC_CAM_GID)
level_builder.commit(static_cam_trigger)

static_cam_spawn = SpawnTrigger(30, 0, STATIC_CAM_GID)
static_cam_spawn.touch_triggered = True
level_builder.commit(static_cam_spawn)

zoom_trigger = ZoomCameraTrigger(30, 0, 0.4)
level_builder.commit(zoom_trigger)

black_bg_trigger = GameObject(899, 30, 0)
black_bg_trigger.opacity = 1
black_bg_trigger.target_color_channel = 1000
level_builder.commit(black_bg_trigger)


move_offset = 5000
anticheat_move_offset = 150

reset_i = None
reset_chunks = 20
reset_x_ends = [min(round(RES_X / reset_chunks * (i + 1)), RES_X) for i in range(reset_chunks)]
reset_new_gid_i = 0
reset_old_gid_i = 0
reset_new_groups = [level_builder.free_groups.pop(0) for _ in range(TONES * reset_chunks)]
reset_old_groups = sorted(level_builder.free_groups.pop() for _ in range(TONES * reset_chunks * 2))
reset_pulses = []
reset_move_groups = sorted(level_builder.free_groups.pop(0) for _ in range(reset_chunks * 2))
reset_move_gid_i = 0

tone_gid_i = level_builder.free_groups[0]

trigger_x = None

def all_pixels():
    return ((p, (y, x)) for y, r in enumerate(pixels) for x, p in enumerate(r))

for frame_idx, frame in enumerate(video.process_video(VIDEO_FILEPATH, TONES, FPS_REDUCTION)):

    print('generating frame', frame_idx)

    move_offset += anticheat_move_offset

    move_pixels = set()

    if reset_i is None and tone_gid_i + TONES + 1 > max(level_builder.free_groups):

        reset_i = -1

        level_builder.stop_pulses(reset_pulses, frame_idx)
        reset_pulses.clear()

    if reset_i is not None:

        reset_i += 1

        if reset_i == reset_chunks:

            reset_i = None
            level_builder.free_all_groups()
            tone_gid_i = min(level_builder.free_groups)

        else:

            x_start = reset_x_ends[reset_i - 1] if reset_i > 0 else 0
            x_end = reset_x_ends[reset_i]
            move_pixels.update((row[x], (y, x)) for y, row in enumerate(pixels) for x in range(x_start, x_end))

    for (y, x), _ in frame.items() if reset_i != 0 else ((coord, None) for _, coord in all_pixels()):
        pixel = pixels[y][x]
        if len(pixel.groups) == 9:
            move_pixels.add((pixel, (y, x)))

    move_gid = None
    new_pixels = []

    if move_pixels:

        if reset_i is None:
            if level_builder.free_move_groups:
                move_gid = level_builder.free_move_groups.pop(0)
            else:
                move_gid = level_builder.free_groups.pop()
                level_builder.claimed_move_groups.add(move_gid)
        else:
            move_gid = reset_move_groups[reset_move_gid_i]
            reset_move_gid_i += 1
            if reset_move_gid_i == len(reset_move_groups):
                reset_move_gid_i = 0
        level_builder.move_counter[move_gid] += move_offset
        total_move_offset = level_builder.move_counter[move_gid]

        for pixel, (y, x) in move_pixels:

            pixel.groups.append(move_gid)
            pixel.x += total_move_offset - move_offset
            level_builder.commit(pixel)

            pixel = deepcopy(pixel)
            pixels[y][x] = pixel
            pixel.groups = [move_gid]
            pixel.entry_frame_idx = frame_idx
            pixel.x = pixel.base_x + total_move_offset

            new_pixels.append((pixel, (y, x)))

    tone_pixel_map = defaultdict(set)
    changed = [[False for pixel in row] for row in pixels]
    for (y, x), tone in frame.items():
        tone_pixel_map[tone].add((pixels[y][x], (y, x)))
        changed[y][x] = True
    
    for pixel, (y, x) in (new_pixels if reset_i != 0 else all_pixels()):
        if not changed[y][x]:
            tone_pixel_map[pixel.last_tone].add((pixel, (y, x)))

    ##################
    
    tone_gid_map = None
    new_tone_gid_map = {}

    if reset_i is None:

        tones = sorted(set(tone_pixel_map.keys()))
        tone_count = len(tones)

        tone_groups = list(range(tone_gid_i, tone_gid_i + tone_count))
        tone_gid_map = {tones[i]: tone_groups[i] for i in range(len(tones))}

    else:

        tones = list(range(TONES))
        tone_count = len(tones)

        new_tone_groups = []
        for _ in range(tone_count):
            new_tone_groups.append(reset_new_groups[reset_new_gid_i])
            reset_new_gid_i += 1
            if reset_new_gid_i == len(reset_new_groups):
                reset_new_gid_i = 0
        new_tone_gid_map = {tones[i]: new_tone_groups[i] for i in range(len(tones))}

        tone_groups = []
        for _ in range(tone_count):
            tone_groups.append(reset_old_groups[reset_old_gid_i])
            reset_old_gid_i += 1
            if reset_old_gid_i == len(reset_old_groups):
                reset_old_gid_i = 0
        tone_gid_map = {tones[i]: tone_groups[i] for i in range(len(tones))}

    tone_gid_i += tone_count

    ##################

    if reset_i is None:
        for gid in tone_gid_map.values():
            if gid not in level_builder.free_groups:
                raise RuntimeError(f'group not free ({gid})')
            level_builder.free_groups.remove(gid)
            level_builder.claimed_groups.add(gid)

    tone_used = { tone: False for tone in tone_gid_map }
    new_tone_used = { tone: False for tone in new_tone_gid_map }

    for tone, tone_pixels in tone_pixel_map.items():
        for pixel, (y, x) in tone_pixels:
            gid = None
            if reset_i is None or x >= reset_x_ends[reset_i]:
                gid = tone_gid_map[tone]
                tone_used[tone] = True
            else:
                gid = new_tone_gid_map[tone]
                new_tone_used[tone] = True
            pixel.groups.append(gid)
            pixel.last_tone = tone
    
    for tone, used in tone_used.items():
        if not used:
            del tone_gid_map[tone]
    for tone, used in new_tone_used.items():
        if not used:
            del new_tone_gid_map[tone]

    trigger_x = ANIM_START_X + FRAME_GAP_X * frame_idx
    
    if move_gid is not None:
        move = MoveTrigger(trigger_x - 2.4)
        move.target_id = move_gid
        move.offset_x = -move_offset
        level_builder.commit(move)

    for i, (tone, gid) in enumerate(
        list(tone_gid_map.items()) + list(new_tone_gid_map.items())
    ):
        tone = round(tone / (TONES - 1) * 255)
        pulse = PulseTrigger(trigger_x)
        pulse.red = tone
        pulse.green = tone
        pulse.blue = tone
        pulse.target_id = gid
        pulse.pulse_target_type_group = True
        pulse.entry_frame_idx = frame_idx
        reset_pulses.append(pulse)

for row in pixels:
    for pixel in row:
        level_builder.commit(pixel)

level_builder.stop_pulses(reset_pulses)


trigger_x += 30 * 15

stop_song_trigger = GameObject(3605, trigger_x)
stop_song_trigger.hardcoded[406] = 1
stop_song_trigger.hardcoded[417] = 1
level_builder.commit(stop_song_trigger)

end_trigger = GameObject(3600, trigger_x)
level_builder.commit(end_trigger)


gmd = level_builder.get_gmd()
with open(OUTPUT_FILEPATH, 'w') as f:
    f.write(gmd)