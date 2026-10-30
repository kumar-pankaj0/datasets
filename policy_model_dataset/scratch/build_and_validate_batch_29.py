import json
import re
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
    # --- SHORT SAMPLES (<25 words, exactly 1 sentence, 0 newlines, max 1 cut-word) ---
    # Sample 1: FreeRTOS task notification
    {
        "raw_asr": "um right the free are toss task notification value buy calling x task notify from i s r",
        "refined_text": "Write the FreeRTOS task notification value by calling xTaskNotifyFromISR."
    },
    # Sample 2: RISC-V CSR
    {
        "raw_asr": "basically clear bit three in the r i s c v mstatus register buy writing zero x eight wait zero x zero eight instead",
        "refined_text": "Clear bit 3 in the RISC-V mstatus register by writing 0x08."
    },
    # Sample 3: STM32 GPIO alternate function
    {
        "raw_asr": "configur the alternate function register buy setting pin nine to u art mode four",
        "refined_text": "Configure the alternate function register by setting pin 9 to UART mode 4."
    },
    # Sample 4: I2C bus clock control
    {
        "raw_asr": "right the i two c clock control register buy setting the standard speed divider to four zero",
        "refined_text": "Write the I2C clock control register by setting the standard speed divider to 40."
    },

    # --- MEDIUM SAMPLES (25-90 words, 1-3 sentences, natural \n\n) ---
    # Sample 5: Hardware timer PWM generation & prescaler
    {
        "raw_asr": "initializ the hardware timer prescaler buy loading sixty four into the prescaler register to step the counter clock right fifty into the auto reload register to generate a twenty kilohertz pulse width modulation signal on channel one",
        "refined_text": "Initialize the hardware timer prescaler by loading 64 into the prescaler register to step the counter clock.\n\nWrite 50 into the auto reload register to generate a 20 kilohertz pulse width modulation signal on channel 1."
    },
    # Sample 6: FreeRTOS priority inheritance mutex
    {
        "raw_asr": "um create a mutex semaphore buy calling x semaphore create mutex to protect the shared s p i peripheral when the low priority sensor knowed holds the lock free are toss temporarily raises its execution priority to match any requesting high priority thread",
        "refined_text": "Create a mutex semaphore by calling xSemaphoreCreateMutex to protect the shared SPI peripheral.\n\nWhen the low-priority sensor node holds the lock, FreeRTOS temporarily raises its execution priority to match any requesting high-priority thread."
    },
    # Sample 7: STM32 DMA memory-to-peripheral transfer
    {
        "raw_asr": "allocat a sixty four byte buffer for the d m a memory to peripheral transfer on stream five set the data transfer direction to memory to peripheral wait peripheral to memory instead enable the half transfer and transfer complete interrupts in the control register",
        "refined_text": "Allocate a 64 byte buffer for the DMA memory to peripheral transfer on stream 5. Set the data transfer direction to peripheral to memory instead.\n\nEnable the half transfer and transfer complete interrupts in the control register."
    },
    # Sample 8: SPI bus clock polarity and phase
    {
        "raw_asr": "configur the s p i control register buy setting clock polarity to zero and clock phase to one right zero x zero two into the baud rate control bits to divide the peripheral clock buy eight during serial communicat",
        "refined_text": "Configure the SPI control register by setting clock polarity to 0 and clock phase to 1.\n\nWrite 0x02 into the baud rate control bits to divide the peripheral clock by 8 during serial communication."
    },
    # Sample 9: RISC-V trap vector setup
    {
        "raw_asr": "basically right the base address of the trap vector table into the r i s c v mtvec register align the vector table address to a sixty four byte boundary wait one hundred twenty eight byte boundary instead set mode bits to vectored mode buy writing one into the lowest two bits",
        "refined_text": "Write the base address of the trap vector table into the RISC-V mtvec register. Align the vector table address to a 128 byte boundary instead.\n\nSet mode bits to vectored mode by writing 1 into the lowest 2 bits."
    },
    # Sample 10: Watchdog timer window refresh
    {
        "raw_asr": "um service the window watchdog timer buy loading the reload register with zero x seven f before the counter downcounts past sixty four right zero x a a into the key register to refresh the watchdog and terminat the fault condition",
        "refined_text": "Service the window watchdog timer by loading the reload register with 0x7F before the counter downcounts past 64.\n\nWrite 0xAA into the key register to refresh the watchdog and terminate the fault condition."
    },

    # --- LONG SAMPLES (90+ words, multi-paragraph \n\n, 0 checklist stereotypes, natural spoken engineer narration) ---
    # Sample 11: FreeRTOS message queue overrun during burst sensor telemetry
    {
        "raw_asr": "okay so our high rate sensor telemetry task was dropping packets due to queue overflow events under free are toss we investigated the sensor pipeline buy inspecting the queue handle and reading the high water mark during continuous data acquisition the producer task was pushing thirty two byte telemetry packets into a sixteen element message queue at two hundred hertz but the consumer thread blocked whenever the flash storage subsystem performed block erase operations um this latency caused the message queue to fill completely within eighty milliseconds triggering queue send timeouts to fix the packet loss we doubled the queue length to thirty two elements buy updating the buffer allocation in internal memory we also adjusted task priorities buy raising the telemetry consumer thread to priority four while lowering the background flash logger to priority two now the message queue absorbs telemetry bursts without dropping frames during heavy flash operat",
        "refined_text": "Our high-rate sensor telemetry task was dropping packets due to queue overflow events under FreeRTOS. We investigated the sensor pipeline by inspecting the queue handle and reading the high water mark during continuous data acquisition. The producer task was pushing 32 byte telemetry packets into a 16 element message queue at 200 hertz, but the consumer thread blocked whenever the flash storage subsystem performed block erase operations.\n\nThis latency caused the message queue to fill completely within 80 milliseconds, triggering queue send timeouts. To fix the packet loss, we doubled the queue length to 32 elements by updating the buffer allocation in internal memory.\n\nWe also adjusted task priorities by raising the telemetry consumer thread to priority 4 while lowering the background flash logger to priority 2. Now the message queue absorbs telemetry bursts without dropping frames during heavy flash operation."
    },
    # Sample 12: STM32 circular DMA audio stream underrun
    {
        "raw_asr": "basically the stm thirty two digital audio playback suffered from audible clicks when streaming sound samples through the circular d m a pipeline the firmware allocat a double buffer of two hundred fifty six words wait five hundred twelve words in memory to feed the digital to analog converter serializer root the audio stream failure down to interrupt latency in the half transfer callback handler when the d m a controller raised the half complete flag the c p u failed to service the interrupt before the hardware finished transmitting the remaining half of the circular buffer um to eliminate the audio underruns we enlarged the circular buffer allocation to one zero two four words in dedicated s r a m we also increased the d m a stream interrupt priority in the n v i c from priority three to priority one right zero x zero three into the d m a control register to enable circular mode with burst transfers of four beats after these adjustments the audio stream maintains continuous playback without pops or stutter during active d m a transmiss",
        "refined_text": "The STM32 digital audio playback suffered from audible clicks when streaming sound samples through the circular DMA pipeline. The firmware allocated a double buffer of 512 words in memory to feed the digital to analog converter serializer. Route the audio stream failure down to interrupt latency in the half transfer callback handler.\n\nWhen the DMA controller raised the half complete flag, the CPU failed to service the interrupt before the hardware finished transmitting the remaining half of the circular buffer. To eliminate the audio underruns, we enlarged the circular buffer allocation to 1024 words in dedicated SRAM.\n\nWe also increased the DMA stream interrupt priority in the NVIC from priority 3 to priority 1. Write 0x03 into the DMA control register to enable circular mode with burst transfers of 4 beats. After these adjustments, the audio stream maintains continuous playback without pops or stutter during active DMA transmission."
    },
    # Sample 13: RISC-V physical memory protection (PMP) fault
    {
        "raw_asr": "okay so our custom r i s c v firmware triggered unexpected access fault traps when the user mode application tried to execute code from flash memory we analyzed the machine trap registers buy reading mcause and mepc upon entering the machine trap handler the mcause register stored value one indicating an instruction access fault while mepc pointed to address zero x eight zero zero zero zero zero zero zero um we checked the physical memory protection configur and discovered that pmpcfg zero was uninitialized leaving user mode execution disabled for the target memory region to grant access we configur pmp entry zero buy writing zero x zero f into pmpcfg zero to permit read write and execute permissions in top of range mode we also right the upper boundary address zero x eight zero zero four zero zero zero zero into pmpaddr zero after executing the mret instruction the r i s c v core resumed execution in user mode without generating memory protection faults during application operat",
        "refined_text": "Our custom RISC-V firmware triggered unexpected access fault traps when the user mode application tried to execute code from flash memory. We analyzed the machine trap registers by reading mcause and mepc upon entering the machine trap handler. The mcause register stored value 1, indicating an instruction access fault, while mepc pointed to address 0x80000000.\n\nWe checked the physical memory protection configuration and discovered that pmpcfg0 was uninitialized, leaving user mode execution disabled for the target memory region. To grant access, we configure pmp entry 0 by writing 0x0F into pmpcfg0 to permit read, write, and execute permissions in top of range mode.\n\nWe also write the upper boundary address 0x80040000 into pmpaddr0. After executing the mret instruction, the RISC-V core resumed execution in user mode without generating memory protection faults during application operation."
    },
    # Sample 14: I2C bus lockup recovery
    {
        "raw_asr": "basically our temperature sensor knowed on the i two c bus locked up completely during power cycling tests causing the bus master to hang waiting for acknowledgement we attached an oscilloscope and discovered that the sensor held the serial data line low because a reset occurred during a read transaction while the peripheral was asserting an a c k bit the hardware i two c controller cannot generate clock cycles while s d a is pulled low buy a slave device um to clear the bus lockup we reconfigured the serial clock and serial data pins as general purpose output pins under software control we toggled the serial clock line nine times at one hundred kilohertz to clock out the stuck bit from the peripheral shift register then we generated a manual stop condition buy pulling s d a low and releasing it high while s c l remained high finally we reinitialized the i two c peripheral registers buy setting the peripheral clock to sixteen megahertz and the bus resumed normal communicat",
        "refined_text": "Our temperature sensor node on the I2C bus locked up completely during power cycling tests, causing the bus master to hang waiting for acknowledgement. We attached an oscilloscope and discovered that the sensor held the serial data line low because a reset occurred during a read transaction while the peripheral was asserting an ACK bit. The hardware I2C controller cannot generate clock cycles while SDA is pulled low by a slave device.\n\nTo clear the bus lockup, we reconfigured the serial clock and serial data pins as general purpose output pins under software control. We toggled the serial clock line 9 times at 100 kilohertz to clock out the stuck bit from the peripheral shift register.\n\nThen we generated a manual stop condition by pulling SDA low and releasing it high while SCL remained high. Finally, we reinitialized the I2C peripheral registers by setting the peripheral clock to 16 megahertz, and the bus resumed normal communication."
    },
    # Sample 15: CAN bus bit timing and arbitration
    {
        "raw_asr": "okay so the automotive controller was experiencing passive error flags and dropped frames on the c a n bus when communicating at five hundred kilobits per second we checked the bit timing register configur buy reading the prescaler and time segment fields using the debugger the nominal prescaler was set to four wait set to eight instead giving sixteen time quanta per bit but the sample point was configured at sixty percent of the bit duration which failed to compensate for physical transceiver propagation delay um during multi knowed arbitrat reflections on the differential bus distorted the recessive bit edge causing false bit errors to resolve the timing errors we recalculated the bit segments buy assigning three time quanta to propagation segment five time quanta to phase segment one and four time quanta to phase segment two this shifted the sample point to seventy five percent of the nominal bit time right the updated timing values into the control register to eliminate stuff errors and restore reliable frame transmiss",
        "refined_text": "The automotive controller was experiencing passive error flags and dropped frames on the CAN bus when communicating at 500 kilobits per second. We checked the bit timing register configuration by reading the prescaler and time segment fields using the debugger. The nominal prescaler was set to 8, giving 16 time quanta per bit, but the sample point was configured at 60 percent of the bit duration, which failed to compensate for physical transceiver propagation delay.\n\nDuring multi node arbitration, reflections on the differential bus distorted the recessive bit edge, causing false bit errors. To resolve the timing errors, we recalculated the bit segments by assigning 3 time quanta to propagation segment, 5 time quanta to phase segment 1, and 4 time quanta to phase segment 2.\n\nThis shifted the sample point to 75 percent of the nominal bit time. Write the updated timing values into the control register to eliminate stuff errors and restore reliable frame transmission."
    },
    # Sample 16: ADC continuous DMA scanning with multiple channels
    {
        "raw_asr": "basically our motor controller analog front end exhibited erratic current measurements during continuous multi channel a d c sampling root the measurement noise issue to incorrect sampling time and d m a channel configuration the firmware was scanning four analog input channels at one megasample per second using continuous scan mode but the channel sequencer was configured to trigger d m a transfers before the sample and hold capacitor fully charged um we investigated the a d c control registers and increased the sample time from three cycles to fifty six cycles for each analog channel in the sample time register we also configur the d m a controller to operate in circular mode buy loading four into the number of data transfers register right zero x zero one into the a d c control register to enable the end of conversion interrupt and d m a requests these adjustments allowed the d m a engine to transfer clean voltage readings directly into memory without c p u overhead during continuous sensor calibrat",
        "refined_text": "Our motor controller analog front end exhibited erratic current measurements during continuous multi channel ADC sampling. Route the measurement noise issue to incorrect sampling time and DMA channel configuration. The firmware was scanning 4 analog input channels at 1 megasample per second using continuous scan mode, but the channel sequencer was configured to trigger DMA transfers before the sample and hold capacitor fully charged.\n\nWe investigated the ADC control registers and increased the sample time from 3 cycles to 56 cycles for each analog channel in the sample time register. We also configure the DMA controller to operate in circular mode by loading 4 into the number of data transfers register.\n\nWrite 0x01 into the ADC control register to enable the end of conversion interrupt and DMA requests. These adjustments allowed the DMA engine to transfer clean voltage readings directly into memory without CPU overhead during continuous sensor calibration."
    },
    # Sample 17: Window watchdog timer reset issue during flash erase
    {
        "raw_asr": "okay so the industrial telemetry unit suffered from spurious resets whenever the firmware initiated a sector erase on internal flash memory we inspected the reset status register and confirmed that a window watchdog timer event caused the system reset the window watchdog downcounter was configured buy setting the prescaler to eight and loading the counter with one hundred twenty seven yielding an early reset window of forty milliseconds um however the hardware flash erase routine disables interrupts and stalls the bus matrix for sixty milliseconds while the high voltage charge pump erases the flash sector this hardware stall prevented the supervisory thread from executing its periodic refresh write before the watchdog counter reached zero x three f to resolve the spurious reset we restructured the firmware buy servicing the watchdog counter immediately before initiating flash erase operations we also right forty eight milliseconds into the watchdog window register to broaden the valid kick interval now the device performs flash updates reliably without triggering unintended watchdog resets during runtime operat",
        "refined_text": "The industrial telemetry unit suffered from spurious resets whenever the firmware initiated a sector erase on internal flash memory. We inspected the reset status register and confirmed that a window watchdog timer event caused the system reset. The window watchdog downcounter was configured by setting the prescaler to 8 and loading the counter with 127, yielding an early reset window of 40 milliseconds.\n\nHowever, the hardware flash erase routine disables interrupts and stalls the bus matrix for 60 milliseconds while the high voltage charge pump erases the flash sector. This hardware stall prevented the supervisory thread from executing its periodic refresh write before the watchdog counter reached 0x3F.\n\nTo resolve the spurious reset, we restructured the firmware by servicing the watchdog counter immediately before initiating flash erase operations. We also write 48 milliseconds into the watchdog window register to broaden the valid kick interval. Now the device performs flash updates reliably without triggering unintended watchdog resets during runtime operation."
    },
    # Sample 18: SPI NOR flash Quad-SPI (QSPI) memory-mapped mode
    {
        "raw_asr": "basically the graphic display controller experienced memory bus faults when executing code directly from external nor flash via quad s p i memory mapped mode we traced the bus error buy probing the chip select and serial clock lines with a logic analyzer the quad s p i peripheral was configured with six dummy clock cycles but the high speed flash chip required eight dummy cycles when operating at eighty megahertz this timing mismatch caused the memory controller to read invalid instruction opcodes before the flash output buffers settled um to correct the bus timing we configur the quad s p i control register buy setting the dummy cycle count to eight in the device configuration register we also right zero x e b into the instruction register to select quad output fast read mode and configured thirty two bit addressing mode after refreshing the peripheral configuration the core mapped the external flash seamlessly into the memory address space at zero x nine zero zero zero zero zero zero zero without bus faults during high speed code execut",
        "refined_text": "The graphic display controller experienced memory bus faults when executing code directly from external NOR flash via Quad SPI memory mapped mode. We traced the bus error by probing the chip select and serial clock lines with a logic analyzer. The Quad SPI peripheral was configured with 6 dummy clock cycles, but the high speed flash chip required 8 dummy cycles when operating at 80 megahertz.\n\nThis timing mismatch caused the memory controller to read invalid instruction opcodes before the flash output buffers settled. To correct the bus timing, we configure the Quad SPI control register by setting the dummy cycle count to 8 in the device configuration register.\n\nWe also write 0xEB into the instruction register to select quad output fast read mode and configured 32 bit addressing mode. After refreshing the peripheral configuration, the core mapped the external flash seamlessly into the memory address space at 0x90000000 without bus faults during high speed code execution."
    },
    # Sample 19: Hardware UART frame error and overrun error handling
    {
        "raw_asr": "okay so our cellular modem gateway was losing command responses due to u art framing and overrun errors during high baud rate serial communicat we investigated the u art peripheral status registers and found that the receiver error flag was set buy framing errors when receiving packets at nine two one six zero zero baud the problem arose because the receiver was operating under interrupt driven polling where high priority interrupts blocked the serial isr from reading the receive data register in time um to eliminate the data overrun condition we reconfigured the u art receiver to use d m a circular reception with idle line detection we configur d m a channel two buy loading a circular buffer of two hundred fifty six bytes in internal memory and enabled the idle line interrupt in the control register right zero x zero eight into the interrupt enable register to wake the parser when a full frame arrives this architecture processes high speed telemetry streams smoothly without data overrun or frame errors during serial operat",
        "refined_text": "Our cellular modem gateway was losing command responses due to UART framing and overrun errors during high baud rate serial communication. We investigated the UART peripheral status registers and found that the receiver error flag was set by framing errors when receiving packets at 921600 baud. The problem arose because the receiver was operating under interrupt driven polling where high priority interrupts blocked the serial ISR from reading the receive data register in time.\n\nTo eliminate the data overrun condition, we reconfigured the UART receiver to use DMA circular reception with idle line detection. We configure DMA channel 2 by loading a circular buffer of 256 bytes in internal memory and enabled the idle line interrupt in the control register.\n\nWrite 0x08 into the interrupt enable register to wake the parser when a full frame arrives. This architecture processes high speed telemetry streams smoothly without data overrun or frame errors during serial operation."
    },
    # Sample 20: FreeRTOS event group bit synchronization
    {
        "raw_asr": "basically our industrial sensor hub failed to complete system startup because worker threads hung waiting for synchronization flags under free are toss we examined the synchronization architecture buy inspecting the task states in the runtime trace the supervisor thread created an event group buy calling x event group create and expected three worker tasks to signal their ready status buy setting bits zero one and two in the event group bits mask um however the sensor calibration thread encountered a timeout and never asserted bit two causing the main application thread to wait indefinitely in x event group wait bits to break the startup deadlock we updated the synchronization logic buy setting a five thousand milliseconds timeout on the wait call instead of waiting forever we also right recovery logic to check the returned event bits mask and log the missing subsystem status before proceeding with degraded sensor operat",
        "refined_text": "Our industrial sensor hub failed to complete system startup because worker threads hung waiting for synchronization flags under FreeRTOS. We examined the synchronization architecture by inspecting the task states in the runtime trace. The supervisor thread created an event group by calling xEventGroupCreate and expected 3 worker tasks to signal their ready status by setting bits 0, 1, and 2 in the event group bits mask.\n\nHowever, the sensor calibration thread encountered a timeout and never asserted bit 2, causing the main application thread to wait indefinitely in xEventGroupWaitBits. To break the startup deadlock, we updated the synchronization logic by setting a 5000 milliseconds timeout on the wait call instead of waiting forever.\n\nWe also write recovery logic to check the returned event bits mask and log the missing subsystem status before proceeding with degraded sensor operation."
    }
]

