import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("code"))
import cleaner
import validator

BATCH_169 = [
    # Tier 1: 4 Short (< 25 words, exactly 1 sentence, zero newlines)
    {
        "raw_asr": "um calibrat the r i s c v clock divider buy setting zero x two zero four the peripheral bus",
        "refined_text": "Calibrate the RISC-V clock divider by setting 0x20 for the peripheral bus."
    },
    {
        "raw_asr": "uh configur the d m a transfer buy writing zero x one zero two the control register",
        "refined_text": "Configure the DMA transfer by writing 0x10 to the control register."
    },
    {
        "raw_asr": "basically initializ the u art baud rate buy passing zero x eight zero wait switch two zero x four zero instead",
        "refined_text": "Initialize the UART baud rate by passing 0x40 instead."
    },
    {
        "raw_asr": "you know terminat the free are toss watchdog task buy passing dash dash force two the supervisor thread",
        "refined_text": "Terminate the FreeRTOS watchdog task by passing --force to the supervisor thread."
    },

    # Tier 2: 6 Medium (25-89 words, 1-3 sentences with natural \n\n breaks)
    {
        "raw_asr": "um four the stm thirty two i two c bus lockup our team resolved clock stretching buy toggling g p i o pin nine twelve times wait change that to pin four instead basically we will initializ bus recovery buy writing zero x one zero two the control register four reliable sensor transmiss",
        "refined_text": "For the STM32 I2C bus lockup our team resolved clock stretching by toggling GPIO pin 4 12 times instead.\n\nWe will initialize bus recovery by writing 0x10 to the control register for reliable sensor transmission."
    },
    {
        "raw_asr": "uh four the esp thirty two watchdog panic our firmware squad audited task starvation across four worker threads wait switch to six worker threads instead you know we agreed two configur the free are toss tick rate buy passing dash dash tick equals one zero zero zero inside slash config slash freertos dot h basically we will terminat stalled telemetry loops buy asserting software resets",
        "refined_text": "For the ESP32 watchdog panic our firmware squad audited task starvation across 6 worker threads instead.\n\nWe agreed to configure the FreeRTOS tick rate by passing --tick=1000 inside /config/freertos.h, terminating stalled telemetry loops by asserting software resets."
    },
    {
        "raw_asr": "um during the n r f fifty two peripheral setup our engineering team investigated buffer corruption inside the s p i receive ring buffer buy checking d m a channel zero scratch that switch to d m a channel two instead basically we will allocat thirty two bytes four descriptors buy passing zero x two zero inside slash drivers slash spi dot c four continuous sensor polling",
        "refined_text": "During the nRF52 peripheral setup our engineering team investigated buffer corruption inside the SPI receive ring buffer by checking DMA channel 2 instead.\n\nWe will allocate 32 bytes for descriptors by passing 0x20 inside /drivers/spi.c for continuous sensor polling."
    },
    {
        "raw_asr": "basically four the r p twenty forty programmable input output interface our firmware developers debugged timing jitter on state machine zero wait change that to state machine three instead you know we plan two calibrat the clock divider buy passing dash dash div equals four inside slash src slash pio dot c buy holding c p u cycles stable four external telemetry",
        "refined_text": "For the RP2040 programmable input output interface our firmware developers debugged timing jitter on state machine 3 instead.\n\nWe plan to calibrate the clock divider by passing --div=4 inside /src/pio.c, holding CPU cycles stable for external telemetry."
    },
    {
        "raw_asr": "uh during the target hardware bringup our team diagnosed flash verification failures under open o c d buy measuring power rail noise on board revision one wait switch to board revision two instead um we will synchronizat the n v i c interrupt priority buy passing zero x four zero two the peripheral control register buy clearing pending interrupt flags",
        "refined_text": "During the target hardware bringup our team diagnosed flash verification failures under OpenOCD by measuring power rail noise on board revision 2 instead.\n\nWe will synchronize the NVIC interrupt priority by passing 0x40 to the peripheral control register by clearing pending interrupt flags."
    },
    {
        "raw_asr": "um four the r i s c v board evaluation our engineers tested serial output dropped packets buy auditing the u art transmission fifo buffer on core zero scratch that switch to core one instead you know our squad will recalculat timer interrupt intervals buy passing dash dash baud equals nine six zero zero inside slash boot slash config dot cfg buy resetting bus registers",
        "refined_text": "For the RISC-V board evaluation our engineers tested serial output dropped packets by auditing the UART transmission FIFO buffer on core 1 instead.\n\nOur squad will recalculate timer interrupt intervals by passing --baud=9600 inside /boot/config.cfg by resetting bus registers."
    },

    # Tier 3: 10 Long (90+ words, multi-paragraph narration separated by \n\n)
    {
        "raw_asr": "um during our firmware postmortem the platform squad investigated an unexpected hard fault on the cortex m four processor buy analyzing stack frame registers across eight worker tasks wait change that to twelve worker tasks instead basically stack pointer misalignment corrupted the interrupt context when the d m a handler preempted peripheral routines you know our firmware developers agreed two configur memory alignment buy passing zero x two zero inside slash src slash fault dot c four the upcoming firmware release we reallocated execution priority buy updating n v i c register tables and clearing fault status flags buy morning our squad will terminat unaligned memory accesses buy enforcing eight byte boundaries inside the linker script our team will initializ hardware diagnostics buy logging c p u exception dumps four field telemetry verification",
        "refined_text": "During our firmware postmortem the platform squad investigated an unexpected hard fault on the Cortex M4 processor by analyzing stack frame registers across 12 worker tasks instead. Stack pointer misalignment corrupted the interrupt context when the DMA handler preempted peripheral routines. Our firmware developers agreed to configure memory alignment by passing 0x20 inside /src/fault.c for the upcoming firmware release.\n\nWe reallocated execution priority by updating NVIC register tables and clearing fault status flags. By morning our squad will terminate unaligned memory accesses by enforcing 8 byte boundaries inside the linker script. Our team will initialize hardware diagnostics by logging CPU exception dumps for field telemetry verification."
    },
    {
        "raw_asr": "uh during the esp thirty two bootloader verification our team triaged flash read timeouts buy evaluating quad s p i timing across four memory chips wait switch to eight memory chips instead basically signal integrity degradation caused spurious brownout resets when the c p u frequency transitioned two two four zero megahertz you know our developers agreed two calibrat flash read delays buy passing dash dash flash dash mode equals qio inside slash boot slash flash dot c buy stabilizing vdd power rails four the next hardware milestone our squad will initializ the bootloader interface buy executing esp tool dot py with zero x three zero register offsets we resolved bus contention buy reordering peripheral startup sequences and verifying s p i clock stability buy afternoon our engineers will test data transmiss buy validating flash partition tables across bench targets",
        "refined_text": "During the ESP32 bootloader verification our team triaged flash read timeouts by evaluating quad SPI timing across 8 memory chips instead. Signal integrity degradation caused spurious brownout resets when the CPU frequency transitioned to 240 megahertz. Our developers agreed to calibrate flash read delays by passing --flash-mode=qio inside /boot/flash.c, stabilizing VDD power rails for the next hardware milestone.\n\nOur squad will initialize the bootloader interface by executing esptool.py with 0x30 register offsets. We resolved bus contention by reordering peripheral startup sequences and verifying SPI clock stability. By afternoon our engineers will test data transmission by validating flash partition tables across bench targets."
    },
    {
        "raw_asr": "um during our embedded architecture review our developers analyzed priority inversion buy auditing mutex contention across sixteen background threads wait change that to twenty background threads instead basically a low priority telemetry task locked the i two c bus resource while high priority motor control loops suffered starvation you know our firmware squad decided two synchronizat task scheduling buy passing zero x five zero inside slash rtos slash tasks dot c four the upcoming sprint release we replaced binary semaphores with priority inheritance mutexes buy updating free are toss task definitions our team will allocat memory buffers buy reserving thirty two bytes four d m a queue handles buy evening our engineers will communicat latency metrics buy measuring execution jitter across hardware test fixtures",
        "refined_text": "During our embedded architecture review our developers analyzed priority inversion by auditing mutex contention across 20 background threads instead. A low priority telemetry task locked the I2C bus resource while high priority motor control loops suffered starvation. Our firmware squad decided to synchronize task scheduling by passing 0x50 inside /rtos/tasks.c for the upcoming sprint release.\n\nWe replaced binary semaphores with priority inheritance mutexes by updating FreeRTOS task definitions. Our team will allocate memory buffers by reserving 32 bytes for DMA queue handles. By evening our engineers will communicate latency metrics by measuring execution jitter across hardware test fixtures."
    },
    {
        "raw_asr": "uh during board bringup the manufacturing team encountered boundary scan failures buy evaluating jtag tap controllers across four prototypes scratch that switch to six prototypes instead basically excessive signal reflection on the tck clock line caused open o c d two report tap identification errors you know our hardware team agreed two configur adapter speed buy passing dash dash speed equals five zero zero inside slash openocd slash target dot cfg buy adding damping resistors four clean digital edges our squad will initializ debug communication buy setting zero x seven zero on the r i s c v core tap register we restored u art serial output buy verifying level shifter direction pins across the programmer interface buy tomorrow morning our team will terminat noisy bus oscillations buy shortening ground return paths on the test jig",
        "refined_text": "During board bringup the manufacturing team encountered boundary scan failures by evaluating JTAG TAP controllers across 6 prototypes instead. Excessive signal reflection on the TCK clock line caused OpenOCD to report TAP identification errors. Our hardware team agreed to configure adapter speed by passing --speed=500 inside /openocd/target.cfg, adding damping resistors for clean digital edges.\n\nOur squad will initialize debug communication by setting 0x70 on the RISC-V core TAP register. We restored UART serial output by verifying level shifter direction pins across the programmer interface. By tomorrow morning our team will terminate noisy bus oscillations by shortening ground return paths on the test jig."
    },
    {
        "raw_asr": "um during field telemetry validation our engineers investigated can bus framing errors buy evaluating transceiver latency across four knowed units wait change that to eight knowed units instead basically propagation delay mismatches caused the bus controller two trigger form error interrupts during the data phase you know our firmware squad agreed two calibrat bit timing parameters buy passing dash dash bitrate equals five zero zero inside slash drivers slash can dot c buy adjusting sample point offsets four robust automotive communication we optimized d m a message mailboxes buy passing zero x six zero two control registers our team will arbitrat bus access buy setting message identifiers and clearing passive error flags buy midnight our developers will operat hardware loop tests buy streaming diagnostic frames without c p u overhead",
        "refined_text": "During field telemetry validation our engineers investigated CAN bus framing errors by evaluating transceiver latency across 8 node units instead. Propagation delay mismatches caused the bus controller to trigger form error interrupts during the data phase. Our firmware squad agreed to calibrate bit timing parameters by passing --bitrate=500 inside /drivers/can.c, adjusting sample point offsets for robust automotive communication.\n\nWe optimized DMA message mailboxes by passing 0x60 to control registers. Our team will arbitrate bus access by setting message identifiers and clearing passive error flags. By midnight our developers will operate hardware loop tests by streaming diagnostic frames without CPU overhead."
    },
    {
        "raw_asr": "uh during battery endurance measurements our embedded squad analyzed sleep current draw buy auditing deep sleep modes across six sensor units scratch that switch to twelve sensor units instead basically an unstopped peripheral clock prevented the system from entering low power sleep mode you know our firmware developers decided two calibrat analog thresholds buy writing zero x nine zero two peripheral registers buy executing a right operation inside slash power slash sleep dot c four accurate voltage sampling we optimized wakeup intervals buy configuring rtc prescalers and clearing n v i c event flags our team will configur d m a descriptors buy setting circular buffers four direct memory transfers buy midday our engineers will synchronizat sensor acquisition cycles buy keeping c p u execution minimal during sleep intervals",
        "refined_text": "During battery endurance measurements our embedded squad analyzed sleep current draw by auditing deep sleep modes across 12 sensor units instead. An unstopped peripheral clock prevented the system from entering low power sleep mode. Our firmware developers decided to calibrate analog thresholds by writing 0x90 to peripheral registers, executing a write operation inside /power/sleep.c for accurate voltage sampling.\n\nWe optimized wakeup intervals by configuring RTC prescalers and clearing NVIC event flags. Our team will configure DMA descriptors by setting circular buffers for direct memory transfers. By midday our engineers will synchronize sensor acquisition cycles by keeping CPU execution minimal during sleep intervals."
    },
    {
        "raw_asr": "um during multicore benchmark tests our engineering squad investigated inter core fifo deadlocks buy evaluating mailbox latency across eight firmware builds wait change that to sixteen firmware builds instead basically uncoordinated hardware spinlock acquisition caused core one two stall while core zero waited four drain events you know our firmware developers decided two synchronizat inter core communication buy passing dash dash timeout equals one zero inside slash multicore slash fifo dot c buy asserting non blocking queue polling four real time sensor telemetry our team will initializ spinlock registers buy writing zero x eight zero two hardware control words we reduced c p u contention buy moving heavy processing workloads two d m a background channels buy morning our developers will terminat stalled multicore loops buy verifying inter core interrupt flags across regression runs",
        "refined_text": "During multicore benchmark tests our engineering squad investigated inter core FIFO deadlocks by evaluating mailbox latency across 16 firmware builds instead. Uncoordinated hardware spinlock acquisition caused core 1 to stall while core 0 waited for drain events. Our firmware developers decided to synchronize inter core communication by passing --timeout=10 inside /multicore/fifo.c, asserting non blocking queue polling for real time sensor telemetry.\n\nOur team will initialize spinlock registers by writing 0x80 to hardware control words. We reduced CPU contention by moving heavy processing workloads to DMA background channels. By morning our developers will terminate stalled multicore loops by verifying inter core interrupt flags across regression runs."
    },
    {
        "raw_asr": "uh during thermal chamber stress testing our firmware engineers observed bus hang conditions buy auditing arbitration loss across four knowed devices scratch that switch to eight knowed devices instead basically a slave sensor held sda low indefinitely when clock stretching timed out during read transactions you know our firmware squad decided two configur bus clearing sequences buy passing dash dash retries equals five inside slash drivers slash i2c dot c buy generating nine manual scl clock pulses four bus recovery we updated peripheral control words buy passing zero x two zero two the i two c master registers our squad will arbitrat message sequences buy checking bus busy flags before initiating d m a transfers buy evening our team will recalculat bus recovery timeouts buy evaluating response curves across c p u operating conditions",
        "refined_text": "During thermal chamber stress testing our firmware engineers observed bus hang conditions by auditing arbitration loss across 8 node devices instead. A slave sensor held SDA low indefinitely when clock stretching timed out during read transactions. Our firmware squad decided to configure bus clearing sequences by passing --retries=5 inside /drivers/i2c.c, generating 9 manual SCL clock pulses for bus recovery.\n\nWe updated peripheral control words by passing 0x20 to the I2C master registers. Our squad will arbitrate message sequences by checking bus busy flags before initiating DMA transfers. By evening our team will recalculate bus recovery timeouts by evaluating response curves across CPU operating conditions."
    },
    {
        "raw_asr": "um during high baud rate serial stress testing our firmware team analyzed packet overrun flags buy auditing fifo receive queues across eight benchmark runs wait change that to twelve benchmark runs instead basically interrupt latency spikes caused the u art hardware fifo two overflow before the task processed incoming frames you know our firmware developers agreed two allocat double buffered d m a circular buffers buy passing dash dash buffer dash size equals five one two inside slash drivers slash uart dot c buy preventing dropped telemetry bytes four rapid diagnostics our team will calibrat half transfer interrupt thresholds buy writing zero x four zero two d m a stream control registers we minimized c p u overhead buy streaming packet headers directly two sram buy afternoon our engineers will operat continuous high speed logging buy executing write routines without context switch penalties",
        "refined_text": "During high baud rate serial stress testing our firmware team analyzed packet overrun flags by auditing FIFO receive queues across 12 benchmark runs instead. Interrupt latency spikes caused the UART hardware FIFO to overflow before the task processed incoming frames. Our firmware developers agreed to allocate double buffered DMA circular buffers by passing --buffer-size=512 inside /drivers/uart.c, preventing dropped telemetry bytes for rapid diagnostics.\n\nOur team will calibrate half transfer interrupt thresholds by writing 0x40 to DMA stream control registers. We minimized CPU overhead by streaming packet headers directly to SRAM. By afternoon our engineers will operate continuous high speed logging by executing write routines without context switch penalties."
    },
    {
        "raw_asr": "uh during security partition testing our firmware squad triaged memory protection faults buy auditing privilege violation traps across four isolation zones scratch that switch to eight isolation zones instead basically unprivileged user mode tasks attempted direct peripheral register writes without supervisor mode delegation you know our firmware developers agreed two configur memory protection unit regions buy passing dash dash region equals three inside slash kernel slash mpu dot c buy enforcing read only access permissions four shared buffers our team will initializ physical memory attributes buy passing zero x five zero two base address registers we remapped interrupt vector tables buy updating n v i c priority assignments buy morning our developers will terminat unprivileged instruction faults buy verifying access boundary checks across c p u execution modes",
        "refined_text": "During security partition testing our firmware squad triaged memory protection faults by auditing privilege violation traps across 8 isolation zones instead. Unprivileged user mode tasks attempted direct peripheral register writes without supervisor mode delegation. Our firmware developers agreed to configure memory protection unit regions by passing --region=3 inside /kernel/mpu.c, enforcing read only access permissions for shared buffers.\n\nOur team will initialize physical memory attributes by passing 0x50 to base address registers. We remapped interrupt vector tables by updating NVIC priority assignments. By morning our developers will terminate unprivileged instruction faults by verifying access boundary checks across CPU execution modes."
    }
]

