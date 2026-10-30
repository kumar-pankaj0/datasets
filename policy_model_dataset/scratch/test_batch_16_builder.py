import json
import os
import sys

sys.path.append("scratch")
from test_batch import test_samples, validate_pair, validate_batch, clean_sample

samples = [
    # Tier 1: Short (< 25 words) - Sample 1
    # Chip: STM32, Topic: Watchdog timer (WDT) windowed reset sequencing
    {
        "raw_asr": "right zero x three f wait right zero x seven f to the s t m thirty two windowed watchdog timer configur register buy updating the counter window bits",
        "refined_text": "Write 0x7F to the `STM32` windowed watchdog timer configuration register by updating the counter window bits."
    },
    # Tier 1: Short (< 25 words) - Sample 2
    # Chip: RP2040, Topic: I3C dynamic address assignment
    {
        "raw_asr": "set the r p twenty forty i three c dynamic address table register to sixteen wait set it to thirty two buy writing the secondary target slot",
        "refined_text": "Set the `RP2040` `I3C` dynamic address table register to 32 by writing the secondary target slot."
    },
    # Tier 2: Medium (25-90 words) - Sample 3
    # Chip: ESP32, Topic: DMA circular buffer overruns in audio codecs
    {
        "raw_asr": "basically the e s p thirty two i two s audio codec controller suffered d m a circular buffer overruns during forty eight kilohertz stereo stream transmiss because the ring buffer depth was insufficient set the descriptor count to two wait right four to the d m a descriptor ring length register buy reloading the circular buffer linked list configur",
        "refined_text": "The `ESP32` `I2S` audio codec controller suffered `DMA` circular buffer overruns during 48 kilohertz stereo stream transmission because the ring buffer depth was insufficient.\n\nWrite 4 to the `DMA` descriptor ring length register by reloading the circular buffer linked list configuration."
    },
    # Tier 2: Medium (25-90 words) - Sample 4
    # Chip: nRF52, Topic: BLE bonding and GATT attribute database persistence
    {
        "raw_asr": "the n r f fifty two b l e stack dropped bonding credentials and failed g a t t attribute database persistence during peer reconnection because the flash table hash mismatched the cached attributes write zero x zero zero wait right zero x zero one to the flash persistence register buy updating the database synchronizat flag",
        "refined_text": "The `nRF52` `BLE` stack dropped bonding credentials and failed `GATT` attribute database persistence during peer reconnection because the flash table hash mismatched the cached attributes.\n\nWrite 0x01 to the flash persistence register by updating the database synchronization flag."
    },
    # Tier 2: Medium (25-90 words) - Sample 5
    # Chip: RISC-V, Topic: CAN-FD bitrate switching and transceiver delay compensation
    {
        "raw_asr": "the r i s c v c a n f d controller generated bit stuffing errors during high speed bitrate switching because the transceiver delay compensation offset was misaligned buy sixteen nanoseconds write sixteen wait right thirty two to the transceiver delay compensation offset register buy calibrat the secondary sample point",
        "refined_text": "The `RISC-V` `CAN-FD` controller generated bit stuffing errors during high-speed bitrate switching because the transceiver delay compensation offset was misaligned by 16 nanoseconds.\n\nWrite 32 to the transceiver delay compensation offset register by calibrating the secondary sample point."
    },
    # Tier 3: Long (90+ words) - Sample 6
    # Chip: STM32, Topic: DMA circular buffer overruns in audio codecs
    {
        "raw_asr": "basically the s t m thirty two audio codec subsystem suffered direct memory access circular buffer overruns during ninety six kilohertz twenty four bit stereo stream transmiss because the d m a transfer complete interrupt latency exceeded the half transfer callback execution window the audio pipeline streamed pulse code modulation samples from internal static r a m into the external d a c via the i two s peripheral logic analyzer captures and oscilloscope probes showed that high interrupt contention on the n v i c delayed core zero from swapping buffer pointers which caused the d m a controller two overwrite pending audio frames after thirty two wait after sixty four samples um register inspection through the hardware debugger confirmed that the circular buffer was configured with only two buffers of one hundred twenty eight bytes each while the d m a fifo threshold remained set at four words core zero flagged an underrun error interrupt when the codec output dropped below audible thresholds during heavy flash access we resolved the audio buffer overruns buy increasing the circular buffer depth two four ping pong buffers of two hundred fifty six bytes each and raising the d m a stream interrupt priority in the n v i c we also updated the i two s control configur register buy enabling circular double buffer mode and adjusting the d m a request burst size two eight beats which eliminated audio stuttering across sustained playback",
        "refined_text": "The `STM32` audio codec subsystem suffered direct memory access circular buffer overruns during 96 kilohertz 24-bit stereo stream transmission because the `DMA` transfer complete interrupt latency exceeded the half-transfer callback execution window. The audio pipeline streamed pulse code modulation samples from internal static `RAM` into the external `DAC` via the `I2S` peripheral. Logic analyzer captures and oscilloscope probes showed that high interrupt contention on the `NVIC` delayed core 0 from swapping buffer pointers, which caused the `DMA` controller to overwrite pending audio frames after 64 samples.\n\nRegister inspection through the hardware debugger confirmed that the circular buffer was configured with only 2 buffers of 128 bytes each, while the `DMA` `FIFO` threshold remained set at 4 words. Core 0 flagged an underrun error interrupt when the codec output dropped below audible thresholds during heavy flash access.\n\nWe resolved the audio buffer overruns by increasing the circular buffer depth to 4 ping-pong buffers of 256 bytes each and raising the `DMA` stream interrupt priority in the `NVIC`. We also updated the `I2S` control configuration register by enabling circular double-buffer mode and adjusting the `DMA` request burst size to 8 beats, which eliminated audio stuttering across sustained playback."
    },
    # Tier 3: Long (90+ words) - Sample 7
    # Chip: nRF52, Topic: BLE bonding and GATT attribute database persistence
    {
        "raw_asr": "the n r f fifty two peripheral controller failed b l e bonding and g a t t attribute database persistence across system reset cycles because flash page compaction corrupted the security key store during concurrent radio events the device stored bonded peer identity keys and g a t t service change hashes inside a dedicated four kilobyte non volatile flash sector wi re shark packet sniffing and logic analyzer captures revealed that the peripheral asserted an attribute database out of sync error when bonded central devices reconnected after eight wait after sixteen connection attempts um flash memory inspection with a j link debugger showed that the bond manager table header was overwritten buy garbage bytes during an unaligned sector write while the radio high priority interrupt interrupted flash page erasure core zero panicked with an invalid memory handle error when the security manager failed two retrieve the long term key for the connected peer we resolved the g a t t persistence failure buy allocating two hundred fifty six bytes of dedicated swap memory for attribute table caching and moving flash compaction into a low priority background worker thread we also updated the flash memory control configur register buy enabling flash write protection during active radio connection events and writing zero x zero four to the bond manager status register which restored reliable peer key persistence across power cycles",
        "refined_text": "The `nRF52` peripheral controller failed `BLE` bonding and `GATT` attribute database persistence across system reset cycles because flash page compaction corrupted the security key store during concurrent radio events. The device stored bonded peer identity keys and `GATT` service change hashes inside a dedicated 4-kilobyte non-volatile flash sector. `Wireshark` packet sniffing and logic analyzer captures revealed that the peripheral asserted an attribute database out-of-sync error when bonded central devices reconnected after 16 connection attempts.\n\nFlash memory inspection with a J-Link debugger showed that the bond manager table header was overwritten by garbage bytes during an unaligned sector write while the radio high-priority interrupt interrupted flash page erasure. Core 0 panicked with an invalid memory handle error when the security manager failed to retrieve the long-term key for the connected peer.\n\nWe resolved the `GATT` persistence failure by allocating 256 bytes of dedicated swap memory for attribute table caching and moving flash compaction into a low-priority background worker thread. We also updated the flash memory control configuration register by enabling flash write protection during active radio connection events and writing 0x04 to the bond manager status register, which restored reliable peer key persistence across power cycles."
    },
    # Tier 3: Long (90+ words) - Sample 8
    # Chip: RISC-V, Topic: CAN-FD bitrate switching and transceiver delay compensation
    {
        "raw_asr": "basically the r i s c v c a n f d network controller generated bit error interrupts and protocol exceptions during data phase bitrate switching because the transceiver delay compensation mechanism failed two measure loop delay correctly on the physical bus the controller communicated across a dual speed bus using one megabit per second nominal arbitrat and switching to two megabits wait switching to five megabits per second during payload transmiss logic analyzer traces and differential bus probing revealed that transceiver propagation delay created a sixty four nanosecond phase shift which caused the secondary sample point two fall outside the data bit time window after thirty two consecutive frames um register inspection through openocd confirmed that the transceiver delay compensation offset register was set to zero which disabled automatic loop delay measurement and forced the receiver two sample bits before the signal edge stabilized core zero triggered a bus off condition after the transmit error counter exceeded one hundred twenty eight we corrected the bitrate switching failure buy writing zero x ten to the transceiver delay compensation configur register and programming thirty two to the secondary sample point offset register we also updated the c a n f d timing register buy extending the data phase time segment two buy sixteen clock cycles which restored zero error frame transmiss across the automotive harness",
        "refined_text": "The `RISC-V` `CAN-FD` network controller generated bit error interrupts and protocol exceptions during data phase bitrate switching because the transceiver delay compensation mechanism failed to measure loop delay correctly on the physical bus. The controller communicated across a dual-speed bus using 1 megabit per second nominal arbitration and switching to 5 megabits per second during payload transmission. Logic analyzer traces and differential bus probing revealed that transceiver propagation delay created a 64-nanosecond phase shift, which caused the secondary sample point to fall outside the data bit time window after 32 consecutive frames.\n\nRegister inspection through OpenOCD confirmed that the transceiver delay compensation offset register was set to 0, which disabled automatic loop delay measurement and forced the receiver to sample bits before the signal edge stabilized. Core 0 triggered a bus-off condition after the transmit error counter exceeded 128.\n\nWe corrected the bitrate switching failure by writing 0x10 to the transceiver delay compensation configuration register and programming 32 to the secondary sample point offset register. We also updated the `CAN-FD` timing register by extending the data phase time segment 2 by 16 clock cycles, which restored zero-error frame transmission across the automotive harness."
    },
    # Tier 3: Long (90+ words) - Sample 9
    # Chip: RP2040, Topic: Watchdog timer (WDT) windowed reset sequencing
    {
        "raw_asr": "basically the r p twenty forty microcontroller suffered unexpected system resets during inter core f i f o communicat because core one serviced the windowed watchdog timer before the closed window interval expired the system firmware configured a windowed w d t with a lower threshold of ten milliseconds wait lower threshold of twenty milliseconds and an upper timeout of one hundred milliseconds logic analyzer captures and trace buffer logs showed that core zero offloaded mathematical tasks to core one over the inter core f i f o while core one refreshed the watchdog register at fifteen milliseconds which triggered an immediate early kick hardware reset fault um register inspection with segger j link showed that the w d t window comparison register retained the strict twenty millisecond lower threshold while the task scheduler executed with varying execution jitter core zero encountered three consecutive reset loops before the inter core handshake completed we fixed the early watchdog reset buy rewriting the windowed w d t service sequence to verify the elapsed tick counter before writing the reload keyword and setting the lower window threshold to eight milliseconds instead of twenty milliseconds we also updated the watchdog control configur register buy enabling pause on debugger halt and configuring the reset delay cycle counter two thirty two clock cycles which eliminated spurious resets during active flash programming",
        "refined_text": "The `RP2040` microcontroller suffered unexpected system resets during inter-core `FIFO` communication because core 1 serviced the windowed watchdog timer before the closed window interval expired. The system firmware configured a windowed `WDT` with a lower threshold of 20 milliseconds and an upper timeout of 100 milliseconds. Logic analyzer captures and trace buffer logs showed that core 0 offloaded mathematical tasks to core 1 over the inter-core `FIFO`, while core 1 refreshed the watchdog register at 15 milliseconds, which triggered an immediate early-kick hardware reset fault.\n\nRegister inspection with SEGGER J-Link showed that the `WDT` window comparison register retained the strict 20 millisecond lower threshold while the task scheduler executed with varying execution jitter. Core 0 encountered 3 consecutive reset loops before the inter-core handshake completed.\n\nWe fixed the early watchdog reset by rewriting the windowed `WDT` service sequence to verify the elapsed tick counter before writing the reload keyword, and setting the lower window threshold to 8 milliseconds instead of 20 milliseconds. We also updated the watchdog control configuration register by enabling pause on debugger halt and configuring the reset delay cycle counter to 32 clock cycles, which eliminated spurious resets during active flash programming."
    },
    # Tier 3: Long (90+ words) - Sample 10
    # Chip: ESP32, Topic: I3C dynamic address assignment
    {
        "raw_asr": "the e s p thirty two host controller failed i three c dynamic address assignment during the enter dynamic address assignment procedure because bus open drain clock timing caused target devices two drop out during arbitrat the controller operated as primary bus master communicating with four smart sensors at twelve megahertz single data rate logic analyzer decodes and voltage measurements showed that rise time on the serial clock line exceeded one hundred twenty nanoseconds which caused target slave devices two misread broadcast commands after two wait after four dynamic address assignment cycles um hardware debugger register inspection showed that the master i three c controller transmitted address zero x zero eight wait transmitted address zero x zero a with incorrect odd parity while the target address assignment table remained unpopulated in static r a m core zero asserted an arbitration lost interrupt when a secondary target pulled the data line low during the acknowledge phase we resolved the dynamic address assignment failure buy reprogramming the bus timing register with forty nanosecond open drain high period and enabling the internal pull up boost circuit we also updated the master dynamic address configur register buy writing zero x zero a to the secondary target assignment slot and setting the parity generation bit which allowed all four target sensors two successfully complete dynamic address assignment",
        "refined_text": "The `ESP32` host controller failed `I3C` dynamic address assignment during the enter dynamic address assignment procedure because bus open-drain clock timing caused target devices to drop out during arbitration. The controller operated as primary bus master communicating with 4 smart sensors at 12 megahertz single data rate. Logic analyzer decodes and voltage measurements showed that rise time on the serial clock line exceeded 120 nanoseconds, which caused target slave devices to misread broadcast commands after 4 dynamic address assignment cycles.\n\nHardware debugger register inspection showed that the master `I3C` controller transmitted address 0x0A with incorrect odd parity while the target address assignment table remained unpopulated in static `RAM`. Core 0 asserted an arbitration-lost interrupt when a secondary target pulled the data line low during the acknowledge phase.\n\nWe resolved the dynamic address assignment failure by reprogramming the bus timing register with 40-nanosecond open-drain high period and enabling the internal pull-up boost circuit. We also updated the master dynamic address configuration register by writing 0x0A to the secondary target assignment slot and setting the parity generation bit, which allowed all 4 target sensors to successfully complete dynamic address assignment."
    }
]

print("Validating individual pairs...")
for idx, s in enumerate(samples):
    ok, reason = validate_pair(s)
    if not ok:
        print(f"FAILED validate_pair on sample {idx+1}: {reason}")
        sys.exit(1)
    res, status = clean_sample(s["raw_asr"], s["refined_text"])
    if status != "kept":
        print(f"FAILED clean_sample on sample {idx+1}: {status}")
        sys.exit(1)
    w_raw = len(s["raw_asr"].split())
    w_ref = len(s["refined_text"].split())
    print(f"Sample {idx+1:2d}: validate_pair OK, clean_sample OK. Words: raw={w_raw:3d}, ref={w_ref:3d}, ratio={w_ref/w_raw:.2f}")

print("\nValidating batch...")
b_ok, b_reason, b_tiers = validate_batch(samples, min_short=2, min_medium=3, min_long=5)
if not b_ok:
    print(f"FAILED validate_batch: {b_reason}")
    sys.exit(1)

print(f"Batch validation SUCCESS: {b_reason}")
print(f"Tier counts: {b_tiers}")

out_path = "scratch/subagent_batch_16.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(samples)} samples to {out_path}")
