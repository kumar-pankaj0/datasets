import json
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
    # Tier 1: Short (< 25 words) - Sample 1
    # Chip: STM32, Topic: PMBus power management telemetry (reading voltage ADC register)
    {
        "raw_asr": "basically we read the p m b u s voltage a d c register zero x eight b on the s t m thirty two buy morning",
        "refined_text": "We read the PMBus voltage ADC register 0x8B on the STM32 by morning."
    },
    # Tier 1: Short (< 25 words) - Sample 2
    # Chip: RP2040, Topic: I2C bus recovery sequence (clock toggling 9 cycles to release stuck SDA)
    {
        "raw_asr": "uh the r p two zero four zero cleared the stuck i two c bus buy pulsing eight wait pulsing nine clock cycles",
        "refined_text": "The RP2040 cleared the stuck I2C bus by pulsing 9 clock cycles."
    },
    # Tier 2: Medium (25 to 90 words) - Sample 3
    # Chip: STM32, Topic: Hardware watchdog feeding during low-power stop mode
    {
        "raw_asr": "basically the s t m thirty two watchdog triggered a reset during stop mode because the counter expired before the r t c interrupt woke the processor after thirty wait forty milliseconds um right zero x a a a a two the watchdog key register before entering stop mode buy configuring the independent watchdog freeze bit configur",
        "refined_text": "The STM32 watchdog triggered a reset during stop mode because the counter expired before the RTC interrupt woke the processor after 40 milliseconds.\n\nWrite 0xAAAA to the watchdog key register before entering stop mode by configuring the independent watchdog freeze bit."
    },
    # Tier 2: Medium (25 to 90 words) - Sample 4
    # Chip: ESP32, Topic: SPI flash dual-quad mode pin multiplexing
    {
        "raw_asr": "um the e s p thirty two flash controller halted during quad s p i transmiss because the g p i o matrix routed the right protect line two g p i o eight wait two g p i o nine basically right zero x zero one two the peripheral multiplexing control register buy mapping the hold signal two g p i o ten",
        "refined_text": "The ESP32 flash controller halted during quad SPI transmission because the GPIO matrix routed the write-protect line to GPIO 9.\n\nWrite 0x01 to the peripheral multiplexing control register by mapping the hold signal to GPIO 10."
    },
    # Tier 2: Medium (25 to 90 words) - Sample 5
    # Chip: RP2040, Topic: UART baud rate fractional prescaler calculation under PLL jitter
    {
        "raw_asr": "the r p two zero four zero u art generated framing errors at one one five two zero zero baud because p l l jitter shifted the fractional prescaler divisor after sixteen wait after thirty two packets basically right forty two the u art fractional baud rate register buy setting the integer divisor two sixty seven",
        "refined_text": "The RP2040 UART generated framing errors at 115200 baud because PLL jitter shifted the fractional prescaler divisor after 32 packets.\n\nWrite 40 to the UART fractional baud rate register by setting the integer divisor to 67."
    },
    # Tier 3: Long (90+ words) - Sample 6
    # Chip: RISC-V, Topic: PMBus power management telemetry (reading voltage/current/temperature ADC registers)
    {
        "raw_asr": "basically the r i s c v controller failed two read p m b u s power management telemetry from the voltage regulator during thermal testing the firmware attempted two sample input voltage register zero x eight eight output current register zero x eight c and temperature a d c register zero x eight d across the shared i two c bus at four hundred kilohertz logic analyzer traces showed that the regulator pulled the s m b u s alert pin low after eight wait after sixteen read cycles halting telemetry updates um register inspection confirmed that the regulator flagged an unhandled overtemperature warning at eighty five degrees celsius the r i s c v core missed the alert interrupt because the peripheral interrupt mask register left bit four cleared continuous polling blocked the telemetry task queue while the a d c conversion buffer retained stale voltage measurements of ten wait twelve volts and thirty amperes we resolved the p m b u s telemetry failure buy setting bit four in the interrupt mask register two service the alert pin we updated the telemetry driver configur buy issuing clear faults command zero x zero three and reading status byte register zero x seven eight before resuming a d c conversions the regulator released the alert line and the r i s c v core resumed telemetry monitoring at one hundred kilohertz without further bus stalls",
        "refined_text": "The RISC-V controller failed to read PMBus power management telemetry from the voltage regulator during thermal testing. The firmware attempted to sample input voltage register 0x88, output current register 0x8C, and temperature ADC register 0x8D across the shared I2C bus at 400 kilohertz. Logic analyzer traces showed that the regulator pulled the SMBus alert pin low after 16 read cycles, halting telemetry updates.\n\nRegister inspection confirmed that the regulator flagged an unhandled overtemperature warning at 85 degrees Celsius. The RISC-V core missed the alert interrupt because the peripheral interrupt mask register left bit 4 cleared. Continuous polling blocked the telemetry task queue while the ADC conversion buffer retained stale voltage measurements of 12 volts and 30 amperes.\n\nWe resolved the PMBus telemetry failure by setting bit 4 in the interrupt mask register to service the alert pin. We updated the telemetry driver configuration by issuing clear faults command 0x03 and reading status byte register 0x78 before resuming ADC conversions. The regulator released the alert line, and the RISC-V core resumed telemetry monitoring at 100 kilohertz without further bus stalls."
    },
    # Tier 3: Long (90+ words) - Sample 7
    # Chip: nRF52, Topic: Hardware watchdog feeding during low-power stop mode
    {
        "raw_asr": "basically the n r f fifty two microcontroller suffered unexpected watchdog resets during extended low power system off sleep mode the application configured the hardware watchdog timer with a four thousand millisecond timeout while putting the radio core two sleep between bluetooth advertising intervals current measurement logs showed that the device drew two wait drew three microamperes during sleep but core resets occurred every four seconds uh register inspection through s e g g e r j link revealed that the watchdog config register bit zero was set two keep the timer running during sleep mode the firmware scheduled a real time clock timer interrupt two wake the c p u and reload the watchdog counter at three thousand milliseconds however an uncalibrated low frequency crystal oscillator drifted buy ten wait buy fifteen percent delaying the r t c wake up event until after the four thousand millisecond watchdog window closed we resolved the low power watchdog reset buy writing zero x zero one two the watchdog reload request register inside the r t c event handler we calibrated the thirty two kilohertz low frequency clock source using the internal r c oscillator calibrat timer every sixteen seconds we also increased the watchdog timeout interval two eight thousand milliseconds in the reload value register preventing premature system resets during sleep intervals",
        "refined_text": "The nRF52 microcontroller suffered unexpected watchdog resets during extended low-power system off sleep mode. The application configured the hardware watchdog timer with a 4000 millisecond timeout while putting the radio core to sleep between Bluetooth advertising intervals. Current measurement logs showed that the device drew 3 microamperes during sleep, but core resets occurred every 4 seconds.\n\nRegister inspection through SEGGER J-Link revealed that the watchdog config register bit 0 was set to keep the timer running during sleep mode. The firmware scheduled a real-time clock timer interrupt to wake the CPU and reload the watchdog counter at 3000 milliseconds. However, an uncalibrated low-frequency crystal oscillator drifted by 15 percent, delaying the RTC wake-up event until after the 4000 millisecond watchdog window closed.\n\nWe resolved the low-power watchdog reset by writing 0x01 to the watchdog reload request register inside the RTC event handler. We calibrated the 32 kilohertz low-frequency clock source using the internal RC oscillator calibration timer every 16 seconds. We also increased the watchdog timeout interval to 8000 milliseconds in the reload value register, preventing premature system resets during sleep intervals."
    },
    # Tier 3: Long (90+ words) - Sample 8
    # Chip: ESP32, Topic: SPI flash dual-quad mode pin multiplexing
    {
        "raw_asr": "basically the e s p thirty two secondary bootloader failed two switch external n o r flash from dual s p i in two quad s p i mode during high speed boot the memory subsystem functioned correctly in dual s p i at twenty wait at forty megahertz reading the partition table without errors however enabling quad mode triggered an immediate illegal instruction panic when the c p u fetched application instructions across the quad s p i interface um logic analyzer captures showed that the i o two right protect line and i o three hold line floated high during quad read commands the g p i o matrix multiplexer failed two route flash controller pins two g p i o nine and g p i o ten because the boot r o m pin override bits remained enabled the s p i flash chip ignored quad output fast read commands and returned zero x f f across two wait across all four data lines causing cache fetch misses across sixty four consecutive cache lines we resolved the quad s p i boot crash buy clearing the g p i o matrix override bits in the peripheral multiplexing control register we configured the g p i o pin function registers two map i o two two g p i o nine and i o three two g p i o ten with forty milliampere drive strength we also updated the flash clock divider register two run at eighty megahertz restoring zero wait state quad s p i instruction caching across both cores",
        "refined_text": "The ESP32 secondary bootloader failed to switch external NOR flash from dual SPI into quad SPI mode during high-speed boot. The memory subsystem functioned correctly in dual SPI at 40 megahertz, reading the partition table without errors. However, enabling quad mode triggered an immediate illegal instruction panic when the CPU fetched application instructions across the quad SPI interface.\n\nLogic analyzer captures showed that the IO2 write-protect line and IO3 hold line floated high during quad read commands. The GPIO matrix multiplexer failed to route flash controller pins to GPIO 9 and GPIO 10 because the boot ROM pin override bits remained enabled. The SPI flash chip ignored quad output fast read commands and returned 0xFF across all 4 data lines, causing cache fetch misses across 64 consecutive cache lines.\n\nWe resolved the quad SPI boot crash by clearing the GPIO matrix override bits in the peripheral multiplexing control register. We configured the GPIO pin function registers to map IO2 to GPIO 9 and IO3 to GPIO 10 with 40-milliampere drive strength. We also updated the flash clock divider register to run at 80 megahertz, restoring zero-wait-state quad SPI instruction caching across both cores."
    },
    # Tier 3: Long (90+ words) - Sample 9
    # Chip: RP2040, Topic: I2C bus recovery sequence (clock toggling 9 cycles to release stuck SDA)
    {
        "raw_asr": "basically the r p two zero four zero hardware i two c controller deadlocked during high speed sensor acquisition because a slave device pulled the s d a data line low mid byte the firmware attempted two read sixteen bytes of acceleration telemetry across i two c bus one wait bus zero at four hundred kilohertz a voltage glitch interrupted transmiss during the eighth data bit leaving the slave state machine holding s d a low indefinitely uh register inspection showed that the r p two zero four zero i two c master entered a permanent transmit abort state with bit five asserted in the interrupt status register the hardware controller could not generate a stop condition while s d a remained held low buy the slave the bus recovery timeout triggered after five hundred milliseconds blocking subsequent communicat across the shared sensor bus we resolved the bus deadlock buy taking software control of the s c l and s d a pins using the r p two zero four zero g p i o override registers the recovery routine generated eight wait nine manual clock pulses on s c l at one hundred kilohertz until the slave released s d a we then issued a manual stop condition re enabled the hardware i two c peripheral and resumed sensor telemetry reads without requiring a full board power cycle",
        "refined_text": "The RP2040 hardware I2C controller deadlocked during high-speed sensor acquisition because a slave device pulled the SDA data line low mid-byte. The firmware attempted to read 16 bytes of acceleration telemetry across I2C bus 0 at 400 kilohertz. A voltage glitch interrupted transmission during the eighth data bit, leaving the slave state machine holding SDA low indefinitely.\n\nRegister inspection showed that the RP2040 I2C master entered a permanent transmit abort state with bit 5 asserted in the interrupt status register. The hardware controller could not generate a STOP condition while SDA remained held low by the slave. The bus recovery timeout triggered after 500 milliseconds, blocking subsequent communication across the shared sensor bus.\n\nWe resolved the bus deadlock by taking software control of the SCL and SDA pins using the RP2040 GPIO override registers. The recovery routine generated 9 manual clock pulses on SCL at 100 kilohertz until the slave released SDA. We then issued a manual STOP condition, re-enabled the hardware I2C peripheral, and resumed sensor telemetry reads without requiring a full board power cycle."
    },
    # Tier 3: Long (90+ words) - Sample 10
    # Chip: STM32, Topic: UART baud rate fractional prescaler calculation under PLL jitter
    {
        "raw_asr": "basically the s t m thirty two microcontroller dropped incoming serial packets during high speed communicat because u a r t baud rate sampling drifted under p l l clock jitter the firmware configured u a r t one two operat at nine two one six zero zero baud using the internal high speed p l l clocked at seventy two megahertz receiver error counters logged twenty four wait logged forty eight framing errors and thirty two parity violations across one thousand incoming telemetry packets um register inspection revealed that the baud rate register integer mantissa and fractional prescaler were calculated using an idealized seventy two megahertz clock thermal drift and p l l phase jitter lowered the effective bus frequency buy two percent because the four bit fractional prescaler divider was set two four wait set two seven sampling clock error reached three percent causing the receiver two sample the stop bit outside the valid bit time window we resolved the serial packet corruption buy recalculating the fractional baud rate prescaler for the worst case clock frequency we wrote zero x two seven one two the baud rate register setting the integer divider two thirty nine and the fractional divider two one we also enabled sixteen times oversampling in the u a r t control register reducing sampling error below one percent and eliminating framing errors during continuous packet ingestion",
        "refined_text": "The STM32 microcontroller dropped incoming serial packets during high-speed communication because UART baud rate sampling drifted under PLL clock jitter. The firmware configured UART 1 to operate at 921600 baud using the internal high-speed PLL clocked at 72 megahertz. Receiver error counters logged 48 framing errors and 32 parity violations across 1000 incoming telemetry packets.\n\nRegister inspection revealed that the baud rate register integer mantissa and fractional prescaler were calculated using an idealized 72 megahertz clock. Thermal drift and PLL phase jitter lowered the effective bus frequency by 2 percent. Because the 4-bit fractional prescaler divider was set to 7, sampling clock error reached 3 percent, causing the receiver to sample the stop bit outside the valid bit time window.\n\nWe resolved the serial packet corruption by recalculating the fractional baud rate prescaler for the worst-case clock frequency. We wrote 0x271 to the baud rate register, setting the integer divider to 39 and the fractional divider to 1. We also enabled sixteen-times oversampling in the UART control register, reducing sampling error below 1 percent and eliminating framing errors during continuous packet ingestion."
    }
]

print("Validating individual pairs...")
for idx, s in enumerate(samples):
    ok, reason = validate_pair(s)
    if not ok:
        print(f"FAILED validate_pair on sample {idx+1}: {reason}")
        sys.exit(1)
    res, status = clean_sample(s["raw_asr"], s["refined_text"])
    if status != "kept":
        print(f"FAILED clean_sample on sample {idx+1}: {status}")
        sys.exit(1)
    w_raw = len(s["raw_asr"].split())
    w_ref = len(s["refined_text"].split())
    print(f"Sample {idx+1:2d}: validate_pair OK, clean_sample OK. Words: raw={w_raw:3d}, ref={w_ref:3d}, ratio={w_ref/w_raw:.2f}")

print("\nValidating batch...")
b_ok, b_reason, b_tiers = validate_batch(samples, min_short=2, min_medium=3, min_long=5)
if not b_ok:
    print(f"FAILED validate_batch: {b_reason}")
    sys.exit(1)

print(f"Batch validation: PASS ({b_reason})")
print(f"Tier counts: {b_tiers}")

# Save to scratch/subagent_batch_19.json
output_file = "scratch/subagent_batch_19.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"\nSaved verified batch to {output_file}")