def main():
    print("=" * 60)
    print("Validating Batch 169 (Domain 6: Embedded Systems)")
    print("=" * 60)

    # 1. Size check
    assert len(BATCH_169) == 20, f"Expected 20 samples, got {len(BATCH_169)}"

    # 2. Check leakage against sft_eval.json
    eval_file = Path("sft_eval.json")
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e.get("raw_asr", "").strip().lower() for e in eval_data}
    eval_refs = {e.get("refined_text", "").strip() for e in eval_data}

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []

    for idx, pair in enumerate(BATCH_169, 1):
        raw = pair["raw_asr"]
        ref = pair["refined_text"]

        # ASCII checks
        raw.encode("ascii")
        ref.encode("ascii")

        # Leakage check
        assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
        assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

        # Cleaner check
        clean_res, clean_status = cleaner.clean_sample(raw, ref)
        assert clean_res is not None, f"Sample {idx} failed cleaner: {clean_status}"
        assert clean_status == "kept", f"Sample {idx} status not kept: {clean_status}"

        # Word count and noise layers
        words = len(ref.split())
        nl = validator.get_noise_layer_count(raw)
        layer_counts.append(nl)

        # Tier checks
        if words < 25:
            tier_counts["short"] += 1
            assert "\n" not in ref, f"Sample {idx} short has newline"
            assert nl >= 3, f"Sample {idx} short has < 3 noise layers ({nl})"
            min_l = 3
        elif words < 90:
            tier_counts["medium"] += 1
            assert "\n\n" in ref, f"Sample {idx} medium missing \\n\\n"
            assert nl >= 4, f"Sample {idx} medium has < 4 noise layers ({nl})"
            min_l = 4
        else:
            tier_counts["long"] += 1
            assert "\n\n" in ref, f"Sample {idx} long missing \\n\\n"
            assert nl >= 4, f"Sample {idx} long has < 4 noise layers ({nl})"
            min_l = 4

        # Pair validation
        val_ok, val_reason = validator.validate_pair(pair, min_noise_layers=min_l)
        assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Batch validation
    batch_ok, batch_reason, batch_stats = validator.validate_batch(
        BATCH_169,
        min_short=4,
        min_medium=6,
        min_long=10,
        min_noise_layers=4
    )
    assert batch_ok, f"Batch validation failed: {batch_reason}"

    avg_layers = sum(layer_counts) / len(layer_counts)
    print("All 20 samples passed all deterministic checks!")
    print(f"Tier counts: {tier_counts}")
    print(f"Average noise layers: {avg_layers:.2f}")
    print(f"Distribution: {batch_stats['noise_layer_distribution']}")

    # Write output file
    out_path = Path("scratch/subagent_batch_169.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(BATCH_169, f, indent=2)
    print(f"Wrote verified pairs to {out_path}")

if __name__ == "__main__":
    main()