with open("scratch/subagent_batch_29.json", "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2)

print("\n--- Running Validation Checks on Batch 29 ---")
all_ok = True
tier_counts = {"short": 0, "medium": 0, "long": 0}

for i, s in enumerate(samples, 1):
    v_ok, v_reason = validate_pair(s)
    c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
    
    words = len(s["refined_text"].split())
    raw_words = len(s["raw_asr"].split())
    ratio = words / max(1, raw_words)
    
    if words < 25:
        tier = "SHORT"
        tier_counts["short"] += 1
    elif words <= 90:
        tier = "MEDIUM"
        tier_counts["medium"] += 1
    else:
        tier = "LONG"
        tier_counts["long"] += 1
        
    passed = v_ok and (c_res is not None)
    if not passed:
        all_ok = False
        print(f"Sample {i:02d} [{tier}]: FAIL -> validator: '{v_reason}', cleaner: '{c_reason}'")
    else:
        print(f"Sample {i:02d} [{tier:6s}]: PASS -> words={words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f}")

print("\n--- Tier Counts ---")
print(f"Short:  {tier_counts['short']} / 4")
print(f"Medium: {tier_counts['medium']} / 6")
print(f"Long:   {tier_counts['long']} / 10")

b_ok, b_reason, _ = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
print(f"\nvalidate_batch: {b_reason} (passed={b_ok})")

if all_ok and b_ok:
    print("\nALL 20 SAMPLES PASSED 100%!")
else:
    print("\nSOME SAMPLES FAILED!")
    sys.exit(1)
