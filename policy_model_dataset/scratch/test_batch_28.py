import sys
sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def test_pair(idx, raw, ref):
    c_res, c_msg = clean_sample(raw, ref)
    v_res, v_msg = validate_pair({"raw_asr": raw, "refined_text": ref})
    words = len(ref.split())
    print(f"Sample {idx} (words={words}): cleaner={c_msg}, validator={v_msg}")
    if not c_res or not v_res:
        print(f"  FAILED: cleaner={c_msg}, validator={v_msg}")
        return False
    return True

if __name__ == "__main__":
    raw8 = "okay so create the telemetry worker task on the e s p thirty two buy calling x task create pinned to core allocat a stack depth of four zero nine six bytes and assign priority two wait priority three to the task handle pinning the worker to core one prevents context switching delays during continuous sensor polling under free are toss"
    ref8 = "Create the telemetry worker task on the ESP32 by calling `xTaskCreatePinnedToCore`. Allocate a stack depth of 4096 bytes and assign priority 3 to the task handle.\n\nPinning the worker to Core 1 prevents context switching delays during continuous sensor polling under FreeRTOS."
    test_pair(8, raw8, ref8)
