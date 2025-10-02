import cv2
import numpy as np
import pickle
import os
from collections import defaultdict

CACHE_DIR = 'cache'

def evaluate_tones(frame, tones):
    tone = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    step = 256 // tones
    quantized = tone // step
    quantized = np.clip(quantized, 0, tones - 1).astype(np.uint8)
    return quantized

def process_video(input_filepath, levels, fps_reduction):

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)
    cache_filepath = f'{CACHE_DIR}/{levels}.dat'
    frame_cache, change_cache = {}, {}
    if os.path.exists(cache_filepath):
        frame_cache, change_cache = pickle.load(open(cache_filepath, 'rb'))
    cache_updated = False

    cap = cv2.VideoCapture(input_filepath)
    if not cap.isOpened():
        print(f'failed to open input video at \'{input_filepath}\'')
        return

    i = -1
    prev_frame = None

    while True:
        
        success, frame = cap.read()
        if not success:
            break

        i += 1

        if cache_updated and i % 100 == 0:
            pickle.dump((frame_cache, change_cache), open(cache_filepath, 'wb'))

        i_step = max(1, round(fps_reduction))

        if i % i_step == 0:

            if i in frame_cache:
                frame = frame_cache[i]
            else:
                frame = evaluate_tones(frame, levels)

                frame_cache[i] = frame
                cache_updated = True

            changes = None
            if i in change_cache:
                changes = change_cache[i]
            else:
                changed = None
                if prev_frame is None:
                    changed = tuple(
                        (int(y), int(x))
                        for y in range(frame.shape[0])
                        for x in range(frame.shape[1])
                    )
                else:
                    changed = tuple(
                        (int(y), int(x))
                        for y, x in np.argwhere(frame != prev_frame)
                    )
                
                changes = {
                    (y, x): int(frame[y, x])
                    for y, x in changed
                }

                change_cache[i] = changes
                cache_updated = True
            
            yield changes

            prev_frame = frame