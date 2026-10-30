import sys
from test_batch import test_samples

batch_3 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "set pin five high by writing zero x zero zero two zero to the bit set reset register",
        "refined_text": "Set pin 5 high by writing `0x0020` to the bit set reset register."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "configure external interrupt line zero to trigger on the falling edge",
        "refined_text": "Configure external interrupt line 0 to trigger on the falling edge."
    },
    # --- Short 3 (< 25 words) ---
    {
        "raw_asr": "um write two zero four eight to the twelve bit d a c data holding register",
        "refined_text": "Write 2048 to the 12-bit `DAC` data holding register."
    },
    # --- Short 4 (< 25 words) ---
    {
        "raw_asr": "enable the hardware c r c computation unit by setting bit zero in the control register",
        "refined_text": "Enable the hardware `CRC` computation unit by setting bit 0 in the control register."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "before increasing the system core clock to one hundred sixty eight megahertz you must set the flash latency to five wait states in the flash access control register otherwise the instruction prefetch buffer causes immediate bus faults on memory read operations",
        "refined_text": "Before increasing the system core clock to 168 MHz, you must set the flash latency to 5 wait states in the flash access control register.\n\nOtherwise, the instruction prefetch buffer causes immediate bus faults on memory read operations."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "execute the internal a d c calibration routine by asserting the calibration bit in the control register wait until hardware clears the calibration flag before programming the sampling time of fifty six clock cycles for analog channel three",
        "refined_text": "Execute the internal `ADC` calibration routine by asserting the calibration bit in the control register.\n\nWait until hardware clears the calibration flag before programming the sampling time of 56 clock cycles for analog channel 3."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "the d m a stream triggers a half transfer interrupt when the first sixty four bytes are received in memory read the initial payload block from the lower buffer half while the peripheral hardware fills the upper buffer half without interrupting the transfer",
        "refined_text": "The `DMA` stream triggers a half-transfer interrupt when the first 64 bytes are received in memory.\n\nRead the initial payload block from the lower buffer half while the peripheral hardware fills the upper buffer half without interrupting the transfer."
    },
    # --- Medium 4 (25-90 words) ---
    {
        "raw_asr": "um the timer registers return zero on read operations because the peripheral clock gating bit is cleared in the reset and clock control register enable the timer peripheral clock in the a p b one enable register before accessing any timer configuration registers",
        "refined_text": "The timer registers return 0 on read operations because the peripheral clock gating bit is cleared in the reset and clock control register.\n\nEnable the timer peripheral clock in the `APB1` enable register before accessing any timer configuration registers."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "the device firmware locks up during high speed logging over the virtual serial port because the u s b device controller enters an endpoint stall condition when the host stops polling the bulk in endpoint the peripheral transmission fifo fills up and triggers continuous buffer full interrupts the communication stack handles the full fifo by asserting a n a k handshake but the application layer continues pushing packets into the queue without checking the transmission complete callback this continuous queue insertion exhausts the heap memory and overwrites the active packet descriptor block we addressed the lockup by introducing a software flow control flag that pauses the logger when the u s b transmission buffer exceeds seventy five percent capacity we also added an endpoint reset routine that clears the stall flag and resets the data toggle sequence upon host bus enumerat",
        "refined_text": "The device firmware locks up during high-speed logging over the virtual serial port because the `USB` device controller enters an endpoint stall condition. When the host stops polling the bulk IN endpoint, the peripheral transmission FIFO fills up and triggers continuous buffer full interrupts.\n\nThe communication stack handles the full FIFO by asserting a `NAK` handshake, but the application layer continues pushing packets into the queue without checking the transmission complete callback. This continuous queue insertion exhausts the heap memory and overwrites the active packet descriptor block.\n\nWe addressed the lockup by introducing a software flow control flag that pauses the logger when the `USB` transmission buffer exceeds 75% capacity. We also added an endpoint reset routine that clears the stall flag and resets the data toggle sequence upon host bus enumeration."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the remote telemetry station suffered an unexpected reset cycle triggered by the independent watchdog timer during a flash memory erase operat on boot the reset status register confirmed that the watchdog reset flag was asserted while the software reset and pin reset flags were both clear because the core reset wiped the internal s ram variables the firmware inspected the battery backed backup registers to reconstruct the pre crash state the backup register contained the last executed state machine index of forty two along with the active sensor channel address zero x two zero we updated the bootloader initializat sequence to log the reset cause into the flash event log before clearing the reset flags we also refreshed the watchdog timer reload value to eight seconds to provide sufficient margin for high latency multi sector flash operations",
        "refined_text": "The remote telemetry station suffered an unexpected reset cycle triggered by the independent watchdog timer during a flash memory erase operation. On boot, the reset status register confirmed that the watchdog reset flag was asserted while the software reset and pin reset flags were both clear.\n\nBecause the core reset wiped the internal `SRAM` variables, the firmware inspected the battery backed backup registers to reconstruct the pre-crash state. The backup register contained the last executed state machine index of 42 along with the active sensor channel address `0x20`.\n\nWe updated the bootloader initialization sequence to log the reset cause into the flash event log before clearing the reset flags. We also refreshed the watchdog timer reload value to 8 seconds to provide sufficient margin for high-latency multi-sector flash operations."
    }
]

if __name__ == "__main__":
    success = test_samples(batch_3)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
