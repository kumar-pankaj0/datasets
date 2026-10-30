import sys
import json
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

val_mod = load_module("validator", "code/validator.py")
clean_mod = load_module("cleaner", "code/cleaner.py")

validate_pair = val_mod.validate_pair
validate_batch = val_mod.validate_batch
clean_sample = clean_mod.clean_sample

batch_14 = [
    # Short 1 (< 25 words)
    {
        "raw_asr": "right zero x ten wait right zero x twenty to the s t m thirty two crypto accelerat control register buy clearing the key length bits",
        "refined_text": "Write 0x20 to the `STM32` crypto accelerator control register by clearing the key length bits."
    },
    # Short 2 (< 25 words)
    {
        "raw_asr": "set the r p twenty forty real time clock prescal divider to sixty four wait set it to one hundred twenty eight buy updating the r t c divider register",
        "refined_text": "Set the `RP2040` real-time clock prescaler divider to 128 by updating the `RTC` divider register."
    },
    # Medium 1 (25 to 90 words)
    {
        "raw_asr": "the s t m thirty two quad s p i interface failed memory mapped read operat because double transfer rate mode required eight dummy clock cycles instead of four set the prescal to two wait right eight to the q s p i dummy cycle register buy updating the memory mapped control configur",
        "refined_text": "The `STM32` quad `SPI` interface failed memory-mapped read operations because double transfer rate mode required 8 dummy clock cycles instead of 4.\n\nWrite 8 to the `QSPI` dummy cycle register by updating the memory-mapped control configuration."
    },
    # Medium 2 (25 to 90 words)
    {
        "raw_asr": "basically the e s p thirty two hardware s h a accelerator stalled during hash calculat because the peripheral clock gating register remained masked write zero x zero one wait write zero x zero three to the crypto clock enable register buy updating the peripheral power domain controller",
        "refined_text": "The `ESP32` hardware `SHA` accelerator stalled during hash calculation because the peripheral clock gating register remained masked.\n\nWrite 0x03 to the crypto clock enable register by updating the peripheral power domain controller."
    },
    # Medium 3 (25 to 90 words)
    {
        "raw_asr": "the r i s c v ethernet controller suffered packet frame check sequence errors during r m i i communicat because the fifty megahertz reference clock phase drifted relative two the receive data valid signal write two wait write four to the ethernet clock delay register buy updating the physical interface timing configur",
        "refined_text": "The `RISC-V` Ethernet controller suffered packet frame check sequence errors during `RMII` communication because the 50 megahertz reference clock phase drifted relative to the receive data valid signal.\n\nWrite 4 to the Ethernet clock delay register by updating the physical interface timing configuration."
    },
    # Long 1 (90+ words)
    {
        "raw_asr": "basically the s t m thirty two hardware a e s crypto engine stalled during block cipher encrypt because direct memory access requests were not synchroniz with the input f i f o status flags the cryptographic module processed two hundred fifty six bit keys in cipher block chaining mode streaming four kilobyte payload buffers from static r a m logic analyzer captures revealed that the direct memory access controller pushed sixteen byte blocks faster than the hardware crypto core could compute the cipher state which triggered an input buffer overrun error after sixty four wait after one hundred twenty eight bytes um hardware debugger register inspection showed that the key length field in the crypto control register was configured four one hundred twenty eight bits instead of two hundred fifty six bits while the d m a transfer complete interrupt flag remained masked in the peripheral status register core zero waited on the computation complete flag in an infinite loop while the crypto engine asserted a bus error on the ahb matrix we resolved the stall buy rewriting the crypto control register with the two hundred fifty six bit key size mask and reordering the initializ vector loading sequence we also enabled d m a burst handshake mode buy updating the crypto control register which synchronized input f i f o transfers and restored full cipher throughput at eighty megabits per second",
        "refined_text": "The `STM32` hardware `AES` crypto engine stalled during block cipher encryption because direct memory access requests were not synchronized with the input `FIFO` status flags. The cryptographic module processed 256-bit keys in cipher block chaining mode, streaming 4-kilobyte payload buffers from static `RAM`. Logic analyzer captures revealed that the direct memory access controller pushed 16-byte blocks faster than the hardware crypto core could compute the cipher state, which triggered an input buffer overrun error after 128 bytes.\n\nHardware debugger register inspection showed that the key length field in the crypto control register was configured for 128 bits instead of 256 bits, while the `DMA` transfer complete interrupt flag remained masked in the peripheral status register. Core 0 waited on the computation complete flag in an infinite loop while the crypto engine asserted a bus error on the AHB matrix.\n\nWe resolved the stall by rewriting the crypto control register with the 256-bit key size mask and reordering the initialization vector loading sequence. We also enabled `DMA` burst handshake mode by updating the crypto control register, which synchronized input `FIFO` transfers and restored full cipher throughput at 80 megabits per second."
    },
    # Long 2 (90+ words)
    {
        "raw_asr": "the r p twenty forty real time clock peripheral suffered calendar timing drift and missed wake up alarm events during low power sleep because the r t c prescal divider was miscalculated relative two the external crystal oscillator frequency the calendar subsystem clocked from an external thirty two kilohertz crystal driving the r t c integer and fractional prescaler registers oscilloscope probing showed that the crystal load capacitance was unbalanced buy twelve picofarads which pulled the actual reference clock frequency and generated an accumulat timing error of forty two seconds per day um logic analyzer traces confirmed that the alarm comparison register failed two assert the match interrupt when the calendar transitioned across minute boundaries because the synchronous prescal register cleared the sub second counter prematurely core zero missed three wait missed five consecutive scheduled sensor logging alarms while sleeping in low power dormant mode we corrected the timing drift buy programming the fractional prescal register with forty four instead of twenty eight and updating the integer prescaler two three hundred seventy five we also adjusted the r t c alarm control register buy enabling the sub second match mask which restored exact calendar synchronizat and eliminated missed alarm interrupts",
        "refined_text": "The `RP2040` real-time clock peripheral suffered calendar timing drift and missed wake-up alarm events during low-power sleep because the `RTC` prescaler divider was miscalculated relative to the external crystal oscillator frequency. The calendar subsystem clocked from an external 32 kilohertz crystal driving the `RTC` integer and fractional prescaler registers. Oscilloscope probing showed that the crystal load capacitance was unbalanced by 12 picofarads, which pulled the actual reference clock frequency and generated an accumulated timing error of 42 seconds per day.\n\nLogic analyzer traces confirmed that the alarm comparison register failed to assert the match interrupt when the calendar transitioned across minute boundaries, because the synchronous prescaler register cleared the sub-second counter prematurely. Core 0 missed 5 consecutive scheduled sensor logging alarms while sleeping in low-power dormant mode.\n\nWe corrected the timing drift by programming the fractional prescaler register with 44 instead of 28 and updating the integer prescaler to 375. We also adjusted the `RTC` alarm control register by enabling the sub-second match mask, which restored exact calendar synchronization and eliminated missed alarm interrupts."
    },
    # Long 3 (90+ words)
    {
        "raw_asr": "the e s p thirty two quad s p i memory mapped cache controller crashed during double transfer rate reads because the flash interface dummy clock cycles and input delay taps were misaligned at eighty megahertz the external flash chip supported quad d t r instruction execution streaming thirty two byte cache lines directly into internal instruction r a m oscilloscope measurements on the flash clock and data pins showed severe signal ringing that caused the quad s p i controller two sample data four wait sample data eight nanoseconds before the output valid window stabilized um diagnostic traces captured an instruction fetch abort when core zero executed code across cache page boundaries because the memory mapped controller read corrupted opcodes from flash address zero x forty the cache controller asserted an illegal instruction trap within sixteen clock cycles we eliminated the memory mapped crash buy configuring the dummy cycle register with six dummy cycles instead of four and setting the input clock delay tap register two fourteen steps we also updated the quad s p i timing configur register buy enabling the auto polling status check which stabilized memory mapped d t r throughput at sixty four megabytes per second",
        "refined_text": "The `ESP32` quad `SPI` memory-mapped cache controller crashed during double transfer rate reads because the flash interface dummy clock cycles and input delay taps were misaligned at 80 megahertz. The external flash chip supported quad `DTR` instruction execution, streaming 32-byte cache lines directly into internal instruction `RAM`. Oscilloscope measurements on the flash clock and data pins showed severe signal ringing that caused the quad `SPI` controller to sample data 8 nanoseconds before the output valid window stabilized.\n\nDiagnostic traces captured an instruction fetch abort when core 0 executed code across cache page boundaries, because the memory-mapped controller read corrupted opcodes from flash address 0x40. The cache controller asserted an illegal instruction trap within 16 clock cycles.\n\nWe eliminated the memory-mapped crash by configuring the dummy cycle register with 6 dummy cycles instead of 4 and setting the input clock delay tap register to 14 steps. We also updated the quad `SPI` timing configuration register by enabling the auto-polling status check, which stabilized memory-mapped `DTR` throughput at 64 megabytes per second."
    },
    # Long 4 (90+ words)
    {
        "raw_asr": "the s t m thirty two u s b o t g high speed controller failed high speed chirp handshake negotiat with external host controllers because the internal high speed p h y transceiver squelch threshold and pre emphasis registers were untuned when the peripheral detected host connection on the data plus and data minus lines the u s b device state machine attempted to initiate chirp sequence signalling at four hundred eighty megabits per second wi re shark protocol captures and oscilloscope traces revealed that high speed chirp j and chirp k signal amplitudes dropped below three hundred millivolts which caused the host controller two abort negotiat after twenty wait after forty milliseconds um hardware register inspection confirmed that the transceiver tuning register held the default reset value of zero x zero zero which left the transmit drive current at sixteen milliamperes core zero flagged a protocol error interrupt when the u s b core fell back two full speed twelve megabit mode we fixed the chirp negotiat failure buy writing zero x zero six to the p h y squelch calibrat register and programming thirty two to the transceiver pre emphasis register we also updated the u s b o t g control register buy clearing the transceiver suspend mask which stabilized high speed handshake detect and eliminated spurious bus reset interrupts",
        "refined_text": "The `STM32` `USB` `OTG` high-speed controller failed high-speed chirp handshake negotiation with external host controllers because the internal high-speed `PHY` transceiver squelch threshold and pre-emphasis registers were untuned. When the peripheral detected host connection on the data-plus and data-minus lines, the `USB` device state machine attempted to initiate chirp sequence signalling at 480 megabits per second. `Wireshark` protocol captures and oscilloscope traces revealed that high-speed chirp J and chirp K signal amplitudes dropped below 300 millivolts, which caused the host controller to abort negotiation after 40 milliseconds.\n\nHardware register inspection confirmed that the transceiver tuning register held the default reset value of 0x00, which left the transmit drive current at 16 milliamperes. Core 0 flagged a protocol error interrupt when the `USB` core fell back to full-speed 12 megabit mode.\n\nWe fixed the chirp negotiation failure by writing 0x06 to the `PHY` squelch calibration register and programming 32 to the transceiver pre-emphasis register. We also updated the `USB` `OTG` control register by clearing the transceiver suspend mask, which stabilized high-speed handshake detection and eliminated spurious bus reset interrupts."
    },
    # Long 5 (90+ words)
    {
        "raw_asr": "the r i s c v ethernet media access controller dropped ingress packets during high throughput r m i i transmiss because clock skew between the external fifty megahertz reference clock and receive data valid signals exceeded the hardware setup margin the network subsystem operated in reduced media independent interface mode with d m a ring buffers allocated in static r a m wi re shark packet traces and logic analyzer captures showed that the controller generated cyclic redundancy check errors on sixty four out of one thousand incoming jumbo frames whenever ambient temperature reached forty wait reached fifty degrees celsius um telemetry logs indicated that the physical layer transceiver suffered phase jitter on the reference clock pin which caused the receive state machine two miss the start frame delimiter byte core zero triggered an rx buffer descriptor error interrupt after thirty two consecutive packet drops we resolved the r m i i clock synchronizat failure buy programming twelve to the physical interface receive clock delay register and setting the clock phase invert bit in the ethernet control register we also updated the mac configur register buy enabling hardware checksum offload and increasing d m a descriptor ring depth two one hundred twenty eight entries which eliminated packet drops under continuous line rate traffic",
        "refined_text": "The `RISC-V` Ethernet media access controller dropped ingress packets during high-throughput `RMII` transmission because clock skew between the external 50 megahertz reference clock and receive data valid signals exceeded the hardware setup margin. The network subsystem operated in reduced media-independent interface mode with `DMA` ring buffers allocated in static `RAM`. `Wireshark` packet traces and logic analyzer captures showed that the controller generated cyclic redundancy check errors on 64 out of 1000 incoming jumbo frames whenever ambient temperature reached 50 degrees Celsius.\n\nTelemetry logs indicated that the physical layer transceiver suffered phase jitter on the reference clock pin, which caused the receive state machine to miss the start frame delimiter byte. Core 0 triggered an RX buffer descriptor error interrupt after 32 consecutive packet drops.\n\nWe resolved the `RMII` clock synchronization failure by programming 12 to the physical interface receive clock delay register and setting the clock phase invert bit in the Ethernet control register. We also updated the MAC configuration register by enabling hardware checksum offload and increasing `DMA` descriptor ring depth to 128 entries, which eliminated packet drops under continuous line-rate traffic."
    }
]

def main():
    print("Testing batch 14...")
    all_ok = True
    for idx, s in enumerate(batch_14):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = words / max(1, raw_words)
        tier = "Short" if words < 25 else ("Medium" if words <= 90 else "Long")
        
        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"[{status}] Sample {idx+1} ({tier}, {words} words, raw: {raw_words}, ratio: {ratio:.2f})")
        if not v_ok:
            print(f"  validator fail: {v_reason}")
        if c_res is None:
            print(f"  cleaner fail: {c_reason}")
            
    b_ok, b_reason, b_counts = validate_batch(batch_14, min_short=2, min_medium=3, min_long=5)
    print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
    print(f"Counts: {b_counts}")
    
    if all_ok and b_ok:
        with open("scratch/subagent_batch_14.json", "w", encoding="utf-8") as f:
            json.dump(batch_14, f, ensure_ascii=False, indent=2)
        print("\nSaved verified batch to scratch/subagent_batch_14.json")
    else:
        print("\nBatch had failures, not saved.")

if __name__ == "__main__":
    main()
