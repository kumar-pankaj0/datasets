import sys
import json
import os

# Add scratch to sys.path to import test_batch helper
sys.path.append("scratch")
from test_batch import test_samples, validate_pair, validate_batch, clean_sample

batch_8 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "right one to the software interrupt trigger register buy writing to the e s p thirty two interrupt matrix",
        "refined_text": "Write 1 to the software interrupt trigger register by writing to the `ESP32` interrupt matrix."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "set the r p twenty forty p i o clock divider to zero x four zero wait right zero x ten instead buy updating the state machine control register",
        "refined_text": "Write 0x10 instead to the `RP2040` PIO clock divider by updating the state machine control register."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "the n r f fifty two b l e radio dropped packet transmiss power because the driver omitted the radio tx power configur write four to the transmit power register buy updating the peripheral settings before starting advertis",
        "refined_text": "The `nRF52` `BLE` radio dropped packet transmission power because the driver omitted the radio TX power configuration.\n\nWrite 4 to the transmit power register by updating the peripheral settings before starting advertising."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "the r i s c v core missed periodic timer interrupts because the firmware updated m time c m p without masking the timer interrupt enable bit in the m i e register right sixty four to the machine timer register buy clearing the interrupt flag before reloading the counter",
        "refined_text": "The `RISC-V` core missed periodic timer interrupts because the firmware updated `MTIMECMP` without masking the timer interrupt enable bit in the `MIE` register.\n\nWrite 64 to the machine timer register by clearing the interrupt flag before reloading the counter."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "basically the p m bus regulator flagged a communicat alert during voltage adjustment because packet error checking was disabled in the master controller write twenty to the control register buy appending the checksum byte to enable packet error checking on every transaction",
        "refined_text": "The `PMBus` regulator flagged a communication alert during voltage adjustment because packet error checking was disabled in the master controller.\n\nWrite 20 to the control register by appending the checksum byte to enable packet error checking on every transaction."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "the i three c bus controller failed during dynamic address assignment because two peripheral sensors responded simultaneously to the enter dynamic address common command code the bus arbitrat logic detected a data collision on the serial data line at clock cycle twelve which forced the host controller into an unhandled bus error state j link hardware trace logs showed that the second sensor node asserted its provisional identification register without checking the bus master priority bits um we isolated the timing fault by inspecting logic analyzer captures of the high speed bus transactions during slave enumerat the trace confirmed that the secondary sensor drive strength exceeded fifteen milliamperes which distorted the clock edges at twelve megahertz we resolved the communicat collision buy configuring the slave bus driver pull up registers and delaying target responses buy thirty two bus clock cycles the host controller now assigns dynamic address zero x five zero cleanly",
        "refined_text": "The `I3C` bus controller failed during dynamic address assignment because 2 peripheral sensors responded simultaneously to the enter dynamic address common command code. The bus arbitration logic detected a data collision on the serial data line at clock cycle 12, which forced the host controller into an unhandled bus error state.\n\n`J-Link` hardware trace logs showed that the second sensor node asserted its provisional identification register without checking the bus master priority bits. We isolated the timing fault by inspecting logic analyzer captures of the high speed bus transactions during slave enumeration.\n\nThe trace confirmed that the secondary sensor drive strength exceeded 15 milliamperes, which distorted the clock edges at 12 MHz. We resolved the communication collision by configuring the slave bus driver pull up registers and delaying target responses by 32 bus clock cycles. The host controller now assigns dynamic address 0x50 cleanly."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the e s p thirty two audio streaming device suffered audio playback glitching during flash write operat because core one experienced task starvat while core zero executed non volatile sector erases the high priority digital signal processing thread on core one attempted to pop samples from a shared free are toss queue while core zero held the cache control spinlock for twenty four milliseconds because the external s p i flash driver disabled the instruction cache during erase pulses core one stalled immediately on an external memory fetch debug telemetry recorded two hundred dropped audio frames and showed the playback buffer draining to zero um we eliminated the playback glitching buy moving the critical audio processing functions and queue descriptors into internal static r a m we also modified the flash driver buy yielding execution to the scheduler between sector erases which allows the audio thread to service buffer interrupts within thirty two microseconds",
        "refined_text": "The `ESP32` audio streaming device suffered audio playback glitching during flash write operations because core 1 experienced task starvation while core 0 executed non volatile sector erases. The high-priority digital signal processing thread on core 1 attempted to pop samples from a shared `FreeRTOS` queue while core 0 held the cache control spinlock for 24 milliseconds.\n\nBecause the external `SPI` flash driver disabled the instruction cache during erase pulses, core 1 stalled immediately on an external memory fetch. Debug telemetry recorded 200 dropped audio frames and showed the playback buffer draining to 0.\n\nWe eliminated the playback glitching by moving the critical audio processing functions and queue descriptors into internal static `RAM`. We also modified the flash driver by yielding execution to the scheduler between sector erases, which allows the audio thread to service buffer interrupts within 32 microseconds."
    },
    # --- Long 3 (90+ words) ---
    {
        "raw_asr": "the r p twenty forty data acquisit system halted unexpectedly during continuous analog sampling because both processor cores deadlocked on hardware spinlock seven core zero acquired the spinlock inside the high speed analog to digital converter interrupt handler while programming the d m a transfer descriptor chain at the same time core one attempted to acquire spinlock five wait core one attempted to acquire spinlock seven buy executing a blocking claim loop inside the sensor processing thread because the d m a transfer completed while core zero still held the lock the nested d m a completion interrupt re entered the spinlock claim routine on core zero creating a recursive locking condition logic analyzer captures confirmed that both cores remained trapped in hardware spinlock poll registers for over one hundred milliseconds um we resolved the spinlock lockup buy disabling local interrupts before claiming hardware spinlocks in both core contexts we also converted the analog sample pipeline into a lock free circular ring buffer sized to two hundred fifty six entries which completely decouples the d m a hardware writer from the processing task",
        "refined_text": "The `RP2040` data acquisition system halted unexpectedly during continuous analog sampling because both processor cores deadlocked on hardware spinlock 7. Core 0 acquired the spinlock inside the high speed analog to digital converter interrupt handler while programming the `DMA` transfer descriptor chain.\n\nAt the same time, core 1 attempted to acquire spinlock 7 by executing a blocking claim loop inside the sensor processing thread. Because the `DMA` transfer completed while core 0 still held the lock, the nested `DMA` completion interrupt re-entered the spinlock claim routine on core 0, creating a recursive locking condition. Logic analyzer captures confirmed that both cores remained trapped in hardware spinlock poll registers for over 100 milliseconds.\n\nWe resolved the spinlock lockup by disabling local interrupts before claiming hardware spinlocks in both core contexts. We also converted the analog sample pipeline into a lock-free circular ring buffer sized to 256 entries, which completely decouples the `DMA` hardware writer from the processing task."
    },
    # --- Long 4 (90+ words) ---
    {
        "raw_asr": "the n r f fifty two firmware update failed with a hard fault exception during high speed u art bootloader transmiss because the easy d m a controller encountered an invalid memory address configur the bootloader driver allocated a receive buffer in flash memory instead of internal r a m causing the easy d m a engine to trigger a memory protect violation upon receiving the initial binary image block when the d m a write failed the u art hardware asserted the buffer overrun error flag and dropped thirty two consecutive payload packets serial console traces confirmed that the fault occurred at address zero x twenty thousand where flash write access is strictly prohibited buy hardware um we resolved the firmware update failure buy allocating a dedicated receive staging buffer of two hundred fifty six bytes in internal static r a m we also updated the u art driver buy checking buffer pointer alignment before starting d m a transfers and clearing the error status register upon initializ",
        "refined_text": "The `nRF52` firmware update failed with a hard fault exception during high speed `UART` bootloader transmission because the EasyDMA controller encountered an invalid memory address configuration. The bootloader driver allocated a receive buffer in flash memory instead of internal `RAM`, causing the EasyDMA engine to trigger a memory protection violation upon receiving the initial binary image block.\n\nWhen the `DMA` write failed, the `UART` hardware asserted the buffer overrun error flag and dropped 32 consecutive payload packets. Serial console traces confirmed that the fault occurred at address 0x20000, where flash write access is strictly prohibited by hardware.\n\nWe resolved the firmware update failure by allocating a dedicated receive staging buffer of 256 bytes in internal static `RAM`. We also updated the `UART` driver by checking buffer pointer alignment before starting `DMA` transfers and clearing the error status register upon initialization."
    },
    # --- Long 5 (90+ words) ---
    {
        "raw_asr": "the r i s c v embedded supervisor kernel crashed during user task initializ because the machine mode trap delegat register failed to route system calls to supervisor mode when the user applicat executed an environment call instruct the processor trapped into machine mode instead of supervisor mode causing the kernel scheduler to halt execution with an unhandled exception code telemetry logs showed the machine trap value register captured an illegal delegat state at offset zero x one hundred while the physical memory protect unit blocked kernel memory access we corrected the trap delegat fault buy setting bit eight in the m e d e l e g register to route environment calls from user mode directly to supervisor mode we also configured the physical memory protect address register buy establishing sixteen memory regions with read right and execute permissions",
        "refined_text": "The `RISC-V` embedded supervisor kernel crashed during user task initialization because the machine mode trap delegation register failed to route system calls to supervisor mode. When the user application executed an environment call instruction, the processor trapped into machine mode instead of supervisor mode, causing the kernel scheduler to halt execution with an unhandled exception code.\n\nTelemetry logs showed the machine trap value register captured an illegal delegation state at offset 0x100 while the physical memory protection unit blocked kernel memory access.\n\nWe corrected the trap delegation fault by setting bit 8 in the `MEDELEG` register to route environment calls from user mode directly to supervisor mode. We also configured the physical memory protection address register by establishing 16 memory regions with read, write, and execute permissions."
    }
]

if __name__ == "__main__":
    success = test_samples(batch_8)
    if not success:
        print("ERROR: Validation failed!")
        sys.exit(1)
    
    output_path = "scratch/subagent_batch_8.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch_8, f, indent=2, ensure_ascii=False)
    print(f"\nSaved verified batch to {output_path}")
