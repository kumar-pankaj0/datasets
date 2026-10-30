import json
import re
import sys
import os
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

# Define the 20 candidate pairs for Batch 134 (Domain 6: Embedded Systems & Firmware Development)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_134 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Sample 1: Nordic nRF5340 dual-core IPC channel assignment
    {
        "raw_asr": "uh configur the inter processor communication channel buy writing zero x zero four into the c p u network register",
        "refined_text": "Configure the inter-processor communication channel by writing 0x04 into the CPU network register."
    },
    # Sample 2: ST STM32G474 HRTIM resonant period calibration
    {
        "raw_asr": "um calibrat the high resolution timer resonant period buy assigning sixteen wait thirty two d m a burst cycles",
        "refined_text": "Calibrate the high-resolution timer resonant period by assigning 32 DMA burst cycles."
    },
    # Sample 3: Microchip SAM D21 SERCOM I2C baud rate register
    {
        "raw_asr": "basically initializ the serial communication i two c clock buy writing zero x zero eight into the baud register",
        "refined_text": "Initialize the serial communication I2C clock by writing 0x08 into the baud register."
    },
    # Sample 4: Texas Instruments MSP430FR5994 FRAM memory protection unit segment boundary
    {
        "raw_asr": "uh terminat the ferroelectric ram memory protection segment buy writing zero x one zero into the u art control register",
        "refined_text": "Terminate the ferroelectric RAM memory protection segment by writing 0x10 into the UART control register."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # Sample 5: NXP LPC55S69 TrustZone secure non-secure peripheral interrupt router
    {
        "raw_asr": "um configur the non secure access prescaler register buy routing twelve wait twenty four peripheral vectors instead into the n v i c interrupt controller basically the s p i interface routes secure sensor packets buy driving eight dedicated channels",
        "refined_text": "Configure the non-secure access prescaler register by routing 24 peripheral vectors instead into the NVIC interrupt controller.\n\nThe SPI interface routes secure sensor packets by driving 8 dedicated channels."
    },
    # Sample 6: ST STM32F767 Quad-SPI memory mapped flash execution cache
    {
        "raw_asr": "uh initializ the quad serial peripheral interface flash controller buy writing zero x zero four wait right zero x zero c instead into the communication configuration register the c p u executes cached flash instructions buy prefetching sixteen wait thirty two cache blocks",
        "refined_text": "Initialize the quad serial peripheral interface flash controller by writing 0x0c instead into the communication configuration register.\n\nThe CPU executes cached flash instructions by prefetching 32 cache blocks."
    },
    # Sample 7: Renesas RA6M5 USB High-Speed DMA endpoint buffer allocation
    {
        "raw_asr": "basically allocat the high speed universal serial bus endpoint buffers buy assigning sixty four wait one two eight bytes instead into the d m a descriptor four bulk packet streaming the peripheral controller services bulk transfers buy cycling through eight double buffered fifo channels",
        "refined_text": "Allocate the high-speed universal serial bus endpoint buffers by assigning 128 bytes instead into the DMA descriptor for bulk packet streaming.\n\nThe peripheral controller services bulk transfers by cycling through 8 double-buffered FIFO channels."
    },
    # Sample 8: Silicon Labs EFR32BG22 Bluetooth Low Energy sleep clock calibration
    {
        "raw_asr": "um calibrat the low energy sleep clock oscillator buy loading zero x zero one wait load zero x zero two instead into the tuning register four wireless beacon intervals the free are toss kernel coordinates sleep transitions buy scheduling sixteen hardware timer wakeups",
        "refined_text": "Calibrate the low-energy sleep clock oscillator by loading 0x02 instead into the tuning register for wireless beacon intervals.\n\nThe FreeRTOS kernel coordinates sleep transitions by scheduling 16 hardware timer wakeups."
    },
    # Sample 9: TI SimpleLink CC2340R5 RTC tamper detection prescaler
    {
        "raw_asr": "uh terminat the real time clock tamper detection cycle buy writing zero x zero zero wait right zero x zero a instead into the control register four security boundary monitoring the n v i c core isolates suspicious bus faults buy asserting four dedicated exception traps",
        "refined_text": "Terminate the real-time clock tamper detection cycle by writing 0x0a instead into the control register for security boundary monitoring.\n\nThe NVIC core isolates suspicious bus faults by asserting 4 dedicated exception traps."
    },
    # Sample 10: Espressif ESP32-C3 RISC-V interrupt controller vector table routing
    {
        "raw_asr": "basically operat the r i s c v vector interrupt controller buy routing eight wait sixteen hardware lines instead into the priority matrix register four fast exception dispatch the central core services incoming events buy executing thirty two vectorized handler addresses",
        "refined_text": "Operate the RISC-V vector interrupt controller by routing 16 hardware lines instead into the priority matrix register for fast exception dispatch.\n\nThe central core services incoming events by executing 32 vectorized handler addresses."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Sample 11: ST STM32H7B3 Octo-SPI DLYB tuning during DDR flash access
    {
        "raw_asr": "um our stm thirty two h seven b three graphics board experienced read data corruption during high speed octo serial peripheral interface ddr flash streaming we connected an oscilloscope two the memory clock and data lines and verified signal delays over open o c d the delay block controller sampled corrupted words because phase shifts between the memory clock and read strobe drifted across temperature changes while the flash driver lacked delay block calibrat wait inspect the delay calibration table inside octospi underscore flash driver module instead calibrat the octo serial peripheral interface delay block buy setting sixteen wait thirty two phase delay units instead into the tuning control register right zero x five two zero zero zero zero zero zero into the memory base address register right zero x zero four into the delay block control register wait right zero x zero c instead four phase aligned sampling we cleared the memory sampling error flag buy writing one into the status clear register after updating the delay unit configuration and enabling automatic phase compensation the graphics board streamed four thousand framebuffer images across twenty four hours without memory corruption or crc transfer faults",
        "refined_text": "Our STM32H7B3 graphics board experienced read data corruption during high-speed octo serial peripheral interface DDR flash streaming. We connected an oscilloscope to the memory clock and data lines and verified signal delays over OpenOCD. The delay block controller sampled corrupted words because phase shifts between the memory clock and read strobe drifted across temperature changes while the flash driver lacked delay block calibration, inspecting the delay calibration table inside octospi_flash_driver module instead.\n\nCalibrate the octo serial peripheral interface delay block by setting 32 phase delay units instead into the tuning control register. Write 0x52000000 into the memory base address register. Write 0x0c instead into the delay block control register for phase-aligned sampling. We cleared the memory sampling error flag by writing 1 into the status clear register.\n\nAfter updating the delay unit configuration and enabling automatic phase compensation, the graphics board streamed 4000 framebuffer images across 24 hours without memory corruption or CRC transfer faults."
    },
    # Sample 12: NXP i.MX RT1170 CM7-CM4 shared memory semaphore lockup under FreeRTOS
    {
        "raw_asr": "uh our n x p r t eleven seventy dual core platform experienced inter core communication deadlocks during dual core audio dsp streaming we connected a logic analyzer two the inter processor signaling lines and captured core execution traces over a segger j link debugger the hardware semaphore gate remained locked because the secondary core missed notification interrupts during heavy context switching while the inter core driver lacked mutex synchronizat wait inspect the semaphore release logic inside ipc underscore semaphore manager module instead configur the hardware semaphore gate timeout buy assigning sixteen wait thirty two timeout cycles instead into the gate control register right zero x two zero two zero zero zero zero zero into the shared memory buffer address register right zero x zero eight into the semaphore gate register wait right zero x zero e instead four non blocking core synchronization we cleared the core lockup flag buy writing one into the inter core status register after updating the hardware semaphore timeout and reconfiguring free are toss task priorities the dual core platform processed six thousand audio buffers across twenty four hours without inter core deadlocks or buffer dropouts",
        "refined_text": "Our NXP RT1170 dual-core platform experienced inter-core communication deadlocks during dual-core audio DSP streaming. We connected a logic analyzer to the inter-processor signaling lines and captured core execution traces over a SEGGER J-Link debugger. The hardware semaphore gate remained locked because the secondary core missed notification interrupts during heavy context switching while the inter-core driver lacked mutex synchronization, inspecting the semaphore release logic inside ipc_semaphore_manager module instead.\n\nConfigure the hardware semaphore gate timeout by assigning 32 timeout cycles instead into the gate control register. Write 0x20200000 into the shared memory buffer address register. Write 0x0e instead into the semaphore gate register for non-blocking core synchronization. We cleared the core lockup flag by writing 1 into the inter-core status register.\n\nAfter updating the hardware semaphore timeout and reconfiguring FreeRTOS task priorities, the dual-core platform processed 6000 audio buffers across 24 hours without inter-core deadlocks or buffer dropouts."
    },
    # Sample 13: Microchip dsPIC33CK dual-core digital power PWM phase shift jitter
    {
        "raw_asr": "basically our microchip d s p i c thirty three c k power converter suffered switching phase jitter during high frequency interleaved power conversion we monitored gate driver signals using an oscilloscope connected two the complementary high side gate outputs and analyzed register updates over a pic kit probe the digital pulse width modulator drifted because master period registers updated asynchronously across phase cycles while the power control firmware lacked phase calibrat wait inspect the phase compensation table inside pwm underscore phase controller module instead calibrat the master period phase shift buy loading ten wait twenty nanoseconds delay instead into the phase offset register right zero x zero two zero zero into the master period register right zero x zero three into the generator control register wait right zero x zero b instead four synchronized phase triggering we cleared the phase jitter alarm buy writing one into the fault clear register after tuning master phase offsets and enabling d m a register updates the power converter completed seven thousand load transient tests across eighteen hours without switching jitter or gate driver overlap",
        "refined_text": "Our Microchip dsPIC33CK power converter suffered switching phase jitter during high-frequency interleaved power conversion. We monitored gate driver signals using an oscilloscope connected to the complementary high-side gate outputs and analyzed register updates over a PICkit probe. The digital pulse width modulator drifted because master period registers updated asynchronously across phase cycles while the power control firmware lacked phase calibration, inspecting the phase compensation table inside pwm_phase_controller module instead.\n\nCalibrate the master period phase shift by loading 20 nanoseconds delay instead into the phase offset register. Write 0x0200 into the master period register. Write 0x0b instead into the generator control register for synchronized phase triggering. We cleared the phase jitter alarm by writing 1 into the fault clear register.\n\nAfter tuning master phase offsets and enabling DMA register updates, the power converter completed 7000 load transient tests across 18 hours without switching jitter or gate driver overlap."
    },
    # Sample 14: Texas Instruments AM2434 PRU-ICSS EtherCAT frame CRC error
    {
        "raw_asr": "um our t i a m twenty four thirty four industrial gateway dropped fieldbus packets during high speed ethercat industrial communication we captured network frames using wi re shark and tracked physical layer error counters over an ethernet bus tap the programmable real time unit discarded incoming telegrams because frame start delimiter timestamps misaligned with physical layer clocks while the fieldbus firmware lacked clock initializ wait inspect the physical layer timing inside pru underscore ethercat driver module instead configur the real time communication physical layer clock buy adjusting eight wait sixteen clock phase steps instead into the timing configuration register right zero x zero three zero zero into the physical layer base address register right zero x zero one into the media independent interface register wait right zero x zero d instead four deterministic packet framing we cleared the physical layer framing error buy writing one into the link error status register after adjusting physical layer phase settings and optimizing real time unit buffer descriptors the industrial gateway processed eight thousand ethercat cycles across twenty four hours without packet drops or crc faults",
        "refined_text": "Our TI AM2434 industrial gateway dropped fieldbus packets during high-speed EtherCAT industrial communication. We captured network frames using Wireshark and tracked physical layer error counters over an Ethernet bus tap. The programmable real-time unit discarded incoming telegrams because frame start delimiter timestamps misaligned with physical layer clocks while the fieldbus firmware lacked clock initialization, inspecting the physical layer timing inside pru_ethercat_driver module instead.\n\nConfigure the real-time communication physical layer clock by adjusting 16 clock phase steps instead into the timing configuration register. Write 0x0300 into the physical layer base address register. Write 0x0d instead into the media independent interface register for deterministic packet framing. We cleared the physical layer framing error by writing 1 into the link error status register.\n\nAfter adjusting physical layer phase settings and optimizing real-time unit buffer descriptors, the industrial gateway processed 8000 EtherCAT cycles across 24 hours without packet drops or CRC faults."
    },
    # Sample 15: Nordic nRF52833 Radio direction finding antenna switch matrix timing
    {
        "raw_asr": "uh our nordic n r f fifty two eight thirty three locator beacon experienced angle of arrival calculation errors during real time asset tracking we connected an rf spectrum analyzer two the multi antenna array and tracked i q sample timestamps over a u art serial monitor the radio direction finding subsystem produced phase distortion because antenna switching settle times overlapped with i q sample slots while the beacon firmware lacked antenna matrix calibrat wait inspect the switching offset parameters inside df underscore antenna matrix module instead calibrat the radio direction finding antenna switch settling time buy programming one wait two microseconds delay instead into the switch timing register right zero x zero zero one zero into the antenna pattern configuration register right zero x zero two into the direction finding control register wait right zero x zero e instead four clean sample slot isolation we cleared the phase distortion status buy writing one into the n v i c interrupt clear register after programming antenna switch settling delays and aligning sample timing windows the locator beacon tracked five thousand direction finding packets across sixteen hours without phase distortion or tracking errors",
        "refined_text": "Our Nordic nRF52833 locator beacon experienced angle of arrival calculation errors during real-time asset tracking. We connected an RF spectrum analyzer to the multi-antenna array and tracked IQ sample timestamps over a UART serial monitor. The radio direction finding subsystem produced phase distortion because antenna switching settle times overlapped with IQ sample slots while the beacon firmware lacked antenna matrix calibration, inspecting the switching offset parameters inside df_antenna_matrix module instead.\n\nCalibrate the radio direction finding antenna switch settling time by programming 2 microseconds delay instead into the switch timing register. Write 0x0010 into the antenna pattern configuration register. Write 0x0e instead into the direction finding control register for clean sample slot isolation. We cleared the phase distortion status by writing 1 into the NVIC interrupt clear register.\n\nAfter programming antenna switch settling delays and aligning sample timing windows, the locator beacon tracked 5000 direction finding packets across 16 hours without phase distortion or tracking errors."
    },
    # Sample 16: ST STM32MP157 Cortex-M4 RPMsg IPC channel deadlock
    {
        "raw_asr": "basically our stm thirty two m p one fifty seven heterogeneous compute node experienced inter core message buffer starvation during continuous sensor streaming we connected a logic analyzer two the mailbox signaling pins and traced virtio ring buffer states over open o c d the asymmetric processing subsystem halted message exchanges because shared memory virtio buffers filled faster than the remote core acknowledged transfers while the coprocessor firmware lacked buffer allocat wait inspect the ring allocation parameters inside rpmsg underscore channel driver module instead configur the remote processor messaging ring buffer capacity buy allocating thirty two wait sixty four buffers instead into the virtio ring descriptor right zero x one zero zero zero into the mailbox base address register right zero x zero one into the inter core control register wait right zero x zero f instead four bidirectional message passing we cleared the mailbox buffer starvation flag buy writing one into the communication status register after expanding shared virtio ring capacity and tuning free are toss task queues the compute node transferred seven thousand inter core messages across twenty four hours without channel deadlocks or dropped packets",
        "refined_text": "Our STM32MP157 heterogeneous compute node experienced inter-core message buffer starvation during continuous sensor streaming. We connected a logic analyzer to the mailbox signaling pins and traced virtio ring buffer states over OpenOCD. The asymmetric processing subsystem halted message exchanges because shared memory virtio buffers filled faster than the remote core acknowledged transfers while the coprocessor firmware lacked buffer allocation, inspecting the ring allocation parameters inside rpmsg_channel_driver module instead.\n\nConfigure the remote processor messaging ring buffer capacity by allocating 64 buffers instead into the virtio ring descriptor. Write 0x1000 into the mailbox base address register. Write 0x0f instead into the inter-core control register for bidirectional message passing. We cleared the mailbox buffer starvation flag by writing 1 into the communication status register.\n\nAfter expanding shared virtio ring capacity and tuning FreeRTOS task queues, the compute node transferred 7000 inter-core messages across 24 hours without channel deadlocks or dropped packets."
    },
    # Sample 17: Raspberry Pi RP2040 PIO state machine FIFO underflow
    {
        "raw_asr": "um our raspberry pi r p twenty forty video terminal experienced digital visual interface frame tearing during continuous display output we connected a logic analyzer two the differential transition minimized signaling pins and examined d m a channel triggers over a swd probe the programmable input output state machine halted pixel serialisation because the transmit fifo ran empty during scanline blanking intervals while the video driver lacked d m a synchronizat wait inspect the d m a transfer triggers inside pio underscore dvi controller module instead configur the programmable input output state machine d m a pacing buy assigning four wait eight words burst threshold instead into the execution control register right zero x five zero two zero zero zero zero zero into the state machine base address register right zero x zero two into the clock divider register wait right zero x zero seven instead four continuous pixel stream serialization we cleared the transmit underflow alarm buy writing one into the fifo status register after optimizing d m a pacing thresholds and enabling double buffered scanlines the video terminal generated nine thousand display frames across eighteen hours without visual tearing or pixel underflows",
        "refined_text": "Our Raspberry Pi RP2040 video terminal experienced digital visual interface frame tearing during continuous display output. We connected a logic analyzer to the differential transition-minimized signaling pins and examined DMA channel triggers over a SWD probe. The programmable input-output state machine halted pixel serialisation because the transmit FIFO ran empty during scanline blanking intervals while the video driver lacked DMA synchronization, inspecting the DMA transfer triggers inside pio_dvi_controller module instead.\n\nConfigure the programmable input-output state machine DMA pacing by assigning 8 words burst threshold instead into the execution control register. Write 0x50200000 into the state machine base address register. Write 0x07 instead into the clock divider register for continuous pixel stream serialization. We cleared the transmit underflow alarm by writing 1 into the FIFO status register.\n\nAfter optimizing DMA pacing thresholds and enabling double-buffered scanlines, the video terminal generated 9000 display frames across 18 hours without visual tearing or pixel underflows."
    },
    # Sample 18: Infineon CYW20819 Bluetooth LE audio packet framing and PCM audio clock sync
    {
        "raw_asr": "uh our infineon c y w twenty eighty one nine audio headset suffered audio frame stutter during continuous bluetooth low energy voice streaming we connected a digital oscilloscope two the pulse code modulation clock lines and verified sample synchronization over a u art serial bridge the baseband audio processor dropped voice frames because the audio clock drifted relative two incoming packet intervals while the audio subsystem lacked master clock calibrat wait inspect the sample rate divider inside pcm underscore audio manager module instead calibrat the pulse code modulation clock prescaler buy loading sixteen wait thirty two clock divider units instead into the master clock register right zero x zero zero four zero into the audio control register right zero x zero one into the frame synchronization register wait right zero x zero a instead four aligned audio slot transmission we cleared the audio underflow status buy writing one into the interrupt clear register after programming master clock divider settings and reconfiguring pcm frame synchronization the audio headset streamed six thousand voice packets across twelve hours without audio stutter or frame drops",
        "refined_text": "Our Infineon CYW20819 audio headset suffered audio frame stutter during continuous Bluetooth Low Energy voice streaming. We connected a digital oscilloscope to the pulse code modulation clock lines and verified sample synchronization over a UART serial bridge. The baseband audio processor dropped voice frames because the audio clock drifted relative to incoming packet intervals while the audio subsystem lacked master clock calibration, inspecting the sample rate divider inside pcm_audio_manager module instead.\n\nCalibrate the pulse code modulation clock prescaler by loading 32 clock divider units instead into the master clock register. Write 0x0040 into the audio control register. Write 0x0a instead into the frame synchronization register for aligned audio slot transmission. We cleared the audio underflow status by writing 1 into the interrupt clear register.\n\nAfter programming master clock divider settings and reconfiguring PCM frame synchronization, the audio headset streamed 6000 voice packets across 12 hours without audio stutter or frame drops."
    },
    # Sample 19: Renesas RX65N Ethernet EDMAC buffer descriptor chain ring exhaustion
    {
        "raw_asr": "basically our renesas r x sixty five n industrial gateway dropped ethernet frames during burst industrial modbus tcp traffic we monitored packet flows using an ethernet bus tap and traced direct memory access descriptors over open o c d the ethernet direct memory access controller halted frame reception because the receive ring buffer exhausted available descriptors during network bursts while the network driver lacked descriptor ring configur wait inspect the descriptor ring thresholds inside edmac underscore eth controller module instead configur the ethernet controller descriptor ring buy allocating sixteen wait thirty two descriptor buffers instead into the receive ring table right zero x zero zero zero eight zero zero zero zero into the descriptor base address register right zero x zero one into the edmac mode register wait right zero x zero b instead four continuous burst frame processing we cleared the descriptor exhaustion flag buy writing one into the ethernet status register after expanding descriptor ring capacity and enabling frame burst reception the industrial gateway processed eight thousand modbus tcp packets across twenty four hours without dropped frames or descriptor exhaustion errors",
        "refined_text": "Our Renesas RX65N industrial gateway dropped Ethernet frames during burst industrial Modbus TCP traffic. We monitored packet flows using an Ethernet bus tap and traced direct memory access descriptors over OpenOCD. The Ethernet direct memory access controller halted frame reception because the receive ring buffer exhausted available descriptors during network bursts while the network driver lacked descriptor ring configuration, inspecting the descriptor ring thresholds inside edmac_eth_controller module instead.\n\nConfigure the Ethernet controller descriptor ring by allocating 32 descriptor buffers instead into the receive ring table. Write 0x00080000 into the descriptor base address register. Write 0x0b instead into the EDMAC mode register for continuous burst frame processing. We cleared the descriptor exhaustion flag by writing 1 into the Ethernet status register.\n\nAfter expanding descriptor ring capacity and enabling frame burst reception, the industrial gateway processed 8000 Modbus TCP packets across 24 hours without dropped frames or descriptor exhaustion errors."
    },
    # Sample 20: Analog Devices ADuCM4050 ultra-low power sensor node SPI DMA chained descriptor collision
    {
        "raw_asr": "um our analog devices a d u c m forty fifty environmental node suffered sensor data loss during continuous accelerometer burst sampling we captured serial bus waveforms using a logic analyzer and verified channel conversion flags over swd the serial peripheral interface direct memory access controller dropped data packets because primary and alternate descriptor chains collided during ping pong buffer switching while the sensor driver lacked channel arbitrat wait inspect the descriptor switching rules inside spi underscore dma manager module instead configur the direct memory access channel arbitration buy assigning eight wait sixteen transfer cycles instead into the channel priority register right zero x two zero zero zero four zero zero zero into the alternate descriptor base register right zero x zero two into the s p i control register wait right zero x zero c instead four ping pong buffer chaining we cleared the descriptor collision status buy writing one into the d m a error clear register after updating descriptor arbitration thresholds and configuring ping pong buffers the environmental node recorded five thousand sensor readings across sixteen hours without data loss or bus collisions",
        "refined_text": "Our Analog Devices ADuCM4050 environmental node suffered sensor data loss during continuous accelerometer burst sampling. We captured serial bus waveforms using a logic analyzer and verified channel conversion flags over SWD. The serial peripheral interface direct memory access controller dropped data packets because primary and alternate descriptor chains collided during ping-pong buffer switching while the sensor driver lacked channel arbitration, inspecting the descriptor switching rules inside spi_dma_manager module instead.\n\nConfigure the direct memory access channel arbitration by assigning 16 transfer cycles instead into the channel priority register. Write 0x20004000 into the alternate descriptor base register. Write 0x0c instead into the SPI control register for ping-pong buffer chaining. We cleared the descriptor collision status by writing 1 into the DMA error clear register.\n\nAfter updating descriptor arbitration thresholds and configuring ping-pong buffers, the environmental node recorded 5000 sensor readings across 16 hours without data loss or bus collisions."
    }
]

# Validation checks
print(f"Total samples: {len(batch_134)}")

# 1. Leakage check
for idx, s in enumerate(batch_134, 1):
    raw = s["raw_asr"].strip().lower()
    ref = s["refined_text"].strip()
    if raw in eval_raws:
        print(f"ERROR: Sample {idx} raw_asr leaks into eval set!")
        sys.exit(1)
    if ref in eval_refs:
        print(f"ERROR: Sample {idx} refined_text leaks into eval set!")
        sys.exit(1)
print("Leakage check PASSED.")

# 2. Individual pair check & cleaner check
layer_counts = []
tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, s in enumerate(batch_134, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    
    # Cleaner check
    res, status = cleaner.clean_sample(raw, ref)
    if not res:
        print(f"ERROR: Sample {idx} failed cleaner: {status}")
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
    print(f"Sample {idx:02d}: words={w:3d}, noise_layers={nl}, status={status}")

# 3. Batch validation check
ok, reason, stats = validator.validate_batch(
    batch_134,
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
out_path = Path("scratch/subagent_batch_134.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(batch_134, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(batch_134)} samples to {out_path}")
