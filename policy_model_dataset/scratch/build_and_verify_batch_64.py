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

# Define the 20 candidate pairs for Batch 64 (Domain 6: Embedded Systems & Firmware Development)
# Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch_64 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Sample 1: STM32L4 RTC wake-up timer configuration
    {
        "raw_asr": "um configur the real time clock wake up timer buy loading forty eight into the counter register",
        "refined_text": "Configure the real-time clock wake-up timer by loading 48 into the counter register."
    },
    # Sample 2: Nordic nRF52840 USB CDC-ACM endpoint buffer allocation
    {
        "raw_asr": "allocat sixty four bytes four the serial u s b endpoint buffer inside internal s r a m",
        "refined_text": "Allocate 64 bytes for the serial USB endpoint buffer inside internal SRAM."
    },
    # Sample 3: RISC-V GD32VF103 PLIC interrupt priority assignment
    {
        "raw_asr": "uh right priority level three into the p l i c interrupt source register buy using instruction c s r write",
        "refined_text": "Write priority level 3 into the PLIC interrupt source register by using instruction CSR write."
    },
    # Sample 4: NXP RT1060 eMMC controller clock divider adjustment
    {
        "raw_asr": "initializ the embedded storage controller clock divider buy writing sixteen into register zero x four zero zero two",
        "refined_text": "Initialize the embedded storage controller clock divider by writing 16 into register 0x4002."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # Sample 5: ESP32-C3 hardware watchdog timer kick inside FreeRTOS idle hook
    {
        "raw_asr": "um configur the hardware watchdog timer buy writing twenty four into the timeout control register wait write forty eight instead four high system load the free are toss idle hook refreshes the watchdog counter buy writing zero x a five into the service register",
        "refined_text": "Configure the hardware watchdog timer by writing 48 instead into the timeout control register for high system load.\n\nThe FreeRTOS idle hook refreshes the watchdog counter by writing 0xa5 into the service register."
    },
    # Sample 6: Renesas RA6M5 high-speed SPI flash DMA transfer configuration
    {
        "raw_asr": "basically initializ the serial peripheral interface controller buy writing twelve into the baud rate divisor register wait write twenty four instead four flash memory transfers the direct memory access controller manages data transmiss buy reading blocks from the transmit data register",
        "refined_text": "Initialize the serial peripheral interface controller by writing 24 instead into the baud rate divisor register for flash memory transfers.\n\nThe direct memory access controller manages data transmission by reading blocks from the transmit data register."
    },
    # Sample 7: STM32U5 ADC dual-channel regular group conversion over DMA
    {
        "raw_asr": "uh calibrat the analog digital converter offset buy loading sixteen into the calibration factor register wait load thirty two instead four low voltage sensors the converter triggers regular group conversions buy requesting d m a transfers after each channel sample",
        "refined_text": "Calibrate the analog digital converter offset by loading 32 instead into the calibration factor register for low voltage sensors.\n\nThe converter triggers regular group conversions by requesting DMA transfers after each channel sample."
    },
    # Sample 8: SAM E70 Ethernet RMII PHY clock negotiation and speed configuration
    {
        "raw_asr": "configur the physical layer transceiver speed buy writing one into the network status register wait write zero instead four ten megabit fall back mode the ethernet controller clears the transmission error flag buy reading the peripheral status register",
        "refined_text": "Configure the physical layer transceiver speed by writing 0 instead into the network status register for 10 megabit fall back mode.\n\nThe ethernet controller clears the transmission error flag by reading the peripheral status register."
    },
    # Sample 9: RP2040 programmable I/O PIO state machine clock divider setup
    {
        "raw_asr": "um initializ state machine zero on p i o block zero buy writing eight into the clock divider register wait write sixteen instead four slow sensor bus timing the programmable input output state machine synchronizes execution buy polling the input pin status register",
        "refined_text": "Initialize state machine 0 on PIO block 0 by writing 16 instead into the clock divider register for slow sensor bus timing.\n\nThe programmable input output state machine synchronizes execution by polling the input pin status register."
    },
    # Sample 10: TI CC2652R brown-out reset voltage threshold adjustment
    {
        "raw_asr": "uh calibrat the brown out detector voltage threshold buy writing two into the power control register wait write four instead four battery operated sensor nodes the power management unit executes a reset sequence buy asserting the brown out interrupt flag",
        "refined_text": "Calibrate the brown-out detector voltage threshold by writing 4 instead into the power control register for battery operated sensor nodes.\n\nThe power management unit executes a reset sequence by asserting the brown-out interrupt flag."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Sample 11: STM32H7 dual-core inter-processor communication via hardware semaphore and shared SRAM4
    {
        "raw_asr": "our s t m thirty two h seven dual core controller suffered inter core buffer desynchronizat during high throughput messaging between the cortex m seven and cortex m four cores we connected open o c d buy using an st link debug probe and examined shared s r a m four memory where the cortex m four read stale message headers the cortex m four processor read corrupted packets because the hardware semaphore lock routine lacked memory barrier synchronizat wait inspect the inter core communication driver inside ipc underscore buffer dot c instead configur the hardware semaphore two step lock sequence buy writing one into the semaphore lock register wait write two instead four core two channel arbitrat we updated memory protection unit attributes buy writing base address zero x three eight zero zero zero zero zero zero into the m p u base register right zero x zero eight into the region attribute register two set shared memory as non cacheable we cleared the inter core interrupt notification buy writing one into the semaphore interrupt clear register after configuring the hardware semaphore lock sequence and disabling cache allocations on shared memory the dual core controller sustained five thousand inter core message transfers across two cores without buffer overwrite faults or missed interrupt notifications",
        "refined_text": "Our STM32H7 dual core controller suffered inter core buffer desynchronization during high throughput messaging between the Cortex-M7 and Cortex-M4 cores. We connected OpenOCD by using an ST-Link debug probe and examined shared SRAM4 memory where the Cortex-M4 read stale message headers. The Cortex-M4 processor read corrupted packets because the hardware semaphore lock routine lacked memory barrier synchronization, inspecting the inter core communication driver inside ipc_buffer.c instead.\n\nConfigure the hardware semaphore 2-step lock sequence by writing 2 instead into the semaphore lock register for core 2 channel arbitration. We updated memory protection unit attributes by writing base address 0x38000000 into the MPU base register. Write 0x08 into the region attribute register to set shared memory as non-cacheable. We cleared the inter core interrupt notification by writing 1 into the semaphore interrupt clear register.\n\nAfter configuring the hardware semaphore lock sequence and disabling cache allocations on shared memory, the dual core controller sustained 5000 inter core message transfers across 2 cores without buffer overwrite faults or missed interrupt notifications."
    },
    # Sample 12: Nordic nRF5340 dual-core IPC message buffer synchronization
    {
        "raw_asr": "our n r f fifty three forty wireless gateway dropped bluetooth packets during inter processor message exchanges between the application core and network core we connected a segger j link debug probe and inspected the inter processor communication registers over s w d the network core missed incoming transmission requests because the application core cleared the channel status flag before the network core read the message payload wait inspect the inter core transport driver inside ipc underscore trans dot c instead configur the i p c receive channel buy writing zero into the channel configuration register wait write one instead four bidirectional signaling configur the shared message buffer address buy writing zero x two zero zero zero four zero zero zero into the transmit address register we enabled channel interrupts buy writing one into the receive interrupt enable register after updating the i p c channel mask and setting dedicated payload pointers the wireless gateway transferred ten thousand data packets across two cores without channel lockups or dropped bluetooth packets",
        "refined_text": "Our nRF5340 wireless gateway dropped Bluetooth packets during inter processor message exchanges between the application core and network core. We connected a SEGGER J-Link debug probe and inspected the inter processor communication registers over SWD. The network core missed incoming transmission requests because the application core cleared the channel status flag before the network core read the message payload, inspecting the inter core transport driver inside ipc_trans.c instead.\n\nConfigure the IPC receive channel by writing 1 instead into the channel configuration register for bidirectional signaling. Configure the shared message buffer address by writing 0x20004000 into the transmit address register. We enabled channel interrupts by writing 1 into the receive interrupt enable register.\n\nAfter updating the IPC channel mask and setting dedicated payload pointers, the wireless gateway transferred 10000 data packets across 2 cores without channel lockups or dropped Bluetooth packets."
    },
    # Sample 13: ESP32-S2 USB HID composite device descriptor enumeration stall
    {
        "raw_asr": "our esp thirty two s two composite device failed u s b enumerat on the host workstation during peripheral initialization we captured control packets buy using wi re shark and observed repeated stall handshakes on control endpoint zero the host controller timed out because the device descriptor reported sixty four bytes but the hardware endpoint buffer was allocated thirty two bytes wait inspect the peripheral configuration inside usb underscore composite dot c instead configur the endpoint zero maximum packet size buy writing thirty two into the descriptor table wait write sixty four instead four standard full speed transfers we adjusted the receive f i f o depth buy writing one hundred twenty eight into the f i f o allocation register right sixteen into the control endpoint interrupt enable register two detect setup transaction packets after resizing the endpoint buffers and updating descriptor parameters the composite device enumerated cleanly across fifty connection cycles without bus resets or descriptor timeout errors",
        "refined_text": "Our ESP32-S2 composite device failed USB enumeration on the host workstation during peripheral initialization. We captured control packets by using Wireshark and observed repeated STALL handshakes on control endpoint 0. The host controller timed out because the device descriptor reported 64 bytes but the hardware endpoint buffer was allocated 32 bytes, inspecting the peripheral configuration inside usb_composite.c instead.\n\nConfigure the endpoint 0 maximum packet size by writing 64 instead into the descriptor table for standard full speed transfers. We adjusted the receive FIFO depth by writing 128 into the FIFO allocation register. Write 16 into the control endpoint interrupt enable register to detect setup transaction packets.\n\nAfter resizing the endpoint buffers and updating descriptor parameters, the composite device enumerated cleanly across 50 connection cycles without bus resets or descriptor timeout errors."
    },
    # Sample 14: NXP LPC55S69 TrustZone-M SAU peripheral partition violation
    {
        "raw_asr": "our l p c fifty five s sixty nine industrial controller trapped into a secure fault exception when non secure application code invoked hardware acceleration routines we connected a segger j link probe and inspected the secure fault status register register zero x e zero zero zero e d e four flagged an attribution unit violation because crypto peripheral memory was configured as secure access only wait inspect the security attribution configuration inside tz underscore partition dot c instead configur the security attribution unit region two buy writing base address zero x four zero zero two zero zero zero zero into the region base address register wait mark the partition as non secure callable instead four peripheral stub functions right zero x zero one into the attribution unit control register two enable memory partition rules we cleared the secure fault flag buy writing one into the fault clear register after repartitioning peripheral address spaces and enabling non secure callable gates the controller executed two thousand crypto operations across non secure threads without bus aborts or memory fault traps",
        "refined_text": "Our LPC55S69 industrial controller trapped into a secure fault exception when non secure application code invoked hardware acceleration routines. We connected a SEGGER J-Link probe and inspected the Secure Fault Status Register. Register 0xe000ede4 flagged an attribution unit violation because crypto peripheral memory was configured as secure access only, inspecting the security attribution configuration inside tz_partition.c instead.\n\nConfigure the Security Attribution Unit region 2 by writing base address 0x40020000 into the region base address register, marking the partition as non secure callable instead for peripheral stub functions. Write 0x01 into the attribution unit control register to enable memory partition rules. We cleared the secure fault flag by writing 1 into the fault clear register.\n\nAfter repartitioning peripheral address spaces and enabling non secure callable gates, the controller executed 2000 crypto operations across non secure threads without bus aborts or memory fault traps."
    },
    # Sample 15: PIC32MZ CAN acceptance filter mask and FIFO buffer allocation
    {
        "raw_asr": "our p i c thirty two m z automotive unit dropped can frames during high speed sensor bursts on the vehicle powertrain bus we connected a logic analyzer two the transceiver lines and captured error passive flags across the controller area network the can controller discarded telemetry messages because the message filter mask rejected eleven bit standard identifiers during bus arbitrat wait inspect the filter configuration inside can underscore filter dot c instead configur the can acceptance filter mask zero buy writing zero x zero seven f zero into the mask register wait write zero x zero seven f f instead four exact identifier matching we allocated receive buffers buy writing sixteen into the f i f o size control register right zero x zero one into the module interrupt enable register two process incoming frame alerts after updating the filter mask and expanding receive buffer allocation the automotive unit processed eight thousand can messages without dropped frames or f i f o overrun interrupts",
        "refined_text": "Our PIC32MZ automotive unit dropped CAN frames during high speed sensor bursts on the vehicle powertrain bus. We connected a logic analyzer to the transceiver lines and captured error passive flags across the controller area network. The CAN controller discarded telemetry messages because the message filter mask rejected 11-bit standard identifiers during bus arbitration, inspecting the filter configuration inside can_filter.c instead.\n\nConfigure the CAN acceptance filter mask 0 by writing 0x07ff instead into the mask register for exact identifier matching. We allocated receive buffers by writing 16 into the FIFO size control register. Write 0x01 into the module interrupt enable register to process incoming frame alerts.\n\nAfter updating the filter mask and expanding receive buffer allocation, the automotive unit processed 8000 CAN messages without dropped frames or FIFO overrun interrupts."
    },
    # Sample 16: SiFive FE310 RISC-V CLINT timer prescaler and interrupt interval
    {
        "raw_asr": "our r i s c v industrial node suffered severe timer drift and task starvation after switching the system clock source two an external crystal oscillator we connected open o c d over the jtag interface and dumped the core local interrupt controller status registers the machine timer compare register failed two generate interrupts because the firmware omitted timer prescaler updates during the phase locked loop clock transition wait inspect the clock initialization sequence inside clock underscore init dot c instead configur the core local interrupt controller timer compare register buy writing one thousand into the compare register wait write two thousand instead four ten millisecond scheduler ticks we configured the core clock prescaler buy writing sixteen into the clock divider register right one into the machine interrupt enable register two unmask timer interrupts after calibrating the timer compare step and stabilizing clock division ratios the r i s c v node executed ten thousand scheduler ticks across sixteen tasks without timing drift or task preemption faults",
        "refined_text": "Our RISC-V industrial node suffered severe timer drift and task starvation after switching the system clock source to an external crystal oscillator. We connected OpenOCD over the JTAG interface and dumped the Core Local Interrupt Controller status registers. The machine timer compare register failed to generate interrupts because the firmware omitted timer prescaler updates during the phase locked loop clock transition, inspecting the clock initialization sequence inside clock_init.c instead.\n\nConfigure the Core Local Interrupt Controller timer compare register by writing 2000 instead into the compare register for 10 millisecond scheduler ticks. We configured the core clock prescaler by writing 16 into the clock divider register. Write 1 into the machine interrupt enable register to unmask timer interrupts.\n\nAfter calibrating the timer compare step and stabilizing clock division ratios, the RISC-V node executed 10000 scheduler ticks across 16 tasks without timing drift or task preemption faults."
    },
    # Sample 17: STM32F7 SDRAM framebuffer cache coherency with DMA2D Chrom-ART
    {
        "raw_asr": "our s t m thirty two f seven graphical terminal suffered visual tearing and corrupted display scan lines during high frame rate rendering on external s d r a m we attached an st link debug probe and analyzed the memory protection unit registers over s w d the display controller displayed stale pixel data because the c p u held modified frame buffer lines in the l one data cache while the hardware graphics accelerator read unmodified external memory wait inspect the display rendering pipeline inside display underscore dma two d dot c instead configur the memory protection unit region three buy writing base address zero x c zero zero zero zero zero zero zero into the region base register wait configur write through caching instead of write back four external memory buffers right zero x one zero into the region attribute register two set buffer boundaries we executed cache clean instructions before triggering d m a transfers after enforcing write through cache policies and executing cache maintenance the display controller rendered sixty frames per second across twenty four hours without image tearing or frame buffer corrupt",
        "refined_text": "Our STM32F7 graphical terminal suffered visual tearing and corrupted display scan lines during high frame rate rendering on external SDRAM. We attached an ST-Link debug probe and analyzed the memory protection unit registers over SWD. The display controller displayed stale pixel data because the CPU held modified frame buffer lines in the L1 data cache while the hardware graphics accelerator read unmodified external memory, inspecting the display rendering pipeline inside display_dma2d.c instead.\n\nConfigure the memory protection unit region 3 by writing base address 0xc0000000 into the region base register, configuring write through caching instead of write back for external memory buffers. Write 0x10 into the region attribute register to set buffer boundaries. We executed cache clean instructions before triggering DMA transfers.\n\nAfter enforcing write through cache policies and executing cache maintenance, the display controller rendered 60 frames per second across 24 hours without image tearing or frame buffer corruption."
    },
    # Sample 18: SAM E54 QSPI high-frequency read dummy cycles and sample delay
    {
        "raw_asr": "our sam e fifty four gateway node suffered flash read data corrupt during high speed telemetry reads from external flash memory we connected an oscilloscope two the serial clock and data lines and discovered that data setup times collapsed during one hundred twenty megahertz clock bursts the microcontroller read corrupted calibration tables because the q s p i controller sampled data lines before signals stabilized wait inspect the memory controller driver inside qspi underscore driver dot c instead configur the q s p i read dummy cycles buy loading six into the memory control register wait load ten instead four high frequency read bursts right zero x zero three into the receive sample delay register two calibrate the capture phase we verified bus timing buy polling the transfer ready bit in the peripheral status register after tuning read dummy cycles and applying delay line offsets the gateway read fifty megabytes of telemetry data across one hundred benchmark runs without memory corrupt or c r c errors",
        "refined_text": "Our SAM E54 gateway node suffered flash read data corruption during high speed telemetry reads from external flash memory. We connected an oscilloscope to the serial clock and data lines and discovered that data setup times collapsed during 120 megahertz clock bursts. The microcontroller read corrupted calibration tables because the QSPI controller sampled data lines before signals stabilized, inspecting the memory controller driver inside qspi_driver.c instead.\n\nConfigure the QSPI read dummy cycles by loading 10 instead into the memory control register for high frequency read bursts. Write 0x03 into the receive sample delay register to calibrate the capture phase. We verified bus timing by polling the transfer ready bit in the peripheral status register.\n\nAfter tuning read dummy cycles and applying delay line offsets, the gateway read 50 megabytes of telemetry data across 100 benchmark runs without memory corruption or CRC errors."
    },
    # Sample 19: Renesas RX65N FreeRTOS PMBus mutex priority inheritance
    {
        "raw_asr": "our industrial power distribution monitor suffered task lockups during multi channel voltage telemetry polling over p m bus we connected an on chip debugger and dumped the free are toss task status table over jtag the high priority overcurrent protection thread starved because the low priority telemetry task held the shared bus mutex while medium priority communication tasks preempted execution wait inspect the task synchronization logic inside pmbus underscore monitor dot c instead configur the telemetry worker task priority buy assigning priority four wait assign priority eight instead four balanced scheduler preemption we enabled priority inheritance on the shared bus mutex buy writing one into the mutex attribute structure configur the mutex acquisition timeout buy loading two hundred into the timeout parameter after converting the bus locking mechanism two priority inheritance mutexes the monitor acquired ten thousand telemetry packets across eight power rails without task starvation or watchdog reset timeouts",
        "refined_text": "Our industrial power distribution monitor suffered task lockups during multi channel voltage telemetry polling over PMBus. We connected an on chip debugger and dumped the FreeRTOS task status table over JTAG. The high priority overcurrent protection thread starved because the low priority telemetry task held the shared bus mutex while medium priority communication tasks preempted execution, inspecting the task synchronization logic inside pmbus_monitor.c instead.\n\nConfigure the telemetry worker task priority by assigning priority 8 instead for balanced scheduler preemption. We enabled priority inheritance on the shared bus mutex by writing 1 into the mutex attribute structure. Configure the mutex acquisition timeout by loading 200 into the timeout parameter.\n\nAfter converting the bus locking mechanism to priority inheritance mutexes, the monitor acquired 10000 telemetry packets across 8 power rails without task starvation or watchdog reset timeouts."
    },
    # Sample 20: TI MSP432 low-power DMA UART circular ring buffer packet framing
    {
        "raw_asr": "our battery powered sensor node suffered serial framing errors and packet corrupt during wake up transitions from deep sleep mode we attached a logic analyzer two the receive line and observed corrupted start bits on incoming telemetry packets the microcontroller corrupted incoming packets because the u art clock source was unstable when the d m a controller triggered buffer transfers upon wake up wait inspect the power transition logic inside uart underscore lpm dot c instead configur the wake up glitch filter buy writing four into the input filter register wait write eight instead four noisy serial lines configur the circular d m a buffer buy loading two hundred fifty six into the transfer count register right zero x zero one into the low power clock request register two hold active clocks after configuring the glitch filter and expanding the circular receive buffer the sensor node processed five thousand incoming packets across one hundred sleep cycles without framing errors or buffer corrupt",
        "refined_text": "Our battery powered sensor node suffered serial framing errors and packet corruption during wake up transitions from deep sleep mode. We attached a logic analyzer to the receive line and observed corrupted start bits on incoming telemetry packets. The microcontroller corrupted incoming packets because the UART clock source was unstable when the DMA controller triggered buffer transfers upon wake up, inspecting the power transition logic inside uart_lpm.c instead.\n\nConfigure the wake up glitch filter by writing 8 instead into the input filter register for noisy serial lines. Configure the circular DMA buffer by loading 256 into the transfer count register. Write 0x01 into the low power clock request register to hold active clocks.\n\nAfter configuring the glitch filter and expanding the circular receive buffer, the sensor node processed 5000 incoming packets across 100 sleep cycles without framing errors or buffer corruption."
    }
]

# Validation checks
print(f"Total samples: {len(batch_64)}")
assert len(batch_64) == 20, f"Expected 20 samples, got {len(batch_64)}"

tier_counts = {"short": 0, "medium": 0, "long": 0}
clean_passed = 0
val_passed = 0

for idx, pair in enumerate(batch_64):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]
    
    # Eval set leakage check
    if raw.strip().lower() in eval_raws:
        raise ValueError(f"Sample {idx+1} raw_asr leaks from eval set!")
    if ref.strip() in eval_refs:
        raise ValueError(f"Sample {idx+1} refined_text leaks from eval set!")

    # Validator check
    v_ok, v_reason = validator.validate_pair(pair)
    if not v_ok:
        raise ValueError(f"Sample {idx+1} failed validate_pair: {v_reason}")
    val_passed += 1

    # Cleaner check
    c_res, c_reason = cleaner.clean_sample(raw, ref)
    if not c_res or c_reason != "kept":
        raise ValueError(f"Sample {idx+1} failed clean_sample: {c_reason}")
    clean_passed += 1

    words = len(ref.split())
    if words < 25:
        tier_counts["short"] += 1
    elif words < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1

print(f"Validation passed: {val_passed}/20")
print(f"Cleaner passed: {clean_passed}/20")
print(f"Tier counts: {tier_counts}")

# Validate batch
b_ok, b_reason, b_tiers = validator.validate_batch(batch_64, min_short=4, min_medium=6, min_long=10)
if not b_ok:
    raise ValueError(f"Batch validation failed: {b_reason}")
print(f"Batch validation: {b_ok} - {b_reason}")

# Save to scratch/subagent_batch_64.json
out_file = Path("scratch/subagent_batch_64.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(batch_64, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {len(batch_64)} verified samples to {out_file}")
