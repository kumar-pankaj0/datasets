import sys
from test_batch import test_samples

batch_4 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "set even parity by writing one to bit ten in the u art control register",
        "refined_text": "Set even parity by writing 1 to bit 10 in the `UART` control register."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "um sample the internal temperature sensor on analog channel sixteen",
        "refined_text": "Sample the internal temperature sensor on analog channel 16."
    },
    # --- Short 3 (< 25 words) ---
    {
        "raw_asr": "configure s p i mode three by setting both clock polarity and clock phase high",
        "refined_text": "Configure `SPI` mode 3 by setting both clock polarity and clock phase high."
    },
    # --- Short 4 (< 25 words) ---
    {
        "raw_asr": "clear the brown out reset flag by asserting bit twenty seven in the power control register",
        "refined_text": "Clear the brown-out reset flag by asserting bit 27 in the power control register."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "program the new firmware payload into flash bank two while running the application from bank one assert the bank swap bit in the user option bytes and initiate a system reset to boot the secondary flash bank",
        "refined_text": "Program the new firmware payload into flash bank 2 while running the application from bank 1.\n\nAssert the bank swap bit in the user option bytes and initiate a system reset to boot the secondary flash bank."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "the audio output sounds distorted because the i two s prescaler generates an incorrect master clock frequency configure the phase locked loop audio divider to eighteen and select sixteen bit data format on the serial sound bus",
        "refined_text": "The audio output sounds distorted because the `I2S` prescaler generates an incorrect master clock frequency.\n\nConfigure the phase locked loop audio divider to 18 and select 16-bit data format on the serial sound bus."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "um the window watchdog triggers an early reset if the software reloads the counter before the window value of eighty is reached program the counter reload routine to refresh the watchdog between sixty four and eighty counter ticks",
        "refined_text": "The window watchdog triggers an early reset if the software reloads the counter before the window value of 80 is reached.\n\nProgram the counter reload routine to refresh the watchdog between 64 and 80 counter ticks."
    },
    # --- Medium 4 (25-90 words) ---
    {
        "raw_asr": "the c a n controller entered the error passive state after detecting repetitive bit stuffing errors on the physical differential bus inspect the transmission error counter register and verify that the termination resistor across the bus lines measures one hundred twenty ohms",
        "refined_text": "The `CAN` controller entered the error passive state after detecting repetitive bit stuffing errors on the physical differential bus.\n\nInspect the transmission error counter register and verify that the termination resistor across the bus lines measures 120 ohms."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "the graphical interface task froze intermittently during sensor calibrat because of an unhandled priority inversion in the operating system scheduler the high priority display rendering thread was blocked waiting on a binary semaphore protecting the shared communicat bus a low priority telemetry task acquired the semaphore before being preempted by medium priority worker threads that executed continuous mathematical calculat because the medium priority threads never yielded the c p u the low priority task could not finish the bus access or release the semaphore we solved the interface freeze by replacing the binary semaphore with a free are toss mutex that implements automatic priority inheritance the kernel now temporarily elevates the priority of the semaphore owner to match the highest waiting thread which prevents medium priority starvat",
        "refined_text": "The graphical interface task froze intermittently during sensor calibration because of an unhandled priority inversion in the operating system scheduler. The high-priority display rendering thread was blocked waiting on a binary semaphore protecting the shared communication bus.\n\nA low-priority telemetry task acquired the semaphore before being preempted by medium-priority worker threads that executed continuous mathematical calculations. Because the medium-priority threads never yielded the CPU, the low-priority task could not finish the bus access or release the semaphore.\n\nWe solved the interface freeze by replacing the binary semaphore with a `FreeRTOS` mutex that implements automatic priority inheritance. The kernel now temporarily elevates the priority of the semaphore owner to match the highest waiting thread, which prevents medium-priority starvation."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the flight controller logged missing attitude vectors because the serial peripheral interface bus experienced collision between periodic inertial sensor reads and high bandwidth flash memory writes the sensor polling timer triggered a data acquisit interrupt while a six kilobyte flash write block was executing over d m a the interrupt service routine attempted to reconfigure the bus clock prescaler without checking the transfer active status bit in the peripheral control register this mid stream configur change corrupted the active d m a frame counter and triggered a hardware bus error flag in the s p i status register we resolved the bus collision by splitting the sensor and flash peripherals onto separate physical hardware buses with dedicated chip select lines we also configured the d m a controller to abort gracefully upon bus error and assert an alarm flag in the system diagnostic telemetry",
        "refined_text": "The flight controller logged missing attitude vectors because the serial peripheral interface bus experienced collision between periodic inertial sensor reads and high bandwidth flash memory writes. The sensor polling timer triggered a data acquisition interrupt while a 6 kilobyte flash write block was executing over `DMA`.\n\nThe interrupt service routine attempted to reconfigure the bus clock prescaler without checking the transfer active status bit in the peripheral control register. This mid-stream configuration change corrupted the active `DMA` frame counter and triggered a hardware bus error flag in the `SPI` status register.\n\nWe resolved the bus collision by splitting the sensor and flash peripherals onto separate physical hardware buses with dedicated chip select lines. We also configured the `DMA` controller to abort gracefully upon bus error and assert an alarm flag in the system diagnostic telemetry."
    }
]

if __name__ == "__main__":
    success = test_samples(batch_4)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
