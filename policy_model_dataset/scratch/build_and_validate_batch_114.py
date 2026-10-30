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

    # Sample 1: FreeRTOS task priority configuration
    {
        "raw_asr": "um configur the free are toss telemetry task priority two level four",
        "refined_text": "Configure the FreeRTOS telemetry task priority to level 4."
    },

    # Sample 2: I2C bus prescaler register update
    {
        "raw_asr": "uh set the i two c bus prescaler register two thirty two buy updating control bits",
        "refined_text": "Set the I2C bus prescaler register to 32 by updating control bits."
    },

    # Sample 3: Watchdog timer reload allocation
    {
        "raw_asr": "um allocat eight words four the hardware watchdog timer reload value inside the power supervisor",
        "refined_text": "Allocate 8 words for the hardware watchdog timer reload value inside the power supervisor."
    },

    # Sample 4: DMA transfer descriptor synchronization
    {
        "raw_asr": "basically synchronizat the d m a transfer descriptor with peripheral channel six using interrupt flags",
        "refined_text": "Synchronize the DMA transfer descriptor with peripheral channel 6 using interrupt flags."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Avoid backticks.
    # =========================================================================

    # Sample 5: SPI flash memory sector erase and status register polling
    {
        "raw_asr": "during firmware initialization our bootloader inspects the external flash memory at address zero x zero eight zero zero zero zero zero zero buy clearing write protection flags wait clear write protection flags on chip select two instead um right thirty two bytes into the target sector by polling the status register four write completion",
        "refined_text": "During firmware initialization our bootloader inspects the external flash memory at address 0x08000000 by clearing write protection flags, clearing write protection flags on chip select 2 instead.\n\nWrite 32 bytes into the target sector by polling the status register for write completion."
    },

    # Sample 6: CAN-FD controller bit timing configuration and message filtering
    {
        "raw_asr": "in the automotive gateway driver our engineers calibrated nominal bit timing across eight nodes inside can underscore bus dot c buy setting the nominal prescaler register two four wait set the nominal prescaler register two eight instead um configur sixteen message acceptance filters four standard identifier masks",
        "refined_text": "In the automotive gateway driver our engineers calibrated nominal bit timing across 8 nodes inside can_bus.c by setting the nominal prescaler register to 4, setting the nominal prescaler register to 8 instead.\n\nConfigure 16 message acceptance filters for standard identifier masks."
    },

    # Sample 7: ARM Cortex-M NVIC interrupt priority grouping and SysTick reload
    {
        "raw_asr": "the interrupt vector manager configures nested priorities across twelve peripheral interrupts inside nvic underscore ctrl dot c buy programming priority grouping two three bits wait program priority grouping two four bits instead um allocat twenty four words four the exception stack frame during context switching",
        "refined_text": "The interrupt vector manager configures nested priorities across 12 peripheral interrupts inside nvic_ctrl.c by programming priority grouping to 3 bits, programming priority grouping to 4 bits instead.\n\nAllocate 24 words for the exception stack frame during context switching."
    },

    # Sample 8: UART circular DMA receive buffer and idle line interrupt
    {
        "raw_asr": "our sensor gateway processes telemetry streams buy enabling circular d m a reception inside uart underscore dma dot c across eight serial ports wait assign buffer size two two hundred fifty six bytes instead um detect frame boundaries buy monitoring idle line interrupt flags",
        "refined_text": "Our sensor gateway processes telemetry streams by enabling circular DMA reception inside uart_dma.c across 8 serial ports, assigning buffer size to 256 bytes instead.\n\nDetect frame boundaries by monitoring idle line interrupt flags."
    },

    # Sample 9: Low-power stop mode entry and LPTIM wake-up timer configuration
    {
        "raw_asr": "the power management firmware enters stop mode buy gating high speed peripheral clocks inside pwr underscore manager dot c across four power domains wait program the low power timer reload value two five hundred milliseconds instead um measur sleep current consumption down into twelve microamperes using an inline current probe",
        "refined_text": "The power management firmware enters stop mode by gating high-speed peripheral clocks inside pwr_manager.c across 4 power domains, programming the low-power timer reload value to 500 milliseconds instead.\n\nMeasure sleep current consumption down into 12 microamperes using an inline current probe."
    },

    # Sample 10: RISC-V timer comparison register and machine-mode trap handler
    {
        "raw_asr": "our r i s c v core initializ machine timer interrupts inside trap underscore handler dot c buy reading the mtime register across thirty two bit cycles wait load the mtimecmp register value at address zero x zero two zero zero four zero zero zero instead um dispatch timer tick events two the scheduler across eight tasks",
        "refined_text": "Our RISC-V core initializes machine timer interrupts inside trap_handler.c by reading the mtime register across 32 bit cycles, loading the mtimecmp register value at address 0x02004000 instead.\n\nDispatch timer tick events to the scheduler across 8 tasks."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2-3 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Avoid backticks.
    # =========================================================================

    # Sample 11: STM32H7 dual-core inter-processor communication via hardware semaphore and shared SRAM4
    {
        "raw_asr": "during dual core bring up on the stm thirty two h seven board our firmware team debugged inter processor communicat between the cortex m seven and cortex m four cores our primary issue involved memory corruption inside the shared s r a m four message buffer at address zero x three eight zero zero zero zero zero zero when both cores executed concurrent writes without mutual exclusion we resolved the conflict buy enforcing hardware semaphore synchronization using the h s e m peripheral wait lock channel four instead of channel two um our driver acquires semaphore lock four buy writing the core identifier into the h s e m register before updating the shared ring buffer pointers the cortex m seven core transmits telemetry packets across sixteen message slots while the cortex m four core consumes processed records within eight milliseconds of arrival staging validation confirms that hardware locking eliminates buffer overwrites across twenty four hours of continuous dual core stress testing",
        "refined_text": "During dual-core bring-up on the STM32H7 board our firmware team debugged inter-processor communication between the Cortex-M7 and Cortex-M4 cores. Our primary issue involved memory corruption inside the shared SRAM4 message buffer at address 0x38000000 when both cores executed concurrent writes without mutual exclusion. We resolved the conflict by enforcing hardware semaphore synchronization using the HSEM peripheral, locking channel 4 instead of channel 2.\n\nOur driver acquires semaphore lock 4 by writing the core identifier into the HSEM register before updating the shared ring buffer pointers. The Cortex-M7 core transmits telemetry packets across 16 message slots while the Cortex-M4 core consumes processed records within 8 milliseconds of arrival. Staging validation confirms that hardware locking eliminates buffer overwrites across 24 hours of continuous dual-core stress testing."
    },

    # Sample 12: Nordic nRF52840 BLE peripheral radio event scheduling and high-frequency crystal oscillator start
    {
        "raw_asr": "in our low power wireless investigation on the n r f five two eight four zero system on chip our embedded team resolved connection drops during b l e advertising events the issue originated from clock drift when starting the thirty two megahertz high frequency crystal oscillator without sufficient ramp up settling time we stabilized clock switching buy polling the h f c l k started event flag before initiating radio transmiss sequences wait set radio transmit power two four decibels instead of zero decibels um our driver configures the external crystal capacitors buy setting internal load capacitance bits two eight picofarads inside the clock controller this timing adjustment guarantees radio frequency stability across forty six connection intervals without packet retransmissions laboratory measurements confirm that current consumption during advertising drops two twelve milliamperes across three distinct radio advertising channels",
        "refined_text": "In our low-power wireless investigation on the nRF52840 system-on-chip our embedded team resolved connection drops during BLE advertising events. The issue originated from clock drift when starting the 32 megahertz high-frequency crystal oscillator without sufficient ramp-up settling time. We stabilized clock switching by polling the HFCLK started event flag before initiating radio transmission sequences, setting radio transmit power to 4 decibels instead of 0 decibels.\n\nOur driver configures the external crystal capacitors by setting internal load capacitance bits to 8 picofarads inside the clock controller. This timing adjustment guarantees radio frequency stability across 46 connection intervals without packet retransmissions. Laboratory measurements confirm that current consumption during advertising drops to 12 milliamperes across 3 distinct radio advertising channels."
    },

    # Sample 13: FreeRTOS priority inversion postmortem and mutex priority inheritance bugfix in motor controller
    {
        "raw_asr": "in our firmware postmortem following field drive stalls our team analyzed a priority inversion bug inside free are toss task scheduling the critical telemetry task running at priority six missed real time deadlines because a low priority logging task at priority two held an uninherited synchronization lock across sixteen milliseconds an intermediate motor speed calculation task preempted the logging task buy consuming c p u cycles without releasing the shared resource we resolved the schedul deadlock buy restructuring resource arbitrat inside motor underscore task dot c wait replace the binary semaphore with a mutex supporting priority inheritance instead um when the high priority task requests the locked motor telemetry buffer free are toss elevates the low priority logging task priority two level six until the mutex releases firmware regression tests confirm that priority inheritance bounds blocking latency two under two milliseconds across twelve thousand simulated actuation cycles",
        "refined_text": "In our firmware postmortem following field drive stalls our team analyzed a priority inversion bug inside FreeRTOS task scheduling. The critical telemetry task running at priority 6 missed real-time deadlines because a low-priority logging task at priority 2 held an uninherited synchronization lock across 16 milliseconds. An intermediate motor speed calculation task preempted the logging task by consuming CPU cycles without releasing the shared resource. We resolved the schedule deadlock by restructuring resource arbitration inside motor_task.c, replacing the binary semaphore with a mutex supporting priority inheritance instead.\n\nWhen the high-priority task requests the locked motor telemetry buffer, FreeRTOS elevates the low-priority logging task priority to level 6 until the mutex releases. Firmware regression tests confirm that priority inheritance bounds blocking latency to under 2 milliseconds across 12000 simulated actuation cycles."
    },

    # Sample 14: QSPI Quad-SPI NOR flash memory-mapped mode execution-in-place (XIP) configuration on NXP RT1060
    {
        "raw_asr": "during board bring up on the n x p r t one zero six zero microcontroller our firmware engineers configured external quad s p i nor flash memory four high speed code execution in place our initial flash read throughput stalled because the flexspi controller operated in single line mode across sixty megahertz clock rates we enabled quad line read commands buy writing lookup table sequences inside qspi underscore driver dot c wait configure eight dummy clock cycles instead of four dummy cycles um our driver maps external nor flash into the memory address space at address zero x six zero zero zero zero zero zero zero buy enabling memory mapped x i p mode inside the bus interface register this architecture allows the c p u core two execute instructions directly from flash at one hundred thirty three megahertz bench tests confirm that burst read latency drops buy sixty percent across eight memory benchmark suites",
        "refined_text": "During board bring-up on the NXP RT1060 microcontroller our firmware engineers configured external Quad-SPI NOR flash memory for high-speed code execution-in-place. Our initial flash read throughput stalled because the FlexSPI controller operated in single-line mode across 60 megahertz clock rates. We enabled quad-line read commands by writing lookup table sequences inside qspi_driver.c, configuring 8 dummy clock cycles instead of 4 dummy cycles.\n\nOur driver maps external NOR flash into the memory address space at address 0x60000000 by enabling memory-mapped XIP mode inside the bus interface register. This architecture allows the CPU core to execute instructions directly from flash at 133 megahertz. Bench tests confirm that burst read latency drops by 60 percent across 8 memory benchmark suites."
    },

    # Sample 15: I3C sensor bus dynamic address assignment (ENTDAA) and hot-join event handling on automotive board
    {
        "raw_asr": "our telemetry firmware team integrated multi sensor communication across an i three c peripheral bus inside i3c underscore master dot c during bus initializ sequences the primary master failed two enumerate slave devices because hot join requests interrupted static broadcast frames we resolved the timing conflict buy issuing broadcast command e n t d a a four dynamic address assignment across all target sensors wait assign dynamic address zero x two four instead of address zero x two zero um the bus controller assigns dynamic addresses two five peripheral inertial sensors while supporting legacy i two c fallback on slave port two our driver monitors in band interrupt events buy servicing push pull status flags within four microseconds of bus assertion hardware logic analyzer traces verify that bus throughput reaches twelve megabits per second across eight telemetry sensors without bus collision retries",
        "refined_text": "Our telemetry firmware team integrated multi-sensor communication across an I3C peripheral bus inside i3c_master.c. During bus initialization sequences the primary master failed to enumerate slave devices because hot-join requests interrupted static broadcast frames. We resolved the timing conflict by issuing broadcast command ENTDAA for dynamic address assignment across all target sensors, assigning dynamic address 0x24 instead of address 0x20.\n\nThe bus controller assigns dynamic addresses to 5 peripheral inertial sensors while supporting legacy I2C fallback on slave port 2. Our driver monitors in-band interrupt events by servicing push-pull status flags within 4 microseconds of bus assertion. Hardware logic analyzer traces verify that bus throughput reaches 12 megabits per second across 8 telemetry sensors without bus collision retries."
    },

    # Sample 16: Cortex-M7 D-Cache clean and invalidate operations for Ethernet MAC DMA descriptor ring buffers
    {
        "raw_asr": "during gigabit networking validation on our cortex m seven embedded target our team isolated packet drop anomalies inside ethernet underscore dma dot c the underlying defect involved cache coherency mismatches between the c p u data cache and the ethernet d m a descriptor ring buffer when the ethernet d m a controller populated receive buffers in s r a m at address zero x two zero zero zero zero zero zero zero the c p u read stale cache lines because d cache invalidation was omitted we resolved the memory incoherency buy inserting explicit cache maintenance routines before processing incoming frames wait invalidate thirty two cache lines instead of sixteen cache lines um our driver cleans and invalidates buffer cache lines buy executing data synchronization barriers around descriptor ownership handoffs staging stress tests verify that zero copy network throughput reaches eighty four megabits per second across twelve hundred packets without memory corruption",
        "refined_text": "During gigabit networking validation on our Cortex-M7 embedded target our team isolated packet drop anomalies inside ethernet_dma.c. The underlying defect involved cache coherency mismatches between the CPU data cache and the Ethernet DMA descriptor ring buffer. When the Ethernet DMA controller populated receive buffers in SRAM at address 0x20000000, the CPU read stale cache lines because D-cache invalidation was omitted. We resolved the memory incoherency by inserting explicit cache maintenance routines before processing incoming frames, invalidating 32 cache lines instead of 16 cache lines.\n\nOur driver cleans and invalidates buffer cache lines by executing data synchronization barriers around descriptor ownership handoffs. Staging stress tests verify that zero-copy network throughput reaches 84 megabits per second across 1200 packets without memory corruption."
    },

    # Sample 17: RP2040 programmable I/O (PIO) state machine implementation for custom WS2812 LED timing generator
    {
        "raw_asr": "our embedded lighting firmware team built a bit bang timing engine on the r p two zero four zero microcontroller using the hardware p i o peripheral our goal centered on generating precise timing pulses four an addressable w s two eight one two led strip without loading the c p u core during frame updates we developed a dedicated state machine program inside pio underscore driver dot c buy mapping p i o block zero base address at zero x five zero two zero zero zero zero zero wait set the clock divider two sixteen instead of eight um the state machine executes thirty two instructions shifting twenty four bits per pixel from the transmit f i f o directly into g p i o pin four our driver streams frame data using d m a channel one without interrupting active application tasks oscilloscope captures confirm that bit period jitter remains under ten nanoseconds across sixty four chained leds during high refresh rate animations",
        "refined_text": "Our embedded lighting firmware team built a bit-bang timing engine on the RP2040 microcontroller using the hardware PIO peripheral. Our goal centered on generating precise timing pulses for an addressable WS2812 LED strip without loading the CPU core during frame updates. We developed a dedicated state machine program inside pio_driver.c by mapping PIO block 0 base address at 0x50200000, setting the clock divider to 16 instead of 8.\n\nThe state machine executes 32 instructions, shifting 24 bits per pixel from the transmit FIFO directly into GPIO pin 4. Our driver streams frame data using DMA channel 1 without interrupting active application tasks. Oscilloscope captures confirm that bit period jitter remains under 10 nanoseconds across 64 chained LEDs during high refresh rate animations."
    },

    # Sample 18: USB CDC composite device endpoint descriptor configuration and bulk transfer flow control
    {
        "raw_asr": "during high speed serial logging experiments our communication squad diagnosed data throttling across our u s b c d c peripheral interface the primary bottleneck occurred when bulk in endpoint packets dropped because the endpoint transmission f i f o overflowed during continuous sensor logging we resolved the buffer overflow buy tuning endpoint descriptors inside usb underscore cdc dot c wait expand endpoint buffer size two one hundred twenty eight bytes instead of sixty four bytes um our driver configures bulk endpoint one buy writing configuration bits into the endpoint register at offset zero x four zero this setup handles double buffered packet transfers allowing the peripheral two stream logs without stalling the u s b bus hardware analyzer verification confirms that host transfer rates achieve eight hundred kilobytes per second across four simultaneous terminal sessions without packet losses",
        "refined_text": "During high-speed serial logging experiments our communication squad diagnosed data throttling across our USB CDC peripheral interface. The primary bottleneck occurred when bulk IN endpoint packets dropped because the endpoint transmission FIFO overflowed during continuous sensor logging. We resolved the buffer overflow by tuning endpoint descriptors inside usb_cdc.c, expanding endpoint buffer size to 128 bytes instead of 64 bytes.\n\nOur driver configures bulk endpoint 1 by writing configuration bits into the endpoint register at offset 0x40. This setup handles double-buffered packet transfers, allowing the peripheral to stream logs without stalling the USB bus. Hardware analyzer verification confirms that host transfer rates achieve 800 kilobytes per second across 4 simultaneous terminal sessions without packet losses."
    },

    # Sample 19: Hardware secure boot verification using SHA256 and ECDSA signature checks in dual-bank flash
    {
        "raw_asr": "our secure systems squad hardened the bootloader stage two image verification process across dual bank internal flash memory our security objective mandates authenticat the primary application header before executing code jumps inside boot underscore verify dot c during boot sequencing the crypto engine parses the application manifest stored at flash address zero x zero eight zero four zero zero zero zero wait verify the public key hash inside bank two instead of bank one um our routine computes a hardware accelerated s h a two five six digest across two hundred fifty six kilobytes of firmware binary data and checks the signature against thirty two byte e c d s a curve parameters when cryptographic validation succeeds the bootloader relocates the vector table offset register and transfers execution two the main kernel boot benchmark logs show that signature verification completes in forty two milliseconds across five automated recovery cycles without boot failures",
        "refined_text": "Our secure systems squad hardened the bootloader stage 2 image verification process across dual-bank internal flash memory. Our security objective mandates authenticating the primary application header before executing code jumps inside boot_verify.c. During boot sequencing the crypto engine parses the application manifest stored at flash address 0x08040000, verifying the public key hash inside bank 2 instead of bank 1.\n\nOur routine computes a hardware-accelerated SHA256 digest across 256 kilobytes of firmware binary data and checks the signature against 32 byte ECDSA curve parameters. When cryptographic validation succeeds, the bootloader relocates the vector table offset register and transfers execution to the main kernel. Boot benchmark logs show that signature verification completes in 42 milliseconds across 5 automated recovery cycles without boot failures."
    },

    # Sample 20: JTAG boundary scan and SWD openocd debugging of hard fault handler stack unwinding on Cortex-M4
    {
        "raw_asr": "in our embedded test lab our firmware debugging squad investigated recurring hard fault exceptions on our cortex m four field telemetry nodes using an o p e n o c d probe connected through an s w d interface we isolated the crash by inspecting the configurable fault status register at address zero x e zero zero zero e d two eight which indicated an unaligned memory access inside fault underscore handler dot c wait capture stack frame words from the process stack pointer instead of the main stack pointer um our custom fault logger decodes the exception return address by extracting program counter values and status registers stored in s r a m our debugger connects through a four wire j t a g interface allowing engineers two trace instruction flows sixteen cycles prior two fault occurrence test bench postmortem logs confirm that fixing pointer alignment in the sensor data unpacking routine eliminates hard faults across ten thousand simulated bus cycles",
        "refined_text": "In our embedded test lab our firmware debugging squad investigated recurring hard fault exceptions on our Cortex-M4 field telemetry nodes using an OpenOCD probe connected through an SWD interface. We isolated the crash by inspecting the configurable fault status register at address 0xe000ed28, which indicated an unaligned memory access inside fault_handler.c, capturing stack frame words from the process stack pointer instead of the main stack pointer.\n\nOur custom fault logger decodes the exception return address by extracting program counter values and status registers stored in SRAM. Our debugger connects through a 4 wire JTAG interface, allowing engineers to trace instruction flows 16 cycles prior to fault occurrence. Test bench postmortem logs confirm that fixing pointer alignment in the sensor data unpacking routine eliminates hard faults across 10000 simulated bus cycles."
    }
]

print(f"Total samples defined: {len(samples)}")
assert len(samples) == 20, f"Expected 20 samples, got {len(samples)}"

# 1. Leakage check
for idx, s in enumerate(samples):
    raw_clean = s["raw_asr"].strip().lower()
    ref_clean = s["refined_text"].strip()
    assert raw_clean not in eval_raws, f"Sample {idx+1} raw_asr leaked into eval set!"
    assert ref_clean not in eval_refs, f"Sample {idx+1} refined_text leaked into eval set!"
print("Leakage check: PASSED (0 overlaps with sft_eval.json)")

# 2. Pair and batch validation
for idx, s in enumerate(samples):
    is_valid, reason = validate_pair(s)
    assert is_valid, f"Sample {idx+1} failed validate_pair: {reason}"

    res, status = clean_sample(s["raw_asr"], s["refined_text"])
    assert res is not None, f"Sample {idx+1} failed clean_sample: {status}"
    assert status == "kept", f"Sample {idx+1} clean_sample status not 'kept': {status}"

is_batch_valid, batch_reason, tier_counts = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
assert is_batch_valid, f"Batch validation failed: {batch_reason}"
print(f"Batch validation: PASSED, tiers={tier_counts}")

# 3. Structural assertions
tiers = {"short": 0, "medium": 0, "long": 0}
for i, s in enumerate(samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    w_count = len(ref.split())

    raw.encode("ascii")
    ref.encode("ascii")

    assert "`" not in ref, f"Sample {i+1} has backticks!"

    if w_count < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {i+1} short has newline"
        sentences = [sent.strip() for sent in re.split(r"[.!?]+", ref) if sent.strip()]
        assert len(sentences) == 1, f"Sample {i+1} short has {len(sentences)} sentences"
        content_words = [w for w in re.findall(r"[a-zA-Z0-9]+", ref.lower()) if len(w) > 2]
        assert len(content_words) >= 6, f"Sample {i+1} short has too few content words: {len(content_words)}"
    elif w_count < 90:
        tiers["medium"] += 1
        sentences = [sent.strip() for sent in re.split(r"[.!?]+", ref) if sent.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {i+1} medium has {len(sentences)} sentences"
        assert "\n\n" in ref, f"Sample {i+1} medium missing paragraph break"
        max_breaks = max(1, w_count // 25)
        assert ref.count("\n\n") <= max_breaks, f"Sample {i+1} medium has excessive breaks"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {i+1} long missing paragraph break"
        paragraphs = ref.split("\n\n")
        assert len(paragraphs) >= 2, f"Sample {i+1} long has fewer than 2 paragraphs"
        max_breaks = max(1, w_count // 25)
        assert ref.count("\n\n") <= max_breaks, f"Sample {i+1} long has excessive breaks"

print(f"Tier distribution verification: {tiers}")
assert tiers == {"short": 4, "medium": 6, "long": 10}, f"Unexpected tiers: {tiers}"

# Save to output file
out_path = Path("scratch/subagent_batch_114.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Successfully wrote {len(samples)} samples to {out_path}")
