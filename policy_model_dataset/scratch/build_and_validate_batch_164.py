import json
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from cleaner import clean_sample

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. Zero newlines. Max 1 cut-word. Active layers >= 3.
    # =========================================================================

    # Sample 1: STM32 DMA circular buffer base address initialization
    {
        "raw_asr": "um initializ the d m a circular buffer base address register zero x four zero buy assigning eight descriptors",
        "refined_text": "Initialize the DMA circular buffer base address register 0x40 by assigning 8 descriptors."
    },

    # Sample 2: ESP32 FreeRTOS watchdog timer threshold calibration
    {
        "raw_asr": "basically calibrat the free are toss watchdog timer threshold buy setting four millisecond intervals instead of eight",
        "refined_text": "Calibrate the FreeRTOS watchdog timer threshold by setting 4 millisecond intervals instead of 8."
    },

    # Sample 3: RP2040 SPI baud rate clock divider configuration
    {
        "raw_asr": "uh configur the s p i clock divider register zero x two zero buy writing sixteen prescaler ticks wait thirty two ticks instead",
        "refined_text": "Configure the SPI clock divider register 0x20 by writing 32 prescaler ticks instead."
    },

    # Sample 4: RISC-V interrupt priority register allocation
    {
        "raw_asr": "um allocat the r i s c v interrupt priority register zero x one zero buy routing four peripheral channels",
        "refined_text": "Allocate the RISC-V interrupt priority register 0x10 by routing 4 peripheral channels."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 sentences. Natural \n\n breaks. Max \n\n: words // 25. Active layers >= 4.
    # =========================================================================

    # Sample 5: I2C hardware bus lockup recovery via clock pulsing
    {
        "raw_asr": "um operat i two c recovery routines inside i two c underscore bus dot c buy pulsing the serial clock line nine times wait switch to twelve clock pulses instead buy clearing the stuck data line right zero x zero to the control register four reset",
        "refined_text": "Operate I2C recovery routines inside i2c_bus.c by pulsing the serial clock line 12 clock pulses instead, clearing the stuck data line.\n\nWrite 0x0 to the control register for reset."
    },

    # Sample 6: CAN-FD message mailbox filter configuration and transmission arbitration
    {
        "raw_asr": "uh configur the can filter bank inside can underscore driver dot c buy matching identifier zero x one zero zero across sixteen mailboxes wait thirty two mailboxes instead you know arbitrat frame headers buy sorting pending d m a message queues across eight channel buffers four transmission",
        "refined_text": "Configure the CAN filter bank inside can_driver.c by matching identifier 0x100 across 32 mailboxes instead.\n\nArbitrate frame headers by sorting pending DMA message queues across 8 channel buffers for transmission."
    },

    # Sample 7: Zephyr RTOS UART DMA ring buffer receiver overrun handling
    {
        "raw_asr": "basically configur the u art ring buffer inside serial underscore queue dot c buy setting the receiver threshold two sixty four bytes wait one two eight bytes instead um communicat incoming byte streams buy linking d m a channel zero x two zero four streaming right eight error counters four overflow tracking",
        "refined_text": "Configure the UART ring buffer inside serial_queue.c by setting the receiver threshold to 128 bytes instead.\n\nCommunicate incoming byte streams by linking DMA channel 0x20 for streaming. Write 8 error counters for overflow tracking."
    },

    # Sample 8: Flash memory controller sector erase timing on STM32H7
    {
        "raw_asr": "um initializ the flash memory controller sector timing inside flash underscore driver dot c buy locking the erase sequence register zero x four zero wait zero x eight zero instead you know calibrat sector program delays buy reading four c p u status bits right twelve diagnostic words four sector validation",
        "refined_text": "Initialize the flash memory controller sector timing inside flash_driver.c by locking the erase sequence register 0x80 instead.\n\nCalibrate sector program delays by reading 4 CPU status bits. Write 12 diagnostic words for sector validation."
    },

    # Sample 9: ESP32-S3 bootloader partition table flashing via esptool
    {
        "raw_asr": "uh initializ the esp tool flash writer script buy specifying baud rate one one five two zero zero wait four six zero eight zero zero instead inside partition underscore table dot py basically allocat offset zero x nine zero zero zero buy flashing four binary images into boot slots right sixteen status checks four target verification",
        "refined_text": "Initialize the esptool flash writer script by specifying baud rate 460800 instead inside partition_table.py.\n\nAllocate offset 0x9000 by flashing 4 binary images into boot slots. Write 16 status checks for target verification."
    },

    # Sample 10: RISC-V hardware timer SysTick interrupt latency compensation
    {
        "raw_asr": "basically recalculat the r i s c v timer compare register zero x three zero buy writing sixteen thousand clock cycles wait thirty two thousand cycles instead you know operat interrupt latency counters buy capturing eight c p u register states four analysis right four status metrics four diagnostic tracking",
        "refined_text": "Recalculate the RISC-V timer compare register 0x30 by writing 32000 cycles instead.\n\nOperate interrupt latency counters by capturing 8 CPU register states for analysis. Write 4 status metrics for diagnostic tracking."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Active layers >= 4. Rationale with gerunds. Natural spoken engineer narration.
    # =========================================================================

    # Sample 11: STM32 DMA circular buffer cache coherency failure with L1 D-cache invalidation
    {
        "raw_asr": "um our firmware team debugged d m a circular buffer corruption inside adc underscore stream dot c buy isolating l one data cache invalidation failures previously unaligned buffer allocations caused stale c p u cache lines during high speed conversions exhausting four zero nine six sample buffers across eight conversion frames wait sixteen conversion frames instead buy preserving dirty cache lines basically our systems developers updated the memory configuration which aligns d m a buffer descriptors across thirty two byte cache boundaries buy verifying base address zero x two zero zero zero zero zero zero zero before starting stream transfers so basically when incoming analog conversions complete the driver invalidates active cache ranges wait configur circular threshold limits buy setting half transfer interrupt flags across four status registers instead okay so instruct engineering two benchmark sampling throughput across sixty four conversion passes right four unit tests confirming cache clean operations four memory consistency",
        "refined_text": "Our firmware team debugged DMA circular buffer corruption inside adc_stream.c by isolating L1 data cache invalidation failures. Previously unaligned buffer allocations caused stale CPU cache lines during high speed conversions, exhausting 4096 sample buffers across 16 conversion frames instead, by preserving dirty cache lines.\n\nOur systems developers updated the memory configuration which aligns DMA buffer descriptors across 32 byte cache boundaries by verifying base address 0x20000000 before starting stream transfers. When incoming analog conversions complete, the driver invalidates active cache ranges, configuring circular threshold limits by setting half transfer interrupt flags across 4 status registers instead.\n\nInstruct engineering to benchmark sampling throughput across 64 conversion passes, and write 4 unit tests confirming cache clean operations for memory consistency."
    },

    # Sample 12: FreeRTOS task priority inversion on shared I2C telemetry bus
    {
        "raw_asr": "basically our control squad resolved priority inversion latency inside telemetry underscore bus dot c buy upgrading free are toss synchronization primitives across shared peripheral devices previously standard binary semaphores caused unbounded blocking during sensor reads delaying critical motor control loops across ten milliseconds wait twenty milliseconds instead buy stalling high priority threads uh the firmware engineers built a mutex wrapper which enforces priority inheritance across twelve task queues buy boosting holder priority before bus transactions so basically when a background sensor worker acquires the peripheral the scheduler arbitrat task priorities wait allocat priority ceiling structures buy writing zero x four zero to mutex control fields instead okay so instruct validation two profile bus acquisition latency across fifty telemetry cycles right four unit tests confirming priority restoration four suspended tasks",
        "refined_text": "Our control squad resolved priority inversion latency inside telemetry_bus.c by upgrading FreeRTOS synchronization primitives across shared peripheral devices. Previously standard binary semaphores caused unbounded blocking during sensor reads, delaying critical motor control loops across 20 milliseconds instead, by stalling high priority threads.\n\nThe firmware engineers built a mutex wrapper which enforces priority inheritance across 12 task queues by boosting holder priority before bus transactions. When a background sensor worker acquires the peripheral, the scheduler arbitrates task priorities, allocating priority ceiling structures by writing 0x40 to mutex control fields instead.\n\nInstruct validation to profile bus acquisition latency across 50 telemetry cycles, and write 4 unit tests confirming priority restoration for suspended tasks."
    },

    # Sample 13: ESP32-S3 high-speed SPI flash quad-I/O timing skew debug
    {
        "raw_asr": "um our platform infrastructure squad resolved quad flash timing skew inside flash underscore timing dot c buy tuning input delay lines across external s p i flash memory previously high temperature operations caused intermittent read failures during code execution dropping data packets across eight memory sectors wait sixteen memory sectors instead buy corrupting quad data phases basically the hardware engineers deployed open o c d jtag scripts which inspect peripheral timing registers across thirty two flash blocks buy measuring propagation delays before boot execution so basically when the core initializes external flash the controller calibrat timing phases wait communicat diagnostic delay values buy writing zero x one zero two delay register banks instead okay so run esp tool dash dash flash mode qio two verify partition headers across forty read cycles right four unit tests confirming flash integrity four production firmware",
        "refined_text": "Our platform infrastructure squad resolved quad flash timing skew inside flash_timing.c by tuning input delay lines across external SPI flash memory. Previously high temperature operations caused intermittent read failures during code execution, dropping data packets across 16 memory sectors instead, by corrupting quad data phases.\n\nThe hardware engineers deployed OpenOCD JTAG scripts which inspect peripheral timing registers across 32 flash blocks by measuring propagation delays before boot execution. When the core initializes external flash, the controller calibrates timing phases, communicating diagnostic delay values by writing 0x10 to delay register banks instead.\n\nRun `esptool --flash-mode qio` to verify partition headers across 40 read cycles, and write 4 unit tests confirming flash integrity for production firmware."
    },

    # Sample 14: nRF52840 BLE peripheral radio DMA buffer starvation postmortem
    {
        "raw_asr": "basically our wireless group resolved radio buffer starvation inside ble underscore radio dot c buy isolating d m a packet queue bottlenecks previously long flash write operations stalled interrupt handlers dropping radio packets across ten transmission windows wait twenty transmission windows instead buy delaying packet acknowledgments uh the embedded developers designed an asynchronous buffer pool which chains d m a descriptors across thirty two hardware channels buy reserving dedicated ram buffers before radio events so basically when the core starts packet transmission the controller allocat circular descriptor blocks wait configur buffer ring thresholds buy writing zero x eight zero to d m a control registers instead okay so instruct engineering two benchmark radio latency across fifty connection events right four unit tests confirming zero dropped packets four continuous streaming",
        "refined_text": "Our wireless group resolved radio buffer starvation inside ble_radio.c by isolating DMA packet queue bottlenecks. Previously long flash write operations stalled interrupt handlers, dropping radio packets across 20 transmission windows instead, by delaying packet acknowledgments.\n\nThe embedded developers designed an asynchronous buffer pool which chains DMA descriptors across 32 hardware channels by reserving dedicated RAM buffers before radio events. When the core starts packet transmission, the controller allocates circular descriptor blocks, configuring buffer ring thresholds by writing 0x80 to DMA control registers instead.\n\nInstruct engineering to benchmark radio latency across 50 connection events, and write 4 unit tests confirming zero dropped packets for continuous streaming."
    },

    # Sample 15: RISC-V machine-mode trap handler and CSR register state corruption postmortem
    {
        "raw_asr": "um our core architecture group fixed trap handler register corruption inside trap underscore handler dot c buy isolating nested interrupt stack frames previously concurrent interrupt signals overwrote machine status registers during trap handling crashing firmware execution across eight worker threads wait sixteen worker threads instead buy corrupting machine program counters basically the firmware engineers updated the r i s c v interrupt dispatcher which saves control and status registers across thirty two stack words buy disabling global interrupts before context switches so basically when an external exception occurs the core initializ exception frame pointers wait switch to atomic stack allocation buy writing zero x three zero two n v i c priority registers instead okay so instruct verification two audit exception recovery across forty simulated faults right four unit tests confirming register integrity four nested interrupts",
        "refined_text": "Our core architecture group fixed trap handler register corruption inside trap_handler.c by isolating nested interrupt stack frames. Previously concurrent interrupt signals overwrote machine status registers during trap handling, crashing firmware execution across 16 worker threads instead, by corrupting machine program counters.\n\nThe firmware engineers updated the RISC-V interrupt dispatcher which saves control and status registers across 32 stack words by disabling global interrupts before context switches. When an external exception occurs, the core initializes exception frame pointers, switching to atomic stack allocation by writing 0x30 to NVIC priority registers instead.\n\nInstruct verification to audit exception recovery across 40 simulated faults, and write 4 unit tests confirming register integrity for nested interrupts."
    },

    # Sample 16: RP2040 PIO state machine DMA FIFO overflow during video synthesis
    {
        "raw_asr": "uh our graphics subsystem squad resolved pio fifo underflow errors inside video underscore pio dot c buy optimizing d m a channel pacing across video scanlines previously unpaced memory requests caused fifo starvation during active display phases dropping scanline signals across twelve video lines wait twenty four video lines instead buy desynchronizing serial pixel clocks basically our embedded engineers tuned the programmable input output state machine which balances transfer requests across eight data words buy asserting d m a pacing triggers before frame transfers so basically when the display engine generates pixel timing the controller configur fifo depth registers wait operat double buffered streams buy writing zero x five zero to channel control registers instead okay so instruct engineering two benchmark pixel jitter across sixty frame cycles right four unit tests verifying continuous video generation four display panels",
        "refined_text": "Our graphics subsystem squad resolved PIO FIFO underflow errors inside video_pio.c by optimizing DMA channel pacing across video scanlines. Previously unpaced memory requests caused FIFO starvation during active display phases, dropping scanline signals across 24 video lines instead, by desynchronizing serial pixel clocks.\n\nOur embedded engineers tuned the programmable input output state machine which balances transfer requests across 8 data words by asserting DMA pacing triggers before frame transfers. When the display engine generates pixel timing, the controller configures FIFO depth registers, operating double buffered streams by writing 0x50 to channel control registers instead.\n\nInstruct engineering to benchmark pixel jitter across 60 frame cycles, and write 4 unit tests verifying continuous video generation for display panels."
    },

    # Sample 17: PMBus telemetry sensor I2C clock stretching timeout lockup resolution
    {
        "raw_asr": "um our hardware platform squad resolved bus lockup timeouts inside pmbus underscore monitor dot c buy isolating clock stretching delays across power telemetry sensors previously prolonged sensor sampling held clock lines low during voltage queries causing bus lockups across eight telemetry polling loops wait sixteen polling loops instead buy halting peripheral communications basically our firmware engineers implemented a bus timeout interrupt which monitors serial lines across thirty two microsecond intervals buy asserting hardware timeout flags before state machine lockups so basically when an unresponsive sensor holds clock signals the controller initializ bus reset sequences wait communicat recovery clock toggles buy writing zero x seven zero two i two c control registers instead okay so instruct validation two benchmark bus recovery latency across forty fault injections right four unit tests confirming error clearance four telemetry monitors",
        "refined_text": "Our hardware platform squad resolved bus lockup timeouts inside pmbus_monitor.c by isolating clock stretching delays across power telemetry sensors. Previously prolonged sensor sampling held clock lines low during voltage queries, causing bus lockups across 16 polling loops instead, by halting peripheral communications.\n\nOur firmware engineers implemented a bus timeout interrupt which monitors serial lines across 32 microsecond intervals by asserting hardware timeout flags before state machine lockups. When an unresponsive sensor holds clock signals, the controller initializes bus reset sequences, communicating recovery clock toggles by writing 0x70 to I2C control registers instead.\n\nInstruct validation to benchmark bus recovery latency across 40 fault injections, and write 4 unit tests confirming error clearance for telemetry monitors."
    },

    # Sample 18: High-baud rate UART hardware flow control FIFO overrun on industrial gateway
    {
        "raw_asr": "uh our telemetry gateway squad resolved buffer overrun failures inside serial underscore gateway dot c buy reconfiguring hardware flow control watermarks across high speed serial ports previously late request to send deassertion caused buffer overflows during burst reads dropping telemetry frames across ten data packets wait twenty data packets instead buy overflowing receive buffers basically the systems developers tuned the u art fifo thresholds which assert flow control across eight byte margins buy checking remaining buffer capacity before fifo saturation so basically when incoming bursts enter serial queues the controller calibrat threshold levels wait arbitrat flow control lines buy writing zero x six zero two hardware flow registers instead okay so instruct engineering two benchmark throughput across fifty burst transmissions right four unit tests confirming zero byte loss four telemetry streams",
        "refined_text": "Our telemetry gateway squad resolved buffer overrun failures inside serial_gateway.c by reconfiguring hardware flow control watermarks across high speed serial ports. Previously late request to send deassertion caused buffer overflows during burst reads, dropping telemetry frames across 20 data packets instead, by overflowing receive buffers.\n\nThe systems developers tuned the UART FIFO thresholds which assert flow control across 8 byte margins by checking remaining buffer capacity before FIFO saturation. When incoming bursts enter serial queues, the controller calibrates threshold levels, arbitrating flow control lines by writing 0x60 to hardware flow registers instead.\n\nInstruct engineering to benchmark throughput across 50 burst transmissions, and write 4 unit tests confirming zero byte loss for telemetry streams."
    },

    # Sample 19: Microcontroller low-power sleep mode clock domain handover and RTC wake jitter
    {
        "raw_asr": "um our battery optimization group eliminated clock handover instability inside power underscore manager dot c buy isolating phase locked loop stabilization delays across wake transitions previously premature clock switching caused hard faults during wake cycles stalling c p u instructions across twelve clock cycles wait twenty four clock cycles instead buy executing before oscillator lock basically our firmware engineers implemented a clock handover sequencer which polls oscillator ready flags across thirty two microsecond windows buy verifying clock stability before switching system sources so basically when the real time clock wakes the core the controller configur power control registers wait switch to high frequency pll operation buy writing zero x two four two clock configuration registers instead okay so instruct validation two benchmark wake latency across fifty power cycles right four unit tests confirming frequency stability four sleep transitions",
        "refined_text": "Our battery optimization group eliminated clock handover instability inside power_manager.c by isolating phase locked loop stabilization delays across wake transitions. Previously premature clock switching caused hard faults during wake cycles, stalling CPU instructions across 24 clock cycles instead, by executing before oscillator lock.\n\nOur firmware engineers implemented a clock handover sequencer which polls oscillator ready flags across 32 microsecond windows by verifying clock stability before switching system sources. When the real time clock wakes the core, the controller configures power control registers, switching to high frequency PLL operation by writing 0x24 to clock configuration registers instead.\n\nInstruct validation to benchmark wake latency across 50 power cycles, and write 4 unit tests confirming frequency stability for sleep transitions."
    },

    # Sample 20: Embedded bootloader firmware signature verification and fault injection mitigation
    {
        "raw_asr": "basically our security firmware squad prevented glitch bypass vulnerabilities inside secure underscore boot dot c buy hardening signature verification branches across external flash partitions previously single branch checks allowed fault injection bypasses during voltage glitching booting corrupted binaries across eight execution attempts wait sixteen execution attempts instead buy skipping cryptographic assertions uh the embedded security engineers deployed redundant verification checks which evaluate signature digests across thirty two memory words buy comparing intermediate states before r i s c v core execution so basically when the bootloader validates an application image the controller terminat unverified boot sequences wait halt execution buy writing zero x four four two watchdog control registers instead okay so instruct engineering two benchmark verification duration across forty boot iterations right four unit tests confirming fault resistance four production devices",
        "refined_text": "Our security firmware squad prevented glitch bypass vulnerabilities inside secure_boot.c by hardening signature verification branches across external flash partitions. Previously single branch checks allowed fault injection bypasses during voltage glitching, booting corrupted binaries across 16 execution attempts instead, by skipping cryptographic assertions.\n\nThe embedded security engineers deployed redundant verification checks which evaluate signature digests across 32 memory words by comparing intermediate states before RISC-V core execution. When the bootloader validates an application image, the controller terminates unverified boot sequences, halting execution by writing 0x44 to watchdog control registers instead.\n\nInstruct engineering to benchmark verification duration across 40 boot iterations, and write 4 unit tests confirming fault resistance for production devices."
    }
]

# Output file path
output_file = Path("scratch/subagent_batch_164.json")

print(f"Validating {len(batch)} pairs...")
assert len(batch) == 20, f"Expected exactly 20 pairs, got {len(batch)}"

# Check leakage against sft_eval.json
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(batch, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    # Validate pair
    words = len(ref.split())
    target_min = 3 if words < 25 else 4
    val_ok, val_reason = validate_pair(pair, min_noise_layers=target_min)
    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Clean sample
    clean_obj, clean_reason = clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

    # Tier tracking
    nl = get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tier_counts["short"] += 1
        assert "\n" not in ref, f"Sample {idx} short has newline"
        assert nl >= 3, f"Sample {idx} short noise layers < 3 ({nl})"
    elif words < 90:
        tier_counts["medium"] += 1
        assert nl >= 4, f"Sample {idx} medium noise layers < 4 ({nl})"
    else:
        tier_counts["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} long missing paragraph break"
        assert nl >= 4, f"Sample {idx} long noise layers < 4 ({nl})"

# Batch validation
batch_ok, batch_reason, batch_stats = validate_batch(
    batch,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"

# Write verified pairs
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Batch written to {output_file}")
print(f"Tier counts: {tier_counts}")
print(f"Average noise layers: {batch_stats.get('avg_noise_layers')}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")
