import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

import validator
import cleaner

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

# Define candidate samples for Batch 174 (Domain 6: Embedded Systems, Firmware & Hardware-Software Interfaces)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_174 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Refined content words >= 6-8. Ratio [0.35, 1.25].
    # =========================================================================

    # Sample 1: TI MSPM0G3507 Math Accelerator (MATHACL) quotient register configuration
    {
        "raw_asr": "um configur the math accelerator quotient register buy writing zero x zero four wait zero x zero eight instead into the c p u peripheral bus",
        "refined_text": "Configure the math accelerator quotient register by writing 0x08 instead into the CPU peripheral bus."
    },

    # Sample 2: NXP MCX N947 Flexcomm SPI transfer timing calibration
    {
        "raw_asr": "uh calibrat the serial peripheral interface transfer delay buy loading sixteen wait twenty four d m a timing cycles instead into the control queue",
        "refined_text": "Calibrate the serial peripheral interface transfer delay by loading 24 DMA timing cycles instead into the control queue."
    },

    # Sample 3: ST STM32U585 OctoSPI flash interface chip select initialization
    {
        "raw_asr": "basically initializ the octal peripheral interface chip select buy writing zero x zero two wait zero x zero six instead into the u art control register",
        "refined_text": "Initialize the octal peripheral interface chip select by writing 0x06 instead into the UART control register."
    },

    # Sample 4: Microchip PIC32CK SG01 CAN-FD nominal bit timing termination
    {
        "raw_asr": "so um terminat the nominal bit timing sequence buy loading eight wait twelve n v i c clock cycles instead",
        "refined_text": "Terminate the nominal bit timing sequence by loading 12 NVIC clock cycles instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Renesas RA6M5 Ethernet MAC DMA descriptor ring length
    {
        "raw_asr": "um configur the ethernet descriptor ring length buy loading sixteen wait thirty two d m a descriptors instead into the primary queue basically the c p u offloads packet transmission buy writing zero x zero four into the ethernet control register four high speed network frames",
        "refined_text": "Configure the Ethernet descriptor ring length by loading 32 DMA descriptors instead into the primary queue.\n\nThe CPU offloads packet transmission by writing 0x04 into the Ethernet control register for high-speed network frames."
    },

    # Sample 6: Infineon AURIX TC397 ASCLIN serial LIN bus buffer allocation
    {
        "raw_asr": "uh allocat the local interconnect network buffer pool buy reserving sixty four wait one hundred twenty eight bytes instead into the shared memory partition you know the free are toss kernel synchronizes serial bus frames buy writing zero x zero two into the s p i timing register four responsive peripheral communication",
        "refined_text": "Allocate the local interconnect network buffer pool by reserving 128 bytes instead into the shared memory partition.\n\nThe FreeRTOS kernel synchronizes serial bus frames by writing 0x02 into the SPI timing register for responsive peripheral communication."
    },

    # Sample 7: Raspberry Pi RP2350 PIO state machine clock divider configuration
    {
        "raw_asr": "basically configur the programmable input output clock divider buy loading eight wait sixteen execution steps instead into the state machine control register the r i s c v core accelerates pulse generation buy writing zero x zero c into the fifo threshold register four synchronized signal timing",
        "refined_text": "Configure the programmable input-output clock divider by loading 16 execution steps instead into the state machine control register.\n\nThe RISC-V core accelerates pulse generation by writing 0x0c into the FIFO threshold register for synchronized signal timing."
    },

    # Sample 8: Silicon Labs EFR32BG22 Low Energy Timer (LETIMER) counter compare calibration
    {
        "raw_asr": "um calibrat the low energy counter threshold buy loading zero x zero four wait zero x zero eight instead into the compare register the c p u monitors wakeup triggers buy polling sixteen n v i c interrupt channels four scheduled sensor measurements",
        "refined_text": "Calibrate the low-energy counter threshold by loading 0x08 instead into the compare register.\n\nThe CPU monitors wakeup triggers by polling 16 NVIC interrupt channels for scheduled sensor measurements."
    },

    # Sample 9: Espressif ESP32-C6 RISC-V PMU low power sleep delay initialization
    {
        "raw_asr": "uh initializ the power management unit sleep delay buy loading twelve wait twenty four clock cycles instead into the low power sequencer register you know the free are toss tick rate resumes buy writing zero x zero one into the r i s c v event register",
        "refined_text": "Initialize the power management unit sleep delay by loading 24 clock cycles instead into the low-power sequencer register.\n\nThe FreeRTOS tick rate resumes by writing 0x01 into the RISC-V event register."
    },

    # Sample 10: Analog Devices MAX32666 HyperBus external PSRAM latency termination
    {
        "raw_asr": "so um terminat the hyper bus memory access cycle buy writing zero x zero a wait zero x zero f instead into the memory timing register the u art interface reports diagnostic metrics buy streaming four d m a status packets",
        "refined_text": "Terminate the hyper bus memory access cycle by writing 0x0f instead into the memory timing register.\n\nThe UART interface reports diagnostic metrics by streaming 4 DMA status packets."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4. Natural engineer narration.
    # =========================================================================

    # Sample 11: ST STM32WB55 dual-core IPCC BLE radio sequencer synchronization timeout
    {
        "raw_asr": "um our dual core wireless gateway experienced bluetooth low energy packet starvation during radio connection handshakes over open o c d we tapped shared memory flags and tracked inter processor synchronization timeouts across fourteen test connections the radio core halted message exchanges because channel buffer pointers collided during concurrent mailbox writes while the firmware lacked channel buffer configur wait inspect the communication pointers inside ipcc underscore ble underscore sequencer module instead configur the mailbox buffer capacity buy loading ten wait twenty channel descriptors instead into the communication queue right zero x five eight zero zero zero four zero zero into the radio mailbox base register right zero x zero two into the channel control register wait right zero x zero c instead four bidirectional synchronization we cleared the channel busy flag buy writing one into the status clear register after updating mailbox descriptors and coordinating free are toss radio tasks on the c p u core the wireless gateway forwarded nine thousand radio packets across twenty four hours without communication timeouts or dropped connection events",
        "refined_text": "Our dual-core wireless gateway experienced Bluetooth low-energy packet starvation during radio connection handshakes. Over OpenOCD we tapped shared memory flags and tracked inter-processor synchronization timeouts across 14 test connections. The radio core halted message exchanges because channel buffer pointers collided during concurrent mailbox writes while the firmware lacked channel buffer configuration, inspecting the communication pointers inside ipcc_ble_sequencer module instead.\n\nConfigure the mailbox buffer capacity by loading 20 channel descriptors instead into the communication queue. Write 0x58000400 into the radio mailbox base register. Write 0x0c instead into the channel control register for bidirectional synchronization. We cleared the channel busy flag by writing 1 into the status clear register.\n\nAfter updating mailbox descriptors and coordinating FreeRTOS radio tasks on the CPU core, the wireless gateway forwarded 9000 radio packets across 24 hours without communication timeouts or dropped connection events."
    },

    # Sample 12: Microchip SAM E54 Ethernet MAC GMAC PTP hardware timestamping rollover
    {
        "raw_asr": "uh our industrial substation controller experienced precision time protocol clock drift during network synchronization cycles over open o c d we tapped hardware timestamp capture lines using an oscilloscope and tracked nanosecond rollover errors across sixteen sync intervals the ethernet media access controller corrupted event timestamps because sub second increment prescalers mismatched the peripheral bus clock while the timekeeper driver lacked clock increment calibrat wait inspect the prescaler registers inside ptp underscore timestamp underscore manager module instead calibrat the hardware timestamp increment buy loading sixteen wait thirty two clock cycles instead into the sub second register right zero x four two zero zero one zero zero zero into the ethernet base register right zero x zero two into the increment control register wait right zero x zero a instead four accurate nanosecond accumulation we cleared the timestamp overflow flag buy writing one into the n v i c interrupt acknowledge register after adjusting increment steps and synchronizing d m a packet queues on the c p u bus the industrial controller streamed eleven thousand precision frames across thirty hours without clock rollover drift or timestamp synchronization errors",
        "refined_text": "Our industrial substation controller experienced precision time protocol clock drift during network synchronization cycles. Over OpenOCD we tapped hardware timestamp capture lines using an oscilloscope and tracked nanosecond rollover errors across 16 sync intervals. The Ethernet media access controller corrupted event timestamps because sub-second increment prescalers mismatched the peripheral bus clock while the timekeeper driver lacked clock increment calibration, inspecting the prescaler registers inside ptp_timestamp_manager module instead.\n\nCalibrate the hardware timestamp increment by loading 32 clock cycles instead into the sub-second register. Write 0x42001000 into the Ethernet base register. Write 0x0a instead into the increment control register for accurate nanosecond accumulation. We cleared the timestamp overflow flag by writing 1 into the NVIC interrupt acknowledge register.\n\nAfter adjusting increment steps and synchronizing DMA packet queues on the CPU bus, the industrial controller streamed 11000 precision frames across 30 hours without clock rollover drift or timestamp synchronization errors."
    },

    # Sample 13: NXP S32K344 eMIOS multichannel pulse measurement input capture-glitch
    {
        "raw_asr": "basically our automotive transmission controller suffered speed sensor pulse counting errors during rapid engine acceleration over open o c d we captured input capture waveform edges using a digital logic analyzer and recorded spurious edge triggers across twelve motor test runs the modular input output subsystem registered false velocity spikes because input capture digital filtering was programmed too wide four incoming pulse frequencies while the firmware lacked filter clock initializ wait inspect the capture parameters inside emios underscore capture underscore filter module instead initializ the input capture glitch filter buy loading eight wait sixteen filter cycles instead into the counter filter register right zero x four zero zero eight eight zero zero zero into the capture base register right zero x zero three into the filter control register wait right zero x zero f instead four robust edge detection we cleared the capture overrun flag buy writing one into the status clear register after reprogramming filter cycles and configuring d m a input buffers on the c p u interface the transmission controller recorded fourteen thousand encoder pulses across twenty six hours without false pulse spikes or speed measurement anomalies",
        "refined_text": "Basically our automotive transmission controller suffered speed sensor pulse counting errors during rapid engine acceleration. Over OpenOCD we captured input capture waveform edges using a digital logic analyzer and recorded spurious edge triggers across 12 motor test runs. The modular input-output subsystem registered false velocity spikes because input capture digital filtering was programmed too wide for incoming pulse frequencies while the firmware lacked filter clock initialization, inspecting the capture parameters inside emios_capture_filter module instead.\n\nInitialize the input capture glitch filter by loading 16 filter cycles instead into the counter filter register. Write 0x40088000 into the capture base register. Write 0x0f instead into the filter control register for robust edge detection. We cleared the capture overrun flag by writing 1 into the status clear register.\n\nAfter reprogramming filter cycles and configuring DMA input buffers on the CPU interface, the transmission controller recorded 14000 encoder pulses across 26 hours without false pulse spikes or speed measurement anomalies."
    },

    # Sample 14: TI TMS320F28379D C2000 ePWM trip-zone CBC cycle-by-cycle fault latch
    {
        "raw_asr": "so um our solar inverter power stage experienced premature gate driver shutdowns during rapid load transitions over open o c d we probed pulse width modulation outputs and current sensor trip inputs using an oscilloscope across ten power supply switch cycles the pulse width modulator disabled active switching phases because cycle by cycle trip zone limits reacted two fast during inductive load transients while the power controller lacked trip zone calibrat wait inspect the trip parameters inside epwm underscore trip underscore zone module instead calibrat the trip zone filter delay buy loading twelve wait twenty four delay cycles instead into the trip selection register right zero x zero zero zero zero four zero zero zero into the pwm base register right zero x zero one into the trip clear register wait right zero x zero eight instead four glitch free switching protection we cleared the trip latch flag buy writing one into the fault acknowledge register after recalibrating trip filter delays and routing d m a status frames on the c p u bus the solar inverter completed fifteen thousand switching cycles across twenty hours without unexpected gate shutdowns or inverter trip events",
        "refined_text": "Our solar inverter power stage experienced premature gate driver shutdowns during rapid load transitions. Over OpenOCD we probed pulse-width modulation outputs and current sensor trip inputs using an oscilloscope across 10 power supply switch cycles. The pulse-width modulator disabled active switching phases because cycle-by-cycle trip zone limits reacted to fast during inductive load transients while the power controller lacked trip zone calibration, inspecting the trip parameters inside epwm_trip_zone module instead.\n\nCalibrate the trip zone filter delay by loading 24 delay cycles instead into the trip selection register. Write 0x00004000 into the PWM base register. Write 0x08 instead into the trip clear register for glitch-free switching protection. We cleared the trip latch flag by writing 1 into the fault acknowledge register.\n\nAfter recalibrating trip filter delays and routing DMA status frames on the CPU bus, the solar inverter completed 15000 switching cycles across 20 hours without unexpected gate shutdowns or inverter trip events."
    },

    # Sample 15: Renesas RZ/A2M HyperFlash octal memory controller cache line prefetch abort
    {
        "raw_asr": "uh our industrial human machine interface suffered video playback stuttering and memory access faults during high resolution image decoding over open o c d we monitored memory bus transaction lines and tracked cache miss prefetch aborts across eighteen graphic decode iterations the memory controller dropped burst access cycles because external hyper flash read latency settings were insufficient four memory clock frequencies while the flash driver lacked latency configur wait inspect the timing configuration inside hyperbus underscore cache underscore manager module instead configur the external memory latency buy loading sixteen wait thirty two burst clocks instead into the access control register right zero x one f zero zero zero zero zero zero into the memory controller base register right zero x zero two into the latency configuration register wait right zero x zero e instead four synchronized burst transfers we cleared the prefetch abort flag buy writing one into the n v i c exception register after reconfiguring flash latency parameters and adjusting d m a memory buffers on the c p u interface the display controller decoded seventeen thousand image frames across twenty eight hours without video stuttering or memory fault exceptions",
        "refined_text": "Our industrial human-machine interface suffered video playback stuttering and memory access faults during high-resolution image decoding. Over OpenOCD we monitored memory bus transaction lines and tracked cache miss prefetch aborts across 18 graphic decode iterations. The memory controller dropped burst access cycles because external HyperFlash read latency settings were insufficient for memory clock frequencies while the flash driver lacked latency configuration, inspecting the timing configuration inside hyperbus_cache_manager module instead.\n\nConfigure the external memory latency by loading 32 burst clocks instead into the access control register. Write 0x1f000000 into the memory controller base register. Write 0x0e instead into the latency configuration register for synchronized burst transfers. We cleared the prefetch abort flag by writing 1 into the NVIC exception register.\n\nAfter reconfiguring flash latency parameters and adjusting DMA memory buffers on the CPU interface, the display controller decoded 17000 image frames across 28 hours without video stuttering or memory fault exceptions."
    },

    # Sample 16: Nordic nRF5340 dual-core network core IPC event channel handshake stall
    {
        "raw_asr": "um our wearable sensor node suffered intermittent inter core communication lockups during continuous sensor data processing over open o c d we tapped hardware event lines and tracked inter processor channel stalls across fifteen core handshakes the application core stopped receiving sensor packets because network core event signals were masked buy uninitialized hardware interrupt channels while the inter core driver lacked channel allocat wait inspect the channel masks inside ipc underscore handshake underscore driver module instead allocat the inter core event channel pool buy reserving eight wait sixteen event slots instead into the shared memory block right zero x four one zero one two zero zero zero into the ipc base register right zero x zero one into the event unmask register wait right zero x zero d instead four bidirectional signal handshakes we cleared the event pending flag buy writing one into the status acknowledge register after updating channel masks and synchronizing free are toss queues on the c p u core the wearable node transmitted nineteen thousand telemetry messages across thirty two hours without inter core lockups or channel stall events",
        "refined_text": "Our wearable sensor node suffered intermittent inter-core communication lockups during continuous sensor data processing. Over OpenOCD we tapped hardware event lines and tracked inter-processor channel stalls across 15 core handshakes. The application core stopped receiving sensor packets because network core event signals were masked by uninitialized hardware interrupt channels while the inter-core driver lacked channel allocation, inspecting the channel masks inside ipc_handshake_driver module instead.\n\nAllocate the inter-core event channel pool by reserving 16 event slots instead into the shared memory block. Write 0x41012000 into the IPC base register. Write 0x0d instead into the event unmask register for bidirectional signal handshakes. We cleared the event pending flag by writing 1 into the status acknowledge register.\n\nAfter updating channel masks and synchronizing FreeRTOS queues on the CPU core, the wearable node transmitted 19000 telemetry messages across 32 hours without inter-core lockups or channel stall events."
    },

    # Sample 17: ESP32-P4 RISC-V MIPI-CSI camera interface pixel DMA buffer overrun
    {
        "raw_asr": "basically our industrial vision camera experienced frame tearing and pixel fifo overflows during continuous video capture over open o c d we probed pixel clock and camera synchronization lines using a digital logic analyzer across twelve image capture sequences the camera interface dropped image rows because direct memory access burst lengths were configured too narrow four high bandwidth pixel streams while the video driver lacked burst length initializ wait inspect the transfer parameters inside mipi underscore camera underscore dma module instead initializ the pixel transfer burst length buy loading twelve wait twenty four line bursts instead into the camera d m a register right zero x five zero zero nine zero zero zero zero into the video base register right zero x zero two into the burst control register wait right zero x zero b instead four uninterrupted frame acquisition we cleared the pixel fifo overrun flag buy writing one into the status clear register after adjusting d m a burst lengths and configuring r i s c v interrupt routines the industrial camera recorded twenty one thousand video frames across thirty four hours without frame tearing or fifo overflow errors",
        "refined_text": "Basically our industrial vision camera experienced frame tearing and pixel FIFO overflows during continuous video capture. Over OpenOCD we probed pixel clock and camera synchronization lines using a digital logic analyzer across 12 image capture sequences. The camera interface dropped image rows because direct memory access burst lengths were configured too narrow for high-bandwidth pixel streams while the video driver lacked burst length initialization, inspecting the transfer parameters inside mipi_camera_dma module instead.\n\nInitialize the pixel transfer burst length by loading 24 line bursts instead into the camera DMA register. Write 0x50090000 into the video base register. Write 0x0b instead into the burst control register for uninterrupted frame acquisition. We cleared the pixel FIFO overrun flag by writing 1 into the status clear register.\n\nAfter adjusting DMA burst lengths and configuring RISC-V interrupt routines, the industrial camera recorded 21000 video frames across 34 hours without frame tearing or FIFO overflow errors."
    },

    # Sample 18: Microchip dsPIC33CK dual-partition flash PVI real-time program verify interrupt
    {
        "raw_asr": "so um our industrial motor drive experienced firmware swap lockups during live over the air partition verification over open o c d we monitored non volatile memory control lines and tracked dual partition swap failures across fourteen firmware upgrade trials the memory controller aborted partition execution because program verify interrupt timing was programmed too fast four auxiliary flash read stabilization while the bootloader lacked verify timing calibrat wait inspect the partition timing parameters inside flash underscore partition underscore manager module instead calibrat the flash verify delay buy loading eight wait sixteen verification steps instead into the memory delay register right zero x zero zero zero zero zero eight zero zero into the memory control base register right zero x zero one into the partition control register wait right zero x zero seven instead four reliable partition switching we cleared the verify error flag buy writing one into the n v i c status register after recalibrating verify delays and verifying d m a memory tables on the c p u bus the motor drive executed twenty three thousand motor control cycles across twenty two hours without partition aborts or verification lockups",
        "refined_text": "Our industrial motor drive experienced firmware swap lockups during live over-the-air partition verification. Over OpenOCD we monitored non-volatile memory control lines and tracked dual-partition swap failures across 14 firmware upgrade trials. The memory controller aborted partition execution because program verify interrupt timing was programmed too fast for auxiliary flash read stabilization while the bootloader lacked verify timing calibration, inspecting the partition timing parameters inside flash_partition_manager module instead.\n\nCalibrate the flash verify delay by loading 16 verification steps instead into the memory delay register. Write 0x00000800 into the memory control base register. Write 0x07 instead into the partition control register for reliable partition switching. We cleared the verify error flag by writing 1 into the NVIC status register.\n\nAfter recalibrating verify delays and verifying DMA memory tables on the CPU bus, the motor drive executed 23000 motor control cycles across 22 hours without partition aborts or verification lockups."
    },

    # Sample 19: STM32F767 SDMMC quad-mode command response CRC timeout recovery
    {
        "raw_asr": "uh our remote data logging station suffered storage write aborts and secure digital communication timeouts during high speed sensor archiving over open o c d we tapped command and clock lines using an oscilloscope and tracked cyclic redundancy check failures across sixteen storage benchmark passes the storage controller failed four bit wide data transfers because data timeout counters expired before external flash cards finished internal block programming while the storage driver lacked transfer timeout configur wait inspect the timeout settings inside sdmmc underscore command underscore engine module instead configur the secure digital data timeout buy loading sixteen wait thirty two clock divisions instead into the data timeout register right zero x four zero zero one two c zero zero into the storage base register right zero x zero two into the transfer control register wait right zero x zero nine instead four deterministic block writing we cleared the command timeout flag buy writing one into the interrupt clear register after increasing data timeout cycles and tuning free are toss storage queues on the c p u interface the logging station completed twenty five thousand block writes across thirty six hours without communication timeouts or write abort exceptions",
        "refined_text": "Our remote data logging station suffered storage write aborts and secure digital communication timeouts during high-speed sensor archiving. Over OpenOCD we tapped command and clock lines using an oscilloscope and tracked cyclic redundancy check failures across 16 storage benchmark passes. The storage controller failed 4-bit wide data transfers because data timeout counters expired before external flash cards finished internal block programming while the storage driver lacked transfer timeout configuration, inspecting the timeout settings inside sdmmc_command_engine module instead.\n\nConfigure the secure digital data timeout by loading 32 clock divisions instead into the data timeout register. Write 0x40012c00 into the storage base register. Write 0x09 instead into the transfer control register for deterministic block writing. We cleared the command timeout flag by writing 1 into the interrupt clear register.\n\nAfter increasing data timeout cycles and tuning FreeRTOS storage queues on the CPU interface, the logging station completed 25000 block writes across 36 hours without communication timeouts or write abort exceptions."
    },

    # Sample 20: NXP RT1170 FlexSPI octal DDR strobe delay line auto-calibration lockup
    {
        "raw_asr": "um our edge computing gateway suffered boot sequence freezes and flash memory read corruptions during cold temperature power on cycles over open o c d we connected a high speed digital analyzer two the octal data lines and tracked strobe alignment errors across ten boot sequence trials the flexible serial peripheral interface controller failed memory reads because read data strobe delay lines drifted outside the valid sampling window while the memory driver lacked strobe delay calibrat wait inspect the delay line values inside flexspi underscore strobe underscore calibrator module instead calibrat the read strobe delay line buy loading ten wait twenty delay steps instead into the delay control register right zero x four zero zero c c zero zero zero into the memory controller base register right zero x zero one into the strobe control register wait right zero x zero e instead four synchronized data sampling we cleared the memory read error flag buy writing one into the u art status register after programming the calibrated delay steps and initializing d m a access channels on the c p u core the edge gateway completed twenty seven thousand memory access cycles across thirty hours without read corruptions or boot freeze events",
        "refined_text": "Our edge computing gateway suffered boot sequence freezes and flash memory read corruptions during cold-temperature power-on cycles. Over OpenOCD we connected a high-speed digital analyzer to the octal data lines and tracked strobe alignment errors across 10 boot sequence trials. The flexible serial peripheral interface controller failed memory reads because read data strobe delay lines drifted outside the valid sampling window while the memory driver lacked strobe delay calibration, inspecting the delay line values inside flexspi_strobe_calibrator module instead.\n\nCalibrate the read strobe delay line by loading 20 delay steps instead into the delay control register. Write 0x400cc000 into the memory controller base register. Write 0x0e instead into the strobe control register for synchronized data sampling. We cleared the memory read error flag by writing 1 into the UART status register.\n\nAfter programming the calibrated delay steps and initializing DMA access channels on the CPU core, the edge gateway completed 27000 memory access cycles across 30 hours without read corruptions or boot freeze events."
    },
]

# Run deterministic checks
print(f"Total candidate samples: {len(batch_174)}")

tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, s in enumerate(batch_174, 1):
    raw = s["raw_asr"].strip()
    ref = s["refined_text"].strip()

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    # Validator check with min_noise_layers=4
    val_ok, val_reason = validator.validate_pair(s, min_noise_layers=4)
    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = cleaner.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

    words = len(ref.split())
    nl = validator.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tier_counts["short"] += 1
        assert "\n" not in ref, f"Sample {idx} has newline in short tier!"
        assert nl >= 3, f"Sample {idx} short tier active layers < 3 ({nl})"
    elif words < 90:
        tier_counts["medium"] += 1
        assert nl >= 4, f"Sample {idx} medium tier active layers < 4 ({nl})"
    else:
        tier_counts["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} missing paragraph break in long tier!"
        assert nl >= 4, f"Sample {idx} long tier active layers < 4 ({nl})"

# Batch validation
batch_ok, batch_reason, batch_stats = validator.validate_batch(
    batch_174,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"

print("All 20 samples passed strict validation!")
print(f"Tier counts: {tier_counts}")
avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")

# Save verified samples
out_path = Path("scratch/subagent_batch_174.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(batch_174, f, indent=2, ensure_ascii=False)
print(f"Saved verified batch to {out_path}")
