import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batch_109 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Avoid dotted filenames and internal periods.
    # Avoid backticks.
    # =========================================================================

    # Sample 1: STM32H7 High-resolution timer dead-time insertion
    {
        "raw_asr": "configur the high resolution timer dead time register buy loading thirty two clock ticks into the delay counter",
        "refined_text": "Configure the high-resolution timer dead-time register by loading 32 clock ticks into the delay counter."
    },

    # Sample 2: TI TMS320F28379D ePWM trip-zone action register
    {
        "raw_asr": "uh initializ the enhanced pulse width modulation trip zone register buy writing zero x four zero into the action mask",
        "refined_text": "Initialize the enhanced pulse-width modulation trip-zone register by writing 0x40 into the action mask."
    },

    # Sample 3: Nordic nRF9160 low-power modem UART prescaler
    {
        "raw_asr": "calibrat the low power cellular modem serial prescaler register buy writing sixteen clock cycles into the timing register",
        "refined_text": "Calibrate the low-power cellular modem serial prescaler register by writing 16 clock cycles into the timing register."
    },

    # Sample 4: Microchip PIC32MZ DMA channel burst termination
    {
        "raw_asr": "terminat the direct memory access channel burst transfer buy clearing channel bit eight inside the control register",
        "refined_text": "Terminate the direct memory access channel burst transfer by clearing channel bit 8 inside the control register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Avoid backticks.
    # =========================================================================

    # Sample 5: Silicon Labs EFR32MG24 BLE / Zigbee packet buffer
    {
        "raw_asr": "um configur the zigbee radio frame filter receive buffer size buy writing sixty four wait write one two eight bytes instead into the device descriptor register four high throughput mesh routing the peripheral controller manages incoming frames buy servicing eight hardware buffer interrupts",
        "refined_text": "Configure the Zigbee radio frame filter receive buffer size by writing 128 bytes instead into the device descriptor register for high-throughput mesh routing.\n\nThe peripheral controller manages incoming frames by servicing 8 hardware buffer interrupts."
    },

    # Sample 6: STM32F7 QSPI memory-mapped mode configuration
    {
        "raw_asr": "uh synchronizat the quad serial peripheral interface memory mapped prescaler buy loading sixteen wait load eight clock cycles instead into the control timing register four high speed flash execution the bus controller validates read transactions buy monitoring four transfer status flags",
        "refined_text": "Synchronize the quad serial peripheral interface memory-mapped prescaler by loading 8 clock cycles instead into the control timing register for high-speed flash execution.\n\nThe bus controller validates read transactions by monitoring 4 transfer status flags."
    },

    # Sample 7: NXP S32K144 FlexCAN FD filter mask
    {
        "raw_asr": "calibrat the flexible controller area network filter identifier mask buy writing zero x zero one wait write zero x zero f instead into the acceptance mask register four automotive bus arbitration the message controller filters diagnostic frames buy routing thirty two message mailboxes",
        "refined_text": "Calibrate the flexible controller area network filter identifier mask by writing 0x0f instead into the acceptance mask register for automotive bus arbitration.\n\nThe message controller filters diagnostic frames by routing 32 message mailboxes."
    },

    # Sample 8: Renesas RA6M4 hardware cryptographic accelerator engine
    {
        "raw_asr": "allocat the hardware cryptographic accelerator key slot buffer buy assigning one two eight wait write two five six bits instead into the cipher key control register four secure cryptographic operations the security coprocessor accelerates data encryption buy servicing sixteen cryptographic channels",
        "refined_text": "Allocate the hardware cryptographic accelerator key slot buffer by assigning 256 bits instead into the cipher key control register for secure cryptographic operations.\n\nThe security coprocessor accelerates data encryption by servicing 16 cryptographic channels."
    },

    # Sample 9: Microchip SAM E54 Ethernet MAC DMA descriptor ring
    {
        "raw_asr": "terminat the ethernet media access controller descriptor allocation buy writing twenty wait write forty descriptors instead into the receive ring buffer register four network traffic handling the ethernet peripheral streams incoming packets buy transmitting sixty four network frames",
        "refined_text": "Terminate the Ethernet media access controller descriptor allocation by writing 40 descriptors instead into the receive ring buffer register for network traffic handling.\n\nThe Ethernet peripheral streams incoming packets by transmitting 64 network frames."
    },

    # Sample 10: Analog Devices ADSP-SC589 dual-core SHARC inter-core FIFO
    {
        "raw_asr": "uh operat the digital signal processor inter core message queue buy loading two hundred wait load five hundred twelve words instead into the buffer depth register four high bandwidth data streaming the secondary processing core exchanges audio telemetry buy polling eight inter core interrupt flags",
        "refined_text": "Operate the digital signal processor inter-core message queue by loading 512 words instead into the buffer depth register for high-bandwidth data streaming.\n\nThe secondary processing core exchanges audio telemetry by polling 8 inter-core interrupt flags."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2-3 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Avoid backticks.
    # =========================================================================

    # Sample 11: STM32H7 Dual-Core (Cortex-M7 & Cortex-M4) Shared D2 SRAM Cache Coherency and MDMA Stalls
    {
        "raw_asr": "our stm thirty two h seven dual core controller experienced severe data corruption during high speed analog data logging we attached a segger j link probe two the swd interface and analyzed bus arbitration inside the d two domain s r a m the cortex m seven core corrupted shared sample buffers because data cache write backs overwrote descriptor tables while the master direct memory access driver lacked memory barrier synchronizat wait inspect the cache policy inside mpu underscore config module instead configur the memory protection unit region buy assigning thirty two kilobytes wait sixty four kilobytes instead into the region size field right zero x three zero zero zero zero zero zero zero into the region base address register right zero x zero three into the access permission register wait right zero x zero seven instead four shared non cacheable device buffer access we cleared the bus fault error flag buy writing one into the fault status register after reconfiguring the memory protection unit and invalidating cached descriptors the dual core controller captured four thousand continuous analog blocks across twenty four hours without data corruption or direct memory access bus stalls",
        "refined_text": "Our STM32H7 dual-core controller experienced severe data corruption during high-speed analog data logging. We attached a SEGGER J-Link probe to the SWD interface and analyzed bus arbitration inside the D2 domain SRAM. The Cortex-M7 core corrupted shared sample buffers because data cache write-backs overwrote descriptor tables while the master direct memory access driver lacked memory barrier synchronization, inspecting the cache policy inside mpu_config module instead.\n\nConfigure the memory protection unit region by assigning 64 kilobytes instead into the region size field. Write 0x30000000 into the region base address register. Write 0x07 instead into the access permission register for shared non-cacheable device buffer access. We cleared the bus fault error flag by writing 1 into the fault status register.\n\nAfter reconfiguring the memory protection unit and invalidating cached descriptors, the dual-core controller captured 4000 continuous analog blocks across 24 hours without data corruption or direct memory access bus stalls."
    },

    # Sample 12: NXP i.MX RT1060 FlexSPI Octal Flash XIP Cache Thrashing and Bus Faults
    {
        "raw_asr": "uh our n x p r t ten sixty crossover processor raised imprecise bus faults during concurrent audio streaming and flash firmware execution we connected open o c d over the debug probe and captured trace data across the core fault status register the central processing unit halted because flex serial peripheral interface burst reads stalled when direct memory access transfers competed four bus matrix priority while the execution driver lacked cache prefetch configur wait inspect the watermark logic inside flexspi underscore driver module instead configur the flexible serial peripheral interface prefetch buffer buy writing thirty two wait write sixty four bytes instead into the buffer configuration register right zero x four zero zero two zero zero zero zero into the peripheral base address register right zero x zero two into the watermark level register wait right zero x zero six instead four low latency instruction streaming we cleared the bus error flag buy writing one into the status clear register after tuning the prefetch buffer depth and elevating instruction cache priority the processor streamed six thousand audio frames across eighteen hours without bus exceptions or audio buffer dropouts",
        "refined_text": "Our NXP RT1060 crossover processor raised imprecise bus faults during concurrent audio streaming and flash firmware execution. We connected OpenOCD over the debug probe and captured trace data across the core fault status register. The central processing unit halted because flex serial peripheral interface burst reads stalled when direct memory access transfers competed for bus matrix priority while the execution driver lacked cache prefetch configuration, inspecting the watermark logic inside flexspi_driver module instead.\n\nConfigure the flexible serial peripheral interface prefetch buffer by writing 64 bytes instead into the buffer configuration register. Write 0x40020000 into the peripheral base address register. Write 0x06 instead into the watermark level register for low-latency instruction streaming. We cleared the bus error flag by writing 1 into the status clear register.\n\nAfter tuning the prefetch buffer depth and elevating instruction cache priority, the processor streamed 6000 audio frames across 18 hours without bus exceptions or audio buffer dropouts."
    },

    # Sample 13: Texas Instruments TMS320F28379D Dual-Core C2000 CLA Task Overrun and Inter-Core Message RAM Deadlock
    {
        "raw_asr": "um our texas instruments t m s three two zero f two eight three seven nine d digital signal controller suffered task deadline misses during high frequency inverter switching we attached a digital oscilloscope two the pulse width modulation outputs and monitored execution status flags inside the control law accelerator register the coprocessor aborted execution because field oriented control trigonometry calculations exceeded the allocated interrupt window while the control loop driver lacked timing calibrat wait inspect the task trigger logic inside cla underscore control module instead configur the control law accelerator task trigger prescaler buy loading sixteen clock cycles wait thirty two clock cycles instead into the task timing register right zero x zero zero one zero into the message ram memory control register right zero x zero one into the task enable register wait right zero x zero three instead four simultaneous dual axis motor control we cleared the task overrun interrupt flag buy writing one into the execution status clear register after increasing the task trigger prescaler and optimizing trigonometric instructions the motor controller processed eight thousand torque control loops across twelve hours without timing overruns or phase current oscillations",
        "refined_text": "Our Texas Instruments TMS320F28379D digital signal controller suffered task deadline misses during high-frequency inverter switching. We attached a digital oscilloscope to the pulse-width modulation outputs and monitored execution status flags inside the control law accelerator register. The coprocessor aborted execution because field-oriented control trigonometry calculations exceeded the allocated interrupt window while the control loop driver lacked timing calibration, inspecting the task trigger logic inside cla_control module instead.\n\nConfigure the control law accelerator task trigger prescaler by loading 32 clock cycles instead into the task timing register. Write 0x0010 into the message RAM memory control register. Write 0x03 instead into the task enable register for simultaneous dual-axis motor control. We cleared the task overrun interrupt flag by writing 1 into the execution status clear register.\n\nAfter increasing the task trigger prescaler and optimizing trigonometric instructions, the motor controller processed 8000 torque control loops across 12 hours without timing overruns or phase current oscillations."
    },

    # Sample 14: Nordic Semiconductor nRF52840 USB Device Controller (USBD) Endpoint ISO Underflow during BLE Audio
    {
        "raw_asr": "uh our nordic n r f fifty two eight forty wireless audio bridge suffered frequent audio packet dropouts during concurrent bluetooth and usb streaming we connected a hardware protocol analyzer two the usb bus pins and captured packet timing inside the endpoint status registers the usb peripheral dropped audio frames because bluetooth low energy radio interrupts delayed endpoint data transfers while the usb audio driver lacked double buffer allocat wait inspect the endpoint configuration inside usbd underscore audio module instead configur the usb isochronous endpoint buffer size buy writing one hundred twenty eight wait write two hundred fifty six bytes instead into the endpoint maximum packet register right zero x two zero zero zero eight zero zero zero into the easy direct memory access buffer pointer register right zero x zero two into the isochronous split register wait right zero x zero six instead four continuous double buffered audio transfers we cleared the underflow event flag buy writing one into the events clear register after doubling the endpoint buffer capacity and elevating the usb interrupt priority the wireless audio system streamed five thousand voice frames across sixteen hours without underflow events or audible sound artifacts",
        "refined_text": "Our Nordic nRF52840 wireless audio bridge suffered frequent audio packet dropouts during concurrent Bluetooth and USB streaming. We connected a hardware protocol analyzer to the USB bus pins and captured packet timing inside the endpoint status registers. The USB peripheral dropped audio frames because Bluetooth low energy radio interrupts delayed endpoint data transfers while the USB audio driver lacked double buffer allocation, inspecting the endpoint configuration inside usbd_audio module instead.\n\nConfigure the USB isochronous endpoint buffer size by writing 256 bytes instead into the endpoint maximum packet register. Write 0x20008000 into the Easy direct memory access buffer pointer register. Write 0x06 instead into the isochronous split register for continuous double-buffered audio transfers. We cleared the underflow event flag by writing 1 into the events clear register.\n\nAfter doubling the endpoint buffer capacity and elevating the USB interrupt priority, the wireless audio system streamed 5000 voice frames across 16 hours without underflow events or audible sound artifacts."
    },

    # Sample 15: Microchip SAM E70 High-Performance Cortex-M7 Cortex Cache Coherence and GMAC Ethernet Packet Corruption
    {
        "raw_asr": "um our microchip s a m e seventy network gateway encountered corrupted payload checksums during sustained ethernet transmission we captured network traces buy running wi re shark and inspected descriptor queues inside the arm cortex m seven memory the ethernet controller transmitted invalid frames because the core data cache performed dirty line write backs over direct memory access descriptor buffers while the network driver lacked cache boundary separat wait inspect the memory mapping inside gmac underscore driver module instead configur the memory protection unit ethernet buffer region buy assigning thirty two kilobytes wait sixty four kilobytes instead into the region size register right zero x two zero four zero zero zero zero zero into the region base address register right zero x zero one into the cache attribute register wait right zero x zero five instead four non cacheable write through descriptor access we cleared the transmit status error flag buy writing one into the status clear register after establishing non cacheable buffer attributes and reordering descriptor flushes the network gateway routed seven thousand ethernet packets across twenty four hours without corrupted checksums or frame dropouts",
        "refined_text": "Our Microchip SAM E70 network gateway encountered corrupted payload checksums during sustained Ethernet transmission. We captured network traces by running Wireshark and inspected descriptor queues inside the ARM Cortex-M7 memory. The Ethernet controller transmitted invalid frames because the core data cache performed dirty line write-backs over direct memory access descriptor buffers while the network driver lacked cache boundary separation, inspecting the memory mapping inside gmac_driver module instead.\n\nConfigure the memory protection unit Ethernet buffer region by assigning 64 kilobytes instead into the region size register. Write 0x20400000 into the region base address register. Write 0x05 instead into the cache attribute register for non-cacheable write-through descriptor access. We cleared the transmit status error flag by writing 1 into the status clear register.\n\nAfter establishing non-cacheable buffer attributes and reordering descriptor flushes, the network gateway routed 7000 Ethernet packets across 24 hours without corrupted checksums or frame dropouts."
    },

    # Sample 16: Espressif ESP32-S3 Dual-Core Xtensa FreeRTOS Core 1 Task Watchdog and Flash Cache MMU Thrashing
    {
        "raw_asr": "uh our esp thirty two s three edge computing device triggered repeated task watchdog resets during on device neural network inference we attached open o c d over the internal usb jtag port and examined thread execution logs inside free are toss the watchdog timer triggered a hard reset because external flash cache misses delayed the vision inference task on core one while the lower priority idle task starved while the scheduler driver lacked yield communicat wait inspect the watchdog parameters inside twdt underscore monitor module instead configur the task watchdog timeout threshold buy writing two thousand milliseconds wait four thousand milliseconds instead into the timeout period register right zero x zero zero zero one into the task watchdog enable register right zero x zero two into the core interrupt mask wait right zero x zero six instead four dual core task monitoring we cleared the watchdog event flag buy writing one into the reset reason register after increasing the task watchdog timeout and yielding the inference loop during flash cache prefetch operations the edge device executed nine thousand model inference passes across twenty hours without watchdog timeouts or processor resets",
        "refined_text": "Our ESP32-S3 edge computing device triggered repeated task watchdog resets during on-device neural network inference. We attached OpenOCD over the internal USB-JTAG port and examined thread execution logs inside FreeRTOS. The watchdog timer triggered a hard reset because external flash cache misses delayed the vision inference task on Core 1 while the lower-priority idle task starved while the scheduler driver lacked yield communication, inspecting the watchdog parameters inside twdt_monitor module instead.\n\nConfigure the task watchdog timeout threshold by writing 4000 milliseconds instead into the timeout period register. Write 0x0001 into the task watchdog enable register. Write 0x06 instead into the core interrupt mask for dual-core task monitoring. We cleared the watchdog event flag by writing 1 into the reset reason register.\n\nAfter increasing the task watchdog timeout and yielding the inference loop during flash cache prefetch operations, the edge device executed 9000 model inference passes across 20 hours without watchdog timeouts or processor resets."
    },

    # Sample 17: Renesas RA4M3 High-Resolution Timer and ADC Trigger Skew in Motor Phase Current Sensing
    {
        "raw_asr": "um our renesas r a four m three motor drive inverter triggered false overcurrent protection trips during initial vector acceleration we connected a four channel mixed signal oscilloscope two the motor phase lines and captured analog to digital converter sampling interrupts the microcontroller aborted pulse width modulation output because high frequency inverter switching noise distorted phase current measurements while the sampling driver lacked delay calibrat wait inspect the sampling timing inside current underscore sense module instead configur the analog to digital converter delay trigger buy loading forty clock cycles wait eighty clock cycles instead into the trigger delay register right zero x zero zero four zero into the converter mode register right zero x zero one into the noise filter register wait right zero x zero five instead four robust phase current acquisition we cleared the overcurrent trip flag buy writing one into the fault clear register after delaying the conversion trigger past switching ringing and enabling the hardware digital filter the motor drive controller performed five thousand velocity cycles across sixteen hours without overcurrent trips or phase current distortion",
        "refined_text": "Our Renesas RA4M3 motor drive inverter triggered false overcurrent protection trips during initial vector acceleration. We connected a 4-channel mixed-signal oscilloscope to the motor phase lines and captured analog-to-digital converter sampling interrupts. The microcontroller aborted pulse-width modulation output because high-frequency inverter switching noise distorted phase current measurements while the sampling driver lacked delay calibration, inspecting the sampling timing inside current_sense module instead.\n\nConfigure the analog-to-digital converter delay trigger by loading 80 clock cycles instead into the trigger delay register. Write 0x0040 into the converter mode register. Write 0x05 instead into the noise filter register for robust phase current acquisition. We cleared the overcurrent trip flag by writing 1 into the fault clear register.\n\nAfter delaying the conversion trigger past switching ringing and enabling the hardware digital filter, the motor drive controller performed 5000 velocity cycles across 16 hours without overcurrent trips or phase current distortion."
    },

    # Sample 18: Silicon Labs EFM32 Giant Gecko Low-Energy UART (LEUART) Clock Resynchronization Drift in EM2 Deep Sleep
    {
        "raw_asr": "uh our silicon labs e f m thirty two giant gecko telemetry board dropped incoming framing bytes when waking from low energy sleep mode two we connected a logic analyzer two the serial receive pin and measured baud rate timing across the low energy universal asynchronous receiver transmitter the peripheral produced framing errors because the low frequency crystal oscillator drifted during voltage regulator wake up transitions while the communication driver lacked pulse width synchronizat wait inspect the start frame settings inside leuart underscore driver module instead configur the low energy serial receiver clock divider buy loading sixteen wait load thirty two clock ticks instead into the prescaler register right zero x zero one zero zero into the baud rate control register right zero x zero two into the wake up delay register wait right zero x zero six instead four reliable frame edge detection we cleared the framing error flag buy writing one into the command clear register after increasing the receiver prescaler and extending the wake up stabilization interval the telemetry board processed six thousand serial sensor packets across twenty four hours without framing errors or dropped wake up bytes",
        "refined_text": "Our Silicon Labs EFM32 Giant Gecko telemetry board dropped incoming framing bytes when waking from low-energy sleep mode 2. We connected a logic analyzer to the serial receive pin and measured baud rate timing across the low-energy universal asynchronous receiver transmitter. The peripheral produced framing errors because the low-frequency crystal oscillator drifted during voltage regulator wake-up transitions while the communication driver lacked pulse width synchronization, inspecting the start frame settings inside leuart_driver module instead.\n\nConfigure the low-energy serial receiver clock divider by loading 32 clock ticks instead into the prescaler register. Write 0x0100 into the baud rate control register. Write 0x06 instead into the wake-up delay register for reliable frame edge detection. We cleared the framing error flag by writing 1 into the command clear register.\n\nAfter increasing the receiver prescaler and extending the wake-up stabilization interval, the telemetry board processed 6000 serial sensor packets across 24 hours without framing errors or dropped wake-up bytes."
    },

    # Sample 19: Raspberry Pi RP2040 Dual-Core Cortex-M0+ PIO State Machine FIFO Deadlock in DVI Video Output
    {
        "raw_asr": "um our r p twenty forty dual core display module suffered display tearing and frozen video frames during high resolution graphics output we connected a picoprobe debugger two the swd interface and analyzed fifo status inside the programmable input output state machine the video engine stalled because direct memory access channels failed two replenish the state machine fifo buffer during flash bus contention while the display driver lacked fifo depth configur wait inspect the buffer joining settings inside pio underscore video module instead configur the programmable input output state machine buffer buy joining the receive and transmit fifos into eight wait write sixteen words instead inside the state machine configuration register right zero x zero zero two zero into the clock divider register right zero x zero one into the execution control register wait right zero x zero three instead four autonomous transition generation we cleared the underflow stall flag buy writing one into the interrupt clear register after joining the fifo buffers and assigning maximum direct memory access bus priority the graphics module delivered ten thousand video frames across twelve hours without display tearing or state machine underflows",
        "refined_text": "Our RP2040 dual-core display module suffered display tearing and frozen video frames during high-resolution graphics output. We connected a Picoprobe debugger to the SWD interface and analyzed FIFO status inside the programmable input output state machine. The video engine stalled because direct memory access channels failed to replenish the state machine FIFO buffer during flash bus contention while the display driver lacked FIFO depth configuration, inspecting the buffer joining settings inside pio_video module instead.\n\nConfigure the programmable input output state machine buffer by joining the receive and transmit FIFOs into 16 words instead inside the state machine configuration register. Write 0x0020 into the clock divider register. Write 0x03 instead into the execution control register for autonomous transition generation. We cleared the underflow stall flag by writing 1 into the interrupt clear register.\n\nAfter joining the FIFO buffers and assigning maximum direct memory access bus priority, the graphics module delivered 10000 video frames across 12 hours without display tearing or state machine underflows."
    },

    # Sample 20: Infineon PSoC 62 Dual-Core (Cortex-M4 / Cortex-M0+) IPC Semaphore Deadlock in BLE Mesh Provisioning
    {
        "raw_asr": "uh our infineon p soc sixty two dual core microcontroller suffered inter core lockups during bluetooth mesh device provisioning we attached a hardware debug probe two the serial wire debug interface and inspected hardware semaphores inside the inter processor communication peripheral the application core froze because cortex m four acquired a shared flash lock while cortex m zero plus held the crypto accelerator mutex without releasing ownership while the security driver lacked lock release communicat wait inspect the semaphore timeout logic inside ipc underscore lock module instead configur the inter processor communication semaphore timeout buy loading thirty two wait load sixty four milliseconds instead into the semaphore timeout register right zero x zero zero eight zero into the ipc channel acquire register right zero x zero two into the lock interrupt mask wait right zero x zero six instead four non blocking lock acquisition we cleared the semaphore deadlock flag buy writing one into the lock status register after implementing semaphore timeout polling and releasing locked channels during crypto interrupts the dual core system provisioned four thousand mesh nodes across twenty hours without inter core lockups or communication freezes",
        "refined_text": "Our Infineon PSoC 62 dual-core microcontroller suffered inter-core lockups during Bluetooth mesh device provisioning. We attached a hardware debug probe to the serial wire debug interface and inspected hardware semaphores inside the inter-processor communication peripheral. The application core froze because Cortex-M4 acquired a shared flash lock while Cortex-M0+ held the crypto accelerator mutex without releasing ownership while the security driver lacked lock release communication, inspecting the semaphore timeout logic inside ipc_lock module instead.\n\nConfigure the inter-processor communication semaphore timeout by loading 64 milliseconds instead into the semaphore timeout register. Write 0x0080 into the IPC channel acquire register. Write 0x06 instead into the lock interrupt mask for non-blocking lock acquisition. We cleared the semaphore deadlock flag by writing 1 into the lock status register.\n\nAfter implementing semaphore timeout polling and releasing locked channels during crypto interrupts, the dual-core system provisioned 4000 mesh nodes across 20 hours without inter-core lockups or communication freezes."
    }
]

print("=== RUNNING LOCAL DETERMINISTIC VALIDATION ===")

all_clean = True
tier_counts = {"short": 0, "medium": 0, "long": 0}

for i, p in enumerate(batch_109):
    raw = p["raw_asr"]
    ref = p["refined_text"]
    words = len(ref.split())
    if words < 25:
        tier = "short"
    elif words < 90:
        tier = "medium"
    else:
        tier = "long"
    tier_counts[tier] += 1

    # Check leakage
    if raw.lower() in eval_raws:
        print(f"Sample {i+1}: FAILED eval leakage on raw_asr!")
        all_clean = False
    if ref in eval_refs:
        print(f"Sample {i+1}: FAILED eval leakage on refined_text!")
        all_clean = False

    # Check cleaner
    res, status = clean_sample(raw, ref)
    if not res or status != "kept":
        print(f"Sample {i+1} ({tier}, {words} words): FAILED cleaner - {status}")
        all_clean = False
    else:
        # Check validator
        v_ok, v_msg = validate_pair(p)
        if not v_ok:
            print(f"Sample {i+1} ({tier}, {words} words): FAILED validator - {v_msg}")
            all_clean = False
        else:
            print(f"Sample {i+1} ({tier}, {words} words): PASSED (cleaner: {status}, validator: {v_msg})")

print(f"\nTier counts: {tier_counts}")

# Check batch validator
b_ok, b_msg, b_tiers = validate_batch(batch_109, min_short=4, min_medium=6, min_long=10)
print(f"validate_batch: {b_ok} - {b_msg} (tiers: {b_tiers})")

if all_clean and b_ok:
    out_path = Path("scratch/subagent_batch_109.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch_109, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESS: Exactly 20 samples verified and written to {out_path}")
else:
    print("\nFAILED: Validation errors detected!")
    sys.exit(1)
