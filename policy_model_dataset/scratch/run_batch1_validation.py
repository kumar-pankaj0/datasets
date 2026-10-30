import sys
from test_batch import test_samples

batch_1 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "um read the flash status register and verify that the busy bit is cleared",
        "refined_text": "Read the flash status register and verify that the busy bit is cleared."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "write zero x four zero to the g p i o direction register",
        "refined_text": "Write `0x40` to the `GPIO` direction register."
    },
    # --- Short 3 (< 25 words) ---
    {
        "raw_asr": "reload the watchdog timer by writing zero x a a to the key register",
        "refined_text": "Reload the watchdog timer by writing `0xAA` to the key register."
    },
    # --- Short 4 (< 25 words) ---
    {
        "raw_asr": "flash the firmware image with s t dash flash write firmware dot bin zero x zero eight zero zero zero zero zero zero",
        "refined_text": "Flash the firmware image with `st-flash write firmware.bin 0x08000000`."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "the i two c bus is hanging because a peripheral device pulled the data line low during a read transaction uh clock the bus nine times manually on the serial clock line until the slave releases the bus",
        "refined_text": "The `I2C` bus is hanging because a peripheral device pulled the data line low during a read transaction.\n\nClock the bus 9 times manually on the serial clock line until the slave releases the bus."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "we observed task starvation in the sensor polling loop because the logging task runs at a higher priority and starves the queue uh adjust the logging task priority to priority two and yield the c p u after writing each telemetry packet",
        "refined_text": "We observed task starvation in the sensor polling loop because the logging task runs at a higher priority and starves the queue.\n\nAdjust the logging task priority to priority 2 and yield the CPU after writing each telemetry packet."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "the s p i receiver triggers an interrupt on buffer overrun when high baud rates saturate the d m a controller double buffer the rx descriptor chain and clear the overrun flag in the s p i status register before starting the next transaction",
        "refined_text": "The `SPI` receiver triggers an interrupt on buffer overrun when high baud rates saturate the `DMA` controller.\n\nDouble buffer the RX descriptor chain and clear the overrun flag in the `SPI` status register before starting the next transaction."
    },
    # --- Medium 4 (25-90 words) ---
    {
        "raw_asr": "configure timer two with a prescaler of eighty four to achieve a one megahertz counter frequency from the eighty four megahertz internal clock then set the auto reload register to one thousand to generate a one millisecond periodic interrupt",
        "refined_text": "Configure timer 2 with a prescaler of 84 to achieve a 1 MHz counter frequency from the 84 MHz internal clock.\n\nThen set the auto reload register to 1000 to generate a 1 millisecond periodic interrupt."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "um the target board entered a hard fault exception during bootloader initializat when jumping to the application flash vector table inspection of the configurable fault status register shows an imprecise data bus error with the valid bit asserted the stacked program counter points to the memory map register access at address zero x four zero zero two one zero zero zero where the system clock configur was writing the phase lock loop multiplier the root cause is unclocked bus access because the peripheral bus clock was disabled while the register write was issued we need to enable the peripheral clock gating bit before writing the peripheral registers and clear the hard fault status flags in the system control block",
        "refined_text": "The target board entered a hard fault exception during bootloader initialization when jumping to the application flash vector table.\n\nInspection of the configurable fault status register shows an imprecise data bus error with the valid bit asserted. The stacked program counter points to the memory mapped register access at address 0x40021000 where the system clock configuration was writing the phase locked loop multiplier.\n\nThe root cause is unclocked bus access because the peripheral bus clock was disabled while the register write was issued. We need to enable the peripheral clock gating bit before writing the peripheral registers and clear the hard fault status flags in the system control block."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "we diagnosed corrupted audio samples in the analog to digital converter d m a circular buffer when running at forty eight kilohertz sampling rate the d m a transfer complete interrupt was colliding with the half transfer interrupt because the interrupt service routine processing time exceeded the half buffer window duration under high c p u load the d m a controller triggered a fifo underrun flag in the peripheral status register and overwrote unread audio frames we resolved the buffer corruption by expanding the circular buffer size from two hundred fifty six samples to five hundred twelve samples we also elevated the d m a interrupt priority above the communication tasks in the nested vectored interrupt controller and moved frame processing into a worker thread",
        "refined_text": "We diagnosed corrupted audio samples in the analog to digital converter DMA circular buffer when running at 48 kHz sampling rate.\n\nThe DMA transfer complete interrupt was colliding with the half transfer interrupt because the interrupt service routine processing time exceeded the half buffer window duration. Under high CPU load, the DMA controller triggered a FIFO underrun flag in the peripheral status register and overwrote unread audio frames.\n\nWe resolved the buffer corruption by expanding the circular buffer size from 256 samples to 512 samples. We also elevated the DMA interrupt priority above the communication tasks in the nested vectored interrupt controller and moved frame processing into a worker thread."
    }
]

if __name__ == "__main__":
    success = test_samples(batch_1)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
