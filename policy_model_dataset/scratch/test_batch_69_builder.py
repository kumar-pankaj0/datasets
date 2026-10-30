import json
import re
from pathlib import Path
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)

# Load sft_eval.json for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

samples = [
    # Tier 1: Short (< 25 words, exactly 1 complete sentence, 0 newlines) - Exactly 4 samples
    # Sample 1: STM32 TIM2 prescaler
    {
        "raw_asr": "um please configur the timer prescaler reload register four two hundred fifty six",
        "refined_text": "Please configure the timer prescaler reload register for 256."
    },
    # Sample 2: ESP32 FreeRTOS task stack allocation
    {
        "raw_asr": "uh allocat two thousand bytes four the free are toss telemetry task stack",
        "refined_text": "Allocate 2000 bytes for the FreeRTOS telemetry task stack."
    },
    # Sample 3: nRF52 UART baud rate register
    {
        "raw_asr": "um right the value zero x zero two into the u art baud rate register",
        "refined_text": "Write the value 0x02 into the UART baud rate register."
    },
    # Sample 4: RP2040 SPI clock polarity
    {
        "raw_asr": "basically set the s p i clock polarity register two zero wait set it two one instead",
        "refined_text": "Set the SPI clock polarity register to 1 instead."
    },

    # Tier 2: Medium (25-89 words, 1-3 sentences, natural \n\n paragraph break) - Exactly 6 samples
    # Sample 5: RISC-V interrupt vector table
    {
        "raw_asr": "uh initializ the r i s c v machine trap vector base address register with zero x zero zero zero four then route all external interrupts two the direct mode handler buy clearing the lowest two bits",
        "refined_text": "Initialize the RISC-V machine trap vector base address register with 0x0004.\n\nThen route all external interrupts to the direct mode handler by clearing the lowest two bits."
    },
    # Sample 6: CAN-FD bus standby pin
    {
        "raw_asr": "um before the can bus knowed can arbitrat frame transmission you know right zero two the transceiver standby pin this action awakens the physical transceiver and clears the dominant error state",
        "refined_text": "Before the CAN bus node can arbitrate frame transmission, write 0 to the transceiver standby pin.\n\nThis action awakens the physical transceiver and clears the dominant error state."
    },
    # Sample 7: I2C bus clear sequence
    {
        "raw_asr": "basically when an i two c peripheral holds the data line low toggle eight clock pulses wait toggle nine clock pulses instead on the serial clock pin this sequence releases the internal shift register and restores the bus two idle",
        "refined_text": "When an I2C peripheral holds the data line low, toggle 9 clock pulses on the serial clock pin.\n\nThis sequence releases the internal shift register and restores the bus to idle."
    },
    # Sample 8: DMA circular buffer half-transfer
    {
        "raw_asr": "okay so the d m a controller transfers sixty four bytes directly from peripheral communicat registers two local memory always process the lower thirty two bytes inside the half transfer callback before the transfer complete flag triggers",
        "refined_text": "The DMA controller transfers 64 bytes directly from peripheral communication registers to local memory.\n\nAlways process the lower 32 bytes inside the half transfer callback before the transfer complete flag triggers."
    },
    # Sample 9: Window watchdog timer refresh
    {
        "raw_asr": "uh the window watchdog timer expects a reload refresh during normal firmware operat right the key value zero x a a two the key register inside the valid refresh window this prevents an unexpected reset during long sensor polling loops",
        "refined_text": "The window watchdog timer expects a reload refresh during normal firmware operation.\n\nWrite the key value 0xaa to the key register inside the valid refresh window. This prevents an unexpected reset during long sensor polling loops."
    },
    # Sample 10: Flash bootloader dual-bank swap
    {
        "raw_asr": "like the bootloader swaps bank two four the new application image after verifying the signature right zero x zero eight zero zero into the vector table offset register this relocates exception vectors before branching two the application reset handler",
        "refined_text": "The bootloader swaps bank 2 for the new application image after verifying the signature.\n\nWrite 0x0800 into the vector table offset register. This relocates exception vectors before branching to the application reset handler."
    },

    # Tier 3: Long (90+ words, multi-paragraph separated by \n\n, zero checklist stereotypes) - Exactly 10 samples
    # Sample 11: FreeRTOS priority inversion postmortem
    {
        "raw_asr": "okay so during our hardware in the loop tests we hit a severe priority inversion inside the free are toss kernel the low priority logging task priority two wait priority three held the shared telemetry ring buffer while the medium priority motor control task consumed eighty percent of the c p u time because the logging task could not run the high priority safety monitor task stalled four fifty milliseconds waiting four the resource we traced this lockup two our choice of synchronizat primitive where the firmware used a binary semaphore instead of a mutex binary semaphores do not support priority inheritance so the low priority worker never inherited the high priority level of the waiting safety task right the fix buy replacing the binary semaphore with a free are toss mutex with priority inheritance enabled this allows the low priority task two finish flushing and release the lock immediately",
        "refined_text": "During our hardware in the loop tests, we hit a severe priority inversion inside the FreeRTOS kernel. The low priority logging task at priority 3 held the shared telemetry ring buffer while the medium priority motor control task consumed 80 percent of the CPU time. Because the logging task could not run, the high priority safety monitor task stalled for 50 milliseconds waiting for the resource.\n\nWe traced this lockup to our choice of synchronization primitive, where the firmware used a binary semaphore instead of a mutex. Binary semaphores do not support priority inheritance, so the low priority worker never inherited the high priority level of the waiting safety task.\n\nWrite the fix by replacing the binary semaphore with a FreeRTOS mutex with priority inheritance enabled. This allows the low priority task to finish flushing and release the lock immediately."
    },
    # Sample 12: Cortex-M7 D-Cache coherency and DMA
    {
        "raw_asr": "basically on the cortex m seven platform we observed data corruption during high speed s p i sensor capture using d m a the d m a controller writes incoming packets directly two sram starting at zero x two zero zero zero four zero zero zero but when the c p u reads the packet buffer it receives stale sensor values from the internal l one data cache because the cache controller does not know the memory changed two resolve this cache coherency issue we must invalidate the d cache lines covering the destination buffer before the c p u inspects the payload similarly whenever the firmware prepares an outgoing transmiss buffer the c p u must clean the cache right the dirty lines back two physical sram before triggering the d m a channel otherwise the d m a engine reads old values from memory we can also configur an mpu region as non cacheable four shared descriptor rings",
        "refined_text": "On the Cortex-M7 platform, we observed data corruption during high speed SPI sensor capture using DMA. The DMA controller writes incoming packets directly to SRAM starting at 0x20004000, but when the CPU reads the packet buffer, it receives stale sensor values from the internal L1 data cache because the cache controller does not know the memory changed.\n\nTo resolve this cache coherency issue, we must invalidate the D-cache lines covering the destination buffer before the CPU inspects the payload. Similarly, whenever the firmware prepares an outgoing transmission buffer, the CPU must clean the cache, write the dirty lines back to physical SRAM before triggering the DMA channel.\n\nOtherwise the DMA engine reads old values from memory. We can also configure an MPU region as non-cacheable for shared descriptor rings."
    },
    # Sample 13: HardFault exception CFSR analysis
    {
        "raw_asr": "okay so when debugging the hard fault exception on the stm thirty two the fault handler must extract the stacked program counter and link register from the current stack frame whether process stack or main stack looking at the configurable fault status register at address zero x e zero zero zero e d two eight bit one of the bus fault byte indicates a precise data bus error this specific flag means that the c p u attempted an invalid memory access during a store operat and the exact address was captured inside the bus fault address register the captured address was zero x two zero zero one f f f c which lies beyond the physical sram boundary right the fault handler logic two inspect the stacked exception frame print the register dump over serial and root the system two a controlled diagnostic halt",
        "refined_text": "When debugging the HardFault exception on the STM32, the fault handler must extract the stacked program counter and link register from the current stack frame, whether process stack or main stack. Looking at the configurable fault status register at address 0xe000ed28, bit 1 of the BusFault byte indicates a precise data bus error.\n\nThis specific flag means that the CPU attempted an invalid memory access during a store operation, and the exact address was captured inside the bus fault address register. The captured address was 0x2001fffc, which lies beyond the physical SRAM boundary.\n\nWrite the fault handler logic to inspect the stacked exception frame, print the register dump over serial, and route the system to a controlled diagnostic halt."
    },
    # Sample 14: Ultra-low power sleep modes
    {
        "raw_asr": "uh during battery life benchmarking the sensor knowed consumed forty five microamps in stop mode instead of the expected ten microamps wait fifteen microamps our power audit revealed that several unused g p i o pins remained configured as floating inputs rather than analog mode floating digital inputs oscillate due two thermal noise and draw parasitic current through internal input buffers buy reconfiguring all unrouted pins two analog mode with pull down disabled we eliminated the leakage we also noticed that the adc voltage reference remained energized during sleep switching off the internal buffer and gating the r t c wakeup timer four a sixty second interval reduced total sleep current two twelve microamps calibrat the r t c prescaler ensures accurate periodic wakeups without waking the c p u early",
        "refined_text": "During battery life benchmarking, the sensor node consumed 45 microamps in stop mode instead of the expected 15 microamps. Our power audit revealed that several unused GPIO pins remained configured as floating inputs rather than analog mode. Floating digital inputs oscillate due to thermal noise and draw parasitic current through internal input buffers.\n\nBy reconfiguring all unrouted pins to analog mode with pull down disabled, we eliminated the leakage. We also noticed that the ADC voltage reference remained energized during sleep.\n\nSwitching off the internal buffer and gating the RTC wakeup timer for a 60 second interval reduced total sleep current to 12 microamps. Calibrating the RTC prescaler ensures accurate periodic wakeups without waking the CPU early."
    },
    # Sample 15: USB CDC device enumeration
    {
        "raw_asr": "um during usb cdc device enumeration on the microcontroller the host issues a get descriptor setup packet on control endpoint zero our firmware was responding with a protocol stall because the device descriptor table reported a packet size of sixty four bytes while endpoint zero was initialized four only eight bytes you know this mismatch caused the host controller two abort the enumeration handshake two fix this issue we updated the endpoint zero buffer allocation two sixty four bytes inside the hardware setup routine right the correct configuration descriptor containing both the communication class interface and the data class interface once the host receives the complete configuration descriptor it assigns a dynamic address and enables bulk endpoints one and two four continuous serial data transfer",
        "refined_text": "During USB CDC device enumeration on the microcontroller, the host issues a GET_DESCRIPTOR setup packet on control endpoint 0. Our firmware was responding with a protocol stall because the device descriptor table reported a packet size of 64 bytes while endpoint 0 was initialized for only 8 bytes. This mismatch caused the host controller to abort the enumeration handshake.\n\nTo fix this issue, we updated the endpoint 0 buffer allocation to 64 bytes inside the hardware setup routine. Write the correct configuration descriptor containing both the communication class interface and the data class interface.\n\nOnce the host receives the complete configuration descriptor, it assigns a dynamic address and enables bulk endpoints 1 and 2 for continuous serial data transfer."
    },
    # Sample 16: I3C dynamic address assignment
    {
        "raw_asr": "okay so migrating from legacy i two c two the modern i three c protocol introduces dynamic address assignment during bus initialization the main master controller broadcasts the enter dynamic address assignment command across the shared bus each secondary target knowed pulls the serial data line low using open drain signaling during address arbitrat the device with the lowest provisional identifier wins the arbitration slot buy asserting its vendor and part identification bits once the controller assigns a seven bit dynamic address the target acknowledges and releases the bus allowing the next peripheral two participate after all secondary targets receive unique addresses the bus transitions from open drain mode two push pull mode four high speed data transfers up two twelve megahertz",
        "refined_text": "Migrating from legacy I2C to the modern I3C protocol introduces dynamic address assignment during bus initialization. The main master controller broadcasts the enter dynamic address assignment command across the shared bus. Each secondary target node pulls the serial data line low using open-drain signaling during address arbitration.\n\nThe device with the lowest provisional identifier wins the arbitration slot by asserting its vendor and part identification bits. Once the controller assigns a 7 bit dynamic address, the target acknowledges and releases the bus, allowing the next peripheral to participate.\n\nAfter all secondary targets receive unique addresses, the bus transitions from open-drain mode to push-pull mode for high speed data transfers up to 12 megahertz."
    },
    # Sample 17: Zephyr RTOS device tree PM
    {
        "raw_asr": "basically in zephyr rtos we configured device power management four our peripheral sensors using the device tree overlay each sensor knowed declares its power states including active standby and suspended when the power manager transitions the system into low power idle it calls the peripheral suspend handler which disables clocks and cuts sensor v d d we discovered a race condition where a high priority worker thread attempted u art communicat while the serial controller was still executing its resume callback right the thread synchronization buy acquiring a device ready semaphore before initiating transfers this prevents unaligned access errors and ensures the peripheral clock stabilizes before the driver transmits packets across the physical serial bus",
        "refined_text": "In Zephyr RTOS, we configured device power management for our peripheral sensors using the device tree overlay. Each sensor node declares its power states, including active, standby, and suspended. When the power manager transitions the system into low power idle, it calls the peripheral suspend handler, which disables clocks and cuts sensor VDD.\n\nWe discovered a race condition where a high priority worker thread attempted UART communication while the serial controller was still executing its resume callback.\n\nWrite the thread synchronization by acquiring a device ready semaphore before initiating transfers. This prevents unaligned access errors and ensures the peripheral clock stabilizes before the driver transmits packets across the physical serial bus."
    },
    # Sample 18: CAN bus signal integrity
    {
        "raw_asr": "uh while investigating intermittent can bus error frames our logic analyzer and oscilloscope revealed severe signal ringing on the differential lines the bus exhibited ringing voltages exceeding two volts during dominant bit transitions which caused receivers two miss the sample point and trigger form errors our inspection showed that the far end knowed lacked a one hundred twenty ohm termination resistor buy installing the missing resistor and shortening the stub wiring from forty centimeters down two five centimeters we eliminated reflections and restored a clean differential voltage swing we also adjusted the nominal bit timing prescaler so the sample point shifted from fifty percent wait shifted two eighty percent of the bit duration this timing alignment allows the transceivers two reliably decode packet data across twenty consecutive transmission cycles",
        "refined_text": "While investigating intermittent CAN bus error frames, our logic analyzer and oscilloscope revealed severe signal ringing on the differential lines. The bus exhibited ringing voltages exceeding 2 volts during dominant bit transitions, which caused receivers to miss the sample point and trigger form errors. Our inspection showed that the far end node lacked a 120 ohm termination resistor.\n\nBy installing the missing resistor and shortening the stub wiring from 40 centimeters down to 5 centimeters, we eliminated reflections and restored a clean differential voltage swing.\n\nWe also adjusted the nominal bit timing prescaler so the sample point shifted to 80 percent of the bit duration. This timing alignment allows the transceivers to reliably decode packet data across 20 consecutive transmission cycles."
    },
    # Sample 19: Bootloader UART upgrade
    {
        "raw_asr": "okay so the in field firmware update utility transmits the binary payload over u art in chunks of two hundred fifty six bytes each chunk contains a sequence number payload length and a thirty two bit cyclic redundancy check if any packet fails verification the bootloader sends a negative acknowledgment and requests retransmission up two three times once the complete image resides in the staging flash partition the bootloader computes a crc thirty two checksum across the entire image and compares it two the header metadata if the checksum matches the bootloader clears write protection on the application flash sectors and erases the application flash sectors before writing the new code right the updated boot status flag into non volatile memory and trigger a system reset",
        "refined_text": "The in-field firmware update utility transmits the binary payload over UART in chunks of 256 bytes. Each chunk contains a sequence number, payload length, and a 32 bit cyclic redundancy check. If any packet fails verification, the bootloader sends a negative acknowledgment and requests retransmission up to 3 times.\n\nOnce the complete image resides in the staging flash partition, the bootloader computes a CRC32 checksum across the entire image and compares it to the header metadata.\n\nIf the checksum matches, the bootloader clears write protection on the application flash sectors and erases the application flash sectors before writing the new code. Write the updated boot status flag into non-volatile memory and trigger a system reset."
    },
    # Sample 20: ADC multi-channel scan with DMA
    {
        "raw_asr": "uh when sampling multiple analog sensors using the adc in scan mode with d m a each channel requires sufficient sample and hold cycles two charge the internal sampling capacitor when we sampled high impedance thermistors with short sample times of three cycles the measured voltages suffered from channel cross talk and inaccurate temperature readings two resolve this issue we increased the sampling time two forty eight cycles four all thermistor channels and enabled the internal buffer amplifier we also read the factory calibrat bandgap reference voltage at address zero x one f f f seven five a zero buy comparing the measured bandgap value with the factory constant the firmware dynamically compensates four power supply voltage drift",
        "refined_text": "When sampling multiple analog sensors using the ADC in scan mode with DMA, each channel requires sufficient sample and hold cycles to charge the internal sampling capacitor. When we sampled high impedance thermistors with short sample times of 3 cycles, the measured voltages suffered from channel cross talk and inaccurate temperature readings.\n\nTo resolve this issue, we increased the sampling time to 48 cycles for all thermistor channels and enabled the internal buffer amplifier.\n\nWe also read the factory calibration bandgap reference voltage at address 0x1fff75a0. By comparing the measured bandgap value with the factory constant, the firmware dynamically compensates for power supply voltage drift."
    }
]

print(f"Total samples defined: {len(samples)}")
assert len(samples) == 20

tiers = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(samples):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator check
    val_ok, val_reason = val_mod.validate_pair(pair)
    if not val_ok:
        print(f"Sample {idx+1} failed validate_pair: {val_reason}")
        print("RAW:", raw)
        print("REF:", ref)
        raise AssertionError(f"Sample {idx+1} failed validate_pair: {val_reason}")

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    if clean_obj is None or clean_reason != "kept":
        print(f"Sample {idx+1} failed clean_sample: {clean_reason}")
        print("RAW:", raw)
        print("REF:", ref)
        raise AssertionError(f"Sample {idx+1} failed clean_sample: {clean_reason}")

    words = len(ref.split())
    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
    elif words < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3! Got: {sentences}"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"

print("Tier distribution:", tiers)
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

batch_ok, batch_msg, batch_tiers = val_mod.validate_batch(samples, min_short=4, min_medium=6, min_long=10)
assert batch_ok, f"Batch validation failed: {batch_msg}"

out_path = Path("scratch/subagent_batch_69.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {len(samples)} samples to {out_path} and verified all criteria!")
