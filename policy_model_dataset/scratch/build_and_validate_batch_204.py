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

# Define candidate samples for Batch 204 (Domain 6: Firmware, Embedded Registers, Hardware HAL)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_204 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Refined content words >= 6-8. Ratio [0.35, 1.25].
    # =========================================================================

    # Sample 1: STM32G474 High Resolution Timer (HRTIM) fault blanking window
    {
        "raw_asr": "um configur the fault input blanking window buy writing zero x zero four wait zero x zero eight instead into the c p u control register",
        "refined_text": "Configure the fault input blanking window by writing 0x08 instead into the CPU control register."
    },

    # Sample 2: NXP LPC55S69 High Speed SPI (HS_SPI) FIFO trigger threshold
    {
        "raw_asr": "uh calibrat the serial fifo trigger threshold buy loading zero x zero two wait zero x zero six instead into the s p i configuration register",
        "refined_text": "Calibrate the serial FIFO trigger threshold by loading 0x06 instead into the SPI configuration register."
    },

    # Sample 3: TI TMS320F28379D enhanced capture (eCAP) prescaler divider
    {
        "raw_asr": "basically initializ the capture prescaler divider buy loading zero x zero one wait zero x zero four instead into the n v i c vector register",
        "refined_text": "Initialize the capture prescaler divider by loading 0x04 instead into the NVIC vector register."
    },

    # Sample 4: Microchip SAME70 AFEC analog trigger sample hold
    {
        "raw_asr": "so um terminat the analog trigger sample hold buy writing zero x zero a wait zero x zero f instead into the d m a channel register",
        "refined_text": "Terminate the analog trigger sample hold by writing 0x0f instead into the DMA channel register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Nordic nRF52840: PPI programmable peripheral interconnect channel configuration
    {
        "raw_asr": "um configur the peripheral interconnect event channel buy routing eight wait sixteen compare events instead into the task endpoint you know the c p u offloads timer capture sequences buy writing zero x zero two into the peripheral status register four synchronized sensor polling",
        "refined_text": "Configure the peripheral interconnect event channel by routing 16 compare events instead into the task endpoint.\n\nThe CPU offloads timer capture sequences by writing 0x02 into the peripheral status register for synchronized sensor polling."
    },

    # Sample 6: Espressif ESP32-S3: General DMA (GDMA) burst mode for LCD RGB interface
    {
        "raw_asr": "uh allocat the direct memory access burst buffer buy reserving thirty two wait sixty four bytes instead into the shared memory segment you know the free are toss kernel synchronizes frame refreshes buy writing zero x zero four into the s p i control register four coordinated display updates",
        "refined_text": "Allocate the direct memory access burst buffer by reserving 64 bytes instead into the shared memory segment.\n\nThe FreeRTOS kernel synchronizes frame refreshes by writing 0x04 into the SPI control register for coordinated display updates."
    },

    # Sample 7: Raspberry Pi RP2040: Programmable I/O (PIO) state machine clock divider
    {
        "raw_asr": "basically calibrat the programmable input output clock divider buy loading twelve wait twenty four divider steps instead into the clock register the r i s c v core accelerates serial frame decoding buy writing zero x zero eight into the latency control register four synchronized bus reads",
        "refined_text": "Calibrate the programmable input output clock divider by loading 24 divider steps instead into the clock register.\n\nThe RISC-V core accelerates serial frame decoding by writing 0x08 into the latency control register for synchronized bus reads."
    },

    # Sample 8: Infineon PSoC 6: Serial Communication Block (SCB) I2C master glitch filter
    {
        "raw_asr": "um initializ the serial communication bus glitch filter buy loading zero x zero three wait zero x zero six instead into the filter register the c p u monitors bus arbitration status buy polling sixteen n v i c interrupt flags four queued telemetry frames",
        "refined_text": "Initialize the serial communication bus glitch filter by loading 0x06 instead into the filter register.\n\nThe CPU monitors bus arbitration status by polling 16 NVIC interrupt flags for queued telemetry frames."
    },

    # Sample 9: Microchip AVR128DA: Event System (EVSYS) asynchronous routing channel
    {
        "raw_asr": "uh terminat the event routing sequence buy writing zero x zero six wait zero x zero c instead into the channel mask register you know the free are toss tick rate resumes buy writing zero x zero one into the r i s c v control register",
        "refined_text": "Terminate the event routing sequence by writing 0x0c instead into the channel mask register.\n\nThe FreeRTOS tick rate resumes by writing 0x01 into the RISC-V control register."
    },

    # Sample 10: Renesas RX65N: Data Transfer Controller (DTC) vector activation sequence
    {
        "raw_asr": "so um calibrat the vector activation sequence buy writing zero x zero c wait zero x one eight instead into the transfer count register the u art bus reports diagnostic status buy streaming four d m a status frames",
        "refined_text": "Calibrate the vector activation sequence by writing 0x18 instead into the transfer count register.\n\nThe UART bus reports diagnostic status by streaming 4 DMA status frames."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4. Natural engineer narration.
    # =========================================================================

    # Sample 11: ST STM32H743 FMC SDRAM controller refresh timing calibration
    {
        "raw_asr": "um our industrial motor drive experienced external memory controller stalls and timing desynchronization during thermal cycling over open o c d we tapped memory bus signals using an oscilloscope and tracked bus arbitration stalls across fourteen thermal cycles the memory controller halted transactions because dynamic memory refresh periods drifted under elevated temperatures while the memory driver lacked timing calibrat wait inspect the timing parameters inside fmc underscore sdram underscore timing module instead calibrat the dynamic refresh period buy loading sixteen wait thirty two refresh cycles instead into the timing register right zero x c zero zero zero zero zero zero zero into the fmc base register right zero x zero one into the control register wait right zero x zero b instead four stable memory refresh operations we cleared the memory bus fault flag buy writing one into the status clear register after calibrating refresh cycles and coordinating free are toss tasks on the c p u core the motor drive executed eight zero zero zero memory transactions across twenty four hours without bus stalls or timing faults",
        "refined_text": "Our industrial motor drive experienced external memory controller stalls and timing desynchronization during thermal cycling. Over OpenOCD we tapped memory bus signals using an oscilloscope and tracked bus arbitration stalls across 14 thermal cycles. The memory controller halted transactions because dynamic memory refresh periods drifted under elevated temperatures while the memory driver lacked timing calibration, inspecting the timing parameters inside fmc_sdram_timing module instead.\n\nCalibrate the dynamic refresh period by loading 32 refresh cycles instead into the timing register. Write 0xc0000000 into the FMC base register. Write 0x0b instead into the control register for stable memory refresh operations. We cleared the memory bus fault flag by writing 1 into the status clear register.\n\nAfter calibrating refresh cycles and coordinating FreeRTOS tasks on the CPU core, the motor drive executed 8000 memory transactions across 24 hours without bus stalls or timing faults."
    },

    # Sample 12: NXP i.MX RT1062 eDMA scatter-gather descriptor ring exhaustion
    {
        "raw_asr": "uh our smart audio soundbar suffered direct memory access descriptor underruns and audio buffer crackling during high definition audio streaming over open o c d we tapped inter ic sound signals using a logic analyzer and tracked transfer buffer underruns across twelve streaming sessions the direct memory access controller halted audio feeds because scatter gather descriptor links exhausted channel memory buffers while the audio driver lacked descriptor configur wait inspect the descriptor configuration tables inside edma underscore stream underscore config module instead configur the scatter gather transfer capacity buy loading twelve wait twenty four transfer descriptors instead into the channel queue right zero x four zero zero one eight zero zero zero into the edma base register right zero x zero two into the chain control register wait right zero x zero e instead four continuous audio streaming we cleared the transfer error flag buy writing one into the status clear register after adjusting descriptor queue depth and scheduling d m a stream handlers on the c p u bus the audio soundbar processed nine zero zero zero audio streaming buffers across twenty eight hours without direct memory access underruns or buffer corruption",
        "refined_text": "Our smart audio soundbar suffered direct memory access descriptor underruns and audio buffer crackling during high-definition audio streaming. Over OpenOCD we tapped inter-IC sound signals using a logic analyzer and tracked transfer buffer underruns across 12 streaming sessions. The direct memory access controller halted audio feeds because scatter-gather descriptor links exhausted channel memory buffers while the audio driver lacked descriptor configuration, inspecting the descriptor configuration tables inside edma_stream_config module instead.\n\nConfigure the scatter-gather transfer capacity by loading 24 transfer descriptors instead into the channel queue. Write 0x40018000 into the EDMA base register. Write 0x0e instead into the chain control register for continuous audio streaming. We cleared the transfer error flag by writing 1 into the status clear register.\n\nAfter adjusting descriptor queue depth and scheduling DMA stream handlers on the CPU bus, the audio soundbar processed 9000 audio streaming buffers across 28 hours without direct memory access underruns or buffer corruption."
    },

    # Sample 13: TI TMS320F28379D ePWM trip-zone cycle comparator protection
    {
        "raw_asr": "basically our digital power converter suffered pulse width modulator shutdown cycles and overcurrent protection trip stalls during synchronous inverter switching over open o c d we tapped complementary gate drive signals using an oscilloscope and tracked trip zone fault events across sixteen switching sweeps the pulse width modulator aborted gate pulses because trip zone cycle by cycle comparator flags locked out high side outputs while the firmware lacked comparator initializ wait inspect the trip zone comparator thresholds inside epwm underscore tripzone underscore ctrl module instead initializ the trip zone cycle comparator registers buy loading eight wait sixteen filtering steps instead into the qualification register right zero x zero zero zero zero four zero zero zero into the epwm base register right zero x zero one into the clear control register wait right zero x zero d instead four deterministic fault recovery transitions we cleared the cycle trip fault flag buy writing one into the status clear register after programming comparator qualification steps and coordinating n v i c interrupt handlers on the c p u core the power converter regulated seven zero zero zero switching cycles across thirty hours without gate trip lockouts or overcurrent stalls",
        "refined_text": "Our digital power converter suffered pulse-width modulator shutdown cycles and overcurrent protection trip stalls during synchronous inverter switching. Over OpenOCD we tapped complementary gate drive signals using an oscilloscope and tracked trip-zone fault events across 16 switching sweeps. The pulse-width modulator aborted gate pulses because trip-zone cycle-by-cycle comparator flags locked out high-side outputs while the firmware lacked comparator initialization, inspecting the trip-zone comparator thresholds inside epwm_tripzone_ctrl module instead.\n\nInitialize the trip-zone cycle comparator registers by loading 16 filtering steps instead into the qualification register. Write 0x00004000 into the EPWM base register. Write 0x0d instead into the clear control register for deterministic fault recovery transitions. We cleared the cycle trip fault flag by writing 1 into the status clear register.\n\nAfter programming comparator qualification steps and coordinating NVIC interrupt handlers on the CPU core, the power converter regulated 7000 switching cycles across 30 hours without gate trip lockouts or overcurrent stalls."
    },

    # Sample 14: Nordic nRF9160 DPPI non-secure channel event allocation
    {
        "raw_asr": "so um our cellular iot gateway experienced event routing stalls and publish subscribe channel lockups during low power wake cycles over open o c d we tapped hardware event trigger lines and tracked peripheral interconnect exceptions across fourteen sleep cycles the distributed programmable peripheral interconnect controller halted event propagation because non secure channel subscription masks conflicted with secure domain partitions while the low power firmware lacked channel allocat wait inspect the subscription channel mappings inside dppi underscore channel underscore routing module instead allocat the peripheral interconnect channel memory buy reserving eight wait sixteen channel subscriptions instead into the routing table right zero x five zero zero one four zero zero zero into the dppi base register right zero x zero one into the publish control register wait right zero x zero a instead four deterministic event distribution we cleared the channel subscription error flag buy writing one into the status clear register after adjusting channel subscription tables and scheduling free are toss tasks on the c p u core the cellular gateway routed six zero zero zero telemetry packets across twenty six hours without event routing stalls or channel lockups",
        "refined_text": "Our cellular IoT gateway experienced event routing stalls and publish-subscribe channel lockups during low-power wake cycles. Over OpenOCD we tapped hardware event trigger lines and tracked peripheral interconnect exceptions across 14 sleep cycles. The distributed programmable peripheral interconnect controller halted event propagation because non-secure channel subscription masks conflicted with secure domain partitions while the low-power firmware lacked channel allocation, inspecting the subscription channel mappings inside dppi_channel_routing module instead.\n\nAllocate the peripheral interconnect channel memory by reserving 16 channel subscriptions instead into the routing table. Write 0x50014000 into the DPPI base register. Write 0x0a instead into the publish control register for deterministic event distribution. We cleared the channel subscription error flag by writing 1 into the status clear register.\n\nAfter adjusting channel subscription tables and scheduling FreeRTOS tasks on the CPU core, the cellular gateway routed 6000 telemetry packets across 26 hours without event routing stalls or channel lockups."
    },

    # Sample 15: Microchip PIC32MZ DA GLCD raster DMA line underrun
    {
        "raw_asr": "uh our industrial human machine panel experienced screen tearing artifacts and graphics buffer underruns during dynamic display page swaps over open o c d we tapped parallel rgb interface signals using an oscilloscope and tracked line timing errors across twelve display refresh cycles the graphics controller halted raster output because line buffer direct memory access transfers failed to keep pace with pixel clock bursts while the display driver lacked timing calibrat wait inspect the horizontal front porch parameters inside glcd underscore raster underscore dma module instead calibrat the horizontal blanking interval buy loading sixteen wait thirty two pixel clock cycles instead into the timing register right zero x b zero zero zero zero zero zero zero into the glcd base register right zero x zero one into the raster control register wait right zero x zero f instead four smooth frame transitions we cleared the raster underrun flag buy writing one into the status clear register after calibrating horizontal blanking cycles and scheduling d m a transfer descriptors on the c p u bus the operator panel rendered five zero zero zero display frames across twenty four hours without screen tearing or graphics underruns",
        "refined_text": "Our industrial human-machine panel experienced screen tearing artifacts and graphics buffer underruns during dynamic display page swaps. Over OpenOCD we tapped parallel RGB interface signals using an oscilloscope and tracked line timing errors across 12 display refresh cycles. The graphics controller halted raster output because line buffer direct memory access transfers failed to keep pace with pixel clock bursts while the display driver lacked timing calibration, inspecting the horizontal front-porch parameters inside glcd_raster_dma module instead.\n\nCalibrate the horizontal blanking interval by loading 32 pixel clock cycles instead into the timing register. Write 0xb0000000 into the GLCD base register. Write 0x0f instead into the raster control register for smooth frame transitions. We cleared the raster underrun flag by writing 1 into the status clear register.\n\nAfter calibrating horizontal blanking cycles and scheduling DMA transfer descriptors on the CPU bus, the operator panel rendered 5000 display frames across 24 hours without screen tearing or graphics underruns."
    },

    # Sample 16: Renesas RA4M2 SCI SPI clock phase and polarity desynchronization
    {
        "raw_asr": "basically our smart metering controller experienced serial communication framing errors and memory write aborts during external nor flash updates over open o c d we probed serial peripheral interface bus lines using a logic analyzer and tracked chip select timing errors across sixteen flash write cycles the serial communication peripheral aborted sector writes because clock phase polarity parameters desynchronized from flash latch requirements while the communication driver lacked timing configur wait inspect the serial bus timing settings inside sci underscore spi underscore transfer module instead configur the serial clock timing parameters buy loading eight wait sixteen clock delay cycles instead into the control register right zero x four zero zero one eight zero zero zero into the sci base register right zero x zero one into the transfer control register wait right zero x zero c instead four reliable flash sector programming we cleared the framing error flag buy writing one into the status clear register after adjusting clock phase delays and scheduling background tasks on the r i s c v core the metering controller programmed eight zero zero zero flash sectors across thirty hours without framing errors or write aborts",
        "refined_text": "Our smart metering controller experienced serial communication framing errors and memory write aborts during external NOR flash updates. Over OpenOCD we probed serial peripheral interface bus lines using a logic analyzer and tracked chip-select timing errors across 16 flash write cycles. The serial communication peripheral aborted sector writes because clock phase polarity parameters desynchronized from flash latch requirements while the communication driver lacked timing configuration, inspecting the serial bus timing settings inside sci_spi_transfer module instead.\n\nConfigure the serial clock timing parameters by loading 16 clock delay cycles instead into the control register. Write 0x40018000 into the SCI base register. Write 0x0c instead into the transfer control register for reliable flash sector programming. We cleared the framing error flag by writing 1 into the status clear register.\n\nAfter adjusting clock phase delays and scheduling background tasks on the RISC-V core, the metering controller programmed 8000 flash sectors across 30 hours without framing errors or write aborts."
    },

    # Sample 17: Espressif ESP32-P4 Cryptographic Coprocessor AES-XTS alignment
    {
        "raw_asr": "um our high performance secure hub experienced cryptographic pipeline stalls and memory fault exceptions during block cipher transfers over open o c d we tapped memory bus signals and tracked cryptographic coprocessor error codes across fourteen encryption runs the hardware engine rejected encryption bursts because direct memory access word alignment failed across sixty four byte cipher block boundaries while the encryption firmware lacked buffer allocat wait inspect the memory alignment parameters inside crypto underscore aes underscore engine module instead allocat the cipher block memory buffers buy reserving sixteen wait thirty two word aligned blocks instead into the descriptor table right zero x five zero zero zero two zero zero zero into the crypto base register right zero x zero one into the pipeline control register wait right zero x zero b instead four continuous block cipher processing we cleared the hardware fault error flag buy writing one into the status clear register after adjusting descriptor word alignment and coordinating free are toss tasks on the r i s c v core the secure hub processed nine zero zero zero encrypted blocks across twenty eight hours without cryptographic stalls or memory alignment faults",
        "refined_text": "Our high-performance secure hub experienced cryptographic pipeline stalls and memory fault exceptions during block cipher transfers. Over OpenOCD we tapped memory bus signals and tracked cryptographic coprocessor error codes across 14 encryption runs. The hardware engine rejected encryption bursts because direct memory access word alignment failed across 64-byte cipher block boundaries while the encryption firmware lacked buffer allocation, inspecting the memory alignment parameters inside crypto_aes_engine module instead.\n\nAllocate the cipher block memory buffers by reserving 32 word-aligned blocks instead into the descriptor table. Write 0x50002000 into the crypto base register. Write 0x0b instead into the pipeline control register for continuous block cipher processing. We cleared the hardware fault error flag by writing 1 into the status clear register.\n\nAfter adjusting descriptor word alignment and coordinating FreeRTOS tasks on the RISC-V core, the secure hub processed 9000 encrypted blocks across 28 hours without cryptographic stalls or memory alignment faults."
    },

    # Sample 18: Infineon AURIX TC387 EVADC queue priority arbiter
    {
        "raw_asr": "uh our automotive engine management unit experienced analog conversion delays and trigger arbitration stalls during multi channel sensor sampling over open o c d we tapped analog trigger lines using an oscilloscope and tracked queue arbitration faults across sixteen engine firing cycles the analog converter halted conversions because lower priority queue requests starved time critical knock sensor triggers while the adc firmware lacked queue calibrat wait inspect the queue arbitration priority inside evadc underscore queue underscore arbiter module instead calibrat the queue arbiter slot priorities buy loading eight wait sixteen conversion slots instead into the priority register right zero x f zero zero zero zero zero zero zero into the evadc base register right zero x zero one into the arbiter control register wait right zero x zero e instead four predictable channel arbitration we cleared the conversion timeout flag buy writing one into the status clear register after adjusting queue priority slots and coordinating n v i c interrupt handlers on the c p u interface the engine controller acquired seven zero zero zero analog samples across thirty hours without trigger stalls or conversion delays",
        "refined_text": "Our automotive engine management unit experienced analog conversion delays and trigger arbitration stalls during multi-channel sensor sampling. Over OpenOCD we tapped analog trigger lines using an oscilloscope and tracked queue arbitration faults across 16 engine firing cycles. The analog converter halted conversions because lower-priority queue requests starved time-critical knock sensor triggers while the ADC firmware lacked queue calibration, inspecting the queue arbitration priority inside evadc_queue_arbiter module instead.\n\nCalibrate the queue arbiter slot priorities by loading 16 conversion slots instead into the priority register. Write 0xf0000000 into the EVADC base register. Write 0x0e instead into the arbiter control register for predictable channel arbitration. We cleared the conversion timeout flag by writing 1 into the status clear register.\n\nAfter adjusting queue priority slots and coordinating NVIC interrupt handlers on the CPU interface, the engine controller acquired 7000 analog samples across 30 hours without trigger stalls or conversion delays."
    },

    # Sample 19: Silicon Labs EFR32MG24 LDMA ping-pong descriptor synchronization
    {
        "raw_asr": "basically our wireless asset beacon experienced radio packet transmission drops and descriptor chain stalls during continuous bluetooth broadcasting over open o c d we captured radio frequency transmit lines using a logic analyzer and tracked descriptor linking errors across twelve advertising bursts the linked direct memory access controller halted packet payloads because ping pong buffer descriptors wrapped around without acknowledging transfer completions while the radio driver lacked descriptor configur wait inspect the descriptor link parameters inside ldma underscore channel underscore descriptor module instead configur the linked descriptor chain depth buy loading twelve wait twenty four buffer descriptors instead into the channel table right zero x five zero zero two zero zero zero zero into the ldma base register right zero x zero one into the descriptor control register wait right zero x zero d instead four uninterrupted packet transmission we cleared the descriptor fault flag buy writing one into the status clear register after adjusting descriptor chain depth and scheduling free are toss radio tasks on the c p u core the asset beacon transmitted six zero zero zero beacon packets across twenty six hours without packet drops or descriptor stalls",
        "refined_text": "Our wireless asset beacon experienced radio packet transmission drops and descriptor chain stalls during continuous Bluetooth broadcasting. Over OpenOCD we captured radio frequency transmit lines using a logic analyzer and tracked descriptor linking errors across 12 advertising bursts. The linked direct memory access controller halted packet payloads because ping-pong buffer descriptors wrapped around without acknowledging transfer completions while the radio driver lacked descriptor configuration, inspecting the descriptor link parameters inside ldma_channel_descriptor module instead.\n\nConfigure the linked descriptor chain depth by loading 24 buffer descriptors instead into the channel table. Write 0x50020000 into the LDMA base register. Write 0x0d instead into the descriptor control register for uninterrupted packet transmission. We cleared the descriptor fault flag by writing 1 into the status clear register.\n\nAfter adjusting descriptor chain depth and scheduling FreeRTOS radio tasks on the CPU core, the asset beacon transmitted 6000 beacon packets across 26 hours without packet drops or descriptor stalls."
    },

    # Sample 20: Raspberry Pi RP2350 UART FIFO hardware flow control RTS/CTS
    {
        "raw_asr": "so um our telemetry data logger experienced serial buffer overruns and hardware flow control stalls during high speed sensor streaming over open o c d we probed request to send and clear to send lines using an oscilloscope and tracked handshake glitches across fourteen communication sessions the serial controller dropped telemetry bytes because hardware flow control fifo watermarks deasserted clear to send signals prematurely while the serial driver lacked watermark initializ wait inspect the hardware flow control thresholds inside uart underscore flow underscore control module instead initializ the serial flow control threshold buy loading eight wait sixteen bytes instead into the fifo watermark register right zero x four zero zero five zero zero zero zero into the uart base register right zero x zero one into the handshake control register wait right zero x zero f instead four uninterrupted serial data streaming we cleared the buffer overrun flag buy writing one into the status clear register after programming fifo watermarks and managing serial buffers on the r i s c v core the telemetry logger streamed eight zero zero zero telemetry packets across twenty eight hours without buffer overruns or handshake stalls",
        "refined_text": "Our telemetry data logger experienced serial buffer overruns and hardware flow control stalls during high-speed sensor streaming. Over OpenOCD we probed request-to-send and clear-to-send lines using an oscilloscope and tracked handshake glitches across 14 communication sessions. The serial controller dropped telemetry bytes because hardware flow control FIFO watermarks deasserted clear-to-send signals prematurely while the serial driver lacked watermark initialization, inspecting the hardware flow control thresholds inside uart_flow_control module instead.\n\nInitialize the serial flow control threshold by loading 16 bytes instead into the FIFO watermark register. Write 0x40050000 into the UART base register. Write 0x0f instead into the handshake control register for uninterrupted serial data streaming. We cleared the buffer overrun flag by writing 1 into the status clear register.\n\nAfter programming FIFO watermarks and managing serial buffers on the RISC-V core, the telemetry logger streamed 8000 telemetry packets across 28 hours without buffer overruns or handshake stalls."
    },
]

print(f"Total candidate samples: {len(batch_204)}")
assert len(batch_204) == 20, f"Expected 20 samples, got {len(batch_204)}"

tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []
all_valid = True

for idx, s in enumerate(batch_204, 1):
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

    # Validator check with min_noise_layers=4 (or 3 for short)
    words = len(ref.split())
    min_l = 3 if words < 25 else 4
    val_ok, val_reason = validator.validate_pair(s, min_noise_layers=min_l)
    if not val_ok:
        print(f"Sample {idx} failed validate_pair: {val_reason}")
        all_valid = False

    # Cleaner check
    clean_obj, clean_reason = cleaner.clean_sample(raw, ref)
    if clean_obj is None or clean_reason != "kept":
        print(f"Sample {idx} failed clean_sample: {clean_reason}")
        all_valid = False

    nl = validator.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tier_counts["short"] += 1
        if "\n" in ref:
            print(f"Sample {idx} has newline in short tier!")
            all_valid = False
        if nl < 3:
            print(f"Sample {idx} short tier active layers < 3 ({nl})")
            all_valid = False
        cut_words_found = validator.CUT_WORD_REGEX.findall(raw)
        if len(cut_words_found) > 1:
            print(f"Sample {idx} has >1 cut word: {cut_words_found}")
            all_valid = False
        sentences = [sen for sen in re.split(r'[.!?]+', ref.strip()) if sen.strip()]
        if len(sentences) != 1:
            print(f"Sample {idx} short tier has {len(sentences)} sentences: {sentences}")
            all_valid = False
    elif words < 90:
        tier_counts["medium"] += 1
        if "\n\n" not in ref:
            print(f"Sample {idx} missing paragraph break in medium tier!")
            all_valid = False
        if nl < 4:
            print(f"Sample {idx} medium tier active layers < 4 ({nl})")
            all_valid = False
        sentences = [sen for sen in re.split(r'[.!?]+', ref.strip()) if sen.strip()]
        if not (1 <= len(sentences) <= 3):
            print(f"Sample {idx} medium tier has {len(sentences)} sentences: {sentences}")
            all_valid = False
    else:
        tier_counts["long"] += 1
        if "\n\n" not in ref:
            print(f"Sample {idx} missing paragraph break in long tier!")
            all_valid = False
        if nl < 4:
            print(f"Sample {idx} long tier active layers < 4 ({nl})")
            all_valid = False
        if re.search(r'(^|\n)\s*[-*]\s+', ref):
            print(f"Sample {idx} has markdown bullets!")
            all_valid = False
        if re.search(r'(^|\n)\s*\d+\.\s+', ref):
            print(f"Sample {idx} has numbered list!")
            all_valid = False

# Batch validation
batch_ok, batch_reason, batch_stats = validator.validate_batch(
    batch_204,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
if not batch_ok:
    print(f"Batch validation failed: {batch_reason}")
    all_valid = False

avg_layers = sum(layer_counts) / len(layer_counts)
if avg_layers < 4.0:
    print(f"Average noise layers {avg_layers:.2f} < 4.0")
    all_valid = False

print(f"\nAll valid status: {all_valid}")
print(f"Tier counts: {tier_counts}")
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")

if all_valid:
    out_path = Path("scratch/subagent_batch_204.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch_204, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote verified batch to {out_path}")
else:
    print("\nErrors encountered! Did not write output.")
    sys.exit(1)
