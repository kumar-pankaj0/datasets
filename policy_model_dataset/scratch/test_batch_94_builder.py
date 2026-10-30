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

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Avoid dotted filenames and internal periods.
    # Avoid backticks.
    # =========================================================================

    # Sample 1: STM32H753 Precision Time Protocol (PTP) clock subsecond increment register
    {
        "raw_asr": "um calibrat the precision time protocol clock buy loading forty into the subsecond increment register",
        "refined_text": "Calibrate the precision time protocol clock by loading 40 into the subsecond increment register."
    },

    # Sample 2: TI CC2652R RF crystal oscillator control register
    {
        "raw_asr": "configur the radio frequency crystal oscillator buy writing thirty two into the oscillator control register",
        "refined_text": "Configure the radio frequency crystal oscillator by writing 32 into the oscillator control register."
    },

    # Sample 3: NXP RT1060 FlexSPI baud rate divisor register
    {
        "raw_asr": "uh initializ the serial peripheral flash interface buy writing zero x zero four into the clock divisor register",
        "refined_text": "Initialize the serial peripheral flash interface by writing 0x04 into the clock divisor register."
    },

    # Sample 4: Microchip SAMD21 Direct Memory Access trigger source register
    {
        "raw_asr": "terminat the direct memory access channel buy writing sixteen into the channel trigger register",
        "refined_text": "Terminate the direct memory access channel by writing 16 into the channel trigger register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Avoid backticks.
    # =========================================================================

    # Sample 5: Nordic nRF52840 QSPI external flash read delay timing
    {
        "raw_asr": "configur the quad serial peripheral interface read delay buy setting two wait set three clock cycles instead into the read delay register four external memory transfers um the memory controller synchronizat external flash access buy latching serial data lines across four high speed io pins",
        "refined_text": "Configure the quad serial peripheral interface read delay by setting 3 clock cycles instead into the read delay register for external memory transfers.\n\nThe memory controller synchronizes external flash access by latching serial data lines across 4 high-speed IO pins."
    },

    # Sample 6: Espressif ESP32-H2 IEEE 802.15.4 sleep timer prescaler
    {
        "raw_asr": "uh calibrat the low power sleep timer prescaler buy writing sixty four wait write one hundred twenty eight into the timer divisor register instead four thread mesh networking um the wireless modem maintains sleep synchronizat buy updating beacon timestamp counters across eight periodic wake intervals",
        "refined_text": "Calibrate the low-power sleep timer prescaler by writing 128 into the timer divisor register instead for Thread mesh networking.\n\nThe wireless modem maintains sleep synchronization by updating beacon timestamp counters across 8 periodic wake intervals."
    },

    # Sample 7: STMicroelectronics STM32F407 CAN bus baud prescaler
    {
        "raw_asr": "initializ the controller area network bit timing buy writing twelve wait right six into the baud prescaler register instead four vehicle telemetry streaming um the communication transceiver filters incoming sensor frames buy matching message identifiers across fourteen acceptance filter banks",
        "refined_text": "Initialize the controller area network bit timing by writing 6 into the baud prescaler register instead for vehicle telemetry streaming.\n\nThe communication transceiver filters incoming sensor frames by matching message identifiers across 14 acceptance filter banks."
    },

    # Sample 8: Microchip dsPIC33CK dual high-speed PWM dead-time generator
    {
        "raw_asr": "configur the high speed pulse width modulation dead time buy loading sixteen wait load thirty two clock ticks instead into the dead time control register four resonant power conversion um the power stage controller drives switching transistors buy generating complementary gate signals across two half bridge phases",
        "refined_text": "Configure the high-speed pulse-width modulation dead time by loading 32 clock ticks instead into the dead-time control register for resonant power conversion.\n\nThe power stage controller drives complementary gate signals across 2 half-bridge phases."
    },

    # Sample 9: Silicon Labs EFM32 Giant Gecko Low Energy UART baud prescaler
    {
        "raw_asr": "um initializ the low energy universal asynchronous receiver transmitter prescaler buy writing zero x zero two wait right zero x zero four into the clock divisor register instead four low baud sensor communication um the peripheral interface streams environmental telemetry buy servicing receive buffer interrupts across sixteen sample intervals",
        "refined_text": "Initialize the low-energy universal asynchronous receiver transmitter prescaler by writing 0x04 into the clock divisor register instead for low baud sensor communication.\n\nThe peripheral interface streams environmental telemetry by servicing receive buffer interrupts across 16 sample intervals."
    },

    # Sample 10: TI MSP430FR2355 Smart Analog Combo operational amplifier gain register
    {
        "raw_asr": "calibrat the smart analog combo operational amplifier gain buy writing zero x zero eight wait right zero x one zero into the amplifier control register instead four precision current sensing um the analog subsystem measures shunt voltage drops buy routing amplified signals across eight internal analog digital converter channels",
        "refined_text": "Calibrate the smart analog combo operational amplifier gain by writing 0x10 into the amplifier control register instead for precision current sensing.\n\nThe analog subsystem measures shunt voltage drops by routing amplified signals across 8 internal analog digital converter channels."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n (2 to 3 solid paragraphs).
    # Natural spoken engineer narration. Zero numbered checklists.
    # Avoid backticks.
    # =========================================================================

    # Sample 11: NXP LPC55S16 TrustZone Secure Attribution Unit (SAU) and memory partitioning
    {
        "raw_asr": "our l p c fifty five s sixteen microcontroller triggered a secure fault during non secure memory partitioning inside the connected asset tracker we connected a segger j link probe and analyzed core fault status registers inside g d b the security attribution unit asserted a memory management fault because non secure firmware attempted accessing secure static ram blocks while the security driver lacked memory partition configur wait inspect the memory partitioning routine inside sau underscore mpc dot c instead configur the security attribution unit memory region buy setting non secure callable attributes right zero x zero eight into the secure memory control register wait right zero x one zero into the secure memory control register instead two authorize non secure peripheral access we cleared the secure fault flag buy writing one into the fault status register after setting memory partition boundaries and refreshing security registers the microcontroller ran five thousand secure service calls across twenty four hours without security faults or unexpected memory resets",
        "refined_text": "Our LPC55S16 microcontroller triggered a secure fault during non-secure memory partitioning inside the connected asset tracker. We connected a SEGGER J-Link probe and analyzed core fault status registers inside GDB. The security attribution unit asserted a memory management fault because non-secure firmware attempted accessing secure static RAM blocks while the security driver lacked memory partition configuration, inspecting the memory partitioning routine inside sau_mpc.c instead.\n\nConfigure the security attribution unit memory region by setting non-secure callable attributes. Write 0x10 into the secure memory control register instead to authorize non-secure peripheral access. We cleared the secure fault flag by writing 1 into the fault status register.\n\nAfter setting memory partition boundaries and refreshing security registers, the microcontroller ran 5000 secure service calls across 24 hours without security faults or unexpected memory resets."
    },

    # Sample 12: Renesas RA6M5 USB High-Speed DMA descriptor buffer underrun
    {
        "raw_asr": "our r a six m five communication gateway dropped bulk data packets during high speed universal serial bus transfers inside the industrial data logger we connected open o c d over the serial wire debug interface and analyzed transfer descriptors inside free are toss the direct memory access controller flagged a buffer underrun condition because incoming bulk transfer packets exhausted descriptor buffers while the usb driver lacked descriptor ring configur wait inspect the buffer allocation routine inside usb underscore dma dot c instead configur the universal serial bus direct memory access ring buy allocating sixty four bytes into the endpoint transfer buffer right zero x zero four into the transfer control register wait right zero x zero eight into the transfer control register instead two authorize continuous endpoint transfers we cleared the buffer underrun interrupt buy writing one into the interrupt status clear register after allocating descriptor rings and updating transfer control registers the communication gateway streamed eight thousand bulk data frames across sixteen hours without usb packet loss or transfer stalls",
        "refined_text": "Our RA6M5 communication gateway dropped bulk data packets during high-speed universal serial bus transfers inside the industrial data logger. We connected OpenOCD over the serial wire debug interface and analyzed transfer descriptors inside FreeRTOS. The direct memory access controller flagged a buffer underrun condition because incoming bulk transfer packets exhausted descriptor buffers while the USB driver lacked descriptor ring configuration, inspecting the buffer allocation routine inside usb_dma.c instead.\n\nConfigure the universal serial bus direct memory access ring by allocating 64 bytes into the endpoint transfer buffer. Write 0x08 into the transfer control register instead to authorize continuous endpoint transfers. We cleared the buffer underrun interrupt by writing 1 into the interrupt status clear register.\n\nAfter allocating descriptor rings and updating transfer control registers, the communication gateway streamed 8000 bulk data frames across 16 hours without USB packet loss or transfer stalls."
    },

    # Sample 13: STMicroelectronics STM32U585 Low-Power Autonomous Mode (LPBAM) linked-list circular DMA queue
    {
        "raw_asr": "our s t m thirty two u five eight five wearable monitor froze during low power autonomous background sensor acquisition inside the medical tracking patch we connected a segger j link probe and monitored execution states inside g d b the low power background autonomous mode controller halted execution because linked list circular direct memory access descriptors pointed two an unmapped circular buffer node while the sensor driver lacked autonomous queue configur wait inspect the descriptor initialization routine inside lpbam underscore queue dot c instead configur the low power autonomous mode linked list buy setting circular queue descriptors right zero x two zero into the linked list control register wait right zero x four zero into the linked list control register instead two restore continuous background execution we cleared the autonomous mode transfer complete flag buy writing one into the interrupt clear register after relinking circular descriptor nodes and refreshing control registers the wearable monitor gathered seven thousand sensor readings across twenty four hours without autonomous mode freezes or data queue interruptions",
        "refined_text": "Our STM32U585 wearable monitor froze during low-power autonomous background sensor acquisition inside the medical tracking patch. We connected a SEGGER J-Link probe and monitored execution states inside GDB. The low-power background autonomous mode controller halted execution because linked-list circular direct memory access descriptors pointed to an unmapped circular buffer node while the sensor driver lacked autonomous queue configuration, inspecting the descriptor initialization routine inside lpbam_queue.c instead.\n\nConfigure the low-power autonomous mode linked list by setting circular queue descriptors. Write 0x40 into the linked list control register instead to restore continuous background execution. We cleared the autonomous mode transfer complete flag by writing 1 into the interrupt clear register.\n\nAfter relinking circular descriptor nodes and refreshing control registers, the wearable monitor gathered 7000 sensor readings across 24 hours without autonomous mode freezes or data queue interruptions."
    },

    # Sample 14: Raspberry Pi RP2350 RISC-V Hazard3 dual-core inter-processor mailbox & spinlock
    {
        "raw_asr": "our r p two three five zero dual core board locked up during inter processor data exchange inside the digital signal synthesizer we connected open o c d over the r i s c v debug adapter and analyzed execution states across both hazard three cores core one stalled indefinitely because core zero acquired hardware spinlock eight without releasing the lock during inter core mailbox writes while the system firmware lacked spinlock timeout configur wait inspect the mailbox synchronization routine inside mailbox underscore sync dot c instead configur the inter processor mailbox channel buy setting message depth right zero x zero two into the spinlock clear register wait right zero x zero four into the spinlock clear register instead two clear hardware lock ownership we cleared the mailbox interrupt request buy writing one into the interrupt acknowledgment register after adjusting mailbox queue depths and releasing spinlock resources the dual core board processed six thousand audio samples across twelve hours without hardware lockups or core communication deadlocks",
        "refined_text": "Our RP2350 dual-core board locked up during inter-processor data exchange inside the digital signal synthesizer. We connected OpenOCD over the RISC-V debug adapter and analyzed execution states across both Hazard3 cores. Core 1 stalled indefinitely because core 0 acquired hardware spinlock 8 without releasing the lock during inter-core mailbox writes while the system firmware lacked spinlock timeout configuration, inspecting the mailbox synchronization routine inside mailbox_sync.c instead.\n\nConfigure the inter-processor mailbox channel by setting message depth. Write 0x04 into the spinlock clear register instead to clear hardware lock ownership. We cleared the mailbox interrupt request by writing 1 into the interrupt acknowledgment register.\n\nAfter adjusting mailbox queue depths and releasing spinlock resources, the dual-core board processed 6000 audio samples across 12 hours without hardware lockups or core communication deadlocks."
    },

    # Sample 15: Infineon AURIX TC397 Automotive multicore lockstep safety watchdog trip
    {
        "raw_asr": "our t c three nine seven automotive electronic control unit suffered unexpected safety resets during high speed torque arbitration inside the hybrid powertrain controller we attached a logic analyzer two the safety reset line and analyzed core fault status registers inside g d b the safety watchdog timer asserted a fault condition because background core execution exceeded the heartbeat timing window while the safety firmware lacked watchdog refresh configur wait inspect the watchdog servicing routine inside safety underscore wdt dot c instead configur the automotive safety watchdog window buy setting the valid refresh threshold right zero x two zero into the watchdog control register wait right zero x four zero into the watchdog control register instead two authorize core heartbeat execution we cleared the safety fault status flag buy writing one into the error clear register after adjusting watchdog window thresholds and refreshing heartbeat control registers the control unit processed nine thousand torque calculation cycles across twenty four hours without safety resets or watchdog timeouts",
        "refined_text": "Our TC397 automotive electronic control unit suffered unexpected safety resets during high-speed torque arbitration inside the hybrid powertrain controller. We attached a logic analyzer to the safety reset line and analyzed core fault status registers inside GDB. The safety watchdog timer asserted a fault condition because background core execution exceeded the heartbeat timing window while the safety firmware lacked watchdog refresh configuration, inspecting the watchdog servicing routine inside safety_wdt.c instead.\n\nConfigure the automotive safety watchdog window by setting the valid refresh threshold. Write 0x40 into the watchdog control register instead to authorize core heartbeat execution. We cleared the safety fault status flag by writing 1 into the error clear register.\n\nAfter adjusting watchdog window thresholds and refreshing heartbeat control registers, the control unit processed 9000 torque calculation cycles across 24 hours without safety resets or watchdog timeouts."
    },

    # Sample 16: Analog Devices ADuCM4050 Ultra-low-power biomedical analog front-end SPI FIFO overflow
    {
        "raw_asr": "our a d u c m four zero five zero sensor node dropped biomedical telemetry during serial peripheral interface data transfers inside the patient health monitor we connected a segger j link probe and analyzed buffer status registers inside free are toss the serial receiver raised a fifo overflow interrupt because the direct memory access controller failed two drain incoming telemetry bytes before buffer limits were exceeded while the sensor driver lacked dma trigger configur wait inspect the transfer initialization routine inside afe underscore spi dot c instead configur the serial peripheral interface direct memory access trigger buy writing sixteen bytes into the fifo threshold register right zero x zero eight into the serial control register wait right zero x one zero into the serial control register instead two enable continuous dma streaming we cleared the overflow interrupt flag buy writing one into the status clear register after configuring fifo threshold levels and enabling continuous dma streaming the sensor node acquired five thousand electrocardiogram frames across eighteen hours without fifo overflows or telemetry corruption",
        "refined_text": "Our ADuCM4050 sensor node dropped biomedical telemetry during serial peripheral interface data transfers inside the patient health monitor. We connected a SEGGER J-Link probe and analyzed buffer status registers inside FreeRTOS. The serial receiver raised a FIFO overflow interrupt because the direct memory access controller failed to drain incoming telemetry bytes before buffer limits were exceeded while the sensor driver lacked DMA trigger configuration, inspecting the transfer initialization routine inside afe_spi.c instead.\n\nConfigure the serial peripheral interface direct memory access trigger by writing 16 bytes into the FIFO threshold register. Write 0x10 into the serial control register instead to enable continuous DMA streaming. We cleared the overflow interrupt flag by writing 1 into the status clear register.\n\nAfter configuring FIFO threshold levels and enabling continuous DMA streaming, the sensor node acquired 5000 electrocardiogram frames across 18 hours without FIFO overflows or telemetry corruption."
    },

    # Sample 17: Nordic nRF9160 LTE-M / NB-IoT modem trace UART baud rate desynchronization
    {
        "raw_asr": "our n r f nine one six zero cellular gateway experienced character framing errors during high speed modem trace logging inside the asset tracking terminal we attached a logic analyzer two the universal asynchronous receiver transmitter trace line and monitored core trace registers inside g d b the trace serial interface flagged framing errors because the fractional baud rate generator drifted buy three percent while the trace logging module lacked high speed clock configur wait inspect the clock divider initialization routine inside modem underscore trace dot c instead configur the modem trace universal asynchronous receiver transmitter buy setting fractional baud divisor values right zero x zero one into the baud control register wait right zero x zero three into the baud control register instead two restore exact bit timing we cleared the framing error flag buy writing one into the error status clear register after adjusting fractional baud divisors and synchronizing serial clocks the cellular gateway transmitted seven thousand diagnostic trace messages across twenty four hours without framing errors or dropped characters",
        "refined_text": "Our nRF9160 cellular gateway experienced character framing errors during high-speed modem trace logging inside the asset tracking terminal. We attached a logic analyzer to the universal asynchronous receiver transmitter trace line and monitored core trace registers inside GDB. The trace serial interface flagged framing errors because the fractional baud rate generator drifted by 3 percent while the trace logging module lacked high-speed clock configuration, inspecting the clock divider initialization routine inside modem_trace.c instead.\n\nConfigure the modem trace universal asynchronous receiver transmitter by setting fractional baud divisor values. Write 0x03 into the baud control register instead to restore exact bit timing. We cleared the framing error flag by writing 1 into the error status clear register.\n\nAfter adjusting fractional baud divisors and synchronizing serial clocks, the cellular gateway transmitted 7000 diagnostic trace messages across 24 hours without framing errors or dropped characters."
    },

    # Sample 18: TI CC1352P Sub-1 GHz RF command queue ring buffer stall
    {
        "raw_asr": "our c c one three five two p sub gigahertz sensor node stalled during continuous packet transmission inside the agricultural sensor network we connected open o c d over the jtag interface and analyzed radio core command descriptors inside free are toss the radio frequency core halted command execution because the transmission ring buffer head pointer wrapped into an unacknowledged command descriptor while the radio firmware lacked queue wrap configur wait inspect the descriptor queue routine inside rf underscore queue dot c instead configur the radio command queue ring buy allocating thirty two descriptors into the command buffer right zero x zero four into the radio command control register wait right zero x zero eight into the radio command control register instead two restart autonomous command execution we cleared the radio error status flag buy writing one into the interrupt clear register after allocating thirty two descriptor entries and refreshing command control registers the sub gigahertz sensor node transmitted four thousand radio frames across sixteen hours without queue stalls or communication timeouts",
        "refined_text": "Our CC1352P sub-gigahertz sensor node stalled during continuous packet transmission inside the agricultural sensor network. We connected OpenOCD over the JTAG interface and analyzed radio core command descriptors inside FreeRTOS. The radio frequency core halted command execution because the transmission ring buffer head pointer wrapped into an unacknowledged command descriptor while the radio firmware lacked queue wrap configuration, inspecting the descriptor queue routine inside rf_queue.c instead.\n\nConfigure the radio command queue ring by allocating 32 descriptors into the command buffer. Write 0x08 into the radio command control register instead to restart autonomous command execution. We cleared the radio error status flag by writing 1 into the interrupt clear register.\n\nAfter allocating 32 descriptor entries and refreshing command control registers, the sub-gigahertz sensor node transmitted 4000 radio frames across 16 hours without queue stalls or communication timeouts."
    },

    # Sample 19: Espressif ESP32-C3 RISC-V hardware crypto AES-XTS DMA block alignment fault
    {
        "raw_asr": "our esp thirty two c three r i s c v microcontroller asserted a hardware exception during flash encryption acceleration inside the smart meter gateway we connected open o c d over the built in serial wire jtag adapter and inspected fault status registers inside g d b the cryptographic acceleration engine raised a memory bus fault because direct memory access source buffers crossed a non sixteen byte alignment boundary while the encryption driver lacked memory alignment configur wait inspect the buffer allocation routine inside crypto underscore dma dot c instead configur the cryptographic direct memory access buffer buy setting thirty two byte alignment thresholds right zero x zero two into the encryption mode register wait right zero x zero six into the encryption mode register instead two authorize hardware block processing we cleared the hardware bus fault interrupt buy writing one into the interrupt status clear register after aligning encryption memory buffers and updating mode registers the microcontroller encrypted eight thousand flash memory pages across twenty hours without memory alignment faults or system exceptions",
        "refined_text": "Our ESP32-C3 RISC-V microcontroller asserted a hardware exception during flash encryption acceleration inside the smart meter gateway. We connected OpenOCD over the built-in serial wire JTAG adapter and inspected fault status registers inside GDB. The cryptographic acceleration engine raised a memory bus fault because direct memory access source buffers crossed a non 16 byte alignment boundary while the encryption driver lacked memory alignment configuration, inspecting the buffer allocation routine inside crypto_dma.c instead.\n\nConfigure the cryptographic direct memory access buffer by setting 32 byte alignment thresholds. Write 0x06 into the encryption mode register instead to authorize hardware block processing. We cleared the hardware bus fault interrupt by writing 1 into the interrupt status clear register.\n\nAfter aligning encryption memory buffers and updating mode registers, the microcontroller encrypted 8000 flash memory pages across 20 hours without memory alignment faults or system exceptions."
    },

    # Sample 20: Microchip PIC32CX Cortex-M7 dual-panel quad-SPI XIP flash caching lockup
    {
        "raw_asr": "our p i c thirty two c x microcontroller locked up during execute in place firmware execution inside the industrial motor controller we attached a segger j link probe and analyzed core execution traces inside free are toss the quad serial peripheral interface memory controller halted execution because cache line invalidation cycles collided with active instruction prefetch requests while the cache driver lacked prefetch buffer configur wait inspect the cache maintenance routine inside qspi underscore xip dot c instead configur the external flash cache line burst buy writing thirty two bytes into the cache line control register right zero x zero four into the cache prefetch control register wait right zero x zero eight into the cache prefetch control register instead two serialize prefetch operations we cleared the memory interface stall flag buy writing one into the status clear register after configuring cache line burst sizes and updating prefetch control registers the microcontroller executed nine thousand motor control loops across twenty four hours without execute in place lockups or instruction cache stalls",
        "refined_text": "Our PIC32CX microcontroller locked up during execute-in-place firmware execution inside the industrial motor controller. We attached a SEGGER J-Link probe and analyzed core execution traces inside FreeRTOS. The quad serial peripheral interface memory controller halted execution because cache line invalidation cycles collided with active instruction prefetch requests while the cache driver lacked prefetch buffer configuration, inspecting the cache maintenance routine inside qspi_xip.c instead.\n\nConfigure the external flash cache line burst by writing 32 bytes into the cache line control register. Write 0x08 into the cache prefetch control register instead to serialize prefetch operations. We cleared the memory interface stall flag by writing 1 into the status clear register.\n\nAfter configuring cache line burst sizes and updating prefetch control registers, the microcontroller executed 9000 motor control loops across 24 hours without execute-in-place lockups or instruction cache stalls."
    }
]

def main():
    print(f"Loaded {len(samples)} candidate samples for Batch 94 (Domain 6)...")

    # Leakage check
    print("\n--- Leakage Check against sft_eval.json ---")
    leak_count = 0
    for idx, s in enumerate(samples):
        r_raw = s["raw_asr"].strip().lower()
        r_ref = s["refined_text"].strip()
        if r_raw in eval_raws:
            print(f"Sample {idx+1} EXACT RAW LEAKAGE!")
            leak_count += 1
        if r_ref in eval_refs:
            print(f"Sample {idx+1} EXACT REF LEAKAGE!")
            leak_count += 1
    if leak_count == 0:
        print("Leakage Check: 100% CLEAN (0 leaks detected).")
    else:
        sys.exit(1)

    # Per-sample validation
    print("\n--- Per-Sample Validation (validator.py & cleaner.py) ---")
    all_pairs_valid = True
    all_clean_kept = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for idx, s in enumerate(samples):
        words = len(s["refined_text"].split())
        if words < 25:
            tier = "short"
        elif words < 90:
            tier = "medium"
        else:
            tier = "long"
        tier_counts[tier] += 1

        v_ok, v_msg = validate_pair(s)
        if not v_ok:
            print(f"Sample {idx+1} [Tier: {tier}, Words: {words}] FAILED validator: {v_msg}")
            all_pairs_valid = False

        c_res, c_msg = clean_sample(s["raw_asr"], s["refined_text"])
        if c_msg != "kept":
            print(f"Sample {idx+1} [Tier: {tier}, Words: {words}] FAILED cleaner: {c_msg}")
            all_clean_kept = False

        if v_ok and c_msg == "kept":
            print(f"Sample {idx+1:02d} [{tier.upper():6s} - {words:3d}w] -> PASSED")

    if not all_pairs_valid or not all_clean_kept:
        print("\nSome samples failed per-sample checks.")
        sys.exit(1)

    # Batch validation
    print("\n--- Batch Diversity Validation ---")
    b_ok, b_msg, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
    print(f"Batch validation result: {b_ok} - {b_msg}")
    print(f"Batch tier counts: {b_tiers}")
    if not b_ok:
        sys.exit(1)

    # Save to scratch/subagent_batch_94.json
    out_file = Path("scratch/subagent_batch_94.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote 20 verified samples to {out_file}")

if __name__ == "__main__":
    main()
