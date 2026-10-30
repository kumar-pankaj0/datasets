import json
import re
import sys
from pathlib import Path

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch = [
    # =========================================================================
    # TIER 1: SHORT (< 25 words) - 4 samples
    # Exactly 1 sentence, 0 newlines, max 1 cut-word restoration, >= 6-8 content words
    # =========================================================================

    # Sample 1: DMA scatter-gather descriptor link
    {
        "raw_asr": "um initializ the d m a scatter gather descriptor link address buy loading register zero x two zero with zero x four zero",
        "refined_text": "Initialize the DMA scatter-gather descriptor link address by loading register 0x20 with 0x40."
    },

    # Sample 2: NVIC preemption priority
    {
        "raw_asr": "uh configur the n v i c preemption priority buy writing level two into the timer interrupt priority register",
        "refined_text": "Configure the NVIC preemption priority by writing level 2 into the timer interrupt priority register."
    },

    # Sample 3: Bootloader CRC verification
    {
        "raw_asr": "basically validat the bootloader c r c checksum buy checking the thirty two bit calculation against register zero x five zero",
        "refined_text": "Validate the bootloader CRC checksum by checking the 32-bit calculation against register 0x50."
    },

    # Sample 4: Brownout reset detection circuit
    {
        "raw_asr": "um calibrat the brownout reset detection circuit buy writing threshold value three into the control register",
        "refined_text": "Calibrate the brownout reset detection circuit by writing threshold value 3 into the control register."
    },

    # =========================================================================
    # TIER 2: MEDIUM (25 to 89 words) - 6 samples
    # 1 to 3 sentences, natural \n\n break between distinct thoughts, max \n\n breaks <= len(words)//25
    # =========================================================================

    # Sample 5: I2S DAC master clock divider
    {
        "raw_asr": "basically configur the i two s d a c master clock buy setting the serial clock prescaler to four right eight wait right sixteen instead into the frame sync divider register the audio codec synchronizes stereo samples across the bus at forty eight kilohertz",
        "refined_text": "Configure the I2S DAC master clock by setting the serial clock prescaler to 4. Write 16 instead into the frame sync divider register.\n\nThe audio codec synchronizes stereo samples across the bus at 48 kilohertz."
    },

    # Sample 6: USB CDC endpoint descriptors
    {
        "raw_asr": "uh initializ the u s b c d c endpoint descriptors buy setting the bulk in transfer size to sixty four bytes right thirty two wait right sixty four instead into the packet buffer size register the device enumerates as a virtual serial port buy registering descriptor table zero x zero two",
        "refined_text": "Initialize the USB CDC endpoint descriptors by setting the bulk IN transfer size to 64 bytes. Write 64 instead into the packet buffer size register.\n\nThe device enumerates as a virtual serial port by registering descriptor table 0x02."
    },

    # Sample 7: Hardware timer PWM generation
    {
        "raw_asr": "okay so configur the hardware timer reload value buy loading register zero x three zero with one thousand right twenty wait right fifty instead into the capture compare register the timer generates pulse width modulation waveforms buy cycling the counter at sixteen megahertz",
        "refined_text": "Configure the hardware timer reload value by loading register 0x30 with 1000. Write 50 instead into the capture compare register.\n\nThe timer generates pulse width modulation waveforms by cycling the counter at 16 megahertz."
    },

    # Sample 8: Watchdog refresh window
    {
        "raw_asr": "um adjust the watchdog refresh window buy programming register zero x four eight with sixty four right one hundred wait right one hundred twenty eight instead into the down counter reload field the system triggers an early warning interrupt buy comparing the counter against threshold eight",
        "refined_text": "Adjust the watchdog refresh window by programming register 0x48 with 64. Write 128 instead into the down counter reload field.\n\nThe system triggers an early warning interrupt by comparing the counter against threshold 8."
    },

    # Sample 9: Brownout reset threshold
    {
        "raw_asr": "basically configur the brownout reset threshold buy writing level four into the power supply supervisor register right two wait right three instead into the brownout falling edge detection register the voltage monitor triggers a hardware reset buy holding the reset line low",
        "refined_text": "Configure the brownout reset threshold by writing level 4 into the power supply supervisor register. Write 3 instead into the brownout falling edge detection register.\n\nThe voltage monitor triggers a hardware reset by holding the reset line low."
    },

    # Sample 10: DMA scatter-gather circular chaining
    {
        "raw_asr": "uh allocat the d m a scatter gather transfer table buy linking descriptor zero x one zero to descriptor zero x two zero right twelve wait right sixteen instead into the transfer count field the controller performs sequential memory copies buy cycling through the linked descriptor chain",
        "refined_text": "Allocate the DMA scatter-gather transfer table by linking descriptor 0x10 to descriptor 0x20. Write 16 instead into the transfer count field.\n\nThe controller performs sequential memory copies by cycling through the linked descriptor chain."
    },

    # =========================================================================
    # TIER 3: LONG (90+ words) - 10 samples
    # Multi-paragraph (\n\n), natural spoken engineer narration, 0 numbered checklists
    # =========================================================================

    # Sample 11: USB CDC descriptors and DMA buffer management on nRF52840
    {
        "raw_asr": "okay so our n r f fifty two eight four zero telemetry module experienced recurring packet drops and endpoint stall conditions during continuous sensor log downloads buy the host machine we connected a hardware protocol analyzer to the u s b bus and verified that the bulk in endpoint descriptor became misaligned because the d m a controller operated with a single flat transfer buffer without ping pong switching the high priority radio baseband interrupt delayed the endpoint buffer reload buy over two milliseconds while incoming telemetry filled the packet buffer um we resolved endpoint stalling buy migrating the u s b c d c endpoint configuration to dual packet d m a buffers configur the endpoint memory mapping register buy allocating two separate sixty four byte endpoints in packet r a m right thirty two wait right sixty four instead into the endpoint packet length register to match full speed u s b bulk transfers basically we also updated the descriptor table pointer buy loading register zero x four zero with the alternate buffer base address right priority level two into the u s b interrupt priority field after activating dual packet buffering and remapping the endpoint descriptors the device maintained continuous twenty megabit throughput without frame errors or communication stalls across extended diagnostic sessions",
        "refined_text": "Our nRF52840 telemetry module experienced recurring packet drops and endpoint stall conditions during continuous sensor log downloads by the host machine. We connected a hardware protocol analyzer to the USB bus and verified that the bulk IN endpoint descriptor became misaligned because the DMA controller operated with a single flat transfer buffer without ping-pong switching. The high-priority radio baseband interrupt delayed the endpoint buffer reload by over 2 milliseconds while incoming telemetry filled the packet buffer.\n\nWe resolved endpoint stalling by migrating the USB CDC endpoint configuration to dual-packet DMA buffers. Configure the endpoint memory mapping register by allocating two separate 64-byte endpoints in packet RAM. Write 64 instead into the endpoint packet length register to match full-speed USB bulk transfers.\n\nWe also updated the descriptor table pointer by loading register 0x40 with the alternate buffer base address. Write priority level 2 into the USB interrupt priority field. After activating dual-packet buffering and remapping the endpoint descriptors, the device maintained continuous 20-megabit throughput without frame errors or communication stalls across extended diagnostic sessions."
    },

    # Sample 12: I2S DAC clocks and PLL fractional synthesizer on ESP32-S3
    {
        "raw_asr": "uh our e s p thirty two s three smart audio gateway suffered noticeable harmonic distortion and jitter on the line out port during simultaneous wi fi transmission we attached a digital oscilloscope to the i two s master clock line and observed that the clock signal exhibited twenty nanoseconds of phase jitter because the audio p l l shared a clock divider with the peripheral bus clock the master clock frequency drifted buy several kilohertz whenever the c p u frequency scaled buy switching between operating states um we resolved the clock jitter buy isolating the audio clock path using a dedicated integer p l l divider configur the i two s clock control register buy selecting the independent audio pll source right twenty four wait right forty eight instead into the sample rate divider register to generate an exact forty eight kilohertz sampling clock basically we also configur the d m a audio transfer ring buffer buy allocating eight circular descriptors right zero x three eight into the i two s d a c control register to lock the frame sync alignment after isolating the audio clock generation and programming the dedicated divider the codec output achieved clean stereo reproduction without phase jitter or harmonic distortion across long playback tests",
        "refined_text": "Our ESP32-S3 smart audio gateway suffered noticeable harmonic distortion and jitter on the line out port during simultaneous Wi-Fi transmission. We attached a digital oscilloscope to the I2S master clock line and observed that the clock signal exhibited 20 nanoseconds of phase jitter because the audio PLL shared a clock divider with the peripheral bus clock. The master clock frequency drifted by several kilohertz whenever the CPU frequency scaled by switching between operating states.\n\nWe resolved the clock jitter by isolating the audio clock path using a dedicated integer PLL divider. Configure the I2S clock control register by selecting the independent audio PLL source. Write 48 instead into the sample rate divider register to generate an exact 48 kilohertz sampling clock.\n\nWe also configured the DMA audio transfer ring buffer by allocating 8 circular descriptors. Write 0x38 into the I2S DAC control register to lock the frame sync alignment. After isolating the audio clock generation and programming the dedicated divider, the codec output achieved clean stereo reproduction without phase jitter or harmonic distortion across long playback tests."
    },

    # Sample 13: Bootloader CRC verification and dual-bank staging on RP2040
    {
        "raw_asr": "basically our r p twenty forty industrial controller experienced unrecoverable boot loops after interrupted over the air firmware updates in remote field deployments we analyzed the flash memory layout using a j tag debugger and discovered that the system jumped into partially erased application partitions because the bootloader lacked atomic staging verificat the old bootloader checked only a sixteen bit header word rather than computing a full image checksum over the binary payload um we eliminated firmware corruption buy implementing dual bank flash partitioning with hardware c r c validation configur the bootloader staging table buy defining two separate two hundred fifty six kilobyte application banks in external flash right sixteen wait right thirty two instead into the hardware c r c polynomial register to select thirty two bit c r c computation okay so we also configur the boot status register buy writing zero x two zero into the partition switch register after confirming matching checksum values across the staging bank after enabling full partition c r c checks and dual bank switching the bootloader rejected corrupted image uploads and executed reliable firmware updates across two hundred test reset cycles",
        "refined_text": "Our RP2040 industrial controller experienced unrecoverable boot loops after interrupted over-the-air firmware updates in remote field deployments. We analyzed the flash memory layout using a JTAG debugger and discovered that the system jumped into partially erased application partitions because the bootloader lacked atomic staging verification. The old bootloader checked only a 16-bit header word rather than computing a full image checksum over the binary payload.\n\nWe eliminated firmware corruption by implementing dual-bank flash partitioning with hardware CRC validation. Configure the bootloader staging table by defining two separate 256-kilobyte application banks in external flash. Write 32 instead into the hardware CRC polynomial register to select 32-bit CRC computation.\n\nWe also configured the boot status register by writing 0x20 into the partition switch register after confirming matching checksum values across the staging bank. After enabling full partition CRC checks and dual-bank switching, the bootloader rejected corrupted image uploads and executed reliable firmware updates across 200 test reset cycles."
    },

    # Sample 14: NVIC preemption priorities and timer interrupt starvation on STM32G4
    {
        "raw_asr": "uh our s t m thirty two g four motor drive board experienced current sampling jitter and missed field oriented control commutations under heavy c a n f d bus traffic we probed the p w m timer interrupt line with a logic analyzer and confirmed that incoming c a n frames delayed the current feedback loop buy up to twenty five microseconds because both interrupt lines shared equal preemption priority level zero the high frequency motor control loop was starved whenever consecutive telemetry packets arrived on the bus um we resolved interrupt starvation buy restructuring the n v i c priority groups configur the n v i c priority grouping register buy setting four bits of preemption priority and zero bits of subpriority right one wait right zero instead into the p w m timer interrupt priority register to assign the motor control loop the highest preemption level basically we also adjusted the communication handlers buy setting the c a n receive interrupt priority to level three right zero x zero c into the system control register to lock the priority map after reassigning the preemption levels the motor control interrupt executed with sub microsecond latency without missing PWM cycles during peak bus communicat",
        "refined_text": "Our STM32G4 motor drive board experienced current sampling jitter and missed field-oriented control commutations under heavy CAN-FD bus traffic. We probed the PWM timer interrupt line with a logic analyzer and confirmed that incoming CAN frames delayed the current feedback loop by up to 25 microseconds because both interrupt lines shared equal preemption priority level 0. The high-frequency motor control loop was starved whenever consecutive telemetry packets arrived on the bus.\n\nWe resolved interrupt starvation by restructuring the NVIC priority groups. Configure the NVIC priority grouping register by setting 4 bits of preemption priority and 0 bits of subpriority. Write 0 instead into the PWM timer interrupt priority register to assign the motor control loop the highest preemption level.\n\nWe also adjusted the communication handlers by setting the CAN receive interrupt priority to level 3. Write 0x0C into the system control register to lock the priority map. After reassigning the preemption levels, the motor control interrupt executed with sub-microsecond latency without missing PWM cycles during peak bus communication."
    },

    # Sample 15: Brownout reset detection and flash protection on SAMD51
    {
        "raw_asr": "okay so our s a m d fifty one environmental telemetry logger suffered silent parameter corruption in internal non volatile flash memory during slow battery voltage drops we captured the three volt power rail using an oscilloscope and discovered that the c p u continued running as voltage decayed below two volts triggering erratic flash write cycles before the clock halted the microcontroller lacked hardware brownout reset enforcement causing uninitialized register states to corrupt configuration blocks um we eliminated flash corruption buy activating the internal brownout detector with hardware reset generation configur the brownout monitor control register buy setting the detection threshold to level seven right two wait right one instead into the brownout action register to trigger an immediate hardware reset rather than a software interrupt basically we also configur the reset filter buy programming a five microsecond debounce delay right zero x zero one into the power manager control register to lock the supervisor settings after enabling the brownout monitor the system executed clean resets across fifty slow supply decay cycles without damaging stored parameters or flash memory sectors",
        "refined_text": "Our SAMD51 environmental telemetry logger suffered silent parameter corruption in internal non-volatile flash memory during slow battery voltage drops. We captured the 3-volt power rail using an oscilloscope and discovered that the CPU continued running as voltage decayed below 2 volts, triggering erratic flash write cycles before the clock halted. The microcontroller lacked hardware brownout reset enforcement, causing uninitialized register states to corrupt configuration blocks.\n\nWe eliminated flash corruption by activating the internal brownout detector with hardware reset generation. Configure the brownout monitor control register by setting the detection threshold to level 7. Write 1 instead into the brownout action register to trigger an immediate hardware reset rather than a software interrupt.\n\nWe also configured the reset filter by programming a 5-microsecond debounce delay. Write 0x01 into the power manager control register to lock the supervisor settings. After enabling the brownout monitor, the system executed clean resets across 50 slow supply decay cycles without damaging stored parameters or flash memory sectors."
    },

    # Sample 16: DMA scatter-gather descriptor chaining for Ethernet MAC on RISC-V CH32V307
    {
        "raw_asr": "uh our r i s c v c h thirty two v three zero seven industrial gateway dropped high speed network packets and suffered descriptor ring collisions under heavy u d p traffic bursts we examined the m a c receive ring using an external logic analyzer and found that the Ethernet controller halted because the d m a transfer descriptors ran out of memory space during back to back packet receptions the original driver used a single contiguous memory block which locked the receive engine whenever a packet exceeded the default buffer boundary um we eliminated packet drops buy implementing a linked scatter gather d m a descriptor ring configur the Ethernet d m a descriptor table buy creating sixteen linked buffer descriptors in non cacheable memory right sixty four wait right one hundred twenty eight instead into the descriptor buffer size register to support variable length network frames basically we also configur the d m a control register buy enabling normal interrupt summary and receive complete flags right zero x one c into the m a c interrupt enable register to handle packet processing in the background after deploying the scatter gather ring the network interface processed continuous sixty megabit packet streams without buffer overruns or dropped frames across twenty four hours of load testing",
        "refined_text": "Our RISC-V CH32V307 industrial gateway dropped high-speed network packets and suffered descriptor ring collisions under heavy UDP traffic bursts. We examined the MAC receive ring using an external logic analyzer and found that the Ethernet controller halted because the DMA transfer descriptors ran out of memory space during back-to-back packet receptions. The original driver used a single contiguous memory block, which locked the receive engine whenever a packet exceeded the default buffer boundary.\n\nWe eliminated packet drops by implementing a linked scatter-gather DMA descriptor ring. Configure the Ethernet DMA descriptor table by creating 16 linked buffer descriptors in non-cacheable memory. Write 128 instead into the descriptor buffer size register to support variable-length network frames.\n\nWe also configured the DMA control register by enabling normal interrupt summary and receive complete flags. Write 0x1C into the MAC interrupt enable register to handle packet processing in the background. After deploying the scatter-gather ring, the network interface processed continuous 60-megabit packet streams without buffer overruns or dropped frames across 24 hours of load testing."
    },

    # Sample 17: Watchdog refresh window and long crypto operations on LPC55S69
    {
        "raw_asr": "basically our l p c fifty five s six nine automated medical controller triggered unexpected hardware watchdog resets during cryptographic signature verificat of patient prescription tokens we connected a debug trace probe to the board and confirmed that r s a modular exponentiation took eighty milliseconds which exceeded the fifty millisecond watchdog trip window the windowed watchdog fired a reset because the firmware refreshed the counter either too early or too late relative to the valid reload window um we eliminated spurious watchdog resets buy widening the watchdog refresh window and adding an intermediate refresh hook configur the windowed watchdog timer buy setting the input clock prescaler to sixty four right one hundred wait right two hundred fifty instead into the watchdog reload register to extend the maximum timeout period to one hundred twenty milliseconds okay so we also configur the window threshold register buy loading thirty two into the upper window boundary field right zero x four four into the watchdog control register to lock the configuration against unauthorized modification after updating the window parameters and timer prescaler the controller verified complex cryptographic signatures without triggering watchdog resets during repetitive infusion cycles",
        "refined_text": "Our LPC55S69 automated medical controller triggered unexpected hardware watchdog resets during cryptographic signature verification of patient prescription tokens. We connected a debug trace probe to the board and confirmed that RSA modular exponentiation took 80 milliseconds, which exceeded the 50-millisecond watchdog trip window. The windowed watchdog fired a reset because the firmware refreshed the counter either too early or too late relative to the valid reload window.\n\nWe eliminated spurious watchdog resets by widening the watchdog refresh window and adding an intermediate refresh hook. Configure the windowed watchdog timer by setting the input clock prescaler to 64. Write 250 instead into the watchdog reload register to extend the maximum timeout period to 120 milliseconds.\n\nWe also configured the window threshold register by loading 32 into the upper window boundary field. Write 0x44 into the watchdog control register to lock the configuration against unauthorized modification. After updating the window parameters and timer prescaler, the controller verified complex cryptographic signatures without triggering watchdog resets during repetitive infusion cycles."
    },

    # Sample 18: Hardware timer quadrature encoder interface on STM32F7
    {
        "raw_asr": "uh our s t m thirty two f seven robotic joint servo suffered position drift and missed encoder step counts during high speed direction reversals we monitored encoder channels a and b using a mixed signal oscilloscope and observed high frequency mechanical contact bounce that tricked the timer into counting false edges the timer input filter was disabled buy default causing contact ringing to corrupt the thirty two bit position counter during sudden deceleration um we restored encoder tracking buy enabling the hardware timer quadrature encoder interface with digital noise filtering configur hardware timer two buy setting the slave mode controller to encoder interface mode three right five one two wait right one zero two four instead into the auto reload register to match the encoder disc resolution basically we also configur the input capture filter buy loading eight into the channel input filter field right zero x two eight into the timer control register to enable the digital filter clock after activating the quadrature encoder mode and input filter the servo controller maintained exact position tracking within one encoder count without drift across ten thousand reversal cycles",
        "refined_text": "Our STM32F7 robotic joint servo suffered position drift and missed encoder step counts during high-speed direction reversals. We monitored encoder channels A and B using a mixed-signal oscilloscope and observed high-frequency mechanical contact bounce that tricked the timer into counting false edges. The timer input filter was disabled by default, causing contact ringing to corrupt the 32-bit position counter during sudden deceleration.\n\nWe restored encoder tracking by enabling the hardware timer quadrature encoder interface with digital noise filtering. Configure hardware timer 2 by setting the slave mode controller to encoder interface mode 3. Write 1024 instead into the auto-reload register to match the encoder disc resolution.\n\nWe also configured the input capture filter by loading 8 into the channel input filter field. Write 0x28 into the timer control register to enable the digital filter clock. After activating the quadrature encoder mode and input filter, the servo controller maintained exact position tracking within 1 encoder count without drift across 10000 reversal cycles."
    },

    # Sample 19: Brownout reset detection and RTC domain on CC1352P
    {
        "raw_asr": "basically our c c thirteen fifty two p agricultural sensor node lost its real time clock calendar configuration whenever field technicians replaced the coin cell battery we analyzed the supply rail decay buy probing the r t c power domain with an oscilloscope and found that residual voltage hovered around one volt for forty milliseconds during battery disconnection the slow voltage decay caused internal logic gates to enter metastable states which corrupted the calendar registers before the backup supply engaged um we prevented r t c state loss buy enabling the dedicated backup domain brownout detector configur the backup domain voltage monitor buy setting the trip threshold to level two right eight wait right sixteen instead into the brownout power down delay register to isolate the backup domain before power rail collapse okay so we also configur the battery switchover control register buy enabling automatic supply transition right zero x zero eight into the power control register to lock the r t c configuration after enabling the backup brownout detector the node preserved calendar data across one hundred battery hot swap tests without clock reset or timestamp loss",
        "refined_text": "Our CC1352P agricultural sensor node lost its real-time clock calendar configuration whenever field technicians replaced the coin cell battery. We analyzed the supply rail decay by probing the RTC power domain with an oscilloscope and found that residual voltage hovered around 1 volt for 40 milliseconds during battery disconnection. The slow voltage decay caused internal logic gates to enter metastable states, which corrupted the calendar registers before the backup supply engaged.\n\nWe prevented RTC state loss by enabling the dedicated backup domain brownout detector. Configure the backup domain voltage monitor by setting the trip threshold to level 2. Write 16 instead into the brownout power down delay register to isolate the backup domain before power rail collapse.\n\nWe also configured the battery switchover control register by enabling automatic supply transition. Write 0x08 into the power control register to lock the RTC configuration. After enabling the backup brownout detector, the node preserved calendar data across 100 battery hot-swap tests without clock reset or timestamp loss."
    },

    # Sample 20: DMA scatter-gather with I2S DAC on SAM E70
    {
        "raw_asr": "uh our s a m e seventy digital audio console experienced intermittent channel phase shifts and popping artifacts when streaming eight channel audio to external d a c chips we probed the i two s serial clock and frame sync signals using a logic analyzer and found that the d m a controller stalled during bus arbitration against the memory controller the single transfer buffer underflowed whenever the c p u performed burst cache refreshes causing frame sync pulses to misalign with audio data words um we eliminated audio buffer starvation buy implementing multi buffer scatter gather d m a chaining in tightly coupled memory configur the i two s master clock generator buy setting the master clock ratio to five hundred twelve times the audio sample rate right two five six wait right five one two instead into the d m a block transfer size register to maintain continuous audio streaming basically we also configur the d m a channel arbiter buy assigning priority level one to the audio streaming channel right zero x six zero into the i two s control register to enable synchronized channel output after deploying the scatter gather descriptors and configuring high priority arbitration the console delivered flawless multi channel audio without clicks or phase errors across forty eight hours of continuous testing",
        "refined_text": "Our SAM E70 digital audio console experienced intermittent channel phase shifts and popping artifacts when streaming 8-channel audio to external DAC chips. We probed the I2S serial clock and frame sync signals using a logic analyzer and found that the DMA controller stalled during bus arbitration against the memory controller. The single transfer buffer underflowed whenever the CPU performed burst cache refreshes, causing frame sync pulses to misalign with audio data words.\n\nWe eliminated audio buffer starvation by implementing multi-buffer scatter-gather DMA chaining in tightly coupled memory. Configure the I2S master clock generator by setting the master clock ratio to 512 times the audio sample rate. Write 512 instead into the DMA block transfer size register to maintain continuous audio streaming.\n\nWe also configured the DMA channel arbiter by assigning priority level 1 to the audio streaming channel. Write 0x60 into the I2S control register to enable synchronized channel output. After deploying the scatter-gather descriptors and configuring high-priority arbitration, the console delivered flawless multi-channel audio without clicks or phase errors across 48 hours of continuous testing."
    }
]

