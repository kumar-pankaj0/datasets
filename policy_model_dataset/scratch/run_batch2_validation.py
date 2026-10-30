import sys
from test_batch import test_samples

batch_2 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "clear the transmit complete flag in the status register by writing zero to bit six",
        "refined_text": "Clear the transmit complete flag in the status register by writing 0 to bit 6."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "um configure the system clock divider by loading zero x zero two into the prescaler register",
        "refined_text": "Configure the system clock divider by loading `0x02` into the prescaler register."
    },
    # --- Short 3 (< 25 words) ---
    {
        "raw_asr": "read the converted analog voltage from the a d c regular data register",
        "refined_text": "Read the converted analog voltage from the `ADC` regular data register."
    },
    # --- Short 4 (< 25 words) ---
    {
        "raw_asr": "flash the bootloader image using open o c d dash f openocd dot cfg",
        "refined_text": "Flash the bootloader image using `openocd -f openocd.cfg`."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "we need to configure channel one and channel two of timer one for complementary p w m output uh set the dead time generator register to fifty four clock cycles and load eighty percent duty cycle into the capture compare register",
        "refined_text": "We need to configure channel 1 and channel 2 of timer 1 for complementary PWM output.\n\nSet the dead time generator register to 54 clock cycles and load 80% duty cycle into the capture compare register."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "the c a n controller drops incoming telemetry messages because the acceptance filter mask rejects identifier zero x one two zero modify the filter register mask to zero x one f zero and switch the message buffer to fifo mode",
        "refined_text": "The `CAN` controller drops incoming telemetry messages because the acceptance filter mask rejects identifier `0x120`.\n\nModify the filter register mask to `0x1F0` and switch the message buffer to FIFO mode."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "the micro controller consumes twelve milliamperes during stop mode because the high speed external oscillator remains enabled disable the peripheral clocks before entering low power sleep and program the real time clock wake up timer for thirty seconds",
        "refined_text": "The microcontroller consumes 12 mA during stop mode because the high-speed external oscillator remains enabled.\n\nDisable the peripheral clocks before entering low-power sleep and program the real-time clock wake-up timer for 30 seconds."
    },
    # --- Medium 4 (25-90 words) ---
    {
        "raw_asr": "the debug probe reports target connection loss because the firmware remapped the serial wire debug pins to g p i o outputs connect the under reset line and assert hardware reset during the connect sequence in open o c d",
        "refined_text": "The debug probe reports target connection loss because the firmware remapped the serial wire debug pins to `GPIO` outputs.\n\nConnect the under-reset line and assert hardware reset during the connect sequence in `openocd`."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "um the over the air firmware update failed during sector erase verificat on the external s p i flash memory chip the flash controller returned a write error status flag because the sector erase cycle exceeded the maximum timeout of four hundred milliseconds investigation showed that incoming radio packets triggered nested interrupts that preempted the flash driver busy wait loop while the processor handled the radio interrupts the s p i chip select line floated high and aborted the active erase instruct we resolved the failure by placing the flash sector erase command inside a critical section that temporarily masks lower priority peripheral interrupts we also configured the s p i peripheral hardware chip select pin to remain actively asserted during continuous multi byte commands",
        "refined_text": "The over the air firmware update failed during sector erase verification on the external `SPI` flash memory chip. The flash controller returned a write error status flag because the sector erase cycle exceeded the maximum timeout of 400 milliseconds.\n\nInvestigation showed that incoming radio packets triggered nested interrupts that preempted the flash driver busy wait loop. While the processor handled the radio interrupts, the `SPI` chip select line floated high and aborted the active erase instruction.\n\nWe resolved the failure by placing the flash sector erase command inside a critical section that temporarily masks lower priority peripheral interrupts. We also configured the `SPI` peripheral hardware chip select pin to remain actively asserted during continuous multi byte commands."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the embedded controller crashed with a memory management fault during high volume serial communication a serial port interrupt service routine invoked a free are toss queue send from i s r function while executing at priority level one the kernel requires all hardware interrupts that call operating system primitives to execute at or below the maximum system call interrupt priority boundary of priority five because the serial interrupt ran at higher urgency it interrupted a critical section and corrupted the kernel task scheduler state we fixed the crash by configur the nested vectored interrupt controller priority grouping to four preemption bits we then assigned the serial port interrupt to preemption priority six and verified that all kernel queue transact execute deterministically under full bus throughput",
        "refined_text": "The embedded controller crashed with a memory management fault during high volume serial communication. A serial port interrupt service routine invoked a `FreeRTOS` queue send from `ISR` function while executing at priority level 1.\n\nThe kernel requires all hardware interrupts that call operating system primitives to execute at or below the maximum system call interrupt priority boundary of priority 5. Because the serial interrupt ran at higher urgency, it interrupted a critical section and corrupted the kernel task scheduler state.\n\nWe fixed the crash by configuring the nested vectored interrupt controller priority grouping to 4 preemption bits. We then assigned the serial port interrupt to preemption priority 6 and verified that all kernel queue transactions execute deterministically under full bus throughput."
    }
]

if __name__ == "__main__":
    success = test_samples(batch_2)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
