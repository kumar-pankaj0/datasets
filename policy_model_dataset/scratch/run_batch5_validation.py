import sys
from test_batch import test_samples

batch_5 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "enable the d a c output buffer by setting bit zero in the channel control register",
        "refined_text": "Enable the `DAC` output buffer by setting bit 0 in the channel control register."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "um read the thirty two bit unique device identifier register at address zero x one f f f seven a one zero",
        "refined_text": "Read the 32-bit unique device identifier register at address `0x1FFF7A10`."
    },
    # --- Short 3 (< 25 words) ---
    {
        "raw_asr": "configure the high speed external oscillator in bypass mode for an external clock signal",
        "refined_text": "Configure the high-speed external oscillator in bypass mode for an external clock signal."
    },
    # --- Short 4 (< 25 words) ---
    {
        "raw_asr": "trigger a software system reset by setting the system reset request bit in the application interrupt and reset control register",
        "refined_text": "Trigger a software system reset by setting the system reset request bit in the application interrupt and reset control register."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "configure m p u region zero as a thirty two byte unprivileged no access guard zone at the bottom of the task stack enable the memory management fault handler to catch stack overflows before they corrupt adjacent heap buffers",
        "refined_text": "Configure `MPU` region 0 as a 32-byte unprivileged no-access guard zone at the bottom of the task stack.\n\nEnable the memory management fault handler to catch stack overflows before they corrupt adjacent heap buffers."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "um configure the quad s p i peripheral for memory mapped mode using dummy cycles of six and instruction code zero x e b read throughput reaches forty megabytes per second directly from external nor flash without manual d m a transfers",
        "refined_text": "Configure the quad `SPI` peripheral for memory-mapped mode using dummy cycles of 6 and instruction code `0xEB`.\n\nRead throughput reaches 40 megabytes per second directly from external NOR flash without manual `DMA` transfers."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "the half bridge power stage experiences shoot through current because the high resolution timer dead time register was initialized to zero program twenty nanoseconds of dead time on complementary outputs before asserting the timer run bit",
        "refined_text": "The half-bridge power stage experiences shoot-through current because the high-resolution timer dead-time register was initialized to 0.\n\nProgram 20 nanoseconds of dead time on complementary outputs before asserting the timer run bit."
    },
    # --- Medium 4 (25-90 words) ---
    {
        "raw_asr": "when the window watchdog reaches counter value forty the early warning interrupt fires save the stacked program counter and link register into battery backed backup s ram before the hardware watchdog asserts system reset",
        "refined_text": "When the window watchdog reaches counter value 40, the early warning interrupt fires.\n\nSave the stacked program counter and link register into battery backed backup `SRAM` before the hardware watchdog asserts system reset."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "the industrial gateway dropped telemetry packets during heavy network broadcast traffic because the ethernet d m a receive descriptor ring suffered buffer starvation the ethernet peripheral asserted the receive buffer unavailable interrupt flag in the d m a status register when incoming frame bursts exhausted all allocated ring descriptors the network stack task was running at equal priority to the storage logger which delayed descriptor replenishment by sixteen milliseconds during flash write bursts while the d m a controller waited for ownership bits to clear the internal mac receive fifo overflowed and discarded four hundred incoming frames we resolved the packet drop issue by expanding the receive descriptor chain from thirty two descriptors to one hundred twenty eight descriptors we also increased the network processing task priority above the flash logger and enabled hardware checksum offloading in the ethernet mac configur register",
        "refined_text": "The industrial gateway dropped telemetry packets during heavy network broadcast traffic because the ethernet `DMA` receive descriptor ring suffered buffer starvation. The ethernet peripheral asserted the receive buffer unavailable interrupt flag in the `DMA` status register when incoming frame bursts exhausted all allocated ring descriptors.\n\nThe network stack task was running at equal priority to the storage logger, which delayed descriptor replenishment by 16 milliseconds during flash write bursts. While the `DMA` controller waited for ownership bits to clear, the internal `MAC` receive FIFO overflowed and discarded 400 incoming frames.\n\nWe resolved the packet drop issue by expanding the receive descriptor chain from 32 descriptors to 128 descriptors. We also increased the network processing task priority above the flash logger and enabled hardware checksum offloading in the ethernet `MAC` configuration register."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "the battery powered tracking node failed to wake up reliably from low power standby mode after entering deep sleep cycles current consumpt during stop mode measured forty milliamperes instead of the target fifteen microamperes which caused the internal low dropout regulator voltage to collapse below the brown out threshold inspection of the hardware schematics showed that eight unrouted general purpose input output pins on port c were left floating without pull up or pull down terminat resistors the floating inputs drifted through the intermediate logic threshold and triggered continuous parasitic switching current inside the input buffer stage we fixed the standby failure by reconfiguring all unrouted g p i o pins to analog mode in the pin mode register prior to entering stop mode the analog mode disables the digital input schmitt trigger which reduced sleep current to twelve microamperes and restored stable wake up timer operat",
        "refined_text": "The battery powered tracking node failed to wake up reliably from low-power standby mode after entering deep sleep cycles. Current consumption during stop mode measured 40 mA instead of the target 15 microamperes, which caused the internal low-dropout regulator voltage to collapse below the brown-out threshold.\n\nInspection of the hardware schematics showed that 8 unrouted general-purpose input output pins on port C were left floating without pull-up or pull-down termination resistors. The floating inputs drifted through the intermediate logic threshold and triggered continuous parasitic switching current inside the input buffer stage.\n\nWe fixed the standby failure by reconfiguring all unrouted `GPIO` pins to analog mode in the pin mode register prior to entering stop mode. The analog mode disables the digital input Schmitt trigger, which reduced sleep current to 12 microamperes and restored stable wake-up timer operation."
    }
]

if __name__ == "__main__":
    success = test_samples(batch_5)
    if not success:
        sys.exit(1)
    print("\nALL SAMPLES AND BATCH VALIDATION PASSED SUCCESSFULLY.")
