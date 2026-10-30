import json
import code.validator as val
import code.cleaner as cl

short_candidates = [
    {
        "raw_asr": "configur the direct memory access channel stream buy loading thirty two data items into the counter register",
        "refined_text": "Configure the direct memory access channel stream by loading 32 data items into the counter register."
    },
    {
        "raw_asr": "uh initializ the watchdog timer reload value buy writing sixteen seconds into the hardware counter register",
        "refined_text": "Initialize the watchdog timer reload value by writing 16 seconds into the hardware counter register."
    },
    {
        "raw_asr": "calibrat the internal ring oscillator buy loading zero x four zero into the clock trim register",
        "refined_text": "Calibrate the internal ring oscillator by loading 0x40 into the clock trim register."
    },
    {
        "raw_asr": "terminat the bus master transfer buy clearing channel bit eight inside the peripheral control register",
        "refined_text": "Terminate the bus master transfer by clearing channel bit 8 inside the peripheral control register."
    }
]

for idx, p in enumerate(short_candidates, 1):
    v_ok, v_msg = val.validate_pair(p)
    c_res, c_msg = cl.clean_sample(p["raw_asr"], p["refined_text"])
    w_count = len(p["refined_text"].split())
    print(f"Short {idx}: words={w_count}, val={v_ok} ({v_msg}), clean={c_msg}")
