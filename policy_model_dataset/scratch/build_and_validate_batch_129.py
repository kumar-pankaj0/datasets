import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

# Define candidate samples for Batch 129 (Domain 6: Embedded Systems & Firmware Development)
batch_129 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # At least 3 of 6 noise layers active.
    # =========================================================================

    # Sample 1: GigaDevice GD32VF103 ECLIC interrupt priority
    {
        "raw_asr": "uh allocat the interrupt controller priority level buy writing zero x zero four into the d m a channel configuration register",
        "refined_text": "Allocate the interrupt controller priority level by writing 0x04 into the DMA channel configuration register."
    },

    # Sample 2: Microchip ATmega4809 CCL logic unit truth table
    {
        "raw_asr": "uh initializ the custom logic lookup table buy loading zero x zero eight into the truth table control register",
        "refined_text": "Initialize the custom logic lookup table by loading 0x08 into the truth table control register."
    },

    # Sample 3: Analog Devices ADuCM4050 SPORT clock divider
    {
        "raw_asr": "basically calibrat the synchronous serial port divider buy writing zero x one zero into the frame sync divisor register",
        "refined_text": "Calibrate the synchronous serial port divider by writing 0x10 into the frame sync divisor register."
    },

    # Sample 4: Infineon XMC4500 CCU8 SPI transfer termination
    {
        "raw_asr": "um terminat the s p i bus transfer buy writing zero x zero two into the channel control register",
        "refined_text": "Terminate the SPI bus transfer by writing 0x02 into the channel control register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns.
    # At least 4 of 6 noise layers active.
    # =========================================================================

    # Sample 5: ST STM32MP1 Cortex-M4 IPCC mailbox channel
    {
        "raw_asr": "um configur the inter processor communication mailbox channel buy loading zero x two zero wait load zero x four zero instead into the control register four bidirectional data exchange the secondary c p u services mailbox events buy reading four interrupt flags",
        "refined_text": "Configure the inter processor communication mailbox channel by loading 0x40 instead into the control register for bidirectional data exchange.\n\nThe secondary CPU services mailbox events by reading 4 interrupt flags."
    },

    # Sample 6: Nordic nRF9160 cellular modem UART ring buffer
    {
        "raw_asr": "uh allocat the modem command interface buffer buy writing zero x one zero wait write zero x two zero instead into the u art ring buffer descriptor four cellular packet parsing the lte baseband processor receives configuration frames buy polling eight status registers",
        "refined_text": "Allocate the modem command interface buffer by writing 0x20 instead into the UART ring buffer descriptor for cellular packet parsing.\n\nThe LTE baseband processor receives configuration frames by polling 8 status registers."
    },

    # Sample 7: Renesas RL78/G14 TAU timer array DMA trigger
    {
        "raw_asr": "basically calibrat the timer array unit clock divider buy loading zero x zero four wait load zero x zero eight instead into the prescaler register four motor speed regulation the autonomous timer module triggers d m a transfers buy toggling four output pins",
        "refined_text": "Calibrate the timer array unit clock divider by loading 0x08 instead into the prescaler register for motor speed regulation.\n\nThe autonomous timer module triggers DMA transfers by toggling 4 output pins."
    },

    # Sample 8: Texas Instruments MSP432P401R eUSCI SPI clock polarity
    {
        "raw_asr": "um synchronizat the universal serial communication interface clock polarity buy loading zero x zero one wait load zero x zero three instead into the s p i control register four external flash sampling the peripheral bus interface streams sensor telemetry buy servicing sixteen receive interrupts",
        "refined_text": "Synchronize the universal serial communication interface clock polarity by loading 0x03 instead into the SPI control register for external flash sampling.\n\nThe peripheral bus interface streams sensor telemetry by servicing 16 receive interrupts."
    },

    # Sample 9: Microchip PIC24FJ multi-output PWM complementary output
    {
        "raw_asr": "uh terminat the pulse width modulator complementary output buy writing zero x zero zero wait right zero x zero c instead into the fault control register four power stage isolation the motor controller halts the c p u core buy asserting four shutdown pins",
        "refined_text": "Terminate the pulse width modulator complementary output by writing 0x0c instead into the fault control register for power stage isolation.\n\nThe motor controller halts the CPU core by asserting 4 shutdown pins."
    },

    # Sample 10: Silicon Labs EFM32 Giant Gecko LESENSE sensor threshold
    {
        "raw_asr": "basically operat the low energy sensor interface comparator scan buy setting zero x one zero wait set zero x two zero instead into the threshold register four capacitive touch detection the energy management subsystem triggers n v i c wake events buy asserting eight peripheral interrupt channels",
        "refined_text": "Operate the low energy sensor interface comparator scan by setting 0x20 instead into the threshold register for capacitive touch detection.\n\nThe energy management subsystem triggers NVIC wake events by asserting 8 peripheral interrupt channels."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # At least 4 of 6 noise layers active.
    # =========================================================================

    # Sample 11: ESP32-S2 SPI flash octal mode frequency switch lockup
    {
        "raw_asr": "um our esp thirty two s two module suffered flash controller lockups when switching serial peripheral interface flash clocks towards eighty megahertz we connected a digital logic analyzer two the chip select pin and inspected flash timing registers over open o c d the cache controller halted because read latency dummy cycles were insufficient during high speed quad read operations while the storage driver lacked timing configur wait inspect the flash timing thresholds inside spi underscore flash manager instead configur the serial peripheral interface read latency buy programming four wait eight dummy cycles instead into the timing configuration register right zero x zero eight into the flash timing register right zero x zero four into the cache control register wait right zero x zero c instead four high speed burst execution we cleared the flash controller lockup flag buy writing one into the error status register after setting adequate dummy cycles and adjusting clock divider settings the esp thirty two s two module executed four thousand flash cache reads across sixteen hours without bus freezes or memory faults",
        "refined_text": "Our ESP32-S2 module suffered flash controller lockups when switching serial peripheral interface flash clocks towards 80 megahertz. We connected a digital logic analyzer to the chip select pin and inspected flash timing registers over OpenOCD. The cache controller halted because read latency dummy cycles were insufficient during high-speed quad read operations while the storage driver lacked timing configuration, inspecting the flash timing thresholds inside spi_flash manager instead.\n\nConfigure the serial peripheral interface read latency by programming 8 dummy cycles instead into the timing configuration register. Write 0x08 into the flash timing register. Write 0x0c instead into the cache control register for high-speed burst execution. We cleared the flash controller lockup flag by writing 1 into the error status register.\n\nAfter setting adequate dummy cycles and adjusting clock divider settings, the ESP32-S2 module executed 4000 flash cache reads across 16 hours without bus freezes or memory faults."
    },

    # Sample 12: STM32F7 DCMI digital camera interface DMA FIFO overrun
    {
        "raw_asr": "uh our stm thirty two f seven vision board dropped video frame pixels during continuous camera image captures across direct memory access streams we connected an oscilloscope two the pixel clock pin and inspected fifo buffer status over open o c d the direct memory access engine asserted a fifo transfer overrun error because peripheral request arbitration was too slow while the camera interface driver lacked buffer allocat wait inspect the fifo allocation inside dcmi underscore dma driver instead configur the direct memory access stream fifo threshold buy assigning two wait four beats instead into the stream control register right zero x zero zero four zero into the stream configuration register right zero x zero one into the camera control register wait right zero x zero three instead four continuous frame captures we cleared the fifo transfer overrun flag buy writing one into the interrupt clear register after increasing fifo burst capacity and setting continuous frame reception the stm thirty two f seven board captured six thousand image frames across eighteen hours without dropped pixels or buffer overruns",
        "refined_text": "Our STM32F7 vision board dropped video frame pixels during continuous camera image captures across direct memory access streams. We connected an oscilloscope to the pixel clock pin and inspected FIFO buffer status over OpenOCD. The direct memory access engine asserted a FIFO transfer overrun error because peripheral request arbitration was too slow while the camera interface driver lacked buffer allocation, inspecting the FIFO allocation inside dcmi_dma driver instead.\n\nConfigure the direct memory access stream FIFO threshold by assigning 4 beats instead into the stream control register. Write 0x0040 into the stream configuration register. Write 0x03 instead into the camera control register for continuous frame captures. We cleared the FIFO transfer overrun flag by writing 1 into the interrupt clear register.\n\nAfter increasing FIFO burst capacity and setting continuous frame reception, the STM32F7 board captured 6000 image frames across 18 hours without dropped pixels or buffer overruns."
    },

    # Sample 13: ST SPC58 Chorus automotive MCU eTimer input capture desync
    {
        "raw_asr": "um our spc fifty eight automotive controller miscalculated engine speed pulse intervals during sudden vehicle acceleration sweeps we connected a logic analyzer two the crankshaft sensor pin and monitored capture edge timestamps over open o c d the timer channel dropped input edges because electrical switching noise exceeded the digital filter duration while the pulse input driver lacked filter calibrat wait inspect the filter duration inside etimer underscore pulse driver instead calibrat the input capture digital filter buy programming eight wait sixteen filter clocks instead into the filter duration register right zero x zero zero four zero into the filter control register right zero x zero two into the capture control register wait right zero x zero six instead four dual edge event timestamping we cleared the capture overflow status flag buy writing one into the channel status register after programming longer filter clock windows and enabling dual edge capture the spc fifty eight controller processed eight thousand sensor pulses across twenty hours without edge misses or timing drift",
        "refined_text": "Our SPC58 automotive controller miscalculated engine speed pulse intervals during sudden vehicle acceleration sweeps. We connected a logic analyzer to the crankshaft sensor pin and monitored capture edge timestamps over OpenOCD. The timer channel dropped input edges because electrical switching noise exceeded the digital filter duration while the pulse input driver lacked filter calibration, inspecting the filter duration inside etimer_pulse driver instead.\n\nCalibrate the input capture digital filter by programming 16 filter clocks instead into the filter duration register. Write 0x0040 into the filter control register. Write 0x06 instead into the capture control register for dual edge event timestamping. We cleared the capture overflow status flag by writing 1 into the channel status register.\n\nAfter programming longer filter clock windows and enabling dual edge capture, the SPC58 controller processed 8000 sensor pulses across 20 hours without edge misses or timing drift."
    },

    # Sample 14: Infineon XMC4500 MultiCAN node arbitration stalling
    {
        "raw_asr": "basically our x m c forty five hundred motor inverter dropped off the industrial communication bus during burst messaging cycles we connected a bus analyzer two the high speed differential transceivers and analyzed error frames over open o c d the controller node entered a bus off state because propagation segment bit timing delays caused phase sampling errors while the bus driver lacked timing configur wait inspect the bit timing allocation inside can underscore bus driver instead configur the bit timing logic prescaler buy setting twelve wait twenty four clock cycles instead into the baud rate register right zero x zero zero two four into the bit timing control register right zero x zero one into the node control register wait right zero x zero five instead four automatic bus recovery we cleared the bus off status flag buy writing one into the node status register after increasing propagation delay margins and enabling automatic bus recovery the x m c forty five hundred controller exchanged nine thousand message frames across twenty two hours without arbitration faults or bus off events",
        "refined_text": "Our XMC4500 motor inverter dropped off the industrial communication bus during burst messaging cycles. We connected a bus analyzer to the high-speed differential transceivers and analyzed error frames over OpenOCD. The controller node entered a bus-off state because propagation segment bit timing delays caused phase sampling errors while the bus driver lacked timing configuration, inspecting the bit timing allocation inside can_bus driver instead.\n\nConfigure the bit timing logic prescaler by setting 24 clock cycles instead into the baud rate register. Write 0x0024 into the bit timing control register. Write 0x05 instead into the node control register for automatic bus recovery. We cleared the bus-off status flag by writing 1 into the node status register.\n\nAfter increasing propagation delay margins and enabling automatic bus recovery, the XMC4500 controller exchanged 9000 message frames across 22 hours without arbitration faults or bus-off events."
    },

    # Sample 15: NXP LPC54628 SCTimer/PWM multi-phase commutation drift
    {
        "raw_asr": "uh our l p c fifty four six twenty eight motor drive experienced phase drift during high speed brushless motor commutation we connected an oscilloscope two the complementary gate driver lines and monitored state transition flags using open o c d the timer state machine skipped commutation events because match registers reloaded without synchronization while the motor control driver lacked state synchronizat wait inspect the reload synchronization inside sctimer underscore motor driver instead configur the state timer match reload buy assigning sixteen wait thirty two clock cycles instead into the match reload register right zero x zero zero six zero into the event control register right zero x zero two into the state control register wait right zero x zero six instead four synchronized state transitions we cleared the match event missed flag buy writing one into the event flag register after enabling synchronized match register updates and tuning event reload windows the l p c fifty four six twenty eight motor drive executed seven thousand commutation cycles across eighteen hours without phase drift or gate drive shoot through",
        "refined_text": "Our LPC54628 motor drive experienced phase drift during high-speed brushless motor commutation. We connected an oscilloscope to the complementary gate driver lines and monitored state transition flags using OpenOCD. The timer state machine skipped commutation events because match registers reloaded without synchronization while the motor control driver lacked state synchronization, inspecting the reload synchronization inside sctimer_motor driver instead.\n\nConfigure the state timer match reload by assigning 32 clock cycles instead into the match reload register. Write 0x0060 into the event control register. Write 0x06 instead into the state control register for synchronized state transitions. We cleared the match event missed flag by writing 1 into the event flag register.\n\nAfter enabling synchronized match register updates and tuning event reload windows, the LPC54628 motor drive executed 7000 commutation cycles across 18 hours without phase drift or gate drive shoot-through."
    },

    # Sample 16: Microchip AVR ATmega4809 Event System desynchronization
    {
        "raw_asr": "um our a t mega forty eight zero nine sensor logger dropped periodic analog conversions when entering power down sleep mode we connected an oscilloscope two the event output pin and checked generator channel status using a hardware debugger the analog converter missed periodic triggers because the real time counter event channel stalled during sleep transitions while the power management driver lacked event configur wait inspect the event multiplexer inside evsys underscore sleep driver instead configur the event system generator channel buy selecting four wait eight event generator pulses instead into the multiplexer register right zero x zero five into the channel routing register right zero x zero one into the event control register wait right zero x zero three instead four asynchronous event propagation we cleared the missed conversion flag buy writing one into the interrupt flag register after routing asynchronous event paths and updating multiplexer registers the a t mega forty eight zero nine sensor logger completed five thousand measurement cycles across twenty four hours without trigger dropouts or sleep wakeup stalls",
        "refined_text": "Our ATmega4809 sensor logger dropped periodic analog conversions when entering power-down sleep mode. We connected an oscilloscope to the event output pin and checked generator channel status using a hardware debugger. The analog converter missed periodic triggers because the real-time counter event channel stalled during sleep transitions while the power management driver lacked event configuration, inspecting the event multiplexer inside evsys_sleep driver instead.\n\nConfigure the event system generator channel by selecting 8 event generator pulses instead into the multiplexer register. Write 0x05 into the channel routing register. Write 0x03 instead into the event control register for asynchronous event propagation. We cleared the missed conversion flag by writing 1 into the interrupt flag register.\n\nAfter routing asynchronous event paths and updating multiplexer registers, the ATmega4809 sensor logger completed 5000 measurement cycles across 24 hours without trigger dropouts or sleep wakeup stalls."
    },

    # Sample 17: GigaDevice GD32VF103 RISC-V ECLIC interrupt latency jitter
    {
        "raw_asr": "basically our g d thirty two v f one zero three board experienced interrupt latency jitter during rapid sensor polling routines we connected a logic analyzer two the gpio trigger pins and measured interrupt service timing using open o c d the processor core delayed critical interrupt routines because unmasked peripheral interrupts preempted low latency handlers while the interrupt subsystem lacked priority configur wait inspect the vector priority inside eclic underscore interrupt driver instead configur the core interrupt controller threshold buy programming forty wait eighty priority levels instead into the threshold register right zero x zero zero eight zero into the interrupt threshold register right zero x zero two into the control register wait right zero x zero six instead four preemptive priority grouping we cleared the interrupt latency jitter flag buy writing one into the pending status register after adjusting threshold levels and assigning high priority groupings the g d thirty two v f one zero three board processed seven thousand sensor interrupts across sixteen hours without latency jitter or handler preemption delays",
        "refined_text": "Our GD32VF103 board experienced interrupt latency jitter during rapid sensor polling routines. We connected a logic analyzer to the GPIO trigger pins and measured interrupt service timing using OpenOCD. The processor core delayed critical interrupt routines because unmasked peripheral interrupts preempted low-latency handlers while the interrupt subsystem lacked priority configuration, inspecting the vector priority inside eclic_interrupt driver instead.\n\nConfigure the core interrupt controller threshold by programming 80 priority levels instead into the threshold register. Write 0x0080 into the interrupt threshold register. Write 0x06 instead into the control register for preemptive priority grouping. We cleared the interrupt latency jitter flag by writing 1 into the pending status register.\n\nAfter adjusting threshold levels and assigning high-priority groupings, the GD32VF103 board processed 7000 sensor interrupts across 16 hours without latency jitter or handler preemption delays."
    },

    # Sample 18: Analog Devices ADuCM4050 flash controller page erase timeout
    {
        "raw_asr": "uh our a d u c m forty fifty node aborted in application firmware updates during high temperature flash memory operations we connected a power monitor two the supply rail and monitored memory status words over open o c d the embedded flash controller asserted a write timeout error because charge pump stabilization delays were insufficient while the memory management driver lacked erase timing calibrat wait inspect the erase timing parameters inside flash underscore update driver instead calibrat the flash memory charge pump wait time buy setting sixteen wait thirty two clock cycles instead into the erase timing register right zero x zero zero two zero into the timing parameter register right zero x zero one into the flash control register wait right zero x zero five instead four extended erase pulse duration we cleared the flash controller write timeout flag buy writing one into the status clear register after updating charge pump delay parameters and lengthening erase pulses the a d u c m forty fifty node erased twelve memory pages across fourteen hours without aborts or verification errors",
        "refined_text": "Our ADuCM4050 node aborted in-application firmware updates during high-temperature flash memory operations. We connected a power monitor to the supply rail and monitored memory status words over OpenOCD. The embedded flash controller asserted a write timeout error because charge pump stabilization delays were insufficient while the memory management driver lacked erase timing calibration, inspecting the erase timing parameters inside flash_update driver instead.\n\nCalibrate the flash memory charge pump wait time by setting 32 clock cycles instead into the erase timing register. Write 0x0020 into the timing parameter register. Write 0x05 instead into the flash control register for extended erase pulse duration. We cleared the flash controller write timeout flag by writing 1 into the status clear register.\n\nAfter updating charge pump delay parameters and lengthening erase pulses, the ADuCM4050 node erased 12 memory pages across 14 hours without aborts or verification errors."
    },

    # Sample 19: ST STM32F407 FSMC SRAM bus timing setup violations
    {
        "raw_asr": "um our stm thirty two f four zero seven controller suffered memory corruption during high speed graphical frame buffer rendering across external static random access memory we connected a logic analyzer two the address bus and monitored chip select timing using open o c d the external memory bus generated garbled pixels because data phase setup times violated memory access thresholds while the memory interface driver lacked bus timing configur wait inspect the bus timing parameters inside fsmc underscore sram driver instead configur the static memory controller address setup time buy assigning one wait two clock cycles instead into the bus timing register right zero x zero zero zero two into the static memory timing register right zero x zero one into the bank control register wait right zero x zero four instead four extended access cycles we cleared the memory bus error flag buy writing one into the bus status register after lengthening data phase cycles and setting extended bus access the stm thirty two f four zero seven controller rendered four thousand graphics frames across twenty hours without memory corruption or timing violations",
        "refined_text": "Our STM32F407 controller suffered memory corruption during high-speed graphical frame buffer rendering across external static random access memory. We connected a logic analyzer to the address bus and monitored chip select timing using OpenOCD. The external memory bus generated garbled pixels because data phase setup times violated memory access thresholds while the memory interface driver lacked bus timing configuration, inspecting the bus timing parameters inside fsmc_sram driver instead.\n\nConfigure the static memory controller address setup time by assigning 2 clock cycles instead into the bus timing register. Write 0x0002 into the static memory timing register. Write 0x04 instead into the bank control register for extended access cycles. We cleared the memory bus error flag by writing 1 into the bus status register.\n\nAfter lengthening data phase cycles and setting extended bus access, the STM32F407 controller rendered 4000 graphics frames across 20 hours without memory corruption or timing violations."
    },

    # Sample 20: Texas Instruments MSP432P401R RTC_C alarm register lockup
    {
        "raw_asr": "basically our m s p four thirty two p four zero one r environmental logger failed two wake from deep sleep mode during periodic sensor sampling schedules we connected a precision current meter two the power pins and analyzed register locks over open o c d the real time clock alarm failed two assert an interrupt because key protected registers locked before write operations completed while the power management driver lacked unlock synchronizat wait inspect the key lock register inside rtc underscore wake driver instead synchronizat the real time clock configuration key buy writing zero x zero two wait right zero x zero five instead into the key register right zero x zero zero zero eight into the alarm enable register right zero x zero one into the clock control register wait right zero x zero three instead four periodic alarm wakeups we cleared the alarm lockup status flag buy writing one into the interrupt clear register after unlocking the key register and enabling alarm interrupts the m s p four thirty two p four zero one r logger completed nine thousand sleep wake cycles across twenty four hours without missed alarms or clock desynchronization",
        "refined_text": "Our MSP432P401R environmental logger failed to wake from deep sleep mode during periodic sensor sampling schedules. We connected a precision current meter to the power pins and analyzed register locks over OpenOCD. The real-time clock alarm failed to assert an interrupt because key-protected registers locked before write operations completed while the power management driver lacked unlock synchronization, inspecting the key lock register inside rtc_wake driver instead.\n\nSynchronize the real-time clock configuration key by writing 0x05 instead into the key register. Write 0x0008 into the alarm enable register. Write 0x03 instead into the clock control register for periodic alarm wakeups. We cleared the alarm lockup status flag by writing 1 into the interrupt clear register.\n\nAfter unlocking the key register and enabling alarm interrupts, the MSP432P401R logger completed 9000 sleep wake cycles across 24 hours without missed alarms or clock desynchronization."
    },
]

print(f"Loaded {len(batch_129)} candidate samples for Batch 129...")

# Run validation loop
tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(batch_129):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Noise layers check
    layers = count_active_noise_layers(raw)
    n_count = sum(layers.values())
    layer_counts.append(n_count)

    # Validator check
    val_ok, val_reason = validate_pair(pair, min_noise_layers=4)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx+1} clean status: {clean_reason}"

    # Tier invariants
    words = len(ref.split())
    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
        assert n_count >= 3, f"Sample {idx+1} has {n_count} noise layers, expected >= 3 for Short!"
    elif words < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3!"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
        assert n_count >= 4, f"Sample {idx+1} has {n_count} noise layers, expected >= 4 for Medium!"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"
        assert n_count >= 4, f"Sample {idx+1} has {n_count} noise layers, expected >= 4 for Long!"

    print(f"Sample {idx+1:02d}: {words:3d} words, {n_count} noise layers {layers} - PASS")

print(f"\nTier counts: {tiers}")
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Average noise layers: {avg_layers:.2f}")
assert avg_layers >= 4.0, f"Average noise layers {avg_layers:.2f} < 4.0!"

# Batch distribution check
batch_ok, batch_msg, batch_tiers = validate_batch(batch_129, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
assert batch_ok, f"Batch validation failed: {batch_msg}"
print(f"Batch validation: {batch_msg}")
print(f"Batch metrics: {batch_tiers}")

output_file = Path("scratch/subagent_batch_129.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(batch_129, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully saved 20 verified samples to {output_file}")
print("ALL 20 SAMPLES PASSED DETERMINISTICALLY WITH 0 ERRORS!")
