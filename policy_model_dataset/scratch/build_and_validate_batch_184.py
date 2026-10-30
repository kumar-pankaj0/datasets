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

# Define candidate samples for Batch 184 (Domain 6: Embedded Systems, Firmware & Hardware-Software Interfaces)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_184 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Refined content words >= 6-8. Ratio [0.35, 1.25].
    # =========================================================================

    # Sample 1: ST STM32G474 HRTIM dead-time generator register configuration
    {
        "raw_asr": "um configur the high resolution timer dead time register buy loading zero x zero four wait zero x zero eight instead into the c p u peripheral bus",
        "refined_text": "Configure the high-resolution timer dead-time register by loading 0x08 instead into the CPU peripheral bus."
    },

    # Sample 2: Microchip SAM D21 SERCOM I2C bus hold time calibration
    {
        "raw_asr": "uh calibrat the serial communication interface hold time buy loading sixteen wait twenty four d m a clock cycles instead into the control bus",
        "refined_text": "Calibrate the serial communication interface hold time by loading 24 DMA clock cycles instead into the control bus."
    },

    # Sample 3: NXP LPC55S69 CTimer match register initialization
    {
        "raw_asr": "basically initializ the standard counter timer match channel buy writing zero x zero two wait zero x zero six instead into the u art status register",
        "refined_text": "Initialize the standard counter timer match channel by writing 0x06 instead into the UART status register."
    },

    # Sample 4: Silicon Labs EFR32xG24 Watchdog Timer (WDOG) clear window termination
    {
        "raw_asr": "so um terminat the watchdog timer clear sequence buy loading eight wait twelve n v i c monitor cycles instead",
        "refined_text": "Terminate the watchdog timer clear sequence by loading 12 NVIC monitor cycles instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: TI CC1352P Sub-1GHz RF core packet length configuration
    {
        "raw_asr": "um configur the radio frequency packet length threshold buy loading sixteen wait thirty two d m a descriptors instead into the primary queue basically the c p u offloads packet transmission buy writing zero x zero four into the radio control register four high throughput wireless frames",
        "refined_text": "Configure the radio frequency packet length threshold by loading 32 DMA descriptors instead into the primary queue.\n\nThe CPU offloads packet transmission by writing 0x04 into the radio control register for high-throughput wireless frames."
    },

    # Sample 6: Renesas RX65N Multi-Function Timer Pulse Unit (MTU3) PWM dead-band allocation
    {
        "raw_asr": "uh allocat the timer pulse buffer pool buy reserving sixty four wait one hundred twenty eight bytes instead into the shared memory partition you know the free are toss kernel synchronizes serial bus frames buy writing zero x zero two into the s p i timing register four responsive motor control",
        "refined_text": "Allocate the timer pulse buffer pool by reserving 128 bytes instead into the shared memory partition.\n\nThe FreeRTOS kernel synchronizes serial bus frames by writing 0x02 into the SPI timing register for responsive motor control."
    },

    # Sample 7: Nordic nRF52840 PWM peripheral sequence counter configuration
    {
        "raw_asr": "basically configur the pulse modulation sequence counter buy loading eight wait sixteen execution steps instead into the sequence control register the r i s c v core accelerates pulse generation buy writing zero x zero c into the fifo threshold register four synchronized audio signals",
        "refined_text": "Configure the pulse modulation sequence counter by loading 16 execution steps instead into the sequence control register.\n\nThe RISC-V core accelerates pulse generation by writing 0x0c into the FIFO threshold register for synchronized audio signals."
    },

    # Sample 8: Espressif ESP32-S3 USB-Serial-JTAG FIFO threshold calibration
    {
        "raw_asr": "um calibrat the hardware serial fifo watermark threshold buy loading zero x zero four wait zero x zero eight instead into the compare register the c p u monitors wakeup triggers buy polling sixteen n v i c interrupt channels four scheduled sensor transmissions",
        "refined_text": "Calibrate the hardware serial FIFO watermark threshold by loading 0x08 instead into the compare register.\n\nThe CPU monitors wakeup triggers by polling 16 NVIC interrupt channels for scheduled sensor transmissions."
    },

    # Sample 9: ST STM32MP157 Shared Resource Controller (HSEM) semaphore initialization
    {
        "raw_asr": "uh initializ the hardware semaphore channel lock delay buy loading twelve wait twenty four clock cycles instead into the resource sequencer register you know the free are toss tick rate resumes buy writing zero x zero one into the r i s c v event register",
        "refined_text": "Initialize the hardware semaphore channel lock delay by loading 24 clock cycles instead into the resource sequencer register.\n\nThe FreeRTOS tick rate resumes by writing 0x01 into the RISC-V event register."
    },

    # Sample 10: Microchip SAM E70 High-Speed USB Device (USBHS) endpoint buffer termination
    {
        "raw_asr": "so um terminat the endpoint transfer sequence buy writing zero x zero a wait zero x zero f instead into the memory timing register the u art interface reports diagnostic metrics buy streaming four d m a status packets",
        "refined_text": "Terminate the endpoint transfer sequence by writing 0x0f instead into the memory timing register.\n\nThe UART interface reports diagnostic metrics by streaming 4 DMA status packets."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4. Natural engineer narration.
    # =========================================================================

    # Sample 11: NXP LPC55S69 TrustZone-M Secure/Non-Secure SAU boundary attribution violation
    {
        "raw_asr": "um our secure dual core microcontroller experienced security attribution faults during non secure callable veneer transitions over open o c d we tapped hardware bus fault signals and tracked security attribution unit violation exceptions across fourteen secure boot sequences the core halted instruction execution because memory region boundaries overlapped between secure and non secure partitions while the bootloader lacked boundary configur wait inspect the region tables inside sau underscore boundary underscore manager module instead configur the memory security region capacity buy loading sixteen wait thirty two memory descriptors instead into the partition table right zero x five zero zero zero zero zero zero zero into the sau base register right zero x zero one into the region control register wait right zero x zero b instead four non secure callable boundary enforcement we cleared the security fault flag buy writing one into the status clear register after adjusting security boundaries and coordinating free are toss context switches on the c p u core the dual core microcontroller executed eight thousand secure function calls across twenty four hours without bus faults or security attribution exceptions",
        "refined_text": "Our secure dual-core microcontroller experienced security attribution faults during non-secure callable veneer transitions. Over OpenOCD we tapped hardware bus fault signals and tracked security attribution unit violation exceptions across 14 secure boot sequences. The core halted instruction execution because memory region boundaries overlapped between secure and non-secure partitions while the bootloader lacked boundary configuration, inspecting the region tables inside sau_boundary_manager module instead.\n\nConfigure the memory security region capacity by loading 32 memory descriptors instead into the partition table. Write 0x50000000 into the SAU base register. Write 0x0b instead into the region control register for non-secure callable boundary enforcement. We cleared the security fault flag by writing 1 into the status clear register.\n\nAfter adjusting security boundaries and coordinating FreeRTOS context switches on the CPU core, the dual-core microcontroller executed 8000 secure function calls across 24 hours without bus faults or security attribution exceptions."
    },

    # Sample 12: ST STM32G474 CORDIC coprocessor calculation timeout
    {
        "raw_asr": "uh our digital motor drive experienced vector calculation timeouts during field oriented control transformations over open o c d we captured coordinate rotation signals using a logic analyzer and tracked calculation stall exceptions across sixteen motor speed sweeps the coprocessor halted trigonometric processing because input register arguments exceeded valid coordinate convergence bounds while the firmware lacked convergence calibrat wait inspect the input scaling factors inside cordic underscore vector underscore calc module instead calibrat the trigonometric calculation steps buy loading ten wait twenty calculation steps instead into the precision control register right zero x four zero zero two zero c zero zero into the cordic base register right zero x zero one into the function control register wait right zero x zero e instead four synchronized coordinate rotation we cleared the calculation ready flag buy writing one into the status clear register after calibrating calculation steps and routing d m a vector arrays on the c p u bus the digital motor drive completed twelve thousand vector iterations across thirty hours without coprocessor timeouts or coordinate stall exceptions",
        "refined_text": "Our digital motor drive experienced vector calculation timeouts during field-oriented control transformations. Over OpenOCD we captured coordinate rotation signals using a logic analyzer and tracked calculation stall exceptions across 16 motor speed sweeps. The coprocessor halted trigonometric processing because input register arguments exceeded valid coordinate convergence bounds while the firmware lacked convergence calibration, inspecting the input scaling factors inside cordic_vector_calc module instead.\n\nCalibrate the trigonometric calculation steps by loading 20 calculation steps instead into the precision control register. Write 0x40020c00 into the CORDIC base register. Write 0x0e instead into the function control register for synchronized coordinate rotation. We cleared the calculation ready flag by writing 1 into the status clear register.\n\nAfter calibrating calculation steps and routing DMA vector arrays on the CPU bus, the digital motor drive completed 12000 vector iterations across 30 hours without coprocessor timeouts or coordinate stall exceptions."
    },

    # Sample 13: Microchip SAM E70 Quad-SPI NOR Flash memory mapped execute-in-place (XIP) prefetch cache stall
    {
        "raw_asr": "basically our industrial gateway controller suffered memory prefetch stalls and instruction cache misses during live firmware execution over open o c d we tapped quad serial peripheral interface lines using an oscilloscope and tracked flash read latency wait states across twelve execution benchmarks the memory interface dropped instruction fetches because external flash latency prescalers mismatched serial bus clock frequencies while the memory driver lacked prefetch configur wait inspect the bus timing parameters inside qspi underscore xip underscore controller module instead configur the flash read wait states buy loading twelve wait twenty four wait states instead into the memory delay register right zero x four zero zero seven c zero zero zero into the qspi base register right zero x zero two into the latency configuration register wait right zero x zero d instead four stable instruction streaming we cleared the prefetch abort flag buy writing one into the status clear register after adjusting read latency steps and verifying d m a memory transactions on the c p u bus the gateway controller executed thirteen thousand memory accesses across twenty six hours without prefetch stalls or instruction cache misses",
        "refined_text": "Basically our industrial gateway controller suffered memory prefetch stalls and instruction cache misses during live firmware execution. Over OpenOCD we tapped quad serial peripheral interface lines using an oscilloscope and tracked flash read latency wait states across 12 execution benchmarks. The memory interface dropped instruction fetches because external flash latency prescalers mismatched serial bus clock frequencies while the memory driver lacked prefetch configuration, inspecting the bus timing parameters inside qspi_xip_controller module instead.\n\nConfigure the flash read wait states by loading 24 wait states instead into the memory delay register. Write 0x4007c000 into the QSPI base register. Write 0x0d instead into the latency configuration register for stable instruction streaming. We cleared the prefetch abort flag by writing 1 into the status clear register.\n\nAfter adjusting read latency steps and verifying DMA memory transactions on the CPU bus, the gateway controller executed 13000 memory accesses across 26 hours without prefetch stalls or instruction cache misses."
    },

    # Sample 14: Silicon Labs EFR32FG23 Sub-GHz Wireless SoC Radio Controller (RAC) PA ramp profile
    {
        "raw_asr": "so um our wireless telemetry transmitter suffered transmission packet corruption and power amplifier ramp glitches during frequency hopping bursts over open o c d we probed radio frequency output lines using a spectrum analyzer and tracked transmission burst anomalies across ten hopping cycles the radio controller aborted packet broadcasts because power amplifier ramp up curves triggered intermediate voltage drops while the radio driver lacked ramp calibrat wait inspect the power ramping parameters inside rac underscore rf underscore sequencer module instead calibrat the power amplifier ramp profile buy loading eight wait sixteen settling cycles instead into the ramp control register right zero x b zero zero zero four zero zero zero into the rac base register right zero x zero one into the ramp sequence register wait right zero x zero a instead four clean spectral emissions we cleared the transmitter error flag buy writing one into the status clear register after tuning ramp cycles and scheduling free are toss packet queues on the c p u core the wireless transmitter broadcast fourteen thousand rf packets across twenty two hours without transmission corruptions or amplifier ramp glitches",
        "refined_text": "Our wireless telemetry transmitter suffered transmission packet corruption and power amplifier ramp glitches during frequency hopping bursts. Over OpenOCD we probed radio frequency output lines using a spectrum analyzer and tracked transmission burst anomalies across 10 hopping cycles. The radio controller aborted packet broadcasts because power amplifier ramp-up curves triggered intermediate voltage drops while the radio driver lacked ramp calibration, inspecting the power ramping parameters inside rac_rf_sequencer module instead.\n\nCalibrate the power amplifier ramp profile by loading 16 settling cycles instead into the ramp control register. Write 0xb0004000 into the RAC base register. Write 0x0a instead into the ramp sequence register for clean spectral emissions. We cleared the transmitter error flag by writing 1 into the status clear register.\n\nAfter tuning ramp cycles and scheduling FreeRTOS packet queues on the CPU core, the wireless transmitter broadcast 14000 RF packets across 22 hours without transmission corruptions or amplifier ramp glitches."
    },

    # Sample 15: TI TMS320F280049C C2000 ADC post-processing block (PPB) offset error
    {
        "raw_asr": "uh our digital power converter suffered current measurement offset errors and false overcurrent trip signals during rapid load variations over open o c d we monitored analog conversion results using a logic analyzer and tracked conversion threshold violations across eighteen load step iterations the analog to digital converter triggered spurious trip flags because post processing block offset limits drifted under elevated operating temperatures while the sampling firmware lacked offset calibrat wait inspect the conversion limit parameters inside adc underscore ppb underscore limiter module instead calibrat the post processing block offset threshold buy loading fourteen wait twenty eight prescaler cycles instead into the offset adjustment register right zero x zero zero zero zero seven c zero zero into the adc base register right zero x zero two into the limit control register wait right zero x zero f instead four accurate overcurrent detection we cleared the comparator trip flag buy writing one into the status clear register after adjusting offset cycles and coordinating d m a sample buffers on the c p u interface the power converter logged fifteen thousand adc conversion samples across twenty eight hours without false overcurrent trips or measurement anomalies",
        "refined_text": "Our digital power converter suffered current measurement offset errors and false overcurrent trip signals during rapid load variations. Over OpenOCD we monitored analog conversion results using a logic analyzer and tracked conversion threshold violations across 18 load step iterations. The analog-to-digital converter triggered spurious trip flags because post-processing block offset limits drifted under elevated operating temperatures while the sampling firmware lacked offset calibration, inspecting the conversion limit parameters inside adc_ppb_limiter module instead.\n\nCalibrate the post-processing block offset threshold by loading 28 prescaler cycles instead into the offset adjustment register. Write 0x00007c00 into the ADC base register. Write 0x0f instead into the limit control register for accurate overcurrent detection. We cleared the comparator trip flag by writing 1 into the status clear register.\n\nAfter adjusting offset cycles and coordinating DMA sample buffers on the CPU interface, the power converter logged 15000 ADC conversion samples across 28 hours without false overcurrent trips or measurement anomalies."
    },

    # Sample 16: Renesas RA4M2 Capacitive Touch Sensing Unit (CTSU) drift compensation filter
    {
        "raw_asr": "um our industrial human machine panel experienced touch detection ghosting and electrode measurement drift during high humidity environmental cycles over open o c d we monitored touch sensor register states and tracked baseline calibration drifts across fifteen environmental test runs the capacitive touch sensing unit registered false touch triggers because baseline drift compensation filters updated too slowly four rapid moisture variations while the sensor driver lacked filter initializ wait inspect the sensor drift thresholds inside ctsu underscore drift underscore filter module instead initializ the baseline compensation filter buy loading sixteen wait thirty two filter steps instead into the drift rate register right zero x four zero zero eight zero zero zero zero into the ctsu base register right zero x zero one into the filter configuration register wait right zero x zero c instead four stable touch baseline tracking we cleared the sensor drift flag buy writing one into the status clear register after updating baseline filter cycles and synchronizing free are toss event groups on the c p u core the touch panel completed sixteen thousand touch scan frames across thirty two hours without ghost triggers or touch baseline drift errors",
        "refined_text": "Our industrial human-machine panel experienced touch detection ghosting and electrode measurement drift during high-humidity environmental cycles. Over OpenOCD we monitored touch sensor register states and tracked baseline calibration drifts across 15 environmental test runs. The capacitive touch sensing unit registered false touch triggers because baseline drift compensation filters updated too slowly for rapid moisture variations while the sensor driver lacked filter initialization, inspecting the sensor drift thresholds inside ctsu_drift_filter module instead.\n\nInitialize the baseline compensation filter by loading 32 filter steps instead into the drift rate register. Write 0x40080000 into the CTSU base register. Write 0x0c instead into the filter configuration register for stable touch baseline tracking. We cleared the sensor drift flag by writing 1 into the status clear register.\n\nAfter updating baseline filter cycles and synchronizing FreeRTOS event groups on the CPU core, the touch panel completed 16000 touch scan frames across 32 hours without ghost triggers or touch baseline drift errors."
    },

    # Sample 17: Infineon PSoC 6 Cryptographic Block AES-GCM hardware tag verification
    {
        "raw_asr": "basically our secure payment terminal suffered encryption authentication failures and payload processing aborts during transaction validation over open o c d we tapped hardware bus lines and tracked cryptographic engine error flags across twelve secure transaction passes the crypto block rejected valid authentication tags because direct memory access burst lengths misaligned Galois counter mode multiplier words while the cryptographic firmware lacked burst allocat wait inspect the memory alignment parameters inside crypto underscore gcm underscore accelerator module instead allocat the authenticated encryption burst buffer buy reserving ten wait twenty word bursts instead into the descriptor chain right zero x four zero three four zero zero zero zero into the crypto base register right zero x zero two into the multiplier control register wait right zero x zero nine instead four uninterrupted hardware tag calculation we cleared the authentication error flag buy writing one into the status clear register after adjusting word burst descriptors and verifying free are toss security tasks on the c p u core the payment terminal processed eighteen thousand cryptographic blocks across thirty four hours without authentication rejections or transaction aborts",
        "refined_text": "Basically our secure payment terminal suffered encryption authentication failures and payload processing aborts during transaction validation. Over OpenOCD we tapped hardware bus lines and tracked cryptographic engine error flags across 12 secure transaction passes. The crypto block rejected valid authentication tags because direct memory access burst lengths misaligned Galois counter mode multiplier words while the cryptographic firmware lacked burst allocation, inspecting the memory alignment parameters inside crypto_gcm_accelerator module instead.\n\nAllocate the authenticated encryption burst buffer by reserving 20 word bursts instead into the descriptor chain. Write 0x40340000 into the crypto base register. Write 0x09 instead into the multiplier control register for uninterrupted hardware tag calculation. We cleared the authentication error flag by writing 1 into the status clear register.\n\nAfter adjusting word burst descriptors and verifying FreeRTOS security tasks on the CPU core, the payment terminal processed 18000 cryptographic blocks across 34 hours without authentication rejections or transaction aborts."
    },

    # Sample 18: Nordic nRF9160 Cellular IoT modem low-power UART EasyDMA frame reception overrun
    {
        "raw_asr": "so um our cellular tracking beacon suffered modem command reception timeouts and character dropouts during heavy network reporting sessions over open o c d we monitored serial bus lines and tracked direct memory access buffer overruns across fourteen cellular data connections the universal asynchronous receiver transmitter dropped modem response characters because receive buffer pointers wrapped around before the parser evacuated data frames while the serial driver lacked buffer initializ wait inspect the receive pointer limits inside uarte underscore easydma underscore rx module instead initializ the receive ring buffer buy loading eight wait sixteen buffer descriptors instead into the d m a queue right zero x five zero zero zero eight zero zero zero into the uarte base register right zero x zero one into the buffer control register wait right zero x zero seven instead four deterministic character reception we cleared the buffer overrun flag buy writing one into the status clear register after expanding ring buffer descriptors and coordinating u art packet handlers on the c p u interface the tracking beacon logged twenty thousand at response packets across twenty hours without buffer overruns or character dropouts",
        "refined_text": "Our cellular tracking beacon suffered modem command reception timeouts and character dropouts during heavy network reporting sessions. Over OpenOCD we monitored serial bus lines and tracked direct memory access buffer overruns across 14 cellular data connections. The universal asynchronous receiver transmitter dropped modem response characters because receive buffer pointers wrapped around before the parser evacuated data frames while the serial driver lacked buffer initialization, inspecting the receive pointer limits inside uarte_easydma_rx module instead.\n\nInitialize the receive ring buffer by loading 16 buffer descriptors instead into the DMA queue. Write 0x50008000 into the UARTE base register. Write 0x07 instead into the buffer control register for deterministic character reception. We cleared the buffer overrun flag by writing 1 into the status clear register.\n\nAfter expanding ring buffer descriptors and coordinating UART packet handlers on the CPU interface, the tracking beacon logged 20000 AT response packets across 20 hours without buffer overruns or character dropouts."
    },

    # Sample 19: Espressif ESP32-H2 IEEE 802.15.4 Zigbee/Thread MAC frame hardware filtering
    {
        "raw_asr": "uh our smart home border router experienced packet acknowledgement drops and mesh network route flapping during high density sensor transmissions over open o c d we captured radio baseband signals using a packet analyzer and tracked frame acknowledgement failures across sixteen mesh communication intervals the radio controller dropped incoming frame acknowledgements because hardware turnaround delays expired before the transmitter switched from receive two transmit mode while the wireless driver lacked turnaround calibrat wait inspect the timing delays inside mac underscore frame underscore filter module instead calibrat the acknowledgement turnaround timing buy loading twelve wait twenty four symbol intervals instead into the turnaround register right zero x six zero zero nine zero zero zero zero into the mac base register right zero x zero two into the filter control register wait right zero x zero e instead four synchronized packet filtering we cleared the turnaround timeout flag buy writing one into the status clear register after adjusting symbol turnaround intervals and configuring r i s c v interrupt queues the border router processed twenty two thousand zigbee mesh frames across thirty six hours without acknowledgement drops or route flapping errors",
        "refined_text": "Our smart home border router experienced packet acknowledgement drops and mesh network route flapping during high-density sensor transmissions. Over OpenOCD we captured radio baseband signals using a packet analyzer and tracked frame acknowledgement failures across 16 mesh communication intervals. The radio controller dropped incoming frame acknowledgements because hardware turnaround delays expired before the transmitter switched from receive to transmit mode while the wireless driver lacked turnaround calibration, inspecting the timing delays inside mac_frame_filter module instead.\n\nCalibrate the acknowledgement turnaround timing by loading 24 symbol intervals instead into the turnaround register. Write 0x60090000 into the MAC base register. Write 0x0e instead into the filter control register for synchronized packet filtering. We cleared the turnaround timeout flag by writing 1 into the status clear register.\n\nAfter adjusting symbol turnaround intervals and configuring RISC-V interrupt queues, the border router processed 22000 Zigbee mesh frames across 36 hours without acknowledgement drops or route flapping errors."
    },

    # Sample 20: Raspberry Pi RP2040 Dual ARM Cortex-M0+ Hardware Inter-Processor FIFO (SIO) deadlock
    {
        "raw_asr": "um our dual core industrial datalogger experienced inter processor deadlock and task starvation during simultaneous peripheral streaming over open o c d we tapped hardware event flags and tracked core mailbox lockups across ten inter core benchmark trials the secondary core stopped responding because inter processor first in first out buffers overflowed during concurrent write attempts while the inter core driver lacked buffer allocat wait inspect the queue threshold settings inside sio underscore fifo underscore mailbox module instead allocat the inter processor mailbox queue buy reserving eight wait sixteen fifo entries instead into the queue table right zero x d zero zero zero zero zero zero zero into the sio base register right zero x zero one into the mailbox control register wait right zero x zero d instead four bidirectional core synchronization we cleared the queue full flag buy writing one into the status clear register after configuring mailbox entry limits and tuning free are toss task priorities on the c p u core the datalogger routed twenty six thousand inter processor messages across thirty hours without mailbox deadlocks or task starvation events",
        "refined_text": "Our dual-core industrial datalogger experienced inter-processor deadlock and task starvation during simultaneous peripheral streaming. Over OpenOCD we tapped hardware event flags and tracked core mailbox lockups across 10 inter-core benchmark trials. The secondary core stopped responding because inter-processor first-in first-out buffers overflowed during concurrent write attempts while the inter-core driver lacked buffer allocation, inspecting the queue threshold settings inside sio_fifo_mailbox module instead.\n\nAllocate the inter-processor mailbox queue by reserving 16 FIFO entries instead into the queue table. Write 0xd0000000 into the SIO base register. Write 0x0d instead into the mailbox control register for bidirectional core synchronization. We cleared the queue full flag by writing 1 into the status clear register.\n\nAfter configuring mailbox entry limits and tuning FreeRTOS task priorities on the CPU core, the datalogger routed 26000 inter-processor messages across 30 hours without mailbox deadlocks or task starvation events."
    },
]

print(f"Total candidate samples: {len(batch_184)}")

tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []
all_valid = True

for idx, s in enumerate(batch_184, 1):
    raw = s["raw_asr"].strip()
    ref = s["refined_text"].strip()

    # ASCII check
    try:
        raw.encode("ascii")
        ref.encode("ascii")
    except UnicodeEncodeError as e:
        print(f"Sample {idx} non-ASCII: {e}")
        all_valid = False

    # Leakage check
    if raw.lower() in eval_raws:
        print(f"Sample {idx} raw leaked into sft_eval.json!")
        all_valid = False
    if ref in eval_refs:
        print(f"Sample {idx} ref leaked into sft_eval.json!")
        all_valid = False

    # Validator check with min_noise_layers=4
    val_ok, val_reason = validator.validate_pair(s, min_noise_layers=4)
    if not val_ok:
        print(f"Sample {idx} failed validate_pair: {val_reason}")
        all_valid = False

    # Cleaner check
    clean_obj, clean_reason = cleaner.clean_sample(raw, ref)
    if clean_obj is None or clean_reason != "kept":
        print(f"Sample {idx} failed clean_sample: {clean_reason}")
        all_valid = False

    words = len(ref.split())
    nl = validator.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tier_counts["short"] += 1
        if "\n" in ref:
            print(f"Sample {idx} has newline in short tier!")
            all_valid = False
        sentences = [sent for sent in re.split(r'[.!?]+', ref) if sent.strip()]
        if len(sentences) != 1:
            print(f"Sample {idx} short tier sentences: {len(sentences)}")
            all_valid = False
        if nl < 3:
            print(f"Sample {idx} short tier active layers < 3 ({nl})")
            all_valid = False
    elif words < 90:
        tier_counts["medium"] += 1
        sentences = [sent for sent in re.split(r'[.!?]+', ref) if sent.strip()]
        if not (1 <= len(sentences) <= 3):
            print(f"Sample {idx} medium tier sentences: {len(sentences)}")
            all_valid = False
        if "\n\n" not in ref:
            print(f"Sample {idx} medium tier missing paragraph break!")
            all_valid = False
        if nl < 4:
            print(f"Sample {idx} medium tier active layers < 4 ({nl})")
            all_valid = False
    else:
        tier_counts["long"] += 1
        if "\n\n" not in ref:
            print(f"Sample {idx} long tier missing paragraph break!")
            all_valid = False
        if nl < 4:
            print(f"Sample {idx} long tier active layers < 4 ({nl})")
            all_valid = False

print(f"Tier counts: {tier_counts}")
print(f"Noise layers per sample: {layer_counts}")
avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Average noise layers: {avg_layers:.2f}")

batch_ok, batch_msg, batch_meta = validator.validate_batch(
    batch_184, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
)
print(f"Batch validation: ok={batch_ok}, msg={batch_msg}")
print(f"Batch meta: {batch_meta}")

if all_valid and batch_ok:
    out_path = Path("scratch/subagent_batch_184.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch_184, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved 20 verified samples to {out_path}")
else:
    print("FAILED VALIDATION!")
    sys.exit(1)
