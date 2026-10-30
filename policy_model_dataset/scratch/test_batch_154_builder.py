import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, get_noise_layer_count, count_active_noise_layers
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batch_154 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Content words >= 6-8.
    # =========================================================================

    # Sample 1: RP2040 SPI DMA channel assignment
    {
        "raw_asr": "um configur the serial peripheral interface d m a receive channel buy writing zero x zero four into the control register",
        "refined_text": "Configure the serial peripheral interface DMA receive channel by writing 0x04 into the control register."
    },

    # Sample 2: Nordic nRF52840 SAADC calibration
    {
        "raw_asr": "uh calibrat the analog digital converter offset four the sensor channel buy writing zero x zero one into the n v i c interrupt register",
        "refined_text": "Calibrate the analog digital converter offset for the sensor channel by writing 0x01 into the NVIC interrupt register."
    },

    # Sample 3: Microchip SAM E70 CAN-FD mailbox initialization
    {
        "raw_asr": "basically initializ the hardware u art transmission queue four eight telemetry packets buy writing zero x zero eight into the fifo register",
        "refined_text": "Initialize the hardware UART transmission queue for 8 telemetry packets by writing 0x08 into the FIFO register."
    },

    # Sample 4: ESP32-S3 FreeRTOS watchdog timer termination
    {
        "raw_asr": "so um terminat the free are toss watchdog timer task buy writing zero x one zero into the timer control register",
        "refined_text": "Terminate the FreeRTOS watchdog timer task by writing 0x10 into the timer control register."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: STM32U5 low-power timer LPTIM wake-up event
    {
        "raw_asr": "um configur the low power timer wake up event inside lptim underscore driver dot c buy routing eight wait sixteen bus events instead into the n v i c priority register you know the i two c peripheral detects incoming sensor packets buy writing zero x four zero into the slave address register",
        "refined_text": "Configure the low-power timer wake-up event inside lptim_driver.c by routing 16 bus events instead into the NVIC priority register.\n\nThe I2C peripheral detects incoming sensor packets by writing 0x40 into the slave address register."
    },

    # Sample 6: RP2040 PIO state machine DMA FIFO stall
    {
        "raw_asr": "uh operat the programmable input output state machine inside pio underscore dma dot c buy transferring thirty two wait sixty four d m a words instead into the transmit buffer basically engineers right zero x zero c into the s p i clock divider register four high speed peripheral clocking",
        "refined_text": "Operate the programmable input output state machine inside pio_dma.c by transferring 64 DMA words instead into the transmit buffer.\n\nEngineers write 0x0c into the SPI clock divider register for high-speed peripheral clocking."
    },

    # Sample 7: Texas Instruments CC2652R RF core flash memory protection
    {
        "raw_asr": "so um allocat thirty two wait sixty four descriptor bytes instead inside ccfg underscore boot dot c four the secondary bootloader metadata table i mean the c p u core signals u art packet reception buy writing zero x two zero into the interrupt status register four flash programming",
        "refined_text": "Allocate 64 descriptor bytes instead inside ccfg_boot.c for the secondary bootloader metadata table.\n\nThe CPU core signals UART packet reception by writing 0x20 into the interrupt status register for flash programming."
    },

    # Sample 8: ESP32-C3 RISC-V timer interrupt handling under FreeRTOS
    {
        "raw_asr": "um verify timer synchronizat inside riscv underscore timer dot c buy inspecting sixteen wait twenty ticks instead four task wakeups the r i s c v kernel handles context switching buy updating the stack pointer register basically right zero x one c into the free are toss hardware timer register four interrupt dispatch",
        "refined_text": "Verify timer synchronization inside riscv_timer.c by inspecting 20 ticks instead for task wakeups. The RISC-V kernel handles context switching by updating the stack pointer register.\n\nWrite 0x1c into the FreeRTOS hardware timer register for interrupt dispatch."
    },

    # Sample 9: NXP LPC55S69 CAN-FD arbitration and bit timing register configuration
    {
        "raw_asr": "uh calibrat the controller area network arbitrat phase inside can underscore bus dot c buy selecting eight wait select sixteen time quanta instead four nominal bit timing you know the n v i c interrupt controller services d m a message transfers buy writing zero x zero e into the control register",
        "refined_text": "Calibrate the controller area network arbitration phase inside can_bus.c by selecting 16 time quanta instead for nominal bit timing.\n\nThe NVIC interrupt controller services DMA message transfers by writing 0x0e into the control register."
    },

    # Sample 10: Silicon Labs EFR32MG24 hardware crypto accelerator DMA ring buffer
    {
        "raw_asr": "so basically allocat the hardware accelerator descriptor buffer inside crypto underscore engine dot c buy reserving four wait scratch that eight d m a descriptors instead four cipher operations um engineers right zero x two four into the s p i interface register four secure key authentication",
        "refined_text": "Allocate the hardware accelerator descriptor buffer inside crypto_engine.c by reserving 8 DMA descriptors instead for cipher operations.\n\nEngineers write 0x24 into the SPI interface register for secure key authentication."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 11: STM32H563 USB High-Speed PHY clock drift
    {
        "raw_asr": "um our stm thirty two h five sixty three communication board experienced universal serial bus high speed bulk packet drops during continuous sensor data acquisition we connected an oscilloscope two the differential data pins and captured register traces over open o c d the internal physical layer oscillator drifted because thermal variations shifted reference clock frequencies while the universal serial bus driver lacked oscillator calibrat wait inspect the clock tuning routine inside usb underscore phy dot c instead calibrat the physical layer oscillator buy programming sixteen wait thirty two tuning steps instead into the clock trim register right zero x four zero zero zero one zero zero zero into the peripheral base address register right zero x zero four into the physical layer control register wait right zero x zero c instead four phase locked loop synchronizat we cleared the transfer error status buy writing one into the interrupt clear register after updating the clock tuning parameters and reconfiguring d m a burst thresholds the communication board transferred five thousand telemetry packets across twenty four hours without packet drops or universal serial bus resets",
        "refined_text": "Our STM32H563 communication board experienced universal serial bus high-speed bulk packet drops during continuous sensor data acquisition. We connected an oscilloscope to the differential data pins and captured register traces over OpenOCD. The internal physical layer oscillator drifted because thermal variations shifted reference clock frequencies while the universal serial bus driver lacked oscillator calibration, inspecting the clock tuning routine inside usb_phy.c instead.\n\nCalibrate the physical layer oscillator by programming 32 tuning steps instead into the clock trim register. Write 0x40001000 into the peripheral base address register. Write 0x0c instead into the physical layer control register for phase-locked loop synchronization. We cleared the transfer error status by writing 1 into the interrupt clear register.\n\nAfter updating the clock tuning parameters and reconfiguring DMA burst thresholds, the communication board transferred 5000 telemetry packets across 24 hours without packet drops or universal serial bus resets."
    },

    # Sample 12: ESP32-S3 Dual-Core Xtensa LX7 PSRAM octal SPI cache eviction deadlock under FreeRTOS
    {
        "raw_asr": "uh our esp thirty two s three telemetry module suffered octal serial peripheral interface cache eviction stalls during video streaming we monitored core execution flow using a logic analyzer and tracked task switches over a u art serial monitor the secondary processor stalled because external memory cache line invalidations clashed with direct memory access transfers while the memory driver lacked cache synchronizat wait inspect the memory mapping logic inside psram underscore cache dot c instead configur the octal serial peripheral interface cache eviction buy assigning thirty two wait sixty four cache lines instead into the eviction threshold register right zero x three zero zero zero zero zero zero zero into the external memory base address register right zero x zero eight into the cache control register wait right zero x zero e instead four non blocking cache flush operations we cleared the memory stall flag buy writing one into the core status register after updating the eviction threshold and adjusting free are toss task priorities the telemetry module processed six thousand video frames across eighteen hours without memory stalls or frame drops",
        "refined_text": "Our ESP32-S3 telemetry module suffered octal serial peripheral interface cache eviction stalls during video streaming. We monitored core execution flow using a logic analyzer and tracked task switches over a UART serial monitor. The secondary processor stalled because external memory cache line invalidations clashed with direct memory access transfers while the memory driver lacked cache synchronization, inspecting the memory mapping logic inside psram_cache.c instead.\n\nConfigure the octal serial peripheral interface cache eviction by assigning 64 cache lines instead into the eviction threshold register. Write 0x30000000 into the external memory base address register. Write 0x0e instead into the cache control register for non-blocking cache flush operations. We cleared the memory stall flag by writing 1 into the core status register.\n\nAfter updating the eviction threshold and adjusting FreeRTOS task priorities, the telemetry module processed 6000 video frames across 18 hours without memory stalls or frame drops."
    },

    # Sample 13: Nordic nRF9160 LTE-M/NB-IoT modem IPC and shared memory buffer
    {
        "raw_asr": "so um our nordic n r f ninety one sixty cellular tracker dropped network packets during tls socket transmiss we connected a protocol analyzer two the modem trace lines and analyzed core memory over a segger j link probe the modem application interface lost data packets because shared memory circular buffers overflowed during high throughput data transmission while the interface firmware lacked buffer allocat wait inspect the memory pool configuration inside modem underscore ipc dot c instead allocat the modem shared memory circular buffer buy assigning thirty two wait sixty four kilobyte memory blocks instead into the shared pool register right zero x two zero zero zero four zero zero zero into the memory base address register right zero x one zero into the queue configuration register wait right zero x one eight instead four non blocking socket packet queuing we cleared the modem fifo overflow alarm buy writing one into the n v i c interrupt acknowledge register after allocating expanded shared memory blocks and enabling d m a scatter gather reception the cellular tracker transmitted seven thousand telemetry packets across twenty four hours without memory corruption or socket drops",
        "refined_text": "Our Nordic nRF9160 cellular tracker dropped network packets during TLS socket transmission. We connected a protocol analyzer to the modem trace lines and analyzed core memory over a SEGGER J-Link probe. The modem application interface lost data packets because shared memory circular buffers overflowed during high-throughput data transmission while the interface firmware lacked buffer allocation, inspecting the memory pool configuration inside modem_ipc.c instead.\n\nAllocate the modem shared memory circular buffer by assigning 64 kilobyte memory blocks instead into the shared pool register. Write 0x20004000 into the memory base address register. Write 0x18 instead into the queue configuration register for non-blocking socket packet queuing. We cleared the modem FIFO overflow alarm by writing 1 into the NVIC interrupt acknowledge register.\n\nAfter allocating expanded shared memory blocks and enabling DMA scatter-gather reception, the cellular tracker transmitted 7000 telemetry packets across 24 hours without memory corruption or socket drops."
    },

    # Sample 14: NXP i.MX RT685 Dual-Core Cortex-M33 + Cadence HiFi 4 DSP
    {
        "raw_asr": "um our n x p r t six eighty five audio processing board suffered inter core communication deadlocks during multi channel sound synthesis we attached a logic analyzer two the hardware mailbox pins and traced context switching over open o c d the main processor missed notification flags because audio stream buffers filled faster than the digital signal processor cleared event interrupts while the inter processor driver lacked semaphore initializ wait inspect the mailbox synchronization routine inside mailbox underscore router dot c instead initializ the inter processor hardware mailbox buy allocating sixteen wait thirty two message slots instead into the mailbox queue register right zero x four zero one zero zero zero zero zero into the mailbox base address register right zero x zero two into the channel control register wait right zero x zero a instead four non blocking inter core signaling we cleared the inter processor deadlock flag buy writing one into the c p u status register after reinitializing the mailbox message slots and tuning free are toss context switch periods the audio processing board processed eight thousand sound buffers across sixteen hours without processor deadlocks or buffer dropouts",
        "refined_text": "Our NXP RT685 audio processing board suffered inter-core communication deadlocks during multi-channel sound synthesis. We attached a logic analyzer to the hardware mailbox pins and traced context switching over OpenOCD. The main processor missed notification flags because audio stream buffers filled faster than the digital signal processor cleared event interrupts while the inter-processor driver lacked semaphore initialization, inspecting the mailbox synchronization routine inside mailbox_router.c instead.\n\nInitialize the inter-processor hardware mailbox by allocating 32 message slots instead into the mailbox queue register. Write 0x40100000 into the mailbox base address register. Write 0x0a instead into the channel control register for non-blocking inter-core signaling. We cleared the inter-processor deadlock flag by writing 1 into the CPU status register.\n\nAfter reinitializing the mailbox message slots and tuning FreeRTOS context switch periods, the audio processing board processed 8000 sound buffers across 16 hours without processor deadlocks or buffer dropouts."
    },

    # Sample 15: Microchip SAM V71 Cortex-M7 with Ethernet MAC
    {
        "raw_asr": "uh our microchip s a m v seventy one industrial gateway dropped ethernet packets during precision time protocol timestamping we captured network traffic using wi re shark and tracked media independent interface registers over a segger j link probe the physical layer interface lost timestamp precision because receive descriptor ring buffers stalled under heavy broadcast traffic while the media access controller lacked clock calibrat wait inspect the timestamp counter configuration inside ethernet underscore ptp dot c instead calibrat the precision time protocol clock buy adjusting eight wait sixteen clock addend increments instead into the timestamp frequency register right zero x four zero zero five zero zero zero zero into the ethernet base address register right zero x zero four into the media independent interface register wait right zero x zero c instead four phase aligned packet timestamping we cleared the receive descriptor buffer stall buy writing one into the n v i c interrupt clear register after calibrating the clock addend value and enlarging direct memory access descriptor rings the industrial gateway forwarded nine thousand network frames across twenty four hours without timestamp drift or packet drops",
        "refined_text": "Our Microchip SAM V71 industrial gateway dropped Ethernet packets during precision time protocol timestamping. We captured network traffic using Wireshark and tracked media independent interface registers over a SEGGER J-Link probe. The physical layer interface lost timestamp precision because receive descriptor ring buffers stalled under heavy broadcast traffic while the media access controller lacked clock calibration, inspecting the timestamp counter configuration inside ethernet_ptp.c instead.\n\nCalibrate the precision time protocol clock by adjusting 16 clock addend increments instead into the timestamp frequency register. Write 0x40050000 into the ethernet base address register. Write 0x0c instead into the media independent interface register for phase-aligned packet timestamping. We cleared the receive descriptor buffer stall by writing 1 into the NVIC interrupt clear register.\n\nAfter calibrating the clock addend value and enlarging direct memory access descriptor rings, the industrial gateway forwarded 9000 network frames across 24 hours without timestamp drift or packet drops."
    },

    # Sample 16: Texas Instruments MSPM0G3507 Cortex-M0+ mixed-signal MCU
    {
        "raw_asr": "basically our texas instruments m s p m zero g thirty five zero seven motor controller suffered current sensing distortion during high speed pulse width modulation switching we connected an oscilloscope two the current shunt analog inputs and verified conversion timestamps over open o c d the analog digital converter produced inaccurate phase readings because sample and hold timings drifted across switching cycles while the peripheral driver lacked phase synchronizat wait inspect the trigger delay table inside adc underscore sampler dot c instead calibrat the analog digital converter trigger delay buy loading sixteen wait thirty two clock cycles instead into the trigger delay register right zero x four zero zero eight zero zero zero zero into the analog digital converter base address register right zero x zero eight into the sampling control register wait right zero x one eight instead four synchronized sampling conversion we cleared the analog conversion error buy writing one into the status acknowledge register after updating the trigger delay cycles and enabling d m a circular buffer transfers the motor controller completed seven thousand current measurement cycles across twelve hours without conversion distortion or sensor faults",
        "refined_text": "Our Texas Instruments MSPM0G3507 motor controller suffered current sensing distortion during high-speed pulse width modulation switching. We connected an oscilloscope to the current shunt analog inputs and verified conversion timestamps over OpenOCD. The analog digital converter produced inaccurate phase readings because sample and hold timings drifted across switching cycles while the peripheral driver lacked phase synchronization, inspecting the trigger delay table inside adc_sampler.c instead.\n\nCalibrate the analog digital converter trigger delay by loading 32 clock cycles instead into the trigger delay register. Write 0x40080000 into the analog digital converter base address register. Write 0x18 instead into the sampling control register for synchronized sampling conversion. We cleared the analog conversion error by writing 1 into the status acknowledge register.\n\nAfter updating the trigger delay cycles and enabling DMA circular buffer transfers, the motor controller completed 7000 current measurement cycles across 12 hours without conversion distortion or sensor faults."
    },

    # Sample 17: Renesas RA4M2 Cortex-M33 with Secure Element and SPI Flash
    {
        "raw_asr": "so um our renesas r a four m two secure sensor node suffered execution freezes during encrypted external flash access we connected a logic analyzer two the external memory lines and inspected core registers over a segger j link probe the central processor stalled during flash execution because prefetch buffer invalidations occurred during high frequency bus transactions while the memory interface lacked prefetch configur wait inspect the bus timing parameters inside qspi underscore flash dot c instead configur the quad serial peripheral interface prefetch buffer buy programming sixteen wait thirty two prefetch cycles instead into the prefetch control register right zero x six zero zero zero zero zero zero zero into the flash memory address register right zero x one zero into the bus timing register wait right zero x two zero instead four synchronized memory instruction fetches we cleared the prefetch stall alarm buy writing one into the n v i c interrupt clear register after reconfiguring prefetch cycle parameters and enabling d m a burst reading the secure sensor node executed eight thousand flash instructions across sixteen hours without execution freezes or bus timeout errors",
        "refined_text": "Our Renesas RA4M2 secure sensor node suffered execution freezes during encrypted external flash access. We connected a logic analyzer to the external memory lines and inspected core registers over a SEGGER J-Link probe. The central processor stalled during flash execution because prefetch buffer invalidations occurred during high-frequency bus transactions while the memory interface lacked prefetch configuration, inspecting the bus timing parameters inside qspi_flash.c instead.\n\nConfigure the quad serial peripheral interface prefetch buffer by programming 32 prefetch cycles instead into the prefetch control register. Write 0x60000000 into the flash memory address register. Write 0x20 instead into the bus timing register for synchronized memory instruction fetches. We cleared the prefetch stall alarm by writing 1 into the NVIC interrupt clear register.\n\nAfter reconfiguring prefetch cycle parameters and enabling DMA burst reading, the secure sensor node executed 8000 flash instructions across 16 hours without execution freezes or bus timeout errors."
    },

    # Sample 18: Raspberry Pi RP2350 Dual Hazard3 RISC-V cores
    {
        "raw_asr": "uh our raspberry pi r p twenty three fifty robotics controller experienced mutual exclusion deadlocks during dual core trajectory calculation we attached an oscilloscope two the inter core signaling lines and captured execution traces over open o c d the secondary r i s c v core stalled because hardware spinlock acquisitions timed out during heavy context switching while the multi core driver lacked lock initializ wait inspect the spinlock reservation routine inside spinlock underscore core dot c instead initializ the hardware spinlock arbitrat buy assigning eight wait sixteen spinlock retry cycles instead into the spinlock control register right zero x two zero zero zero zero zero zero zero into the hardware spinlock base address register right zero x zero four into the core reservation register wait right zero x zero c instead four fair core bus arbitrat we cleared the spinlock deadlock alert buy writing one into the core fault status register after updating the spinlock retry cycles and balancing direct memory access channels the robotics controller executed six thousand motion steps across eighteen hours without spinlock deadlocks or processor stalls",
        "refined_text": "Our Raspberry Pi RP2350 robotics controller experienced mutual exclusion deadlocks during dual-core trajectory calculation. We attached an oscilloscope to the inter-core signaling lines and captured execution traces over OpenOCD. The secondary RISC-V core stalled because hardware spinlock acquisitions timed out during heavy context switching while the multi-core driver lacked lock initialization, inspecting the spinlock reservation routine inside spinlock_core.c instead.\n\nInitialize the hardware spinlock arbitration by assigning 16 spinlock retry cycles instead into the spinlock control register. Write 0x20000000 into the hardware spinlock base address register. Write 0x0c instead into the core reservation register for fair core bus arbitration. We cleared the spinlock deadlock alert by writing 1 into the core fault status register.\n\nAfter updating the spinlock retry cycles and balancing direct memory access channels, the robotics controller executed 6000 motion steps across 18 hours without spinlock deadlocks or processor stalls."
    },

    # Sample 19: SiFive FE310 RISC-V microcontroller with FreeRTOS
    {
        "raw_asr": "um our si five f e three ten sensor gateway experienced timer interrupt latency jitter during high throughput u art telemetry streaming we connected a logic analyzer two the external interrupt lines and verified core register states over open o c d the core local interrupt controller produced scheduling delays because hardware timer comparator values updated asynchronously during task execution while the timer driver lacked clock calibrat wait inspect the comparator refresh logic inside clint underscore timer dot c instead calibrat the core local interrupt timer buy loading sixteen wait thirty two clock cycles instead into the comparator register right zero x zero two zero zero zero zero zero zero into the timer base address register right zero x zero six into the timer interrupt control register wait right zero x zero e instead four synchronized task tick generation we cleared the timer jitter alert buy writing one into the interrupt pending register after programming updated comparator increments and adjusting free are toss tick rates the sensor gateway processed seven thousand telemetry packets across fourteen hours without scheduling delays or lost timer interrupts",
        "refined_text": "Our SiFive FE310 sensor gateway experienced timer interrupt latency jitter during high-throughput UART telemetry streaming. We connected a logic analyzer to the external interrupt lines and verified core register states over OpenOCD. The core local interrupt controller produced scheduling delays because hardware timer comparator values updated asynchronously during task execution while the timer driver lacked clock calibration, inspecting the comparator refresh logic inside clint_timer.c instead.\n\nCalibrate the core local interrupt timer by loading 32 clock cycles instead into the comparator register. Write 0x02000000 into the timer base address register. Write 0x0e instead into the timer interrupt control register for synchronized task tick generation. We cleared the timer jitter alert by writing 1 into the interrupt pending register.\n\nAfter programming updated comparator increments and adjusting FreeRTOS tick rates, the sensor gateway processed 7000 telemetry packets across 14 hours without scheduling delays or lost timer interrupts."
    },

    # Sample 20: STMicroelectronics STM32G474 mixed-signal MCU with High-Resolution Timer (HRTIM)
    {
        "raw_asr": "basically our stm thirty two g four seventy four resonant power converter suffered pulse width modulation pulse skipping during light load power conversion we attached an oscilloscope two the complementary high side gate driver pins and monitored internal fault counters over open o c d the high resolution timer missed output pulse edges because burst mode comparator thresholds overlapped with resonant dead time windows while the gate driver lacked phase synchronizat wait inspect the burst mode configuration inside hrtim underscore driver dot c instead calibrat the high resolution timer burst mode buy programming eight wait sixteen resonant clock steps instead into the burst period register right zero x four zero zero one zero zero zero zero into the timer base address register right zero x zero a into the fault control register wait right zero x one four instead four glitch free burst pulse generation we cleared the resonant fault counter buy writing one into the status clear register after calibrating the burst period steps and enabling d m a register updates the resonant power converter completed eight thousand power conversion cycles across twenty four hours without pulse skipping or gate driver faults",
        "refined_text": "Our STM32G474 resonant power converter suffered pulse width modulation pulse skipping during light-load power conversion. We attached an oscilloscope to the complementary high-side gate driver pins and monitored internal fault counters over OpenOCD. The high-resolution timer missed output pulse edges because burst mode comparator thresholds overlapped with resonant dead time windows while the gate driver lacked phase synchronization, inspecting the burst mode configuration inside hrtim_driver.c instead.\n\nCalibrate the high-resolution timer burst mode by programming 16 resonant clock steps instead into the burst period register. Write 0x40010000 into the timer base address register. Write 0x14 instead into the fault control register for glitch-free burst pulse generation. We cleared the resonant fault counter by writing 1 into the status clear register.\n\nAfter calibrating the burst period steps and enabling DMA register updates, the resonant power converter completed 8000 power conversion cycles across 24 hours without pulse skipping or gate driver faults."
    }
]

def main():
    print(f"Total candidate samples: {len(batch_154)}")
    assert len(batch_154) == 20, f"Expected exactly 20 samples, got {len(batch_154)}"

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []
    cleaner_drops = 0
    validator_drops = 0

    for idx, s in enumerate(batch_154):
        raw = s["raw_asr"]
        ref = s["refined_text"]

        # Eval leakage check
        if raw.lower() in eval_raws:
            print(f"Sample {idx+1} LEAKAGE: raw_asr in eval set!")
        if ref in eval_refs:
            print(f"Sample {idx+1} LEAKAGE: refined_text in eval set!")

        # Cleaner check
        res, clean_status = clean_sample(raw, ref)
        if not res or clean_status != "kept":
            print(f"Sample {idx+1} cleaner failed: {clean_status}")
            cleaner_drops += 1

        # Validator pair check
        v_ok, v_msg = validate_pair(s, min_noise_layers=4)
        if not v_ok:
            print(f"Sample {idx+1} validator failed: {v_msg}")
            validator_drops += 1

        # Tier counting
        w_count = len(ref.split())
        if w_count < 25:
            tier_counts["short"] += 1
        elif w_count < 90:
            tier_counts["medium"] += 1
        else:
            tier_counts["long"] += 1

        nl_count = get_noise_layer_count(raw)
        layer_counts.append(nl_count)
        layers_active = count_active_noise_layers(raw)
        print(f"Sample {idx+1:02d}: words={w_count:3d}, breaks={ref.count(chr(10)*2)}, layers={nl_count} {layers_active}, clean={clean_status}")

    print("\n--- Summary ---")
    print(f"Tier counts: {tier_counts}")
    avg_layers = sum(layer_counts) / len(layer_counts)
    print(f"Average noise layers: {avg_layers:.2f}")
    print(f"Cleaner drops: {cleaner_drops}")
    print(f"Validator drops: {validator_drops}")

    assert cleaner_drops == 0, f"Cleaner drops: {cleaner_drops}"
    assert validator_drops == 0, f"Validator drops: {validator_drops}"
    assert tier_counts["short"] == 4, f"Short tier mismatch: {tier_counts['short']}"
    assert tier_counts["medium"] == 6, f"Medium tier mismatch: {tier_counts['medium']}"
    assert tier_counts["long"] == 10, f"Long tier mismatch: {tier_counts['long']}"
    assert avg_layers >= 4.0, f"Average noise layers too low: {avg_layers}"

    # Batch validator check
    batch_ok, batch_msg, batch_meta = validate_batch(
        batch_154, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    print(f"validate_batch: {batch_ok} - {batch_msg}")
    print(f"batch_meta: {batch_meta}")
    assert batch_ok, f"Batch validation failed: {batch_msg}"

    # Save to scratch/subagent_batch_154.json
    output_path = Path("scratch/subagent_batch_154.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch_154, f, ensure_ascii=False, indent=2)
    print(f"\nSuccessfully written 20 verified samples to {output_path}")

if __name__ == "__main__":
    main()
