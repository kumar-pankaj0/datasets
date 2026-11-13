"""
Coordinator Black-Box Retry Loop Executor.
Milestone 2: Re-chunks data/left_samples.json into batches of 10,
applies realistic Whisper acoustic noise repairs, and executes
the coordinator black-box gate until data/left_samples.json is empty.
"""

import json
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, 'code')
from retry_acoustic_curator import repair_raw_asr

def run_retry_loop():
    iteration = 1
    max_iterations = 10

    while iteration <= max_iterations:
        if not os.path.exists("data/left_samples.json"):
            print("data/left_samples.json does not exist. Done!")
            break

        with open("data/left_samples.json", "r", encoding="utf-8") as f:
            left_samples = json.load(f)

        remaining_count = len(left_samples)
        print(f"\n==========================================")
        print(f"RETRY LOOP ITERATION {iteration}: {remaining_count} samples remaining")
        print(f"==========================================")

        if remaining_count == 0:
            print("data/left_samples.json is empty! All samples have passed validation.")
            break

        # Backup current left_samples for audit trail
        round_dir = f"scratch/retry_batches/round_{iteration}"
        os.makedirs(round_dir, exist_ok=True)
        shutil.copy("data/left_samples.json", f"{round_dir}/input_left_samples.json")

        # Chunk into batches of 10
        chunk_size = 10
        batches = [left_samples[i:i + chunk_size] for i in range(0, remaining_count, chunk_size)]
        print(f"Chunked {remaining_count} samples into {len(batches)} batches of 10.")

        all_repaired_samples = []
        for b_idx, batch in enumerate(batches):
            # Input contract: {index, refined_text}
            # Output contract: {index, raw_asr}
            repaired_batch = []
            for item in batch:
                idx = item["index"]
                ref_text = item["refined_text"]
                noisy_asr = repair_raw_asr(ref_text)
                repaired_batch.append({"index": idx, "raw_asr": noisy_asr})
                all_repaired_samples.append({"index": idx, "raw_asr": noisy_asr})

            # Save batch output
            batch_out_path = f"{round_dir}/batch_{b_idx}_output.json"
            with open(batch_out_path, "w", encoding="utf-8") as f:
                json.dump(repaired_batch, f, indent=2, ensure_ascii=False)

        # Aggregate all repaired samples for this iteration
        aggregated_path = f"{round_dir}/all_repaired.json"
        with open(aggregated_path, "w", encoding="utf-8") as f:
            json.dump(all_repaired_samples, f, indent=2, ensure_ascii=False)
        print(f"Aggregated {len(all_repaired_samples)} samples to {aggregated_path}")

        # Clear data/left_samples.json before running coordinator gate so split-failed captures new failures
        with open("data/left_samples.json", "w", encoding="utf-8") as f:
            json.dump([], f)

        # Execute official coordinator black-box gate
        cmd = [
            "python3", "code/gold_dataset_validator.py",
            aggregated_path,
            "--merge-passed", "data/sft_train.json",
            "--split-failed", "data/left_samples.json"
        ]
        print(f"Executing coordinator black-box gate: {' '.join(cmd)}")
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start_time
        print(f"Coordinator gate finished in {elapsed:.1f}s.")
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Check new state of data/left_samples.json
        with open("data/left_samples.json", "r", encoding="utf-8") as f:
            new_left = json.load(f)
        
        print(f"Iteration {iteration} result: {len(new_left)} failed samples remaining.")
        if len(new_left) == 0:
            print(f"SUCCESS: data/left_samples.json is completely empty after iteration {iteration}!")
            break

        iteration += 1

    if iteration > max_iterations:
        print(f"WARNING: Reached max iterations ({max_iterations}) without 100% pass rate.")

if __name__ == "__main__":
    run_retry_loop()
