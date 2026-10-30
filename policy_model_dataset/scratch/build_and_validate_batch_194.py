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

# Define candidate samples for Batch 194 (Domain 6: Firmware, Embedded Registers, Hardware HAL)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_194 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Refined content words >= 6-8. Ratio [0.35, 1.25].
    # =========================================================================

    # Sample 1: Microchip PIC32MZ EF: External Bus Interface (EBI) SRAM timing control register
    {
        "raw_asr": "um configur the external bus interface timing buy loading zero x zero four wait zero x zero eight instead into the c p u memory register",
        "refined_text": "Configure the external bus interface timing by loading 0x08 instead into the CPU memory register."
    },

    # Sample 2: Renesas RZ/T2M: Real-Time DMA engine transfer block size register
    {
        "raw_asr": "uh calibrat the direct memory access block size buy loading zero x one zero wait zero x two zero instead into the d m a channel register",
        "refined_text": "Calibrate the direct memory access block size by loading 0x20 instead into the DMA channel register."
    },

    # Sample 3: Infineon AURIX TC397: Hardware Security Module (HSM) mailbox interrupt register
    {
        "raw_asr": "basically initializ the hardware security mailbox interrupt line buy writing zero x zero one wait zero x zero five instead into the n v i c vector table",
        "refined_text": "Initialize the hardware security mailbox interrupt line by writing 0x05 instead into the NVIC vector table."
    },

    # Sample 4: ST STM32H753: Flexible Memory Controller (FMC) SDRAM refresh rate register
    {
        "raw_asr": "so um terminat the dynamic memory refresh burst buy writing zero x zero c wait zero x one e instead into the u art control register",
        "refined_text": "Terminate the dynamic memory refresh burst by writing 0x1e instead into the UART control register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: TI MSP430FR5994: Low Energy Accelerator (LEA) transform buffer
    {
        "raw_asr": "um configur the accelerator transform buffer buy loading sixteen wait thirty two d m a descriptors instead into the primary channel basically the c p u offloads complex vector calculations buy writing zero x zero four into the peripheral status register four accelerated sensor filtering",
        "refined_text": "Configure the accelerator transform buffer by loading 32 DMA descriptors instead into the primary channel.\n\nThe CPU offloads complex vector calculations by writing 0x04 into the peripheral status register for accelerated sensor filtering."
    },

    # Sample 6: Nordic nRF5340: Dual-core Inter-Processor Communication (IPC) channel signal register
    {
        "raw_asr": "uh allocat the inter processor signal buffer buy reserving sixty four wait one hundred twenty eight bytes instead into the shared memory segment you know the free are toss kernel synchronizes core events buy writing zero x zero two into the s p i control register four coordinated peripheral transfers",
        "refined_text": "Allocate the inter-processor signal buffer by reserving 128 bytes instead into the shared memory segment.\n\nThe FreeRTOS kernel synchronizes core events by writing 0x02 into the SPI control register for coordinated peripheral transfers."
    },

    # Sample 7: NXP i.MX RT1170: FlexSPI Octal NOR flash read sample clock delay calibration
    {
        "raw_asr": "basically calibrat the octal flash read sample delay buy loading eight wait sixteen clock steps instead into the tuning register the r i s c v core accelerates memory execution buy writing zero x zero c into the latency control register four synchronized bus reads",
        "refined_text": "Basically calibrate the octal flash read sample delay by loading 16 clock steps instead into the tuning register.\n\nThe RISC-V core accelerates memory execution by writing 0x0c into the latency control register for synchronized bus reads."
    },

    # Sample 8: Silicon Labs EFM32GG11: Low Energy UART (LEUART) baud rate pulse generator configuration
    {
        "raw_asr": "um initializ the low energy serial baud rate generator buy loading zero x zero four wait zero x zero eight instead into the compare register the c p u monitors communication status buy polling sixteen n v i c interrupt flags four queued telemetry frames",
        "refined_text": "Initialize the low-energy serial baud rate generator by loading 0x08 instead into the compare register.\n\nThe CPU monitors communication status by polling 16 NVIC interrupt flags for queued telemetry frames."
    },

    # Sample 9: Raspberry Pi RP2350: Hardware SHA-256 accelerator block size
    {
        "raw_asr": "uh terminat the hardware hash digest pipeline buy writing zero x zero a wait zero x zero f instead into the sequence register you know the free are toss tick rate resumes buy writing zero x zero one into the r i s c v control register",
        "refined_text": "Terminate the hardware hash digest pipeline by writing 0x0f instead into the sequence register.\n\nThe FreeRTOS tick rate resumes by writing 0x01 into the RISC-V control register."
    },

    # Sample 10: Analog Devices ADuCM4050: SensorStrobe SPI peripheral timing trigger initialization
    {
        "raw_asr": "so um calibrat the sensor strobe timing sequence buy writing zero x zero a wait zero x one four instead into the interval counter the u art bus reports diagnostic status buy streaming four d m a status frames",
        "refined_text": "Calibrate the sensor strobe timing sequence by writing 0x14 instead into the interval counter.\n\nThe UART bus reports diagnostic status by streaming 4 DMA status frames."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4. Natural engineer narration.
    # =========================================================================

    # Sample 11: Renesas RA6M5: Hardware cryptographic engine (SCE9) ECC curve point multiplication timeout during TLS 1.3 handshake
    {
        "raw_asr": "um our secure edge controller experienced cryptographic engine timeouts and curve calculation stalls during transport layer security handshakes over open o c d we tapped hardware bus signals using an oscilloscope and tracked point multiplication stalls across fourteen cryptographic handshakes the coprocessor halted processing because input scalar register lengths exceeded curve field parameters while the firmware lacked parameter calibrat wait inspect the curve coefficients inside ecc underscore point underscore mul module instead calibrat the scalar multiplier steps buy loading sixteen wait thirty two calculation steps instead into the precision register right zero x four zero zero nine zero zero zero zero into the crypto base register right zero x zero one into the command register wait right zero x zero b instead four uninterrupted point arithmetic we cleared the cryptographic timeout flag buy writing one into the status clear register after calibrating calculation steps and coordinating free are toss thread execution on the c p u core the edge controller completed nine thousand cryptographic handshakes across twenty four hours without coprocessor timeouts or point multiplication stalls",
        "refined_text": "Our secure edge controller experienced cryptographic engine timeouts and curve calculation stalls during transport layer security handshakes. Over OpenOCD we tapped hardware bus signals using an oscilloscope and tracked point multiplication stalls across 14 cryptographic handshakes. The coprocessor halted processing because input scalar register lengths exceeded curve field parameters while the firmware lacked parameter calibration, inspecting the curve coefficients inside ecc_point_mul module instead.\n\nCalibrate the scalar multiplier steps by loading 32 calculation steps instead into the precision register. Write 0x40090000 into the crypto base register. Write 0x0b instead into the command register for uninterrupted point arithmetic. We cleared the cryptographic timeout flag by writing 1 into the status clear register.\n\nAfter calibrating calculation steps and coordinating FreeRTOS thread execution on the CPU core, the edge controller completed 9000 cryptographic handshakes across 24 hours without coprocessor timeouts or point multiplication stalls."
    },

    # Sample 12: ST STM32U585: Low-power Autonomous Direct Memory Access (LPDMA) circular linked-list transfer overrun in Stop 2 mode
    {
        "raw_asr": "uh our battery powered environmental monitor suffered autonomous direct memory access overruns and data buffer corruption during low power stop modes over open o c d we tapped hardware trigger signals using a logic analyzer and tracked transfer overrun exceptions across twelve sleep wakeup cycles the direct memory access controller halted execution because linked list descriptor pointers wrapped around prematurely while the low power driver lacked descriptor configur wait inspect the descriptor address tables inside lpdma underscore channel underscore config module instead configur the circular linked list capacity buy loading twelve wait twenty four transfer descriptors instead into the channel queue right zero x four zero zero two zero zero zero zero into the lpdma base register right zero x zero two into the link control register wait right zero x zero e instead four autonomous linked list execution we cleared the transfer error flag buy writing one into the status clear register after adjusting descriptor queue depth and scheduling d m a stream handlers on the c p u bus the environmental monitor collected eleven thousand sensor telemetry frames across twenty eight hours without direct memory access overruns or descriptor faults",
        "refined_text": "Our battery-powered environmental monitor suffered autonomous direct memory access overruns and data buffer corruption during low-power stop modes. Over OpenOCD we tapped hardware trigger signals using a logic analyzer and tracked transfer overrun exceptions across 12 sleep wakeup cycles. The direct memory access controller halted execution because linked-list descriptor pointers wrapped around prematurely while the low-power driver lacked descriptor configuration, inspecting the descriptor address tables inside lpdma_channel_config module instead.\n\nConfigure the circular linked-list capacity by loading 24 transfer descriptors instead into the channel queue. Write 0x40020000 into the LPDMA base register. Write 0x0e instead into the link control register for autonomous linked-list execution. We cleared the transfer error flag by writing 1 into the status clear register.\n\nAfter adjusting descriptor queue depth and scheduling DMA stream handlers on the CPU bus, the environmental monitor collected 11000 sensor telemetry frames across 28 hours without direct memory access overruns or descriptor faults."
    },

    # Sample 13: TI AM2434 Sitara: Industrial Ethernet PRU-ICSS (Programmable Real-Time Unit) dual-port MAC frame jitter and latency
    {
        "raw_asr": "basically our industrial ethernet gateway suffered packet transmission jitter and media access control latency during real time fieldbus exchanges over open o c d we captured ethernet physical interface signals using a logic analyzer and tracked cycle latency anomalies across sixteen fieldbus communication cycles the programmable real time unit delayed packet delivery because shared memory queue descriptors stalled under bursty packet arrivals while the real time firmware lacked queue allocat wait inspect the shared memory descriptor thresholds inside pru underscore icss underscore mac module instead allocat the media access queue memory buy reserving sixteen wait thirty two frame descriptors instead into the shared memory partition right zero x three zero zero eight zero zero zero zero into the pru base register right zero x zero one into the queue control register wait right zero x zero d instead four bounded latency frame transmission we cleared the queue congestion flag buy writing one into the status clear register after adjusting frame descriptor buffers and managing free are toss tasks on the c p u core the ethernet gateway routed fourteen thousand real time fieldbus frames across thirty two hours without packet jitter or transmission latency anomalies",
        "refined_text": "Basically our industrial ethernet gateway suffered packet transmission jitter and media access control latency during real-time fieldbus exchanges. Over OpenOCD we captured ethernet physical interface signals using a logic analyzer and tracked cycle latency anomalies across 16 fieldbus communication cycles. The programmable real-time unit delayed packet delivery because shared memory queue descriptors stalled under bursty packet arrivals while the real-time firmware lacked queue allocation, inspecting the shared memory descriptor thresholds inside pru_icss_mac module instead.\n\nAllocate the media access queue memory by reserving 32 frame descriptors instead into the shared memory partition. Write 0x30080000 into the PRU base register. Write 0x0d instead into the queue control register for bounded latency frame transmission. We cleared the queue congestion flag by writing 1 into the status clear register.\n\nAfter adjusting frame descriptor buffers and managing FreeRTOS tasks on the CPU core, the ethernet gateway routed 14000 real-time fieldbus frames across 32 hours without packet jitter or transmission latency anomalies."
    },

    # Sample 14: Microchip SAM L11: TrustZone-M and Peripheral Access Controller (PAC) secure non-maskable peripheral bus isolation violation
    {
        "raw_asr": "so um our low power secure microcontroller experienced peripheral access violations and bus lockup exceptions during secure non callable calls over open o c d we tapped hardware error signals using a logic analyzer and tracked peripheral access unit faults across ten secure boot cycles the microcontroller halted bus transactions because peripheral access controller permission masks blocked non secure peripheral registers while the security firmware lacked permission initializ wait inspect the peripheral permission masks inside pac underscore security underscore isolation module instead initializ the peripheral access controller permission registers buy loading eight wait sixteen security masks instead into the domain table right zero x four zero zero zero zero zero zero zero into the pac base register right zero x zero two into the protection control register wait right zero x zero c instead four deterministic peripheral isolation we cleared the bus fault error flag buy writing one into the status clear register after programming peripheral permission masks and coordinating n v i c interrupt handlers on the c p u interface the microcontroller processed twelve thousand secure transactions across twenty six hours without peripheral access violations or bus lockup exceptions",
        "refined_text": "Our low-power secure microcontroller experienced peripheral access violations and bus lockup exceptions during secure non-callable calls. Over OpenOCD we tapped hardware error signals using a logic analyzer and tracked peripheral access unit faults across 10 secure boot cycles. The microcontroller halted bus transactions because peripheral access controller permission masks blocked non-secure peripheral registers while the security firmware lacked permission initialization, inspecting the peripheral permission masks inside pac_security_isolation module instead.\n\nInitialize the peripheral access controller permission registers by loading 16 security masks instead into the domain table. Write 0x40000000 into the PAC base register. Write 0x0c instead into the protection control register for deterministic peripheral isolation. We cleared the bus fault error flag by writing 1 into the status clear register.\n\nAfter programming peripheral permission masks and coordinating NVIC interrupt handlers on the CPU interface, the microcontroller processed 12000 secure transactions across 26 hours without peripheral access violations or bus lockup exceptions."
    },

    # Sample 15: Espressif ESP32-C6: RISC-V LP-I2C bus arbitration loss and clock stretching stall in deep sleep sensor polling
    {
        "raw_asr": "uh our low power wireless node experienced bus arbitration losses and clock stretching lockups during deep sleep sensor polling sessions over open o c d we probed inter integrated circuit clock and data lines using an oscilloscope and tracked bus stall conditions across fourteen sensor wake cycles the low power controller aborted data reads because bus pull up resistors caused rise time delays that exceeded hardware timeout thresholds while the sensor driver lacked timeout calibrat wait inspect the bus timing parameters inside lpi2c underscore bus underscore timing module instead calibrat the bus clock timeout threshold buy loading twelve wait twenty four clock cycles instead into the timeout register right zero x six zero zero zero four zero zero zero into the i two c base register right zero x zero one into the configuration register wait right zero x zero a instead four deterministic bus recovery we cleared the arbitration error flag buy writing one into the status clear register after calibrating clock stretching timeout cycles and scheduling r i s c v low power handlers the wireless node completed ten thousand sensor polling cycles across twenty four hours without bus arbitration losses or clock stretching lockups",
        "refined_text": "Our low-power wireless node experienced bus arbitration losses and clock stretching lockups during deep sleep sensor polling sessions. Over OpenOCD we probed inter-integrated circuit clock and data lines using an oscilloscope and tracked bus stall conditions across 14 sensor wake cycles. The low-power controller aborted data reads because bus pull-up resistors caused rise time delays that exceeded hardware timeout thresholds while the sensor driver lacked timeout calibration, inspecting the bus timing parameters inside lpi2c_bus_timing module instead.\n\nCalibrate the bus clock timeout threshold by loading 24 clock cycles instead into the timeout register. Write 0x60004000 into the I2C base register. Write 0x0a instead into the configuration register for deterministic bus recovery. We cleared the arbitration error flag by writing 1 into the status clear register.\n\nAfter calibrating clock stretching timeout cycles and scheduling RISC-V low-power handlers, the wireless node completed 10000 sensor polling cycles across 24 hours without bus arbitration losses or clock stretching lockups."
    },

    # Sample 16: Infineon TRAVEO T2G: Controller Area Network Flexible Data-Rate (CAN-FD) nominal bit-rate timing prescaler desynchronization
    {
        "raw_asr": "basically our automotive gateway electronic control unit experienced frame synchronization errors and bit rate error passive states during can flexible data rate traffic surges over open o c d we tapped differential bus lines using an oscilloscope and tracked transmission error frames across eighteen automotive drive cycles the can controller aborted message frames because nominal bit time prescaler settings drifted from the bus sample point while the communication stack lacked timing calibrat wait inspect the bit timing parameters inside canfd underscore bit underscore timing module instead calibrat the nominal time quantum prescaler buy loading ten wait twenty time quanta instead into the timing configuration register right zero x four zero zero c zero zero zero zero into the can base register right zero x zero two into the prescaler register wait right zero x zero f instead four accurate bit synchronization we cleared the error passive state flag buy writing one into the status clear register after adjusting time quantum prescalers and configuring free are toss message queues on the c p u core the gateway unit routed sixteen thousand can frames across thirty hours without frame errors or bit rate synchronization faults",
        "refined_text": "Basically our automotive gateway electronic control unit experienced frame synchronization errors and bit rate error passive states during CAN flexible data-rate traffic surges. Over OpenOCD we tapped differential bus lines using an oscilloscope and tracked transmission error frames across 18 automotive drive cycles. The CAN controller aborted message frames because nominal bit time prescaler settings drifted from the bus sample point while the communication stack lacked timing calibration, inspecting the bit timing parameters inside canfd_bit_timing module instead.\n\nCalibrate the nominal time quantum prescaler by loading 20 time quanta instead into the timing configuration register. Write 0x400c0000 into the CAN base register. Write 0x0f instead into the prescaler register for accurate bit synchronization. We cleared the error passive state flag by writing 1 into the status clear register.\n\nAfter adjusting time quantum prescalers and configuring FreeRTOS message queues on the CPU core, the gateway unit routed 16000 CAN frames across 30 hours without frame errors or bit rate synchronization faults."
    },

    # Sample 17: NXP S32K344: Hardware Security Engine (HSE) cryptographic key catalog slot provisioning alignment stall
    {
        "raw_asr": "um our secure automotive domain controller suffered security engine response timeouts and key import aborts during certificate provisioning over open o c d we tapped hardware bus lines and tracked cryptographic engine error codes across twelve firmware provisioning sequences the security engine rejected key import requests because direct memory access word alignment failed across key catalog slot boundaries while the provisioning driver lacked buffer allocat wait inspect the memory alignment parameters inside hse underscore key underscore catalog module instead allocat the secure key catalog buffer buy reserving eight wait sixteen word blocks instead into the descriptor table right zero x four zero zero eight zero zero zero zero into the hse base register right zero x zero one into the catalog control register wait right zero x zero c instead four reliable key import transactions we cleared the security engine error flag buy writing one into the status clear register after adjusting catalog word alignment and coordinating free are toss tasks on the c p u core the automotive controller imported eighteen thousand cryptographic keys across twenty eight hours without engine response timeouts or provisioning aborts",
        "refined_text": "Our secure automotive domain controller suffered security engine response timeouts and key import aborts during certificate provisioning. Over OpenOCD we tapped hardware bus lines and tracked cryptographic engine error codes across 12 firmware provisioning sequences. The security engine rejected key import requests because direct memory access word alignment failed across key catalog slot boundaries while the provisioning driver lacked buffer allocation, inspecting the memory alignment parameters inside hse_key_catalog module instead.\n\nAllocate the secure key catalog buffer by reserving 16 word blocks instead into the descriptor table. Write 0x40080000 into the HSE base register. Write 0x0c instead into the catalog control register for reliable key import transactions. We cleared the security engine error flag by writing 1 into the status clear register.\n\nAfter adjusting catalog word alignment and coordinating FreeRTOS tasks on the CPU core, the automotive controller imported 18000 cryptographic keys across 28 hours without engine response timeouts or provisioning aborts."
    },

    # Sample 18: Nordic nRF52833: Bluetooth 5.1 Direction Finding Radio Angle-of-Arrival (AoA) antenna switching pattern table corruption
    {
        "raw_asr": "uh our asset tracking locator experienced angle of arrival phase calculation errors and antenna switching glitch exceptions during bluetooth direction finding packets over open o c d we probed radio frequency antenna select lines using an oscilloscope and tracked pattern switching errors across fourteen direction finding bursts the radio peripheral corrupted phase samples because antenna pattern switching tables suffered direct memory access memory corruption while the radio driver lacked table initializ wait inspect the pattern switching tables inside radio underscore df underscore pattern module instead initializ the antenna switching pattern table buy loading eight wait sixteen antenna slots instead into the switching queue right zero x five zero zero zero one zero zero zero into the radio base register right zero x zero one into the pattern control register wait right zero x zero e instead four deterministic antenna switching we cleared the pattern error flag buy writing one into the status clear register after programming antenna switching tables and routing d m a radio buffers on the c p u interface the tracking locator evaluated twenty thousand direction finding bursts across thirty hours without phase calculation errors or antenna switching glitches",
        "refined_text": "Our asset tracking locator experienced angle of arrival phase calculation errors and antenna switching glitch exceptions during Bluetooth direction finding packets. Over OpenOCD we probed radio frequency antenna select lines using an oscilloscope and tracked pattern switching errors across 14 direction finding bursts. The radio peripheral corrupted phase samples because antenna pattern switching tables suffered direct memory access memory corruption while the radio driver lacked table initialization, inspecting the pattern switching tables inside radio_df_pattern module instead.\n\nInitialize the antenna switching pattern table by loading 16 antenna slots instead into the switching queue. Write 0x50001000 into the radio base register. Write 0x0e instead into the pattern control register for deterministic antenna switching. We cleared the pattern error flag by writing 1 into the status clear register.\n\nAfter programming antenna switching tables and routing DMA radio buffers on the CPU interface, the tracking locator evaluated 20000 direction finding bursts across 30 hours without phase calculation errors or antenna switching glitches."
    },

    # Sample 19: ST STM32F767: Quad-SPI Memory-Mapped caching and D-Cache coherency clean-and-invalidate boundary mismatch
    {
        "raw_asr": "basically our industrial human machine controller suffered graphic frame corruption and instruction cache inconsistencies during external flash rendering over open o c d we probed quad serial peripheral interface lines using an oscilloscope and tracked memory access errors across sixteen display refresh sweeps the display processor showed torn screen artifacts because data cache lines remained dirty during quad serial peripheral interface memory mapped transfers while the graphics firmware lacked cache calibrat wait inspect the cache line boundaries inside qspi underscore dcache underscore flush module instead calibrat the data cache clean and invalidate boundaries buy loading sixteen wait thirty two cache lines instead into the maintenance register right zero x e zero zero zero e zero zero zero into the scb base register right zero x zero one into the cache control register wait right zero x zero d instead four coherent memory transactions we cleared the cache maintenance flag buy writing one into the status clear register after calibrating cache line boundaries and scheduling free are toss graphics tasks on the c p u core the controller rendered twenty two thousand display frames across thirty six hours without frame corruption or cache inconsistencies",
        "refined_text": "Basically our industrial human-machine controller suffered graphic frame corruption and instruction cache inconsistencies during external flash rendering. Over OpenOCD we probed quad serial peripheral interface lines using an oscilloscope and tracked memory access errors across 16 display refresh sweeps. The display processor showed torn screen artifacts because data cache lines remained dirty during quad serial peripheral interface memory-mapped transfers while the graphics firmware lacked cache calibration, inspecting the cache line boundaries inside qspi_dcache_flush module instead.\n\nCalibrate the data cache clean and invalidate boundaries by loading 32 cache lines instead into the maintenance register. Write 0xe000e000 into the SCB base register. Write 0x0d instead into the cache control register for coherent memory transactions. We cleared the cache maintenance flag by writing 1 into the status clear register.\n\nAfter calibrating cache line boundaries and scheduling FreeRTOS graphics tasks on the CPU core, the controller rendered 22000 display frames across 36 hours without frame corruption or cache inconsistencies."
    },

    # Sample 20: Microchip dsPIC33CK: High-Resolution PWM Dual-Edge trigger dead-time compensation glitch during synchronous buck conversion
    {
        "raw_asr": "so um our digital power converter suffered shoot through current spikes and pulse width modulation trigger glitches during synchronous buck switching over open o c d we tapped complementary gate drive signals using an oscilloscope and tracked dead time violation spikes across eighteen switching cycles the power stage suffered shoot through currents because dead time compensation registers failed to account for power mosfet turn off propagation delays while the control firmware lacked timing calibrat wait inspect the dead time parameters inside pwm underscore deadtime underscore comp module instead calibrat the dead time delay buy loading ten wait twenty nanosecond delay steps instead into the compensation register right zero x zero zero zero zero c zero zero zero into the pwm base register right zero x zero two into the edge control register wait right zero x zero f instead four safe gate switching transitions we cleared the dead time fault flag buy writing one into the status clear register after calibrating dead time delay steps and updating high resolution timer compare registers on the c p u interface the digital power converter regulated twenty four thousand switching cycles across thirty hours without shoot through current spikes or trigger glitches",
        "refined_text": "Our digital power converter suffered shoot-through current spikes and pulse-width modulation trigger glitches during synchronous buck switching. Over OpenOCD we tapped complementary gate drive signals using an oscilloscope and tracked dead-time violation spikes across 18 switching cycles. The power stage suffered shoot-through currents because dead-time compensation registers failed to account for power MOSFET turn-off propagation delays while the control firmware lacked timing calibration, inspecting the dead-time parameters inside pwm_deadtime_comp module instead.\n\nCalibrate the dead-time delay by loading 20 nanosecond delay steps instead into the compensation register. Write 0x0000c000 into the PWM base register. Write 0x0f instead into the edge control register for safe gate switching transitions. We cleared the dead-time fault flag by writing 1 into the status clear register.\n\nAfter calibrating dead-time delay steps and updating high-resolution timer compare registers on the CPU interface, the digital power converter regulated 24000 switching cycles across 30 hours without shoot-through current spikes or trigger glitches."
    },
]

print(f"Total candidate samples: {len(batch_194)}")

tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []
all_valid = True

for idx, s in enumerate(batch_194, 1):
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
    batch_194,
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
    out_path = Path("scratch/subagent_batch_194.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch_194, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote verified batch to {out_path}")
else:
    print("\nErrors encountered! Did not write output.")
    sys.exit(1)
