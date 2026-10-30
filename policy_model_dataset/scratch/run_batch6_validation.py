import sys
from test_batch import test_samples

batch_6 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "write zero x zero two zero eight to the u art baud rate register",
        "refined_text": "Write `0x0208` to the `UART` baud rate register."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "um enable d m a stream zero by asserting bit zero in the configuration register",
        "refined_text": "Enable `DMA` stream 0 by asserting bit 0 in the configuration register."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "the i two c interface logs bus error because an external e e p r o m holds the serial clock line low during internal write cycles enable the clock stretching timeout feature in the control register to abort hung transactions after thirty milliseconds",
        "refined_text": "The `I2C` interface logs bus error because an external `EEPROM` holds the serial clock line low during internal write cycles.\n\nEnable the clock stretching timeout feature in the control register to abort hung transactions after 30 milliseconds."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "um the digital potentiometer ignores programming commands because the s p i chip select line deasserts before the eighth clock pulse finishes add a one microsecond software delay before pulling the slave select pin high",
        "refined_text": "The digital potentiometer ignores programming commands because the `SPI` chip select line deasserts before the eighth clock pulse finishes.\n\nAdd a 1 microsecond software delay before pulling the slave select pin high."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "the floating point calculation returns corrupted values after nested interrupts execute because automatic hardware stack frame stacking was disabled set bit thirty in the floating point context control register to enable lazy stacking of floating point registers",
        "refined_text": "The floating point calculation returns corrupted values after nested interrupts execute because automatic hardware stack frame stacking was disabled.\n\nSet bit 30 in the floating point context control register to enable lazy stacking of floating point registers."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "the target microcontroller failed to boot into the main applicat image because the bootloader detected a checksum mismatch across flash sector two the calculated thirty two bit cyclic redundancy check did not match the expected signature stored in the application header table inspect of the memory contents revealed that an interrupted power cycle during the firmware download corrupted eight bytes at address zero x zero eight zero zero four zero zero zero because the image integrity verificat returned an error flag the bootloader halted the core jump sequence to protect the system the bootloader entered recovery mode over the serial communicat port and signaled the diagnostic interface by flashing the status light emitting diode we restored normal operat by reflashing the application binary across the serial wire debug interface and verifying the sector signatures",
        "refined_text": """The target microcontroller failed to boot into the main application image because the bootloader detected a checksum mismatch across flash sector 2. The calculated 32-bit cyclic redundancy check did not match the expected signature stored in the application header table.

Inspection of the memory contents revealed that an interrupted power cycle during the firmware download corrupted 8 bytes at address 0x08004000. Because the image integrity verification returned an error flag, the bootloader halted the core jump sequence to protect the system.

The bootloader entered recovery mode over the serial communication port and signaled the diagnostic interface by flashing the status light emitting diode. We restored normal operation by reflashing the application binary across the serial wire debug interface and verifying the sector signatures."""
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the telemetry subsystem stopped transmitting data packets across the universal asynchronous receiver transmitter interface during high rate sensor logging the d m a transmiss stream entered a transfer error state because the software updated the memory base address register while a transfer was actively executing this concurrent register access violated the peripheral arbitrat protocol and caused the d m a controller to disable the stream channel and raise an interrupt flag because the firmware never serviced the error interrupt the u art transmit fifo filled to capacity and locked the transmitter state machine we resolved the transmitter lockup by checking the stream enable bit before modifying the memory address pointer and implementing a double buffered descriptor ring we also added an error recovery handler that clears the transfer error flag and restarts the transmission channel upon buffer underrun",
        "refined_text": """The telemetry subsystem stopped transmitting data packets across the universal asynchronous receiver transmitter interface during high rate sensor logging. The `DMA` transmission stream entered a transfer error state because the software updated the memory base address register while a transfer was actively executing.

This concurrent register access violated the peripheral arbitration protocol and caused the `DMA` controller to disable the stream channel and raise an interrupt flag. Because the firmware never serviced the error interrupt, the `UART` transmit FIFO filled to capacity and locked the transmitter state machine.

We resolved the transmitter lockup by checking the stream enable bit before modifying the memory address pointer and implementing a double buffered descriptor ring. We also added an error recovery handler that clears the transfer error flag and restarts the transmission channel upon buffer underrun."""
    },
    # --- Long 3 (90+ words) ---
    {
        "raw_asr": "the industrial controller experienced unexpected system resets whenever saving system calibrat parameters into the external serial peripheral interface e e p r o m the independent watchdog timer expired and asserted hardware reset during the sixty four byte page write sequence the driver was executing a blocking busy wait loop checking the write in progress bit in the e e p r o m status register without refreshing the watchdog counter because the physical write cycle required five milliseconds per page saving sixteen configur pages blocked the processor for eighty milliseconds we eliminated the reset condition by inserting a watchdog refresh call inside the busy polling loop and converting page writes into an asynchronous state machine the application now saves configuration pages across timer callbacks which preserves responsive watchdog servicing throughout the memory write operat",
        "refined_text": """The industrial controller experienced unexpected system resets whenever saving system calibration parameters into the external serial peripheral interface `EEPROM`. The independent watchdog timer expired and asserted hardware reset during the 64-byte page write sequence.

The driver was executing a blocking busy wait loop checking the write in progress bit in the `EEPROM` status register without refreshing the watchdog counter. Because the physical write cycle required 5 milliseconds per page, saving 16 configuration pages blocked the processor for 80 milliseconds.

We eliminated the reset condition by inserting a watchdog refresh call inside the busy polling loop and converting page writes into an asynchronous state machine. The application now saves configuration pages across timer callbacks, which preserves responsive watchdog servicing throughout the memory write operation."""
    },
    # --- Long 4 (90+ words) ---
    {
        "raw_asr": "the brushless motor driver suffered jitter and missed commutat steps when high rate debug logging was active over the serial interface the high priority motor control task executes every one millisecond but was blocked waiting on a queue lock shared with the telemetry logger the telemetry logger formatted verbose character strings inside a critical section while holding the queue mutex for up to three milliseconds because the logging task ran at low priority any intermediate priority communicat thread preempted it and extended the mutex lock duration we resolved the commutat jitter by separating the motor telemetry pipeline into a lock free circular ring buffer that requires zero mutex synchronizat we also transferred message formatting into a dedicated low priority background worker which prevents timing interference with the real time motor control loop",
        "refined_text": """The brushless motor driver suffered jitter and missed commutation steps when high rate debug logging was active over the serial interface. The high-priority motor control task executes every 1 millisecond but was blocked waiting on a queue lock shared with the telemetry logger.

The telemetry logger formatted verbose character strings inside a critical section while holding the queue mutex for up to 3 milliseconds. Because the logging task ran at low priority, any intermediate priority communication thread preempted it and extended the mutex lock duration.

We resolved the commutation jitter by separating the motor telemetry pipeline into a lock free circular ring buffer that requires zero mutex synchronization. We also transferred message formatting into a dedicated low-priority background worker, which prevents timing interference with the real-time motor control loop."""
    },
    # --- Long 5 (90+ words) ---
    {
        "raw_asr": "the battery monitoring unit reported erratic cell voltage readings because the analog to digital converter continuous scan mode produced channel misalignment in the d m a memory buffer voltage readings from analog channel zero were periodically shifted into the buffer index reserved for channel four the converter was configured for continuous convers while the d m a controller was triggered on an external timer update event when a high priority interrupt delayed the timer update the converter completed a conversion cycle before the previous data transfer finished which scrambled the channel sequence we eliminated the channel misalignment by switching the analog converter from continuous mode to timer triggered injected convers the hardware now samples all four analog channels synchronously upon each timer compare event and d m a transfers remain locked to the correct memory buffer indices",
        "refined_text": """The battery monitoring unit reported erratic cell voltage readings because the analog to digital converter continuous scan mode produced channel misalignment in the `DMA` memory buffer. Voltage readings from analog channel 0 were periodically shifted into the buffer index reserved for channel 4.

The converter was configured for continuous conversion while the `DMA` controller was triggered on an external timer update event. When a high-priority interrupt delayed the timer update, the converter completed a conversion cycle before the previous data transfer finished, which scrambled the channel sequence.

We eliminated the channel misalignment by switching the analog converter from continuous mode to timer triggered injected conversion. The hardware now samples all 4 analog channels synchronously upon each timer compare event, and `DMA` transfers remain locked to the correct memory buffer indices."""
    }
]

if __name__ == "__main__":
    success = test_samples(batch_6)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
