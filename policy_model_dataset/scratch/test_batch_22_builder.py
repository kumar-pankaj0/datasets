import json
import os
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def build_batch_22():
    batch = [
        # Sample 1: Short (<25 words) - STM32 LPTIM
        {
            "raw_asr": "basically right zero x zero one into the s t m thirty two l p t i m one c f g r register two select the external clock source buy toggling bit zero wait bit one instead",
            "refined_text": "Write 0x01 into the STM32 `LPTIM1_CFGR` register to select the external clock source by toggling bit 1."
        },
        # Sample 2: Short (<25 words) - RISC-V PMP
        {
            "raw_asr": "um configur the r i s c v p m p a d d r zero register buy setting the region base address two zero x eight zero zero zero for memory protection",
            "refined_text": "Configure the RISC-V `pmpaddr0` register by setting the region base address to 0x8000 for memory protection."
        },
        # Sample 3: Medium (25-90 words) - ESP32 FreeRTOS
        {
            "raw_asr": "basically a high priority worker pinned to core one starves the idle task and triggers a task w d t panic on the e s p thirty two under free are toss yield processor control periodically buy calling v task delay with five ticks wait ten ticks in the execut loop",
            "refined_text": "A high-priority worker pinned to Core 1 starves the idle task and triggers a `task_wdt` panic on the ESP32 under FreeRTOS.\n\nYield processor control periodically by calling `vTaskDelay` with 10 ticks in the execution loop."
        },
        # Sample 4: Medium (25-90 words) - nRF52 PPI
        {
            "raw_asr": "root the n r f fifty two radio events ready signal directly two the tasks start register using p p i channel zero um enable channel zero in the n r f p p i c h e n bitmask buy writing bit zero two automate radio transmiss without processor overhead",
            "refined_text": "Route the nRF52 radio `EVENTS_READY` signal directly to the `TASKS_START` register using PPI channel 0.\n\nEnable channel 0 in the `NRF_PPI->CHEN` bitmask by writing bit 0 to automate radio transmission without processor overhead."
        },
        # Sample 5: Medium (25-90 words) - RP2040 PIO DMA
        {
            "raw_asr": "basically configur r p twenty forty p i o zero state machine one wait state machine zero two stream serialized bitstream words into the r x f i f o bind the d m a channel two d r e q p i o zero r x zero and enable a two hundred fifty six byte circular ring buffer buy setting the address wrap boundary",
            "refined_text": "Configure RP2040 `pio0` state machine 0 to stream serialized bitstream words into the RX FIFO.\n\nBind the DMA channel to `DREQ_PIO0_RX0` and enable a 256-byte circular ring buffer by setting the address wrap boundary."
        },
        # Sample 6: Long (90+ words) - RISC-V PMP Fault Debugging
        {
            "raw_asr": "basically the r i s c v core triggered an unhandled store access fault with exception code five wait exception code seven in the m cause register during user space execution connecting the target buy g d b showed the trap occurred at memory address zero x eight zero zero zero one zero zero zero stored in the m e p c register the fault originated from an invalid physical memory protection configur where the user mode application attempted two access peripheral memory outside its allocated partition um inspecting the physical memory protection configur revealed that the p m p c f g zero register had locked bit seven set with top of range address matching in p m p a d d r zero pointing two address zero x eight zero zero zero zero zero zero zero however right permission bit one was cleared causing the hardware memory management unit two immediately trigger a trap when the store instruction executed modifying p m p c f g zero two grant write permissions and setting p m p a d d r one two address zero x eight zero zero zero two zero zero zero resolved the access violat",
            "refined_text": "The RISC-V core triggered an unhandled store access fault with exception code 7 in the `mcause` register during user-space execution. Connecting the target by GDB showed the trap occurred at memory address 0x80001000 stored in the `mepc` register. The fault originated from an invalid physical memory protection configuration where the user-mode application attempted to access peripheral memory outside its allocated partition.\n\nInspecting the physical memory protection configuration revealed that the `pmpcfg0` register had locked bit 7 set with top-of-range address matching in `pmpaddr0` pointing to address 0x80000000. However, write permission bit 1 was cleared, causing the hardware memory management unit to immediately trigger a trap when the store instruction executed. Modifying `pmpcfg0` to grant write permissions and setting `pmpaddr1` to address 0x80002000 resolved the access violation."
        },
        # Sample 7: Long (90+ words) - ESP32 FreeRTOS Core 1 Task Starvation
        {
            "raw_asr": "okay so the e s p thirty two firmware experienced intermittent panic restarts due two task watchdog timer expiration on core one during high rate telemetry logging investigating the panic backtrace showed that a computat telemetry filter task created using x task create pinned to core with priority three wait priority five monopolized core one the task executed an uninterrupted matrix calculation loop without yielding the c p u two the scheduler um because the telemetry worker never entered a blocked state the free are toss i d l e one task on core one was starved of execut slices four over five thousand milliseconds this condition prevented the idle hook from feeding the watchdog timer which triggered the hardware abort inserting a non blocking v task delay call with ten ticks inside the inner processing loop allowed the i d l e one task two reset the watchdog",
            "refined_text": "The ESP32 firmware experienced intermittent panic restarts due to task watchdog timer expiration on Core 1 during high-rate telemetry logging. Investigating the panic backtrace showed that a computational telemetry filter task created using `xTaskCreatePinnedToCore` with priority 5 monopolized Core 1. The task executed an uninterrupted matrix calculation loop without yielding the CPU to the scheduler.\n\nBecause the telemetry worker never entered a blocked state, the FreeRTOS `IDLE1` task on Core 1 was starved of execution slices for over 5000 milliseconds. This condition prevented the idle hook from feeding the watchdog timer, which triggered the hardware abort. Inserting a non-blocking `vTaskDelay` call with 10 ticks inside the inner processing loop allowed the `IDLE1` task to reset the watchdog."
        },
        # Sample 8: Long (90+ words) - nRF52 Radio PPI Event Chaining
        {
            "raw_asr": "basically the nordic n r f fifty two radio subsystem requires deterministic timing for high speed protocol packets without c p u interrupt jitter two achieve cycle accurate transmiss we root the internal timer compare event directly two the radio peripheral using programmable peripheral interconnect channels specifically p p i channel three wait channel one connects the timer zero events compare zero event endpoint two the radio tasks t x e n task endpoint um once the radio power amplifier ramps up the hardware asserts the events ready signal rather than waking the processor core two initiate packet transmiss p p i channel two links radio events ready directly two radio tasks start setting bits one and two in the n r f p p i c h e n register bitmask enables both hardware channels simultaneously reducing transmiss latency two zero c p u cycles",
            "refined_text": "The Nordic nRF52 radio subsystem requires deterministic timing for high-speed protocol packets without CPU interrupt jitter. To achieve cycle-accurate transmission, we route the internal timer compare event directly to the radio peripheral using programmable peripheral interconnect channels. Specifically, PPI channel 1 connects the `TIMER0->EVENTS_COMPARE[0]` event endpoint to the `RADIO->TASKS_TXEN` task endpoint.\n\nOnce the radio power amplifier ramps up, the hardware asserts the `EVENTS_READY` signal. Rather than waking the processor core to initiate packet transmission, PPI channel 2 links `RADIO->EVENTS_READY` directly to `RADIO->TASKS_START`. Setting bits 1 and 2 in the `NRF_PPI->CHEN` register bitmask enables both hardware channels simultaneously, reducing transmission latency to zero CPU cycles."
        },
        # Sample 9: Long (90+ words) - STM32 LPTIM External Clock Wakeup
        {
            "raw_asr": "okay so the battery powered s t m thirty two remote sensor knowed enters stop two mode between telemetry intervals two conserve battery power two maintain periodic wakeup capabilities without running high frequency oscillators we configur the low power timer l p t i m one two run asynchronously from the thirty two kilohertz low speed external clock we select the external clock source buy writing bit zero in the l p t i m one c f g r register um next set the auto reload value buy writing sixteen thousand wait thirty two thousand into the l p t i m one a r r register two establish a continuous one second timeout interval after enabling the compare interrupt in l p t i m one i e r the c p u executes the w f i instruction two enter deep sleep when the timer counter reaches the target threshold the peripheral raises an asynchronous wakeup event on the e x t i line that resumes execution in five microseconds",
            "refined_text": "The battery-powered STM32 remote sensor node enters Stop 2 mode between telemetry intervals to conserve battery power. To maintain periodic wakeup capabilities without running high-frequency oscillators, we configure the low-power timer `LPTIM1` to run asynchronously from the 32 kilohertz low-speed external clock. We select the external clock source by writing bit 0 in the `LPTIM1_CFGR` register.\n\nNext, set the auto-reload value by writing 32000 into the `LPTIM1_ARR` register to establish a continuous 1-second timeout interval. After enabling the compare interrupt in `LPTIM1_IER`, the CPU executes the `WFI` instruction to enter deep sleep. When the timer counter reaches the target threshold, the peripheral raises an asynchronous wakeup event on the EXTI line that resumes execution in 5 microseconds."
        },
        # Sample 10: Long (90+ words) - RP2040 PIO DMA Ring Buffer Streaming
        {
            "raw_asr": "basically the r p twenty forty programmable input output block captures high speed logic signals directly into internal s r a m buffers state machine one wait state machine zero inside the p i o zero block executes a custom assembly program that samples eight g p i o pins and shifts thirty two bit words into the r x f i f o two prevent f i f o overflows during continuous capture we connect d m a channel zero using the d r e q p i o zero r x zero pacing request um we configur the d m a channel transfer width two thirty two bits and program a one zero two four byte circular ring buffer using wrap boundaries this circular configur forces the write pointer two loop back two the buffer base address after receiving two hundred fifty six words without c p u intervention verifying the f i f o status register shows zero dropped samples across a continuous streaming session of ten thousand transactions",
            "refined_text": "The RP2040 programmable input output block captures high-speed logic signals directly into internal SRAM buffers. State machine 0 inside the `pio0` block executes a custom assembly program that samples 8 GPIO pins and shifts 32-bit words into the RX FIFO. To prevent FIFO overflows during continuous capture, we connect DMA channel 0 using the `DREQ_PIO0_RX0` pacing request.\n\nWe configure the DMA channel transfer width to 32 bits and program a 1024-byte circular ring buffer using wrap boundaries. This circular configuration forces the write pointer to loop back to the buffer base address after receiving 256 words without CPU intervention. Verifying the FIFO status register shows zero dropped samples across a continuous streaming session of 10000 transactions."
        }
    ]

    out_file = "scratch/subagent_batch_22.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(batch)} samples to {out_file}")

    # Run validation
    all_ok = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}
    for i, s in enumerate(batch, 1):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])

        words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = words / max(1, raw_words)

        if words < 25:
            tier_counts["short"] += 1
            tier = "Short"
        elif words <= 90:
            tier_counts["medium"] += 1
            tier = "Medium"
        else:
            tier_counts["long"] += 1
            tier = "Long"

        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"Sample {i:02d} [{tier}]: [{status}] ({words}w ref, {raw_words}w raw, ratio {ratio:.2f})")
        if not v_ok:
            print(f"  Validator failure: {v_reason}")
        if c_res is None:
            print(f"  Cleaner failure: {c_reason}")

    b_ok, b_reason, b_counts = validate_batch(batch, min_short=2, min_medium=3, min_long=5)
    print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
    print(f"Tier counts: {b_counts}")
    print(f"Overall status: {'ALL PASS (10/10)' if all_ok and b_ok else 'AUDIT FAILED'}")

    return all_ok and b_ok

if __name__ == "__main__":
    success = build_batch_22()
    if not success:
        sys.exit(1)
