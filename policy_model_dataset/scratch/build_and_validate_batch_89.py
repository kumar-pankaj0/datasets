import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.append("code")
import validator
import cleaner

# 1. Load eval set for leakage check
eval_file = Path("sft_eval.json")
eval_data = []
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
eval_raws = {e.get("raw_asr", e.get("input", "")).strip().lower() for e in eval_data}
eval_refs = {e.get("refined_text", e.get("output", "")).strip() for e in eval_data}

batch_89 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Sample 1: STM32H753 FMC memory bus controller
    {
        "raw_asr": "configur the flexible memory controller memory bank timing buy writing twelve into the static memory read timing register",
        "refined_text": "Configure the flexible memory controller memory bank timing by writing 12 into the static memory read timing register."
    },
    # Sample 2: NXP RT1060 FlexSPI octal flash controller
    {
        "raw_asr": "um initializ the serial peripheral interface root clock buy writing zero x two zero into the clock divider register",
        "refined_text": "Initialize the serial peripheral interface root clock by writing 0x20 into the clock divider register."
    },
    # Sample 3: Nordic nRF52840 PPI peripheral interconnect
    {
        "raw_asr": "uh terminat the hardware event routing channel buy clearing channel bit four inside the peripheral interconnect enable register",
        "refined_text": "Terminate the hardware event routing channel by clearing channel bit 4 inside the peripheral interconnect enable register."
    },
    # Sample 4: Espressif ESP32-S3 TWAI filter mask
    {
        "raw_asr": "calibrat the automotive bus filter mask buy writing thirty two into the message identifier acceptance register",
        "refined_text": "Calibrate the automotive bus filter mask by writing 32 into the message identifier acceptance register."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # Sample 5: Texas Instruments CC2652R Sub-1 GHz RF prescaler
    {
        "raw_asr": "configur the radio frequency timer prescaler buy setting eight wait set sixteen clock cycles instead into the radio timer control register four wireless frame parsing inside free are toss the radio sequencer captures incoming packet headers buy streaming sixty four bytes across dual direct memory access buffers",
        "refined_text": "Configure the radio frequency timer prescaler by setting 16 clock cycles instead into the radio timer control register for wireless frame parsing inside FreeRTOS.\n\nThe radio sequencer captures incoming packet headers by streaming 64 bytes across dual direct memory access buffers."
    },
    # Sample 6: STMicroelectronics STM32F767 LTDC display controller & DMA2D
    {
        "raw_asr": "uh initializ the liquid crystal display controller layer format buy setting sixteen wait right thirty two bits instead into the display pixel format register four graphical interface rendering the graphics accelerator engine blends bitmap textures buy executing color conversion across four display buffer lines",
        "refined_text": "Initialize the liquid crystal display controller layer format by setting 32 bits instead into the display pixel format register for graphical interface rendering.\n\nThe graphics accelerator engine blends bitmap textures by executing color conversion across 4 display buffer lines."
    },
    # Sample 7: Infineon AURIX TC397 CAN-FD message buffer
    {
        "raw_asr": "um allocat the flexible data rate controller transmit buffer buy writing zero x one zero wait right zero x two zero into the transmission control register instead four chassis domain communications the automotive communication controller transmits diagnostic telemetry buy routing twenty four message frames into the hardware queue",
        "refined_text": "Allocate the flexible data rate controller transmit buffer by writing 0x20 into the transmission control register instead for chassis domain communications.\n\nThe automotive communication controller transmits diagnostic telemetry by routing 24 message frames into the hardware queue."
    },
    # Sample 8: Silicon Labs EFR32BG22 LEUART baud rate generator
    {
        "raw_asr": "calibrat the low energy asynchronous receiver transmitter baud rate generator buy loading sixty four wait load one hundred twenty eight clock divisions instead into the fractional divider register four peripheral sensor logging the low power serial transceiver processes sensor telemetry buy servicing character interrupts across eight ring buffer blocks",
        "refined_text": "Calibrate the low energy asynchronous receiver transmitter baud rate generator by loading 128 clock divisions instead into the fractional divider register for peripheral sensor logging.\n\nThe low power serial transceiver processes sensor telemetry by servicing character interrupts across 8 ring buffer blocks."
    },
    # Sample 9: Renesas RX65N Dual-Bank Flash Swap Controller
    {
        "raw_asr": "synchronizat the dual bank flash memory controller buy selecting bank zero wait select bank one instead into the bank swap control register four firmware image swapping the bootloader firmware validates flash integrity buy calculating cryptographic checksums across sixteen flash blocks",
        "refined_text": "Synchronize the dual-bank flash memory controller by selecting bank 1 instead into the bank swap control register for firmware image swapping.\n\nThe bootloader firmware validates flash integrity by calculating cryptographic checksums across 16 flash blocks."
    },
    # Sample 10: Analog Devices MAX78000 CNN hardware accelerator
    {
        "raw_asr": "terminat the neural network inference stall buy writing zero x four zero wait right zero x eight zero into the layer execution control register instead four acoustic wake word classification the hardware convolution engine streams audio spectrogram tensors buy filling sixty four word circular queues across four processing layers",
        "refined_text": "Terminate the neural network inference stall by writing 0x80 into the layer execution control register instead for acoustic wake word classification.\n\nThe hardware convolution engine streams audio spectrogram tensors by filling 64 word circular queues across 4 processing layers."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Sample 11: STM32H753 Dual-Core Cortex-M7/M4 Shared RAM AXI Bus Contention
    {
        "raw_asr": "our s t m thirty two h seven five three dual core board encountered packet corruption during high throughput ethernet frame transmiss inside the industrial communication gateway we connected a segger j link probe and analyzed direct memory access execution traces inside g d b the direct memory access controller produced frame checksum errors because the cortex m seven data cache held stale memory buffers while the ethernet descriptor ring lacked memory protection configur wait inspect the memory attributes inside ethernet underscore dma dot c instead configur the shared direct memory access buffer buy setting uncacheable memory attributes right zero x zero four wait right zero x zero eight into the memory protection region attribute register instead two enforce buffer coherency we cleared the transmission error flag buy writing one into the status clear register after updating region attribute bits and clearing pending interrupt flags the dual core processor transferred five thousand network frames across twelve hours without memory corruption or dropped ethernet packets",
        "refined_text": "Our STM32H753 dual-core board encountered packet corruption during high-throughput Ethernet frame transmission inside the industrial communication gateway. We connected a SEGGER J-Link probe and analyzed direct memory access execution traces inside GDB. The direct memory access controller produced frame checksum errors because the Cortex-M7 data cache held stale memory buffers while the Ethernet descriptor ring lacked memory protection configuration, inspecting the memory attributes inside ethernet_dma.c instead.\n\nConfigure the shared direct memory access buffer by setting uncacheable memory attributes. Write 0x08 into the memory protection region attribute register instead to enforce buffer coherency. We cleared the transmission error flag by writing 1 into the status clear register.\n\nAfter updating region attribute bits and clearing pending interrupt flags, the dual-core processor transferred 5000 network frames across 12 hours without memory corruption or dropped Ethernet packets."
    },
    # Sample 12: NXP RT1060 FlexSPI Octal Flash Timing Skew & Read Jitter
    {
        "raw_asr": "our n x p r t ten sixty crossover processor generated read verification errors during execute in place flash streaming inside the automated machine controller we attached open o c d over the serial wire debug connection and monitored bus transactions inside g d b the flexible serial peripheral interface controller returned corrupted instruction words because high temperature drift shifted read data strobe timing while the octal flash driver lacked delay line calibrat wait inspect the timing setup inside flexspi underscore flash dot c instead calibrat the octal flash read delay cell buy setting internal loopback strobe delays right zero x zero two wait right zero x zero six into the delay tap control register instead two align read clock edges we cleared the flash controller read error flag buy writing one into the interrupt status register after adjusting delay tap parameters and clearing error status bits the crossover processor executed four thousand instruction blocks across sixteen hours without read verification failures or execute in place pipeline stalls",
        "refined_text": "Our NXP RT1060 crossover processor generated read verification errors during execute-in-place flash streaming inside the automated machine controller. We attached OpenOCD over the serial wire debug connection and monitored bus transactions inside GDB. The flexible serial peripheral interface controller returned corrupted instruction words because high-temperature drift shifted read data strobe timing while the octal flash driver lacked delay line calibration, inspecting the timing setup inside flexspi_flash.c instead.\n\nCalibrate the octal flash read delay cell by setting internal loopback strobe delays. Write 0x06 into the delay tap control register instead to align read clock edges. We cleared the flash controller read error flag by writing 1 into the interrupt status register.\n\nAfter adjusting delay tap parameters and clearing error status bits, the crossover processor executed 4000 instruction blocks across 16 hours without read verification failures or execute-in-place pipeline stalls."
    },
    # Sample 13: Nordic nRF52840 USB CDC-ACM Endpoint Stall & Buffer Wrap
    {
        "raw_asr": "our n r f fifty two eight forty wireless dongle experienced serial buffer loss during continuous sensor streaming inside the health telemetry hub we connected wi re shark two monitor packet streams and captured core registers using a segger j link probe inside free are toss the universal serial bus peripheral triggered an endpoint stall because incoming bulk packets overwhelmed intermediate ring buffers while the usb driver lacked circular buffer communicat wait inspect the endpoint configuration inside usb underscore cdc dot c instead configur the bulk transfer ring buffer buy setting thirty two wait configure sixty four bytes instead into the endpoint maximum packet size register right zero x zero one wait right zero x zero two into the endpoint status register instead two clear the stall condition we cleared the endpoint interrupt request flag buy writing one into the event register after updating endpoint buffer sizing and clearing stall flags the wireless dongle streamed six thousand sensor frames across eighteen hours without packet dropouts or serial communication stalls",
        "refined_text": "Our nRF52840 wireless dongle experienced serial buffer loss during continuous sensor streaming inside the health telemetry hub. We connected Wireshark to monitor packet streams and captured core registers using a SEGGER J-Link probe inside FreeRTOS. The universal serial bus peripheral triggered an endpoint stall because incoming bulk packets overwhelmed intermediate ring buffers while the USB driver lacked circular buffer communication, inspecting the endpoint configuration inside usb_cdc.c instead.\n\nConfigure the bulk transfer ring buffer by setting 64 bytes instead into the endpoint maximum packet size register. Write 0x02 into the endpoint status register instead to clear the stall condition. We cleared the endpoint interrupt request flag by writing 1 into the event register.\n\nAfter updating endpoint buffer sizing and clearing stall flags, the wireless dongle streamed 6000 sensor frames across 18 hours without packet dropouts or serial communication stalls."
    },
    # Sample 14: Espressif ESP32-S3 TWAI / CAN Bus Error Passive & Bit Stuffing Fault
    {
        "raw_asr": "our e s p thirty two s three node entered an error passive state during high speed automotive bus transmiss inside the vehicle gateway we connected a logic analyzer two the two wire automotive interface lines and inspected transmission error counters inside g d b the controller area network controller accumulated bit stuffing errors because cable impedance mismatches corrupted arbitration bits while the interface driver lacked error recovery arbitrat wait inspect the bus timing initialization inside twai underscore driver dot c instead configur the nominal bit timing registers buy setting time segment one right zero x zero four wait right zero x zero eight into the bus timing register instead two widen the sample point window we cleared the bus error flag buy writing one into the command register after updating timing registers and clearing pending error flags the node delivered eight thousand telemetry frames across twenty four hours without entering bus off state or dropping packets",
        "refined_text": "Our ESP32-S3 node entered an error-passive state during high-speed automotive bus transmission inside the vehicle gateway. We connected a logic analyzer to the two-wire automotive interface lines and inspected transmission error counters inside GDB. The controller area network controller accumulated bit stuffing errors because cable impedance mismatches corrupted arbitration bits while the interface driver lacked error recovery arbitration, inspecting the bus timing initialization inside twai_driver.c instead.\n\nConfigure the nominal bit timing registers by setting time segment 1. Write 0x08 into the bus timing register instead to widen the sample point window. We cleared the bus error flag by writing 1 into the command register.\n\nAfter updating timing registers and clearing pending error flags, the node delivered 8000 telemetry frames across 24 hours without entering bus-off state or dropping packets."
    },
    # Sample 15: Raspberry Pi RP2350 Hazard3 RISC-V Core & HSTX Bus Underrun
    {
        "raw_asr": "our r p twenty three fifty microcontroller experienced display tearing during high speed serial transmit video streaming inside the digital signage panel we monitored differential data lines using a logic analyzer and attached open o c d two examine core execution registers inside g d b the high speed serial transmit peripheral triggered a fifo underrun because the r i s c v core stalled direct memory access servicing while the display driver lacked burst transfer allocat wait inspect the burst configuration inside hstx underscore pio dot c instead configur the direct memory access burst size buy setting four wait set eight burst transfers instead into the channel control register right zero x zero two wait right zero x zero four into the output crossbar control register instead two balance fifo bandwidth we cleared the transmitter underrun flag buy writing one into the status register after tuning burst parameters and resetting channel control registers the microcontroller transmitted seven thousand video frames across fourteen hours without pixel artifacts or fifo underruns",
        "refined_text": "Our RP2350 microcontroller experienced display tearing during high-speed serial transmit video streaming inside the digital signage panel. We monitored differential data lines using a logic analyzer and attached OpenOCD to examine core execution registers inside GDB. The high-speed serial transmit peripheral triggered a FIFO underrun because the RISC-V core stalled direct memory access servicing while the display driver lacked burst transfer allocation, inspecting the burst configuration inside hstx_pio.c instead.\n\nConfigure the direct memory access burst size by setting 8 burst transfers instead into the channel control register. Write 0x04 into the output crossbar control register instead to balance FIFO bandwidth. We cleared the transmitter underrun flag by writing 1 into the status register.\n\nAfter tuning burst parameters and resetting channel control registers, the microcontroller transmitted 7000 video frames across 14 hours without pixel artifacts or FIFO underruns."
    },
    # Sample 16: Microchip SAMV71 Aerospace CAN-FD Mailbox Priority Inversion
    {
        "raw_asr": "our s a m v seventy one flight avionics controller experienced priority inversion during high throughput flight bus telemetry inside the actuator management unit we connected a segger j link probe and analyzed message scheduling traces inside free are toss the modular controller area network controller delayed emergency braking frames because low priority sensor telemetry occupied dedicated transmit mailboxes while the message queue driver lacked priority arbitrat wait inspect the mailbox scheduling logic inside mcan underscore queue dot c instead configur the hardware transmission queue buy setting priority based mailbox scheduling right zero x zero four wait right zero x zero eight into the transmit priority register instead two grant preemption two emergency identifiers we cleared the transmit cancellation finished flag buy writing one into the interrupt status register after updating transmit priority masks and reordering queue descriptors the avionics controller transmitted nine thousand command packets across twenty hours without priority inversion or delayed actuator messages",
        "refined_text": "Our SAMV71 flight avionics controller experienced priority inversion during high-throughput flight bus telemetry inside the actuator management unit. We connected a SEGGER J-Link probe and analyzed message scheduling traces inside FreeRTOS. The modular controller area network controller delayed emergency braking frames because low-priority sensor telemetry occupied dedicated transmit mailboxes while the message queue driver lacked priority arbitration, inspecting the mailbox scheduling logic inside mcan_queue.c instead.\n\nConfigure the hardware transmission queue by setting priority-based mailbox scheduling. Write 0x08 into the transmit priority register instead to grant preemption to emergency identifiers. We cleared the transmit cancellation finished flag by writing 1 into the interrupt status register.\n\nAfter updating transmit priority masks and reordering queue descriptors, the avionics controller transmitted 9000 command packets across 20 hours without priority inversion or delayed actuator messages."
    },
    # Sample 17: Texas Instruments TM4C1294 Integrated Ethernet MAC/PHY FIFO Overrun
    {
        "raw_asr": "our t m four c twelve ninety four industrial gateway dropped modbus transmission frames during network burst polling inside the electrical substation hub we connected wi re shark two capture incoming ethernet frames and monitored core memory registers using open o c d inside g d b the ethernet media access controller raised a receiver fifo overflow interrupt because rapid packet bursts exhausted the direct memory access receive descriptor ring while the network driver lacked ring buffer configur wait inspect the descriptor initialization inside emac underscore ring dot c instead configur the receive descriptor chain buy setting thirty two wait configure sixty four descriptor slots instead into the receive buffer size register right zero x zero one wait right zero x zero two into the bus mode register instead two increase dma burst throughput we cleared the receiver overflow flag buy writing one into the interrupt status register after increasing descriptor queue depth and resetting bus mode parameters the gateway received five thousand industrial packets across ten hours without frame dropouts or fifo buffer overruns",
        "refined_text": "Our TM4C1294 industrial gateway dropped Modbus transmission frames during network burst polling inside the electrical substation hub. We connected Wireshark to capture incoming Ethernet frames and monitored core memory registers using OpenOCD inside GDB. The Ethernet media access controller raised a receiver FIFO overflow interrupt because rapid packet bursts exhausted the direct memory access receive descriptor ring while the network driver lacked ring buffer configuration, inspecting the descriptor initialization inside emac_ring.c instead.\n\nConfigure the receive descriptor chain by setting 64 descriptor slots instead into the receive buffer size register. Write 0x02 into the bus mode register instead to increase DMA burst throughput. We cleared the receiver overflow flag by writing 1 into the interrupt status register.\n\nAfter increasing descriptor queue depth and resetting bus mode parameters, the gateway received 5000 industrial packets across 10 hours without frame dropouts or FIFO buffer overruns."
    },
    # Sample 18: WCH CH32V307 QingKe RISC-V USB High-Speed PHY DMA Alignment Trap
    {
        "raw_asr": "our c h thirty two v three zero seven microcontroller halted execution during high speed usb telemetry acquisition inside the lab instrument interface we connected a logic analyzer two the physical layer signals and inspected core trap registers inside g d b the r i s c v core raised an unaligned memory access exception because direct memory access endpoint buffers crossed non four byte aligned boundary addresses while the usb high speed driver lacked buffer alignment initializ wait inspect the buffer allocation routine inside usbhs underscore dma dot c instead configur the endpoint direct memory access buffer buy aligning data pointers on four byte boundaries right zero x one zero wait right zero x two zero into the endpoint control register instead two enable high speed burst transfers we cleared the trap status flag buy writing one into the machine status register after enforcing four byte memory alignment and updating endpoint control registers the microcontroller processed six thousand measurement frames across sixteen hours without processor traps or usb transfer aborts",
        "refined_text": "Our CH32V307 microcontroller halted execution during high-speed USB telemetry acquisition inside the lab instrument interface. We connected a logic analyzer to the physical layer signals and inspected core trap registers inside GDB. The RISC-V core raised an unaligned memory access exception because direct memory access endpoint buffers crossed non-four-byte-aligned boundary addresses while the USB high-speed driver lacked buffer alignment initialization, inspecting the buffer allocation routine inside usbhs_dma.c instead.\n\nConfigure the endpoint direct memory access buffer by aligning data pointers on 4 byte boundaries. Write 0x20 into the endpoint control register instead to enable high-speed burst transfers. We cleared the trap status flag by writing 1 into the machine status register.\n\nAfter enforcing 4 byte memory alignment and updating endpoint control registers, the microcontroller processed 6000 measurement frames across 16 hours without processor traps or USB transfer aborts."
    },
    # Sample 19: Lattice Certus-NX Soft RISC-V Wishbone Bus Arbiter Deadlock
    {
        "raw_asr": "our soft r i s c v system on chip froze during concurrent flash memory access and sensor data acquisition inside the telemetry unit we attached an oscilloscope two the system bus signals and inspected core execution states using open o c d inside g d b the wishbone interconnect arbiter experienced a bus deadlock because the instruction cache controller and serial peripheral interface master requested simultaneous bus grants while the system interconnect lacked bus arbitration wait inspect the bus arbiter priority logic inside wishbone underscore arbiter dot c instead configur the wishbone interconnect arbiter timeout buy setting sixteen wait set thirty two bus cycles instead into the timeout threshold register right zero x zero four wait right zero x zero eight into the arbiter control register instead two grant round robin bus access we cleared the arbiter stall flag buy writing one into the bus status register after tuning arbiter timeouts and updating priority control registers the system on chip executed eight thousand sensor logging transactions across eighteen hours without bus lockups or arbiter deadlocks",
        "refined_text": "Our soft RISC-V system-on-chip froze during concurrent flash memory access and sensor data acquisition inside the telemetry unit. We attached an oscilloscope to the system bus signals and inspected core execution states using OpenOCD inside GDB. The Wishbone interconnect arbiter experienced a bus deadlock because the instruction cache controller and serial peripheral interface master requested simultaneous bus grants while the system interconnect lacked bus arbitration, inspecting the bus arbiter priority logic inside wishbone_arbiter.c instead.\n\nConfigure the Wishbone interconnect arbiter timeout by setting 32 bus cycles instead into the timeout threshold register. Write 0x08 into the arbiter control register instead to grant round-robin bus access. We cleared the arbiter stall flag by writing 1 into the bus status register.\n\nAfter tuning arbiter timeouts and updating priority control registers, the system-on-chip executed 8000 sensor logging transactions across 18 hours without bus lockups or arbiter deadlocks."
    },
    # Sample 20: GigaDevice GD32F450 SDIO High-Speed 4-Bit Bus CRC Error & Clock Phase Skew
    {
        "raw_asr": "our g d thirty two f four five zero industrial computer encountered data crc errors during secure digital input output block transfers inside the automated logging terminal we attached an oscilloscope two the clock and command lines and monitored direct memory access transfer registers inside g d b the secure digital interface asserted a transmission cyclic redundancy check failure because high speed clock edge jitter shifted input data sampling while the storage driver lacked clock edge calibrat wait inspect the clock phase configuration inside sdio underscore emmc dot c instead configur the secure digital host clock phase buy selecting inverted clock sampling right zero x zero one wait right zero x zero three into the clock edge register instead two align data hold timing we cleared the data cyclic redundancy check error flag buy writing one into the command status register after adjusting clock phase alignment and resetting interface control registers the industrial computer recorded nine thousand storage blocks across twenty two hours without data corruption or cyclic redundancy check failures",
        "refined_text": "Our GD32F450 industrial computer encountered data CRC errors during secure digital input output block transfers inside the automated logging terminal. We attached an oscilloscope to the clock and command lines and monitored direct memory access transfer registers inside GDB. The secure digital interface asserted a transmission cyclic redundancy check failure because high-speed clock edge jitter shifted input data sampling while the storage driver lacked clock edge calibration, inspecting the clock phase configuration inside sdio_emmc.c instead.\n\nConfigure the secure digital host clock phase by selecting inverted clock sampling. Write 0x03 into the clock edge register instead to align data hold timing. We cleared the data cyclic redundancy check error flag by writing 1 into the command status register.\n\nAfter adjusting clock phase alignment and resetting interface control registers, the industrial computer recorded 9000 storage blocks across 22 hours without data corruption or cyclic redundancy check failures."
    }
]

print(f"Total samples in batch: {len(batch_89)}")

# Check leakage
for idx, s in enumerate(batch_89, 1):
    raw_l = s["raw_asr"].strip().lower()
    ref_l = s["refined_text"].strip()
    if raw_l in eval_raws:
        print(f"ERROR: Sample {idx} raw_asr leaks into eval!")
        sys.exit(1)
    if ref_l in eval_refs:
        print(f"ERROR: Sample {idx} refined_text leaks into eval!")
        sys.exit(1)

print("Leakage check: PASSED (0 leaks)")

# Check individual validation and cleaning
pair_fails = 0
clean_fails = 0
tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, s in enumerate(batch_89, 1):
    v_ok, v_msg = validator.validate_pair(s)
    if not v_ok:
        print(f"Validation FAILED on sample {idx}: {v_msg}")
        pair_fails += 1

    c_res, c_msg = cleaner.clean_sample(s["raw_asr"], s["refined_text"])
    if c_msg != "kept":
        print(f"Cleaner FAILED on sample {idx}: {c_msg}")
        clean_fails += 1

    words = len(s["refined_text"].split())
    if words < 25:
        tier_counts["short"] += 1
    elif words < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1

print(f"Pair validation: {len(batch_89) - pair_fails}/{len(batch_89)} passed")
print(f"Cleaner validation: {len(batch_89) - clean_fails}/{len(batch_89)} passed")
print(f"Tier counts: {tier_counts}")

# Batch validation
b_ok, b_msg, b_counts = validator.validate_batch(batch_89, min_short=4, min_medium=6, min_long=10)
print(f"Batch validation: {b_ok} ({b_msg}), counts: {b_counts}")

if not (v_ok and c_msg == "kept" and b_ok and pair_fails == 0 and clean_fails == 0):
    print("FAILED checks!")
    sys.exit(1)

# Save to scratch/subagent_batch_89.json
output_file = Path("scratch/subagent_batch_89.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(batch_89, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {len(batch_89)} verified samples to {output_file}")