def main():
    print(f"Auditing {len(batch)} samples for Batch 49...\n")

    # Load eval set for leakage check
    eval_file = Path("sft_eval.json")
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e.get("raw_asr", e.get("input", "")).strip().lower() for e in eval_data}
    eval_refs = {e.get("refined_text", e.get("output", "")).strip() for e in eval_data}

    all_ok = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for i, s in enumerate(batch, 1):
        raw = s.get("raw_asr", "")
        ref = s.get("refined_text", "")

        # Check leakage
        if raw.strip().lower() in eval_raws:
            print(f"Sample {i:02d}: LEAKAGE detected against sft_eval (raw_asr)!")
            all_ok = False
        if ref.strip() in eval_refs:
            print(f"Sample {i:02d}: LEAKAGE detected against sft_eval (refined_text)!")
            all_ok = False

        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(raw, ref)

        words = len(ref.split())
        raw_words = len(raw.split())
        ratio = words / max(1, raw_words)

        if words < 25:
            tier = "SHORT"
            tier_counts["short"] += 1
        elif words < 90:
            tier = "MEDIUM"
            tier_counts["medium"] += 1
        else:
            tier = "LONG"
            tier_counts["long"] += 1

        if not (v_ok and c_res is not None):
            all_ok = False
            print(f"Sample {i:02d} [{tier:6s}]: FAIL - validator: {v_reason}, cleaner: {c_reason} (ref_words={words}, raw_words={raw_words})")
        else:
            print(f"Sample {i:02d} [{tier:6s}]: PASS - words={words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f}")

    print("\n--- Tier Counts ---")
    print(f"Short:  {tier_counts['short']} / 4")
    print(f"Medium: {tier_counts['medium']} / 6")
    print(f"Long:   {tier_counts['long']} / 10")

    b_ok, b_reason, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
    print(f"\nBatch validation: ok={b_ok}, reason='{b_reason}', tiers={b_tiers}")

    if all_ok and b_ok:
        out_path = Path("scratch/subagent_batch_49.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"\nSUCCESS: All 20 samples passed! Saved to {out_path}")
        return 0
    else:
        print("\nFAILURE: Some checks failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
