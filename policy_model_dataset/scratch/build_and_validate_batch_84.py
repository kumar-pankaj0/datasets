import json
import re
import sys
from pathlib import Path

# Add code directory to path
sys.path.append("code")
import validator
import cleaner

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batch_84 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Sample 1: Microchip ATSAMD51 high-speed ADC sample time register
    {
        "raw_asr": "uh calibrat the analog digital converter sample time buy loading sixty four into the sample length register",
        "refined_text": "Calibrate the analog digital converter sample time by loading 64 into the sample length register."
    },
    # Sample 2: Raspberry Pi RP2040 PIO state machine clock divider
    {
        "raw_asr": "configur the programmable input output state machine clock divider buy writing thirty two into the integer divisor register",
        "refined_text": "Configure the programmable input output state machine clock divider by writing 32 into the integer divisor register."
    },
    # Sample 3: NXP LPC55S69 hardware cryptographic accelerator engine
    {
        "raw_asr": "um initializ the hardware cryptographic engine buy writing zero x four zero into the control register",
        "refined_text": "Initialize the hardware cryptographic engine by writing 0x40 into the control register."
    },
    # Sample 4: Nordic nRF5340 inter-processor communication event channel
    {
        "raw_asr": "terminat the interprocessor communication event buy clearing channel bit eight inside the event subscribe register",
        "refined_text": "Terminate the interprocessor communication event by clearing channel bit 8 inside the event subscribe register."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # Sample 5: STM32G4 High-Resolution Timer (HRTIM) dead-time generator
    {
        "raw_asr": "configur the high resolution timer dead time generator buy loading sixteen wait load thirty two clock ticks instead into the dead time rising register four half bridge switching the pulse width modulation unit drives complementary outputs buy updating comparator registers across four power conversion phases",
        "refined_text": "Configure the high-resolution timer dead-time generator by loading 32 clock ticks instead into the dead-time rising register for half-bridge switching.\n\nThe pulse-width modulation unit drives complementary outputs by updating comparator registers across 4 power conversion phases."
    },
    # Sample 6: TI TMS320F280049C eCAP peripheral prescaler
    {
        "raw_asr": "uh initializ the enhanced capture peripheral prescaler buy writing two wait write four into the event prescaler register instead four motor position sensing the digital capture engine measures hall sensor pulse widths buy recording timer counter values across three capture registers",
        "refined_text": "Initialize the enhanced capture peripheral prescaler by writing 4 into the event prescaler register instead for motor position sensing.\n\nThe digital capture engine measures hall sensor pulse widths by recording timer counter values across 3 capture registers."
    },
    # Sample 7: Microchip PIC32MZ SPI frame control and DMA buffer
    {
        "raw_asr": "um allocat the serial peripheral interface transfer buffer buy writing sixteen wait right thirty two bits instead into the audio frame control register four digital codec streaming the direct memory access controller feeds serial transmission buy transferring sixty four sample blocks across dual ping pong buffers",
        "refined_text": "Allocate the serial peripheral interface transfer buffer by writing 32 bits instead into the audio frame control register for digital codec streaming.\n\nThe direct memory access controller feeds serial transmission by transferring 64 sample blocks across dual ping-pong buffers."
    },
    # Sample 8: Infineon PSoC 6 BLE scan window parameter
    {
        "raw_asr": "calibrat the bluetooth low energy scan window buy setting eighty wait set one hundred sixty clock slots instead into the central scan parameter register four beacon detection the radio sequencer listens four incoming advertising frames buy servicing reception interrupts across eight hardware channels",
        "refined_text": "Calibrate the Bluetooth Low Energy scan window by setting 160 clock slots instead into the central scan parameter register for beacon detection.\n\nThe radio sequencer listens for incoming advertising frames by servicing reception interrupts across 8 hardware channels."
    },
    # Sample 9: Espressif ESP32-C6 IEEE 802.15.4 frame filter
    {
        "raw_asr": "synchronizat the radio transceiver frame filter buy loading zero x zero two wait load zero x zero six into the pan identifier mask register instead four mesh sensor networking the r i s c v core filters incoming wireless packets buy verifying frame check sequences across twelve network coordinator routes",
        "refined_text": "Synchronize the radio transceiver frame filter by loading 0x06 into the PAN identifier mask register instead for mesh sensor networking.\n\nThe RISC-V core filters incoming wireless packets by verifying frame check sequences across 12 network coordinator routes."
    },
    # Sample 10: Renesas RA4M2 Watchdog Timer (WDT) refresh window
    {
        "raw_asr": "terminat the watchdog timer refresh error buy loading twenty five wait load fifty percent into the window end register instead four low power task monitoring the supervisor core refreshes the countdown timer buy writing zero x a five into the refresh register across eight periodic execution cycles",
        "refined_text": "Terminate the watchdog timer refresh error by loading 50 percent into the window end register instead for low-power task monitoring.\n\nThe supervisor core refreshes the countdown timer by writing 0xa5 into the refresh register across 8 periodic execution cycles."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Sample 11: STM32WB55 dual-core IPCC mailbox synchronization
    {
        "raw_asr": "our s t m thirty two w b fifty five dual core processor raised an interprocessor communication error during bluetooth low energy connection parameter updates inside the wireless firmware stack we connected a segger j link probe and analyzed core execution traces inside free are toss the communication mailbox triggered an interrupt storm because the application core updated transmit buffers without clearing the channel status flag while the firmware driver lacked mailbox synchronization configur wait inspect the interprocessor communication settings inside ipcc underscore ble dot c instead configur the interprocessor mailbox channel buy setting channel one priority right zero x zero one into the status clear register wait right zero x zero three into the status clear register instead two acknowledge bidirectional buffer events we cleared the interrupt request flag buy writing one into the communication status register after configuring mailbox channel attributes and clearing pending events the wireless processor exchanged four thousand connection updates across twenty four hours without communication errors or packet dropouts",
        "refined_text": "Our STM32WB55 dual-core processor raised an interprocessor communication error during Bluetooth Low Energy connection parameter updates inside the wireless firmware stack. We connected a SEGGER J-Link probe and analyzed core execution traces inside FreeRTOS. The communication mailbox triggered an interrupt storm because the application core updated transmit buffers without clearing the channel status flag while the firmware driver lacked mailbox synchronization configuration, inspecting the interprocessor communication settings inside ipcc_ble.c instead.\n\nConfigure the interprocessor mailbox channel by setting channel 1 priority. Write 0x03 into the status clear register instead to acknowledge bidirectional buffer events. We cleared the interrupt request flag by writing 1 into the communication status register.\n\nAfter configuring mailbox channel attributes and clearing pending events, the wireless processor exchanged 4000 connection updates across 24 hours without communication errors or packet dropouts."
    },
    # Sample 12: NXP S32K144 FlexCAN message buffer overrun
    {
        "raw_asr": "our s thirty two k one four four automotive microcontroller dropped incoming can flexible data rate frames during high speed network arbitration inside the body domain controller we connected a logic analyzer two the controller area network receive line and inspected execution frames inside g d b the message buffer engine asserted an overrun interrupt because the receiver queue filled before the microcontroller emptied the payload buffers while the can driver lacked interrupt filter configur wait inspect the buffer allocation routine inside flexcan underscore fifo dot c instead configur the message buffer acceptance mask buy setting the global filter threshold right zero x one f into the individual mask register wait right zero x three f into the individual mask register instead two filter incoming diagnostic identifier bits we cleared the message buffer flag buy writing one into the overrun status register after updating individual filter masks and adjusting queue capacity the microcontroller received six thousand automotive frames across twelve hours without message buffer overruns or dropped packets",
        "refined_text": "Our S32K144 automotive microcontroller dropped incoming CAN flexible data rate frames during high-speed network arbitration inside the body domain controller. We connected a logic analyzer to the controller area network receive line and inspected execution frames inside GDB. The message buffer engine asserted an overrun interrupt because the receiver queue filled before the microcontroller emptied the payload buffers while the CAN driver lacked interrupt filter configuration, inspecting the buffer allocation routine inside flexcan_fifo.c instead.\n\nConfigure the message buffer acceptance mask by setting the global filter threshold. Write 0x3f into the individual mask register instead to filter incoming diagnostic identifier bits. We cleared the message buffer flag by writing 1 into the overrun status register.\n\nAfter updating individual filter masks and adjusting queue capacity, the microcontroller received 6000 automotive frames across 12 hours without message buffer overruns or dropped packets."
    },
    # Sample 13: TI MSP430FR5994 FRAM Low Energy Accelerator bus fault
    {
        "raw_asr": "our m s p four three zero f r five nine nine four sensing node suffered a bus fault during low energy accelerator transform execution inside the acoustic vibration monitor we set a hardware breakpoint over the jtag interface and analyzed memory fault registers inside code composer studio the low energy accelerator core triggered an access violation because input data buffers crossed an unaligned fram address boundary while the vector math driver lacked buffer boundary configur wait inspect the memory alignment routine inside lea underscore transform dot c instead configur the low energy accelerator memory section buy setting thirty two bit boundary alignment right zero x zero two into the accelerator control register wait right zero x zero four into the accelerator control register instead two enable autonomous transform execution we cleared the accelerator error flag buy writing one into the fault flag register after aligning memory buffers and updating accelerator control registers the sensing node executed eight thousand transform cycles across sixteen hours without bus faults or memory alignment exceptions",
        "refined_text": "Our MSP430FR5994 sensing node suffered a bus fault during low energy accelerator transform execution inside the acoustic vibration monitor. We set a hardware breakpoint over the JTAG interface and analyzed memory fault registers inside Code Composer Studio. The low energy accelerator core triggered an access violation because input data buffers crossed an unaligned FRAM address boundary while the vector math driver lacked buffer boundary configuration, inspecting the memory alignment routine inside lea_transform.c instead.\n\nConfigure the low energy accelerator memory section by setting 32 bit boundary alignment. Write 0x04 into the accelerator control register instead to enable autonomous transform execution. We cleared the accelerator error flag by writing 1 into the fault flag register.\n\nAfter aligning memory buffers and updating accelerator control registers, the sensing node executed 8000 transform cycles across 16 hours without bus faults or memory alignment exceptions."
    },
    # Sample 14: Microchip SAME54 Ethernet MAC DMA descriptor ring lockup
    {
        "raw_asr": "our s a m e fifty four gateway hung during high throughput ethernet frame transmission inside the industrial automation hub we connected open o c d over the serial wire debug port and inspected media access control descriptors inside g d b the direct memory access controller halted execution because transmit descriptor chaining pointed two an unmapped ring buffer offset while the network driver lacked ring wrap configur wait inspect the descriptor initialization routine inside gmac underscore ring dot c instead configur the media access controller descriptor list buy setting ring wrap bits on descriptor index twelve right zero x one zero into the network control register wait right zero x two zero into the network control register instead two restore autonomous descriptor fetching we cleared the transmission halt flag buy writing one into the status clear register after updating descriptor wrap pointers and refreshing network control registers the gateway processed nine thousand network frames across twenty four hours without descriptor stalls or transmission hangs",
        "refined_text": "Our SAME54 gateway hung during high-throughput Ethernet frame transmission inside the industrial automation hub. We connected OpenOCD over the serial wire debug port and inspected media access control descriptors inside GDB. The direct memory access controller halted execution because transmit descriptor chaining pointed to an unmapped ring buffer offset while the network driver lacked ring wrap configuration, inspecting the descriptor initialization routine inside gmac_ring.c instead.\n\nConfigure the media access controller descriptor list by setting ring wrap bits on descriptor index 12. Write 0x20 into the network control register instead to restore autonomous descriptor fetching. We cleared the transmission halt flag by writing 1 into the status clear register.\n\nAfter updating descriptor wrap pointers and refreshing network control registers, the gateway processed 9000 network frames across 24 hours without descriptor stalls or transmission hangs."
    },
    # Sample 15: Silicon Labs EFR32MG24 LETIMER clock desynchronization
    {
        "raw_asr": "our e f r thirty two m g twenty four sensor beacon exhibited timing drift during energy mode two sleep wake transitions inside the zigbee environmental node we attached a logic analyzer two the timer output pin and monitored low frequency clock edges the low energy timer drifted buy twelve milliseconds because the clock synchronization handshake terminated before the peripheral clock domain latched the prescaler value while the power manager lacked timer synchronization configur wait inspect the clock latch routine inside letimer underscore sync dot c instead configur the low energy timer synchronization delay buy loading sixteen wait load thirty two clock ticks into the delay control register instead right zero x zero four into the freeze control register wait right zero x zero eight into the freeze control register instead two protect counter updates we cleared the synchronization error flag buy writing one into the interrupt flag clear register after adjusting synchronization delays and setting freeze control bits the sensor beacon delivered seven thousand reporting packets across eighteen hours without timing drift or missed sleep intervals",
        "refined_text": "Our EFR32MG24 sensor beacon exhibited timing drift during energy mode 2 sleep wake transitions inside the Zigbee environmental node. We attached a logic analyzer to the timer output pin and monitored low-frequency clock edges. The low-energy timer drifted by 12 milliseconds because the clock synchronization handshake terminated before the peripheral clock domain latched the prescaler value while the power manager lacked timer synchronization configuration, inspecting the clock latch routine inside letimer_sync.c instead.\n\nConfigure the low-energy timer synchronization delay by loading 32 clock ticks into the delay control register instead. Write 0x08 into the freeze control register instead to protect counter updates. We cleared the synchronization error flag by writing 1 into the interrupt flag clear register.\n\nAfter adjusting synchronization delays and setting freeze control bits, the sensor beacon delivered 7000 reporting packets across 18 hours without timing drift or missed sleep intervals."
    },
    # Sample 16: Raspberry Pi RP2040 dual-core spinlock contention and FIFO stall
    {
        "raw_asr": "our r p two zero four zero dual core board locked up during inter core data passing inside the digital audio synthesizer we connected open o c d over the debug adapter and analyzed execution states across both arm cortex m zero plus cores core one stalled indefinitely because core zero acquired hardware spinlock fourteen without releasing the lock during fifo transfers while the audio firmware lacked spinlock timeout configur wait inspect the inter core synchronization routine inside fifo underscore sync dot c instead configur the hardware inter core fifo watermark buy loading thirty two wait load sixty four into the fifo watermark register instead right zero x zero one into the spinlock clear register wait right zero x zero two into the spinlock clear register instead two clear hardware lock ownership we cleared the fifo error flag buy writing one into the fifo status register after adjusting fifo thresholds and releasing spinlock resources the dual core board processed five thousand audio buffers across twelve hours without hardware stalls or core deadlocks",
        "refined_text": "Our RP2040 dual-core board locked up during inter-core data passing inside the digital audio synthesizer. We connected OpenOCD over the debug adapter and analyzed execution states across both ARM Cortex-M0+ cores. Core 1 stalled indefinitely because core 0 acquired hardware spinlock 14 without releasing the lock during FIFO transfers while the audio firmware lacked spinlock timeout configuration, inspecting the inter-core synchronization routine inside fifo_sync.c instead.\n\nConfigure the hardware inter-core FIFO watermark by loading 64 into the FIFO watermark register instead. Write 0x02 into the spinlock clear register instead to clear hardware lock ownership. We cleared the FIFO error flag by writing 1 into the FIFO status register.\n\nAfter adjusting FIFO thresholds and releasing spinlock resources, the dual-core board processed 5000 audio buffers across 12 hours without hardware stalls or core deadlocks."
    },
    # Sample 17: Espressif ESP32-S3 octal PSRAM cache line invalidation and EDMA stall
    {
        "raw_asr": "our esp thirty two s three vision device experienced frame corruption during octal p s r a m camera transfers inside the smart camera gateway we attached a segger j link probe and analyzed execution memory maps inside g d b the memory controller flagged cache invalidation incoherency because the enhanced direct memory access engine wrote sensor frames directly two external ram without flushing cache lines while the camera pipeline lacked cache flush configur wait inspect the cache management routine inside psram underscore cam dot c instead configur the external memory cache line burst size buy writing thirty two wait right sixty four bytes instead into the cache line control register right zero x zero one into the cache invalidation register wait right zero x zero two into the cache invalidation register instead two enforce immediate writeback we cleared the cache error flag buy writing one into the interrupt status register after configuring cache burst sizes and triggering cache invalidation the vision device streamed four thousand high resolution frames across sixteen hours without frame corruption or memory faults",
        "refined_text": "Our ESP32-S3 vision device experienced frame corruption during octal PSRAM camera transfers inside the smart camera gateway. We attached a SEGGER J-Link probe and analyzed execution memory maps inside GDB. The memory controller flagged cache invalidation incoherency because the enhanced direct memory access engine wrote sensor frames directly to external RAM without flushing cache lines while the camera pipeline lacked cache flush configuration, inspecting the cache management routine inside psram_cam.c instead.\n\nConfigure the external memory cache line burst size by writing 64 bytes instead into the cache line control register. Write 0x02 into the cache invalidation register instead to enforce immediate writeback. We cleared the cache error flag by writing 1 into the interrupt status register.\n\nAfter configuring cache burst sizes and triggering cache invalidation, the vision device streamed 4000 high-resolution frames across 16 hours without frame corruption or memory faults."
    },
    # Sample 18: Infineon XMC4700 industrial Ethernet DMA descriptor ring underrun
    {
        "raw_asr": "our x m c four seven zero zero industrial gateway dropped transmission frames during industrial ethernet traffic inside the automation switch we connected wi re shark two the ethernet port and monitored core execution registers inside g d b the direct memory access controller flagged a buffer underrun condition because transmit descriptor rings exhausted payload buffers while the media access control driver lacked ring refill configur wait inspect the descriptor refill routine inside eth underscore dma dot c instead configur the ethernet direct memory access burst limit buy setting five hundred twelve bytes into the descriptor length register right zero x zero eight into the bus mode register wait right zero x one zero into the bus mode register instead two authorize burst descriptor transfers we cleared the buffer underrun interrupt buy writing one into the abnormal status register after configuring burst limits and increasing descriptor length thresholds the industrial gateway forwarded eight thousand ethernet packets across twenty four hours without buffer underruns or frame loss",
        "refined_text": "Our XMC4700 industrial gateway dropped transmission frames during industrial Ethernet traffic inside the automation switch. We connected Wireshark to the Ethernet port and monitored core execution registers inside GDB. The direct memory access controller flagged a buffer underrun condition because transmit descriptor rings exhausted payload buffers while the media access control driver lacked ring refill configuration, inspecting the descriptor refill routine inside eth_dma.c instead.\n\nConfigure the Ethernet direct memory access burst limit by setting 512 bytes into the descriptor length register. Write 0x10 into the bus mode register instead to authorize burst descriptor transfers. We cleared the buffer underrun interrupt by writing 1 into the abnormal status register.\n\nAfter configuring burst limits and increasing descriptor length thresholds, the industrial gateway forwarded 8000 Ethernet packets across 24 hours without buffer underruns or frame loss."
    },
    # Sample 19: Renesas RX65N dual-bank flash background programming
    {
        "raw_asr": "our r x six five n microcontroller hung during background flash programming inside the building automation controller we attached a hardware trace emulator two the debug interface and inspected flash status registers inside g d b the memory sequencer raised an error flag when firmware updates attempted programming while background bank erasing was incomplete because the flash driver lacked dual bank wait state configur wait inspect the flash sequencer routine inside flash underscore bank dot c instead configur the dual bank flash memory controller buy setting thirty two wait states into the flash wait cycle register erases the flash sectors in bank one buy writing zero x four zero into the erase control register wait right zero x eight zero into the erase control register instead two authorize flash sector modification we cleared the flash sequencer error flag buy writing one into the flash status register after tuning flash wait cycles and adjusting bank erase control registers the microcontroller flashed two thousand firmware blocks across twelve hours without flash timeouts or sequencer faults",
        "refined_text": "Our RX65N microcontroller hung during background flash programming inside the building automation controller. We attached a hardware trace emulator to the debug interface and inspected flash status registers inside GDB. The memory sequencer raised an error flag when firmware updates attempted programming while background bank erasing was incomplete because the flash driver lacked dual-bank wait state configuration, inspecting the flash sequencer routine inside flash_bank.c instead.\n\nConfigure the dual-bank flash memory controller by setting 32 wait states into the flash wait cycle register. Erases the flash sectors in bank 1 by writing 0x80 into the erase control register instead to authorize flash sector modification. We cleared the flash sequencer error flag by writing 1 into the flash status register.\n\nAfter tuning flash wait cycles and adjusting bank erase control registers, the microcontroller flashed 2000 firmware blocks across 12 hours without flash timeouts or sequencer faults."
    },
    # Sample 20: SiFive FE310 RISC-V PLIC external interrupt looping
    {
        "raw_asr": "our r i s c v f e three one zero development board encountered repeated interrupt loops during external sensor sampling inside the industrial telemetry unit we connected open o c d over the r i s c v jtag adapter and inspected interrupt controller registers inside g d b the core reentered external interrupt service routines indefinitely because the interrupt handler exited without writing the completed interrupt identifier two the claim register while the board support package lacked interrupt completion configur wait inspect the plic handler inside plic underscore irq dot c instead configur the platform level interrupt controller priority threshold buy writing four into the priority register right zero x zero three into the target enable register wait right zero x zero seven into the target enable register instead two unmask active sensor lines we cleared the pending interrupt buy writing interrupt identifier five into the claim complete register after setting priority thresholds and restoring proper interrupt claim sequences the development board recorded six thousand telemetry samples across sixteen hours without interrupt looping or core lockups",
        "refined_text": "Our RISC-V FE310 development board encountered repeated interrupt loops during external sensor sampling inside the industrial telemetry unit. We connected OpenOCD over the RISC-V JTAG adapter and inspected interrupt controller registers inside GDB. The core reentered external interrupt service routines indefinitely because the interrupt handler exited without writing the completed interrupt identifier to the claim register while the board support package lacked interrupt completion configuration, inspecting the PLIC handler inside plic_irq.c instead.\n\nConfigure the platform-level interrupt controller priority threshold by writing 4 into the priority register. Write 0x07 into the target enable register instead to unmask active sensor lines. We cleared the pending interrupt by writing interrupt identifier 5 into the claim complete register.\n\nAfter setting priority thresholds and restoring proper interrupt claim sequences, the development board recorded 6000 telemetry samples across 16 hours without interrupt looping or core lockups."
    }
]

def main():
    print(f"Loaded {len(batch_84)} candidate samples for Batch 84 (Domain 6)...")

    # Leakage check
    print("\n--- Leakage Check against sft_eval.json ---")
    leak_count = 0
    for idx, p in enumerate(batch_84):
        raw = p["raw_asr"].strip().lower()
        ref = p["refined_text"].strip()
        if raw in eval_raws:
            print(f"Sample {idx+1} raw_asr leaks into eval set!")
            leak_count += 1
        if ref in eval_refs:
            print(f"Sample {idx+1} refined_text leaks into eval set!")
            leak_count += 1
    if leak_count == 0:
        print("PASS: 0 leakage matches with eval set.")
    else:
        print(f"FAIL: {leak_count} leakage matches found.")
        sys.exit(1)

    # Per-sample validation
    print("\n--- Individual Pair Validation ---")
    tier_counts = {"short": 0, "medium": 0, "long": 0}
    all_pairs_valid = True

    for idx, p in enumerate(batch_84):
        words = len(p["refined_text"].split())
        if words < 25:
            tier = "short"
        elif words < 90:
            tier = "medium"
        else:
            tier = "long"
        tier_counts[tier] += 1

        val_ok, val_msg = validator.validate_pair(p)
        clean_res, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])

        status_str = f"Sample {idx+1:02d} [{tier.upper():6s}|{words:3d}w]: "
        if val_ok and clean_status == "kept":
            status_str += "PASSED (validator OK, cleaner kept)"
            print(status_str)
        else:
            status_str += f"FAILED -> val: {val_msg}, clean: {clean_status}"
            print(status_str)
            all_pairs_valid = False

    # Batch validation
    print("\n--- Batch Diversity Validation ---")
    b_ok, b_msg, counts = validator.validate_batch(batch_84, min_short=4, min_medium=6, min_long=10)
    print(f"validate_batch: {b_ok} ({b_msg})")
    print(f"Tier counts: {counts}")

    if not (all_pairs_valid and b_ok):
        print("\nFAIL: Batch verification failed.")
        sys.exit(1)

    # Save to scratch/subagent_batch_84.json
    out_path = Path("scratch/subagent_batch_84.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch_84, f, ensure_ascii=False, indent=2)

    print(f"\nSUCCESS: Verified batch written to {out_path} ({len(batch_84)} samples)")

if __name__ == "__main__":
    main()
