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

# Define the 20 candidate pairs for Batch 124 (Domain 6: Embedded Systems & Firmware Development)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_124 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Sample 1: Silicon Labs EFR32 LDMA arbitration priority
    {
        "raw_asr": "configur the linked direct memory access arbitration register buy writing eight priority cycles into the peripheral channel descriptor",
        "refined_text": "Configure the linked direct memory access arbitration register by writing 8 priority cycles into the peripheral channel descriptor."
    },
    # Sample 2: STM32H7 FMC SDRAM refresh timer
    {
        "raw_asr": "uh initializ the flexible memory controller refresh timer register buy writing zero x zero four into the timing configuration register",
        "refined_text": "Initialize the flexible memory controller refresh timer register by writing 0x04 into the timing configuration register."
    },
    # Sample 3: Microchip SAM E70 AFEC conversion clock prescaler
    {
        "raw_asr": "calibrat the analog front end conversion clock prescaler buy loading sixteen clock ticks into the channel control register",
        "refined_text": "Calibrate the analog front end conversion clock prescaler by loading 16 clock ticks into the channel control register."
    },
    # Sample 4: NXP S32K344 eMIOS counter bus disable
    {
        "raw_asr": "terminat the modular input output counter bus transfer buy clearing channel bit four inside the global enable register",
        "refined_text": "Terminate the modular input output counter bus transfer by clearing channel bit 4 inside the global enable register."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # Sample 5: TI CC2652R RF Core Mailbox command ring
    {
        "raw_asr": "um configur the radio frequency core command mailbox ring buy allocating sixty four wait write one two eight bytes instead into the mailbox memory descriptor four high speed packet streaming the rf coprocessor exchanges packet descriptors buy servicing eight mailbox interrupt lines",
        "refined_text": "Configure the radio frequency core command mailbox ring by writing 128 bytes instead into the mailbox memory descriptor for high-speed packet streaming.\n\nThe RF coprocessor exchanges packet descriptors by servicing 8 mailbox interrupt lines."
    },
    # Sample 6: Silicon Labs EFR32 PRS event routing
    {
        "raw_asr": "uh synchronizat the peripheral reflex system event routing buy loading zero x zero two wait load zero x zero six instead into the channel routing register four hardware timer triggering the autonomous peripheral network routes sensor triggers buy driving sixteen event channels",
        "refined_text": "Synchronize the peripheral reflex system event routing by loading 0x06 instead into the channel routing register for hardware timer triggering.\n\nThe autonomous peripheral network routes sensor triggers by driving 16 event channels."
    },
    # Sample 7: Raspberry Pi RP2350 Hazard3 RISC-V timer prescaler
    {
        "raw_asr": "calibrat the r i s c v timer alarm divider register buy loading twenty clock cycles wait forty clock cycles instead into the fractional prescaler register four low jitter task scheduling the timer core dispatches periodic tick interrupts buy asserting four hardware interrupt vectors",
        "refined_text": "Calibrate the RISC-V timer alarm divider register by loading 40 clock cycles instead into the fractional prescaler register for low-jitter task scheduling.\n\nThe timer core dispatches periodic tick interrupts by asserting 4 hardware interrupt vectors."
    },
    # Sample 8: NXP i.MX RT1060 FlexSPI read latency cycles
    {
        "raw_asr": "allocat the flexible serial peripheral interface read latency cycles buy assigning ten dummy cycles wait twenty dummy cycles instead into the lookup table register four high speed flash execution the external memory controller fetches instruction blocks buy reading thirty two cache lines",
        "refined_text": "Allocate the flexible serial peripheral interface read latency cycles by assigning 20 dummy cycles instead into the lookup table register for high-speed flash execution.\n\nThe external memory controller fetches instruction blocks by reading 32 cache lines."
    },
    # Sample 9: Renesas RX72N TPU dead-time generator
    {
        "raw_asr": "terminat the timer pulse unit complementary channel output buy writing zero x zero zero wait right zero x zero c instead into the dead time control register four phase bridge protection the motor timer module disables gate drive pulses buy pulling down six complementary output pins",
        "refined_text": "Terminate the timer pulse unit complementary channel output by writing 0x0c instead into the dead time control register for phase bridge protection.\n\nThe motor timer module disables gate drive pulses by pulling down 6 complementary output pins."
    },
    # Sample 10: Nordic nRF52840 Zephyr RTOS low power comparator
    {
        "raw_asr": "uh operat the low power comparator wake event buy setting thirty millivolts wait sixty millivolts instead into the reference ladder register four battery threshold monitoring the zephyr power management subsystem handles wake events buy servicing sixteen peripheral interrupts",
        "refined_text": "Operate the low-power comparator wake event by setting 60 millivolts instead into the reference ladder register for battery threshold monitoring.\n\nThe Zephyr power management subsystem handles wake events by servicing 16 peripheral interrupts."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Sample 11: NXP RT1060 eDMA scatter-gather channel transfer stall
    {
        "raw_asr": "um our n x p r t ten sixty audio board experienced direct memory access transfer stalls during continuous thirty two bit synchronous audio streaming we attached a segger j link debugger two the swd port and measured clock signals on the audio bit clock pin the direct memory access engine halted because scatter gather transfer descriptors loaded unaligned memory addresses without setting the minor loop completion flag while the audio driver lacked descriptor configur wait inspect the descriptor chain inside edma underscore audio driver module instead configur the enhanced direct memory access scatter gather descriptor buy setting the minor loop size two sixteen transfers wait thirty two transfers instead right zero x two zero zero zero eight zero zero zero into the next descriptor address register right zero x zero two into the channel control register wait right zero x zero six instead four continuous scatter gather chaining we cleared the transfer stall flag buy writing one into the error status register after aligning memory buffers in non cacheable memory and updating descriptor loop thresholds the audio board streamed four thousand audio frames across twenty four hours without bus stalls or fifo underflows",
        "refined_text": "Our NXP RT1060 audio board experienced direct memory access transfer stalls during continuous 32-bit synchronous audio streaming. We attached a SEGGER J-Link debugger to the SWD port and measured clock signals on the audio bit clock pin. The direct memory access engine halted because scatter-gather transfer descriptors loaded unaligned memory addresses without setting the minor loop completion flag while the audio driver lacked descriptor configuration, inspecting the descriptor chain inside edma_audio_driver module instead.\n\nConfigure the enhanced direct memory access scatter-gather descriptor by setting the minor loop size to 32 transfers instead. Write 0x20008000 into the next descriptor address register. Write 0x06 instead into the channel control register for continuous scatter-gather chaining. We cleared the transfer stall flag by writing 1 into the error status register.\n\nAfter aligning memory buffers in non-cacheable memory and updating descriptor loop thresholds, the audio board streamed 4000 audio frames across 24 hours without bus stalls or FIFO underflows."
    },
    # Sample 12: TI CC1352P Sub-1GHz RF core packet CRC mismatch
    {
        "raw_asr": "uh our t i c c thirteen fifty two p radio node suffered cyclic redundancy check failures during sub one gigahertz sensor transmissions we connected an rf spectrum analyzer two the antenna port and inspected demodulator status flags using a cmsis dap debug probe the radio core discarded incoming packets because crystal frequency offset exceeded the intermediate frequency bandwidth while the modem driver lacked receiver frequency calibrat wait inspect the intermediate frequency calibration inside rf underscore frontend manager instead calibrat the radio frequency receiver intermediate frequency buy shifting the demodulator center frequency ten wait twenty kilohertz instead right zero x zero zero four zero into the synthesizer trim register right zero x zero one into the receiver control register wait right zero x zero five instead four wideband frequency tracking we cleared the demodulator error status buy writing one into the interrupt clear register after trimming the synthesizer frequency and expanding receiver bandwidth settings the radio node received five thousand sensor packets across eighteen hours without packet drops or validation errors",
        "refined_text": "Our TI CC1352P radio node suffered cyclic redundancy check failures during sub-1-gigahertz sensor transmissions. We connected an RF spectrum analyzer to the antenna port and inspected demodulator status flags using a CMSIS-DAP debug probe. The radio core discarded incoming packets because crystal frequency offset exceeded the intermediate frequency bandwidth while the modem driver lacked receiver frequency calibration, inspecting the intermediate frequency calibration inside rf_frontend manager instead.\n\nCalibrate the radio frequency receiver intermediate frequency by shifting the demodulator center frequency 20 kilohertz instead. Write 0x0040 into the synthesizer trim register. Write 0x05 instead into the receiver control register for wideband frequency tracking. We cleared the demodulator error status by writing 1 into the interrupt clear register.\n\nAfter trimming the synthesizer frequency and expanding receiver bandwidth settings, the radio node received 5000 sensor packets across 18 hours without packet drops or validation errors."
    },
    # Sample 13: Silicon Labs EFR32MG24 RAIL EM2 wakeup latency
    {
        "raw_asr": "um our silicon labs e f r thirty two wireless sensor dropped incoming packet preambles when waking from deep sleep energy mode two we connected a logic analyzer two the external gpio pins and measured crystal oscillator startup timing across power transitions the radio receiver missed sync words because high frequency crystal startup delays exceeded the preamble detection window while the power management driver lacked oscillator synchronizat wait inspect the startup timer thresholds inside rail underscore sleep manager instead configur the high frequency crystal oscillator startup delay buy programming thirty two wait sixty four clock cycles instead into the oscillator steady state register right zero x two zero zero zero into the power management control register right zero x zero two into the radio wakeup mask register wait right zero x zero a instead four fast energy mode transitions we cleared the wakeup latency flag buy writing one into the power interrupt clear register after tuning crystal startup delays and enabling fast radio wakeup the wireless sensor received six thousand sleep cycle packets across sixteen hours without preamble misses or timing dropouts",
        "refined_text": "Our Silicon Labs EFR32 wireless sensor dropped incoming packet preambles when waking from deep sleep energy mode 2. We connected a logic analyzer to the external GPIO pins and measured crystal oscillator startup timing across power transitions. The radio receiver missed sync words because high-frequency crystal startup delays exceeded the preamble detection window while the power management driver lacked oscillator synchronization, inspecting the startup timer thresholds inside rail_sleep manager instead.\n\nConfigure the high-frequency crystal oscillator startup delay by programming 64 clock cycles instead into the oscillator steady state register. Write 0x2000 into the power management control register. Write 0x0a instead into the radio wakeup mask register for fast energy mode transitions. We cleared the wakeup latency flag by writing 1 into the power interrupt clear register.\n\nAfter tuning crystal startup delays and enabling fast radio wakeup, the wireless sensor received 6000 sleep cycle packets across 16 hours without preamble misses or timing dropouts."
    },
    # Sample 14: Microchip SAM E70 GMAC Ethernet DMA ring descriptor exhaustion
    {
        "raw_asr": "uh our microchip s a m e seventy network gateway dropped ethernet frames during burst tcp streaming across the industrial bus we captured network traffic using wi re shark and inspected ethernet receive buffer descriptors over open o c d the network controller asserted a receive buffer exhaustion error because direct memory access descriptor rings filled faster than the network stack processed incoming packets while the ethernet driver lacked buffer allocat wait inspect the ring descriptor allocation inside gmac underscore eth driver instead configur the ethernet direct memory access receive descriptor ring buy assigning thirty two wait sixty four buffers instead into the queue limit descriptor right zero x three zero zero zero four zero zero zero into the receive buffer base address register right zero x zero one into the network control register wait right zero x zero seven instead four burst direct memory access transfers we cleared the buffer exhaustion status buy writing one into the network status register after increasing receive descriptor ring capacity and enabling frame burst reception the network gateway processed seven thousand ethernet frames across twenty four hours without dropped packets or buffer overruns",
        "refined_text": "Our Microchip SAM E70 network gateway dropped Ethernet frames during burst TCP streaming across the industrial bus. We captured network traffic using Wireshark and inspected Ethernet receive buffer descriptors over OpenOCD. The network controller asserted a receive buffer exhaustion error because direct memory access descriptor rings filled faster than the network stack processed incoming packets while the Ethernet driver lacked buffer allocation, inspecting the ring descriptor allocation inside gmac_eth driver instead.\n\nConfigure the Ethernet direct memory access receive descriptor ring by assigning 64 buffers instead into the queue limit descriptor. Write 0x30004000 into the receive buffer base address register. Write 0x07 instead into the network control register for burst direct memory access transfers. We cleared the buffer exhaustion status by writing 1 into the network status register.\n\nAfter increasing receive descriptor ring capacity and enabling frame burst reception, the network gateway processed 7000 Ethernet frames across 24 hours without dropped packets or buffer overruns."
    },
    # Sample 15: TI TMS320F28379D Delfino ePWM trip zone latching
    {
        "raw_asr": "um our t i t m s three twenty f twenty eight thirty seven nine d motor drive experienced false trip zone shutdowns during high current motor acceleration we connected a digital oscilloscope two the complementary gate driver pins and monitored comparator trip flags across the pulse width modulator the trip zone subsystem latched an overcurrent fault trip because fast switching transients triggered analog comparators before current signals stabilized while the pwm controller lacked blanking window calibrat wait inspect the filter window thresholds inside epwm underscore trip manager instead configur the pulse width modulator digital filter blanking window buy setting ten wait twenty clock cycles instead into the blanking offset register right zero x zero zero eight zero into the trip filter control register right zero x zero two into the trip zone select register wait right zero x zero six instead four advanced cycle by cycle current limiting we cleared the trip latch flag buy writing one into the trip clear register after programming the comparator blanking window and updating trip filter thresholds the motor inverter executed eight thousand motor acceleration cycles across eighteen hours without false trip shutdowns or current shoot through faults",
        "refined_text": "Our TI TMS320F28379D motor drive experienced false trip zone shutdowns during high-current motor acceleration. We connected a digital oscilloscope to the complementary gate driver pins and monitored comparator trip flags across the pulse width modulator. The trip zone subsystem latched an overcurrent fault trip because fast switching transients triggered analog comparators before current signals stabilized while the PWM controller lacked blanking window calibration, inspecting the filter window thresholds inside epwm_trip manager instead.\n\nConfigure the pulse width modulator digital filter blanking window by setting 20 clock cycles instead into the blanking offset register. Write 0x0080 into the trip filter control register. Write 0x06 instead into the trip zone select register for advanced cycle-by-cycle current limiting. We cleared the trip latch flag by writing 1 into the trip clear register.\n\nAfter programming the comparator blanking window and updating trip filter thresholds, the motor inverter executed 8000 motor acceleration cycles across 18 hours without false trip shutdowns or current shoot-through faults."
    },
    # Sample 16: NXP S32K344 FlexCAN-FD message buffer arbitration lock
    {
        "raw_asr": "uh our n x p s thirty two k three forty four automotive controller experienced frame transmission starvation during high bus load can fd communications we connected a can bus protocol analyzer two the differential can lines and traced message buffer status registers over jtag the flexcan controller delayed high priority diagnostic frames because transmit message buffers used round robin arbitration rather than local priority ordering while the bus driver lacked priority configur wait inspect the arbitration rules inside flexcan underscore buffer manager instead configur the flexible controller area network message buffer priorities buy reserving sixteen wait thirty two message buffers instead into the mailbox control table right zero x four zero zero a zero zero zero zero into the buffer base address register right zero x zero one into the arbitration control register wait right zero x zero nine instead four local priority arbitration we cleared the transmission timeout flag buy writing one into the buffer interrupt status register after enabling local priority arbitration and expanding message buffer assignments the controller transmitted nine thousand can fd frames across twenty four hours without frame starvation or bus latency violations",
        "refined_text": "Our NXP S32K344 automotive controller experienced frame transmission starvation during high bus load CAN-FD communications. We connected a CAN bus protocol analyzer to the differential CAN lines and traced message buffer status registers over JTAG. The FlexCAN controller delayed high-priority diagnostic frames because transmit message buffers used round-robin arbitration rather than local priority ordering while the bus driver lacked priority configuration, inspecting the arbitration rules inside flexcan_buffer manager instead.\n\nConfigure the flexible controller area network message buffer priorities by reserving 32 message buffers instead into the mailbox control table. Write 0x400a0000 into the buffer base address register. Write 0x09 instead into the arbitration control register for local priority arbitration. We cleared the transmission timeout flag by writing 1 into the buffer interrupt status register.\n\nAfter enabling local priority arbitration and expanding message buffer assignments, the controller transmitted 9000 CAN-FD frames across 24 hours without frame starvation or bus latency violations."
    },
    # Sample 17: ST STM32L476 DFSDM audio microphone overrun
    {
        "raw_asr": "um our stm thirty two l four seventy six voice logger dropped microphone audio samples during continuous digital sigma delta recording we attached a logic analyzer two the external pulse density modulation clock and data pins and verified channel conversion flags the digital filter asserted a data overrun flag because decimation filter outputs generated audio samples faster than the direct memory access channel serviced transfer requests while the audio acquisition driver lacked decimation filter calibrat wait inspect the filter settings inside dfsdm underscore audio filter module instead calibrat the digital filter for sigma delta modulators decimation rate buy setting thirty two wait sixty four decimation ratio instead into the channel control register right zero x two zero zero zero one zero zero zero into the direct memory access address register right zero x zero two into the filter configuration register wait right zero x zero e instead four fast sinc filter processing we cleared the overrun status flag buy writing one into the filter interrupt flag clear register after adjusting the sinc filter decimation ratio and reconfiguring direct memory access burst sizes the voice logger recorded four thousand audio files across twelve hours without sample overruns or data corruption",
        "refined_text": "Our STM32L476 voice logger dropped microphone audio samples during continuous digital sigma-delta recording. We attached a logic analyzer to the external pulse density modulation clock and data pins and verified channel conversion flags. The digital filter asserted a data overrun flag because decimation filter outputs generated audio samples faster than the direct memory access channel serviced transfer requests while the audio acquisition driver lacked decimation filter calibration, inspecting the filter settings inside dfsdm_audio_filter module instead.\n\nCalibrate the digital filter for sigma delta modulators decimation rate by setting 64 decimation ratio instead into the channel control register. Write 0x20001000 into the direct memory access address register. Write 0x0e instead into the filter configuration register for fast sinc filter processing. We cleared the overrun status flag by writing 1 into the filter interrupt flag clear register.\n\nAfter adjusting the sinc filter decimation ratio and reconfiguring direct memory access burst sizes, the voice logger recorded 4000 audio files across 12 hours without sample overruns or data corruption."
    },
    # Sample 18: Infineon AURIX TC397 GTM angle clock pulse missing
    {
        "raw_asr": "uh our infineon aurix t c three ninety seven engine controller dropped crankshaft angle pulses during rapid engine speed transitions we connected an oscilloscope two the variable reluctance sensor inputs and examined input capture timestamps over a segger j link debugger the generic timer module missed tooth edges because digital glitch filter thresholds filtered valid sensor pulses during high frequency engine revolutions while the capture driver lacked dynamic filter synchronizat wait inspect the noise filter timing inside gtm underscore angle tracker instead configur the generic timer module angle clock filter buy loading ten wait twenty clock ticks instead into the input filter duration register right zero x zero zero six zero into the filter parameter register right zero x zero one into the angle capture mode register wait right zero x zero b instead four bidirectional edge detection we cleared the pulse loss flag buy writing one into the angle clock status register after optimizing input filter thresholds and updating tooth capture parameters the engine controller processed seven thousand crankshaft revolutions across sixteen hours without missing pulses or angle calculation errors",
        "refined_text": "Our Infineon AURIX TC397 engine controller dropped crankshaft angle pulses during rapid engine speed transitions. We connected an oscilloscope to the variable reluctance sensor inputs and examined input capture timestamps over a SEGGER J-Link debugger. The generic timer module missed tooth edges because digital glitch filter thresholds filtered valid sensor pulses during high-frequency engine revolutions while the capture driver lacked dynamic filter synchronization, inspecting the noise filter timing inside gtm_angle_tracker instead.\n\nConfigure the generic timer module angle clock filter by loading 20 clock ticks instead into the input filter duration register. Write 0x0060 into the filter parameter register. Write 0x0b instead into the angle capture mode register for bidirectional edge detection. We cleared the pulse loss flag by writing 1 into the angle clock status register.\n\nAfter optimizing input filter thresholds and updating tooth capture parameters, the engine controller processed 7000 crankshaft revolutions across 16 hours without missing pulses or angle calculation errors."
    },
    # Sample 19: ESP32-S3 TWAI bus error active transitions
    {
        "raw_asr": "um our esp thirty two s three robotics gateway entered error passive state during high speed can bus monitoring we connected a logic analyzer two the transceiver differential pins and evaluated bit error flags inside the peripheral telemetry register the two wire automotive interface controller accumulated bit stuffing errors because the configured bit sampling point drifted relative two external node clocks while the communication controller lacked sample point configur wait inspect the timing parameters inside twai underscore can controller instead configur the two wire automotive interface bit timing register buy selecting fifty wait eighty percent sample point instead into the timing configuration descriptor right zero x zero zero two f into the bus timing register right zero x zero four into the filter mode register wait right zero x zero d instead four extended identifier frame acceptance we cleared the bus error warning flag buy writing one into the interrupt clear register after adjusting the bit sampling point and updating bit rate prescaler settings the robotics gateway monitored eight thousand can frames across twenty four hours without error passive transitions or stuff error alerts",
        "refined_text": "Our ESP32-S3 robotics gateway entered error passive state during high-speed CAN bus monitoring. We connected a logic analyzer to the transceiver differential pins and evaluated bit error flags inside the peripheral telemetry register. The two-wire automotive interface controller accumulated bit stuffing errors because the configured bit sampling point drifted relative to external node clocks while the communication controller lacked sample point configuration, inspecting the timing parameters inside twai_can_controller instead.\n\nConfigure the two-wire automotive interface bit timing register by selecting 80 percent sample point instead into the timing configuration descriptor. Write 0x002f into the bus timing register. Write 0x0d instead into the filter mode register for extended identifier frame acceptance. We cleared the bus error warning flag by writing 1 into the interrupt clear register.\n\nAfter adjusting the bit sampling point and updating bit rate prescaler settings, the robotics gateway monitored 8000 CAN frames across 24 hours without error passive transitions or stuff error alerts."
    },
    # Sample 20: Microchip PIC32MZ EF SQI XIP flash cache stall
    {
        "raw_asr": "uh our microchip p i c thirty two m z graphics board suffered display frame stuttering during high resolution graphical rendering we connected a hardware logic analyzer two the serial quad interface clock and data lines and analyzed cache misses over the debug interface the central processing unit stalled because flash burst read requests delayed reloading cache lines during random vector lookups while the memory driver lacked burst mode initializ wait inspect the flash burst mode configuration inside sqi underscore flash driver instead configur the serial quad interface burst transfer size buy setting sixteen wait thirty two byte burst reads instead into the transfer control register right zero x five zero zero zero zero zero zero zero into the flash memory mapped base register right zero x zero one into the quad mode control register wait right zero x zero f instead four high speed continuous read execution we cleared the bus wait state flag buy writing one into the status clear register after programming continuous quad read mode and optimizing cache prefetch burst lengths the graphics board rendered six thousand display frames across eighteen hours without rendering stalls or visual glitches",
        "refined_text": "Our Microchip PIC32MZ graphics board suffered display frame stuttering during high-resolution graphical rendering. We connected a hardware logic analyzer to the serial quad interface clock and data lines and analyzed cache misses over the debug interface. The central processing unit stalled because flash burst read requests delayed reloading cache lines during random vector lookups while the memory driver lacked burst mode initialization, inspecting the flash burst mode configuration inside sqi_flash_driver instead.\n\nConfigure the serial quad interface burst transfer size by setting 32-byte burst reads instead into the transfer control register. Write 0x50000000 into the flash memory-mapped base register. Write 0x0f instead into the quad mode control register for high-speed continuous read execution. We cleared the bus wait state flag by writing 1 into the status clear register.\n\nAfter programming continuous quad read mode and optimizing cache prefetch burst lengths, the graphics board rendered 6000 display frames across 18 hours without rendering stalls or visual glitches."
    }
]

print(f"Total samples defined: {len(batch_124)}")
assert len(batch_124) == 20, f"Expected 20 samples, got {len(batch_124)}"

tiers = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(batch_124):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator check
    val_ok, val_reason = validator.validate_pair(pair)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = cleaner.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx+1} clean status: {clean_reason}"

    # Tier invariants
    words = len(ref.split())
    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
    elif words < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3!"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"

print(f"Tier counts: {tiers}")
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

# Batch distribution check
batch_ok, batch_msg, batch_tiers = validator.validate_batch(batch_124, min_short=4, min_medium=6, min_long=10)
assert batch_ok, f"Batch validation failed: {batch_msg}"

output_file = Path("scratch/subagent_batch_124.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(batch_124, f, indent=2, ensure_ascii=False)

print(f"Successfully saved 20 verified samples to {output_file}")
print("ALL 20 SAMPLES PASSED DETERMINISTICALLY WITH 0 ERRORS!")
