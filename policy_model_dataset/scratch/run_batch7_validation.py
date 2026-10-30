import sys
import json
from test_batch import test_samples

batch_7 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "um enable the timer three interrupt in the n v i c by writing one to the interrupt set enable register",
        "refined_text": "Enable the timer 3 interrupt in the `NVIC` by writing 1 to the interrupt set enable register."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "clear the watchdog timer interrupt flag by writing one to the status register",
        "refined_text": "Clear the watchdog timer interrupt flag by writing 1 to the status register."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "the i two c controller entered a bus error condition because the slave sensor held the serial clock line low during data transmiss reset the peripheral interface by generating nine clock pulses on the clock pin and cycling the peripheral enable bit in the control register",
        "refined_text": "The `I2C` controller entered a bus error condition because the slave sensor held the serial clock line low during data transmission.\n\nReset the peripheral interface by generating 9 clock pulses on the clock pin and cycling the peripheral enable bit in the control register."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "um the serial peripheral interface communicat failed during flash memory reads because the s p i clock prescaler was set too low divide the peripheral clock frequency by sixteen in the control register to maintain signal integrity",
        "refined_text": "The serial peripheral interface communication failed during flash memory reads because the `SPI` clock prescaler was set too low.\n\nDivide the peripheral clock frequency by 16 in the control register to maintain signal integrity."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "the analog to digital converter sampled inaccurate values because the internal calibrat routine never executed after power on write one to the calibrat start bit in the control register and wait for the hardware to clear the flag before starting convers",
        "refined_text": "The analog to digital converter sampled inaccurate values because the internal calibration routine never executed after power on.\n\nWrite 1 to the calibration start bit in the control register and wait for the hardware to clear the flag before starting conversion."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "the controller area network bus node stopped sending sensor messages because the transmit mailbox encountered an unhandled arbitrat loss when higher priority identifiers won bus access during peak traffic the hardware failed to clear the transmit error counter before the next frame request arrived the peripheral driver entered a passive error state and rejected all subsequent outbound frames from the applicat task inspect of the status register confirmed that the transmit error counter exceeded one hundred twenty eight while the mailbox request bit remained asserted um we corrected the issue by enabling the automatic retransmiss abort feature in the master control register the firmware now aborts blocked mailboxes after three consecutive arbitrat failures and flushes the software transmit queue upon detecting passive error status",
        "refined_text": """The controller area network bus node stopped sending sensor messages because the transmit mailbox encountered an unhandled arbitration loss. When higher priority identifiers won bus access during peak traffic, the hardware failed to clear the transmit error counter before the next frame request arrived.

The peripheral driver entered a passive error state and rejected all subsequent outbound frames from the application task. Inspection of the status register confirmed that the transmit error counter exceeded 128 while the mailbox request bit remained asserted.

We corrected the issue by enabling the automatic retransmission abort feature in the master control register. The firmware now aborts blocked mailboxes after 3 consecutive arbitration failures and flushes the software transmit queue upon detecting passive error status."""
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the system clock initializ routine triggered a hardware fault because the phase locked loop failed to achieve frequency lock within the timeout window the configur code switched the system clock source multiplexer to the phase locked loop output before the lock ready flag asserted in the clock control register because the clock tree operat without a valid reference signal peripheral bus transactions corrupted internal register states across the memory map further diagnosis demonstrated that the external crystal oscillator load capacitors introduced excessive startup delay which exceeded the default polling limit of two hundred iterations um we resolved the startup fault by extending the oscillator stabilizat loop to two thousand cycles and verifying the oscillator ready flag before configuring the multiplier registers the firmware now checks the phase locked loop ready bit and falls back to the internal high speed oscillator if frequency locking fails",
        "refined_text": """The system clock initialization routine triggered a hardware fault because the phase locked loop failed to achieve frequency lock within the timeout window. The configuration code switched the system clock source multiplexer to the phase locked loop output before the lock ready flag asserted in the clock control register.

Because the clock tree operated without a valid reference signal, peripheral bus transactions corrupted internal register states across the memory map. Further diagnosis demonstrated that the external crystal oscillator load capacitors introduced excessive startup delay which exceeded the default polling limit of 200 iterations.

We resolved the startup fault by extending the oscillator stabilization loop to 2000 cycles and verifying the oscillator ready flag before configuring the multiplier registers. The firmware now checks the phase locked loop ready bit and falls back to the internal high speed oscillator if frequency locking fails."""
    },
    # --- Long 3 (90+ words) ---
    {
        "raw_asr": "the pulse width modulat output produced severe motor drive current spikes because the timer capture compare register updated asynchronously during active counter cycles the software wrote new duty cycle values directly into the active compare register while the up counter was mid period this unbuffered register write caused the counter to miss the compare match event forcing the output pin to remain asserted high for an entire extra period of sixty four microseconds the resulting current pulse saturated the low side driver transistor and triggered the overcurrent protect comparator um we eliminated the output glitching by setting the capture compare preload enable bit in the timer control register the timer peripheral now buffers duty cycle modificat in preload shadow registers and transfers them synchronously into active registers only when an update event occurs at counter rollover",
        "refined_text": """The pulse width modulation output produced severe motor drive current spikes because the timer capture compare register updated asynchronously during active counter cycles. The software wrote new duty cycle values directly into the active compare register while the up counter was mid period.

This unbuffered register write caused the counter to miss the compare match event, forcing the output pin to remain asserted high for an entire extra period of 64 microseconds. The resulting current pulse saturated the low side driver transistor and triggered the overcurrent protection comparator.

We eliminated the output glitching by setting the capture compare preload enable bit in the timer control register. The timer peripheral now buffers duty cycle modifications in preload shadow registers and transfers them synchronously into active registers only when an update event occurs at counter rollover."""
    },
    # --- Long 4 (90+ words) ---
    {
        "raw_asr": "the audio output stream generated periodic acoustic popping sounds because the direct memory access controller experienced circular buffer underrun the interrupt service routine serviced only the transfer complete flag while ignoring the half transfer interrupt event this delay forced the audio processing thread to synthesize thirty two samples in a single processing burst which exceeded the execution budget of four milliseconds during peak processing load the d m a reader reached the buffer boundary before the synthesizer filled the next audio block which transmitted stale memory contents to the digital to analog converter um we eliminated the audio pops by enabling both half transfer and transfer complete interrupts in the d m a stream control register the firmware now fills each half of the ping pong buffer alternately which stabilizes processing latency across audio playback cycles",
        "refined_text": """The audio output stream generated periodic acoustic popping sounds because the direct memory access controller experienced circular buffer underrun. The interrupt service routine serviced only the transfer complete flag while ignoring the half transfer interrupt event.

This delay forced the audio processing thread to synthesize 32 samples in a single processing burst, which exceeded the execution budget of 4 milliseconds. During peak processing load, the `DMA` reader reached the buffer boundary before the synthesizer filled the next audio block, which transmitted stale memory contents to the digital to analog converter.

We eliminated the audio pops by enabling both half transfer and transfer complete interrupts in the `DMA` stream control register. The firmware now fills each half of the ping pong buffer alternately, which stabilizes processing latency across audio playback cycles."""
    },
    # --- Long 5 (90+ words) ---
    {
        "raw_asr": "the safety monitoring unit reset the microcontroller unexpectedly because the window watchdog timer detected an early reload attempt the applicat task refreshed the watchdog counter inside a rapid polling loop before the counter decremented past the allowed upper window threshold in window watchdog mode refreshing the counter when its value is higher than the window register value triggers an immediate system reset telemetry logs captured the window register value of eighty and showed the reload instruct executing while the down counter was still at one hundred ten um we resolved the reset condition by synchronizing watchdog servicing with the periodic operating system tick timer executing every twenty milliseconds the firmware now verifies that the counter has entered the valid refresh window below eighty before executing the reload sequence",
        "refined_text": """The safety monitoring unit reset the microcontroller unexpectedly because the window watchdog timer detected an early reload attempt. The application task refreshed the watchdog counter inside a rapid polling loop before the counter decremented past the allowed upper window threshold.

In window watchdog mode, refreshing the counter when its value is higher than the window register value triggers an immediate system reset. Telemetry logs captured the window register value of 80 and showed the reload instruction executing while the down counter was still at 110.

We resolved the reset condition by synchronizing watchdog servicing with the periodic operating system tick timer executing every 20 milliseconds. The firmware now verifies that the counter has entered the valid refresh window below 80 before executing the reload sequence."""
    }
]

if __name__ == "__main__":
    success = test_samples(batch_7)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
