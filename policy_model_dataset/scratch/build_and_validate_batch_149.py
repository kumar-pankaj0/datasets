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

# Define candidate samples for Batch 149 (Domain 6: Embedded Systems & Firmware Development)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_149 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Refined content words >= 6-8. Ratio [0.35, 1.25].
    # =========================================================================

    # Sample 1: Renesas RA6M5 Cortex-M33 OctaSPI prefetch buffer
    {
        "raw_asr": "um configur the octal serial peripheral interface prefetch buffer buy writing zero x zero four into the c p u control register",
        "refined_text": "Configure the octal serial peripheral interface prefetch buffer by writing 0x04 into the CPU control register."
    },

    # Sample 2: Infineon AURIX TC397 CAN-FD nominal baud prescaler
    {
        "raw_asr": "uh calibrat the controller area network nominal baud prescaler buy loading sixteen wait twenty four d m a timing cycles",
        "refined_text": "Calibrate the controller area network nominal baud prescaler by loading 24 DMA timing cycles."
    },

    # Sample 3: Nordic nRF5340 dual-core IPC channel initialization
    {
        "raw_asr": "basically initializ the inter processor communication channel buy writing zero x zero eight into the u art status register",
        "refined_text": "Initialize the inter-processor communication channel by writing 0x08 into the UART status register."
    },

    # Sample 4: ST STM32U585 LPBAM linked-list descriptor termination
    {
        "raw_asr": "uh terminat the low power autonomous mode linked list descriptor buy writing zero x zero c into the n v i c interrupt register",
        "refined_text": "Terminate the low-power autonomous mode linked-list descriptor by writing 0x0c into the NVIC interrupt register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Microchip SAM E54 SERCOM SPI burst transfers & DMA descriptor chain
    {
        "raw_asr": "um configur the serial communication interface burst threshold buy routing sixteen wait thirty two d m a descriptors instead into the primary queue basically the s p i controller handles external telemetry streaming buy dispatching four high priority sensor buffers",
        "refined_text": "Configure the serial communication interface burst threshold by routing 32 DMA descriptors instead into the primary queue.\n\nThe SPI controller handles external telemetry streaming by dispatching 4 high-priority sensor buffers."
    },

    # Sample 6: Espressif ESP32-C6 RISC-V 32-bit FreeRTOS event queue allocation
    {
        "raw_asr": "uh allocat the wireless radio event queue buy reserving sixty four wait one two eight bytes instead into the shared memory partition four packet frames you know the free are toss kernel coordinates radio state transitions buy scheduling eight periodic timer events on the r i s c v core",
        "refined_text": "Allocate the wireless radio event queue by reserving 128 bytes instead into the shared memory partition for packet frames.\n\nThe FreeRTOS kernel coordinates radio state transitions by scheduling 8 periodic timer events on the RISC-V core."
    },

    # Sample 7: Raspberry Pi RP2040 Dual Cortex-M0+ PIO state machine clock divider
    {
        "raw_asr": "basically initializ the programmable input output state machine clock divider buy writing zero x zero four wait right zero x zero eight instead into the control register four bit pulse shaping the c p u offloads serial led frame generation buy configuring four dedicated d m a channels",
        "refined_text": "Initialize the programmable input output state machine clock divider by writing 0x08 instead into the control register for bit pulse shaping.\n\nThe CPU offloads serial LED frame generation by configuring 4 dedicated DMA channels."
    },

    # Sample 8: Texas Instruments TMS320F28379D C2000 PWM dead-band calibration
    {
        "raw_asr": "um calibrat the pulse width modulator dead band delay buy loading zero x zero two wait load zero x zero six instead into the falling edge timing register four half bridge switching the c p u monitors bus current transients buy handling sixteen n v i c conversion interrupts",
        "refined_text": "Calibrate the pulse-width modulator dead-band delay by loading 0x06 instead into the falling-edge timing register for half-bridge switching.\n\nThe CPU monitors bus current transients by handling 16 NVIC conversion interrupts."
    },

    # Sample 9: Analog Devices MAX32655 low-power comparator interrupt termination
    {
        "raw_asr": "uh terminat the analog comparator wake window buy routing eight wait sixteen d m a transfer cycles instead into the accumulator register four sleep staging the u art interface flushes buffered telemetry buy transmitting zero x zero e over two serial lines",
        "refined_text": "Terminate the analog comparator wake window by routing 16 DMA transfer cycles instead into the accumulator register for sleep staging.\n\nThe UART interface flushes buffered telemetry by transmitting 0x0e over 2 serial lines."
    },

    # Sample 10: SiFive Freedom Everywhere FE310-G002 RISC-V QSPI flash execute mode
    {
        "raw_asr": "basically configur the quad serial peripheral interface direct execute mode buy writing zero x zero one wait right zero x zero three instead into the cache control register four instruction staging the r i s c v core accelerates firmware execution buy reading four word s p i bursts",
        "refined_text": "Configure the quad serial peripheral interface direct execute mode by writing 0x03 instead into the cache control register for instruction staging.\n\nThe RISC-V core accelerates firmware execution by reading 4 word SPI bursts."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4. Natural engineer narration.
    # =========================================================================

    # Sample 11: NXP i.MX RT1170 Dual Core Crossover MCU SDIO eMMC CRC timeout
    {
        "raw_asr": "um our nxp crossover microcontroller board encountered high speed secure digital card crc transfer timeouts during burst logging over open o c d we captured the sdio differential bus clock and command lines using a logic analyzer and tracked descriptor faults across fifteen test cycles the high speed host controller stalled multi block read commands because clock phase skew corrupted data line transitions while the storage firmware lacked proper delay calibrat wait inspect the bus timing parameters inside sdio underscore timing manager module instead calibrat the input clock sample phase delay buy setting eight wait sixteen delay taps instead into the delay tuning register right zero x four zero zero four one zero zero zero into the host controller base register right zero x zero two into the clock divisor register wait right zero x zero six instead four synchronized signal sampling we cleared the transaction error flag buy writing one into the status clear register after updating the sample phase register and configuring free are toss queue depths the storage subsystem completed eight thousand block read transactions across eighteen hours without data corruption or bus timeout exceptions",
        "refined_text": "Our NXP crossover microcontroller board encountered high-speed secure digital card CRC transfer timeouts during burst logging. Over OpenOCD we captured the SDIO differential bus clock and command lines using a logic analyzer and tracked descriptor faults across 15 test cycles. The high-speed host controller stalled multi-block read commands because clock phase skew corrupted data line transitions while the storage firmware lacked proper delay calibration, inspecting the bus timing parameters inside sdio_timing_manager module instead.\n\nCalibrate the input clock sample phase delay by setting 16 delay taps instead into the delay tuning register. Write 0x40041000 into the host controller base register. Write 0x06 instead into the clock divisor register for synchronized signal sampling. We cleared the transaction error flag by writing 1 into the status clear register.\n\nAfter updating the sample phase register and configuring FreeRTOS queue depths, the storage subsystem completed 8000 block read transactions across 18 hours without data corruption or bus timeout exceptions."
    },

    # Sample 12: Infineon AURIX TC397 Automotive ASIL-D MCU CAN-FD bit-stuffing error
    {
        "raw_asr": "uh our automotive engine control unit suffered controller area network flexible data rate bit stuffing errors during high priority torque broadcast frames we connected a differential bus probe two the can transceiver pins and analyzed signal reflections over an swd interface the communication controller rejected incoming telemetry frames because edge jitter shifted bit sample points beyond the secondary sample point window while the communication stack lacked bit timing calibrat wait inspect the timing configuration inside can underscore transceiver driver module instead calibrat the transmitter delay compensation offset buy loading sixteen wait thirty two time quanta instead into the timing control register right zero x f zero zero zero four zero zero zero into the controller base register right zero x zero four into the sample point register wait right zero x zero eight instead four synchronized frame sampling we cleared the bus warning interrupt buy writing one into the error acknowledge register after programming delay compensation values and adjusting free are toss task priorities the powertrain gateway processed seven thousand can frames across twenty four hours without bit stuffing errors or message drops",
        "refined_text": "Our automotive engine control unit suffered controller area network flexible data rate bit-stuffing errors during high-priority torque broadcast frames. We connected a differential bus probe to the CAN transceiver pins and analyzed signal reflections over an SWD interface. The communication controller rejected incoming telemetry frames because edge jitter shifted bit sample points beyond the secondary sample point window while the communication stack lacked bit timing calibration, inspecting the timing configuration inside can_transceiver_driver module instead.\n\nCalibrate the transmitter delay compensation offset by loading 32 time quanta instead into the timing control register. Write 0xf0004000 into the controller base register. Write 0x08 instead into the sample point register for synchronized frame sampling. We cleared the bus warning interrupt by writing 1 into the error acknowledge register.\n\nAfter programming delay compensation values and adjusting FreeRTOS task priorities, the powertrain gateway processed 7000 CAN frames across 24 hours without bit-stuffing errors or message drops."
    },

    # Sample 13: ST STM32U585 Cortex-M33 TrustZone LPBAM DMA circular buffer overflow
    {
        "raw_asr": "basically our ultra low power environmental sensor node experienced direct memory access buffer overruns during sleep mode sensor sampling over open o c d we monitored autonomous peripheral transactions and tracked fifo overflow flags across twelve sensing intervals the low power background autonomous controller dropped incoming analog samples because circular queue pointers lost synchronization during sleep wake cycles while the peripheral driver lacked descriptor configur wait inspect the descriptor linked list inside lpbam underscore queue manager module instead configur the autonomous circular buffer size buy allocating twenty four wait forty eight descriptor nodes instead into the memory staging table right zero x four zero zero zero two zero zero zero into the peripheral base register right zero x zero one into the autonomous channel control register wait right zero x zero five instead four continuous hardware trigger servicing we cleared the fifo overflow flag buy writing one into the d m a status register after updating circular descriptor links and configuring n v i c interrupt handlers the sensor node logged nine thousand analog conversions across forty eight hours without buffer overruns or data loss",
        "refined_text": "Basically our ultra-low-power environmental sensor node experienced direct memory access buffer overruns during sleep mode sensor sampling. Over OpenOCD we monitored autonomous peripheral transactions and tracked FIFO overflow flags across 12 sensing intervals. The low-power background autonomous controller dropped incoming analog samples because circular queue pointers lost synchronization during sleep wake cycles while the peripheral driver lacked descriptor configuration, inspecting the descriptor linked list inside lpbam_queue_manager module instead.\n\nConfigure the autonomous circular buffer size by allocating 48 descriptor nodes instead into the memory staging table. Write 0x40002000 into the peripheral base register. Write 0x05 instead into the autonomous channel control register for continuous hardware trigger servicing. We cleared the FIFO overflow flag by writing 1 into the DMA status register.\n\nAfter updating circular descriptor links and configuring NVIC interrupt handlers, the sensor node logged 9000 analog conversions across 48 hours without buffer overruns or data loss."
    },

    # Sample 14: Renesas RA6M5 Cortex-M33 OctaSPI NOR flash read mode execution stall
    {
        "raw_asr": "um our industrial edge controller suffered instruction fetch bus lockups during high speed execute in place memory transitions we connected a digital logic analyzer two the octal memory lines and inspected bus read states over open o c d the memory controller froze external bus cycles because dummy cycle latency was programmed too short for high frequency clock rates while the flash driver lacked latency calibrat wait inspect the timing setup inside ospi underscore flash driver module instead calibrat the octal read dummy cycle duration buy setting ten wait sixteen clock cycles instead into the latency control register right zero x six zero zero zero zero zero zero zero into the memory map base register right zero x zero two into the read mode configuration register wait right zero x zero a instead four stable read data latching we cleared the bus hold exception buy writing one into the memory clear register after configuring correct dummy cycles and clearing the c p u instruction cache the edge controller executed twelve thousand execute in place memory bursts across thirty hours without bus stall events or instruction fetch errors",
        "refined_text": "Our industrial edge controller suffered instruction fetch bus lockups during high-speed execute-in-place memory transitions. We connected a digital logic analyzer to the octal memory lines and inspected bus read states over OpenOCD. The memory controller froze external bus cycles because dummy cycle latency was programmed too short for high-frequency clock rates while the flash driver lacked latency calibration, inspecting the timing setup inside ospi_flash_driver module instead.\n\nCalibrate the octal read dummy cycle duration by setting 16 clock cycles instead into the latency control register. Write 0x60000000 into the memory map base register. Write 0x0a instead into the read mode configuration register for stable read data latching. We cleared the bus hold exception by writing 1 into the memory clear register.\n\nAfter configuring correct dummy cycles and clearing the CPU instruction cache, the edge controller executed 12000 execute-in-place memory bursts across 30 hours without bus stall events or instruction fetch errors."
    },

    # Sample 15: Nordic nRF5340 Dual-Core BLE 5.3 SoC IPC mailbox deadlock
    {
        "raw_asr": "uh our dual core wireless audio transmitter experienced inter processor communication mailbox deadlocks during low latency audio streaming we attached a debugger two the swd interface and traced mutex wait queues across twenty four audio frame transfers the application core halted audio transmission because the network core held the shared message buffer without clearing channel acknowledge events while the inter core stack lacked timeout terminat wait inspect the shared memory map inside ipc underscore message channel module instead terminat the stalled inter processor transaction buy resetting eight wait sixteen channel flags instead into the status register right zero x four one zero one two zero zero zero into the inter processor base register right zero x zero one into the event trigger register wait right zero x zero f instead four fast channel synchronization we cleared the core deadlock fault buy writing one into the interrupt clear register after adjusting inter core channel ring buffers and configuring free are toss thread priorities the audio transmitter streamed fifteen thousand audio frames across twenty hours without core deadlocks or audio dropouts",
        "refined_text": "Our dual-core wireless audio transmitter experienced inter-processor communication mailbox deadlocks during low-latency audio streaming. We attached a debugger to the SWD interface and traced mutex wait queues across 24 audio frame transfers. The application core halted audio transmission because the network core held the shared message buffer without clearing channel acknowledge events while the inter-core stack lacked timeout termination, inspecting the shared memory map inside ipc_message_channel module instead.\n\nTerminate the stalled inter-processor transaction by resetting 16 channel flags instead into the status register. Write 0x41012000 into the inter-processor base register. Write 0x0f instead into the event trigger register for fast channel synchronization. We cleared the core deadlock fault by writing 1 into the interrupt clear register.\n\nAfter adjusting inter-core channel ring buffers and configuring FreeRTOS thread priorities, the audio transmitter streamed 15000 audio frames across 20 hours without core deadlocks or audio dropouts."
    },

    # Sample 16: Microchip SAM E54 Cortex-M4F Ethernet MAC GMAC DMA ring underflow
    {
        "raw_asr": "basically our industrial ethernet gateway suffered packet loss bursts during high throughput telemetry transfers over open o c d we monitored gigabit ethernet media access controller descriptor flags and observed transmit buffer underflow errors across sixteen burst iterations the ethernet direct memory access engine halted frame transmission because descriptor ring ownership bits were flipped prematurely during interrupt handling while the ethernet stack lacked queue allocat wait inspect the descriptor memory pool inside gmac underscore ring buffer module instead allocat the ethernet transmit descriptor pool buy reserving thirty two wait sixty four descriptor blocks instead into the shared sram memory region right zero x four zero zero four zero zero zero zero into the mac base register right zero x zero two into the transmit control register wait right zero x zero eight instead four burst descriptor fetching we cleared the transmit underflow alarm buy writing one into the status acknowledge register after updating descriptor ownership flags and tuning free are toss network buffers the industrial gateway transmitted eighteen thousand ethernet packets across thirty six hours without descriptor stalls or frame drops",
        "refined_text": "Basically our industrial Ethernet gateway suffered packet loss bursts during high-throughput telemetry transfers. Over OpenOCD we monitored gigabit Ethernet media access controller descriptor flags and observed transmit buffer underflow errors across 16 burst iterations. The Ethernet direct memory access engine halted frame transmission because descriptor ring ownership bits were flipped prematurely during interrupt handling while the Ethernet stack lacked queue allocation, inspecting the descriptor memory pool inside gmac_ring_buffer module instead.\n\nAllocate the Ethernet transmit descriptor pool by reserving 64 descriptor blocks instead into the shared SRAM memory region. Write 0x40040000 into the MAC base register. Write 0x08 instead into the transmit control register for burst descriptor fetching. We cleared the transmit underflow alarm by writing 1 into the status acknowledge register.\n\nAfter updating descriptor ownership flags and tuning FreeRTOS network buffers, the industrial gateway transmitted 18000 Ethernet packets across 36 hours without descriptor stalls or frame drops."
    },

    # Sample 17: Raspberry Pi RP2040 Dual Cortex-M0+ PIO video generator FIFO underflow
    {
        "raw_asr": "um our dual core display subsystem experienced video line jitter and display synchronization loss during high resolution scanline rendering we probed horizontal sync and rgb serial pins using an oscilloscope and tracked fifo empty flags over open o c d the programmable input output state machine stalled scanline shifting because d m a transfer requests failed two replenish data words before the fifo drained while the graphics driver lacked transfer configur wait inspect the state machine instructions inside pio underscore video generator module instead configur the display state machine clock divisor buy setting four wait eight clock cycles instead into the execution control register right zero x five zero two zero zero zero zero zero into the pio base register right zero x zero one into the channel enable register wait right zero x zero three instead four synchronized scanline output we cleared the fifo stall flag buy writing one into the interrupt clear register after reordering d m a request priorities and configuring c p u memory arbitration the display subsystem rendered twenty thousand consecutive video frames across twenty four hours without scanline tearing or frame drop faults",
        "refined_text": "Our dual-core display subsystem experienced video line jitter and display synchronization loss during high-resolution scanline rendering. We probed horizontal sync and RGB serial pins using an oscilloscope and tracked FIFO empty flags over OpenOCD. The programmable input-output state machine stalled scanline shifting because DMA transfer requests failed to replenish data words before the FIFO drained while the graphics driver lacked transfer configuration, inspecting the state machine instructions inside pio_video_generator module instead.\n\nConfigure the display state machine clock divisor by setting 8 clock cycles instead into the execution control register. Write 0x50200000 into the PIO base register. Write 0x03 instead into the channel enable register for synchronized scanline output. We cleared the FIFO stall flag by writing 1 into the interrupt clear register.\n\nAfter reordering DMA request priorities and configuring CPU memory arbitration, the display subsystem rendered 20000 consecutive video frames across 24 hours without scanline tearing or frame drop faults."
    },

    # Sample 18: Espressif ESP32-C6 RISC-V 32-bit Hardware Crypto DMA bus lock
    {
        "raw_asr": "uh our secure iot sensor node suffered cryptographic calculation timeouts during transport layer security handshake negotiation we attached a logic analyzer two the internal peripheral bus lines and monitored hardware crypto flags over open o c d the hardware symmetric encryption engine stalled block cipher operations because direct memory access burst alignments mismatched sram cache line boundaries while the cryptographic firmware lacked bus arbitrat wait inspect the crypto buffer descriptors inside aes underscore crypto engine module instead arbitrat the cryptographic memory access buy allocating sixteen wait thirty two burst words instead into the peripheral control register right zero x six zero zero zero eight zero zero zero into the cryptographic base register right zero x zero two into the operation mode register wait right zero x zero c instead four accelerated block processing we cleared the hardware cipher busy flag buy writing one into the status clear register after aligning d m a packet memory and configuring free are toss task priorities on the r i s c v core the sensor node completed eleven thousand handshake operations across twenty hours without bus stalls or authentication timeouts",
        "refined_text": "Our secure IoT sensor node suffered cryptographic calculation timeouts during transport layer security handshake negotiation. We attached a logic analyzer to the internal peripheral bus lines and monitored hardware crypto flags over OpenOCD. The hardware symmetric encryption engine stalled block cipher operations because direct memory access burst alignments mismatched SRAM cache line boundaries while the cryptographic firmware lacked bus arbitration, inspecting the crypto buffer descriptors inside aes_crypto_engine module instead.\n\nArbitrate the cryptographic memory access by allocating 32 burst words instead into the peripheral control register. Write 0x60008000 into the cryptographic base register. Write 0x0c instead into the operation mode register for accelerated block processing. We cleared the hardware cipher busy flag by writing 1 into the status clear register.\n\nAfter aligning DMA packet memory and configuring FreeRTOS task priorities on the RISC-V core, the sensor node completed 11000 handshake operations across 20 hours without bus stalls or authentication timeouts."
    },

    # Sample 19: Texas Instruments TMS320F28379D C2000 CLA task trigger jitter
    {
        "raw_asr": "basically our solar inverter motor control unit experienced phase current distortion during fast load step transients we monitored analog two digital converter interrupt signals and tracked control law execution cycles over an jtag debug probe the auxiliary math coprocessor delayed field oriented control calculations because hardware conversion interrupts collided with trigonometric instruction pipelines while the control firmware lacked timing calibrat wait inspect the math execution schedule inside cla underscore motor controller module instead calibrat the coprocessor task trigger prescaler buy assigning four wait eight timing cycles instead into the trigger control register right zero x zero zero zero zero seven zero zero zero into the coprocessor base register right zero x zero one into the task start register wait right zero x zero seven instead four synchronized current loop execution we cleared the interrupt overrun alarm buy writing one into the n v i c acknowledge register after adjusting analog sampling delays and configuring c p u task handshakes the motor control unit processed twenty two thousand field oriented control cycles across thirty hours without phase distortion or calculation overruns",
        "refined_text": "Basically our solar inverter motor control unit experienced phase current distortion during fast load step transients. We monitored analog-to-digital converter interrupt signals and tracked control law execution cycles over an JTAG debug probe. The auxiliary math coprocessor delayed field-oriented control calculations because hardware conversion interrupts collided with trigonometric instruction pipelines while the control firmware lacked timing calibration, inspecting the math execution schedule inside cla_motor_controller module instead.\n\nCalibrate the coprocessor task trigger prescaler by assigning 8 timing cycles instead into the trigger control register. Write 0x00007000 into the coprocessor base register. Write 0x07 instead into the task start register for synchronized current loop execution. We cleared the interrupt overrun alarm by writing 1 into the NVIC acknowledge register.\n\nAfter adjusting analog sampling delays and configuring CPU task handshakes, the motor control unit processed 22000 field-oriented control cycles across 30 hours without phase distortion or calculation overruns."
    },

    # Sample 20: Silicon Labs EFR32MG24 Series 2 Wireless Gecko DCDC brownout reset
    {
        "raw_asr": "um our zigbee mesh sensor router experienced unexpected hardware watchdog resets during high power radio transmission bursts we probed internal power rails using an oscilloscope and tracked brownout detector status flags over open o c d the on chip power management unit triggered false reset alarms because rapid current transients during power amplifier ramp up caused local supply rail voltage drops while the power configuration lacked threshold configur wait inspect the regulator settings inside dcdc underscore power manager module instead configur the brownout detector trip threshold buy setting twelve wait twenty four millivolt steps instead into the voltage control register right zero x five zero zero four four zero zero zero into the power manager base register right zero x zero two into the regulator trim register wait right zero x zero e instead four stable voltage regulation we cleared the brownout reset event buy writing one into the fault clear register after adjusting buck converter inductor timings and configuring free are toss radio sleep intervals the mesh router forwarded sixteen thousand wireless mesh packets across twenty eight hours without supply voltage drops or unexpected watchdog resets",
        "refined_text": "Our Zigbee mesh sensor router experienced unexpected hardware watchdog resets during high-power radio transmission bursts. We probed internal power rails using an oscilloscope and tracked brownout detector status flags over OpenOCD. The on-chip power management unit triggered false reset alarms because rapid current transients during power amplifier ramp-up caused local supply rail voltage drops while the power configuration lacked threshold configuration, inspecting the regulator settings inside dcdc_power_manager module instead.\n\nConfigure the brownout detector trip threshold by setting 24 millivolt steps instead into the voltage control register. Write 0x50044000 into the power manager base register. Write 0x0e instead into the regulator trim register for stable voltage regulation. We cleared the brownout reset event by writing 1 into the fault clear register.\n\nAfter adjusting buck converter inductor timings and configuring FreeRTOS radio sleep intervals, the mesh router forwarded 16000 wireless mesh packets across 28 hours without supply voltage drops or unexpected watchdog resets."
    },
]

# Run deterministic checks
print(f"Total candidate samples: {len(batch_149)}")

tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, s in enumerate(batch_149, 1):
    raw = s["raw_asr"].strip()
    ref = s["refined_text"].strip()
    
    # Eval set leakage check
    if raw.lower() in eval_raws:
        print(f"ERROR: Sample {idx} raw_asr leaks into eval set!")
        sys.exit(1)
    if ref in eval_refs:
        print(f"ERROR: Sample {idx} refined_text leaks into eval set!")
        sys.exit(1)
        
    # Cleaner check
    cleaned, status = cleaner.clean_sample(raw, ref)
    if status != "kept":
        print(f"ERROR: Sample {idx} failed cleaner with status: {status}")
        sys.exit(1)
        
    # Validator pair check with min_noise_layers=4
    ok, reason = validator.validate_pair(s, min_noise_layers=4)
    if not ok:
        print(f"ERROR: Sample {idx} failed validator: {reason}")
        sys.exit(1)
        
    w = len(ref.split())
    if w < 25:
        tier_counts["short"] += 1
    elif w < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1
        
    nl = validator.get_noise_layer_count(raw)
    layer_counts.append(nl)
    layers_dict = validator.count_active_noise_layers(raw)
    active = [k for k, v in layers_dict.items() if v]
    print(f"Sample {idx:02d}: words={w:3d}, noise_layers={nl} ({', '.join(active)}), status={status}")

# Batch validation check
ok, reason, stats = validator.validate_batch(
    batch_149,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)

if not ok:
    print(f"ERROR: Batch validation failed: {reason}")
    sys.exit(1)

print("\n--- BATCH VALIDATION SUMMARY ---")
print(f"Batch validation: {ok} ({reason})")
print(f"Tier counts: {tier_counts}")
avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {stats.get('noise_layer_distribution')}")

# Save to output file
out_path = Path("scratch/subagent_batch_149.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(batch_149, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(batch_149)} samples to {out_path}")
