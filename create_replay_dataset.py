import json
import random
import collections

# Load the original 2,917 samples
with open("dataset.json", "r") as f:
    original_data = json.load(f)

# Load the 450 new hard-negatives
with open("second_face_dataset.json", "r") as f:
    new_data = json.load(f)

# Stratified Sampling Logic (The user's idea)
# We want exactly 450 samples from the original data.
# To ensure perfect balance, we will pull exactly 90 samples for each score bucket (1,3,5,7,9)
# based on a primary metric (e.g., faithfulness). Because the dataset is perfectly orthogonal,
# balancing one metric naturally balances the others.

random.seed(42)
random.shuffle(original_data)

bucket_counts = {1: 0, 3: 0, 5: 0, 7: 0, 9: 0}
replay_memory = []
limit_distribution: dict = {}
over_all_distribution: dict = {}
for sample in original_data:
    if "output" in sample.keys():
        for catagory in sample["output"]:
            if (
                catagory
                not in limit_distribution.keys()
            ):
                limit_distribution[catagory] = (
                    bucket_counts.copy()
                )

            catagory_score = sample["output"][
                catagory
            ]
            if (
                not limit_distribution[
                    catagory
                ][catagory_score]
                >= 25
            ):
                limit_distribution[catagory][
                    catagory_score
                ] += 1
                replay_memory.append(sample)
                for nested_catagory in sample[
                    "output"
                ]:
                    if (
                        not nested_catagory
                        in over_all_distribution.keys()
                    ):
                        over_all_distribution[
                            nested_catagory
                        ] = bucket_counts.copy()

                    over_all_distribution[
                        nested_catagory
                    ][
                        sample["output"][
                            nested_catagory
                        ]
                    ] += 1
                break


print(len(replay_memory))
print(
    f"limit distribution : {limit_distribution}"
)
print(
    f" over all distribution : {over_all_distribution}"
)
# Combine and shuffle
incremental_dataset = new_data + replay_memory
random.shuffle(incremental_dataset)

# Save the final dataset
with open(
    "incremental_replay_dataset.json", "w"
) as f:
    json.dump(incremental_dataset, f, indent=2)

print(
    f"Created incremental_replay_dataset.json with {len(incremental_dataset)} samples."
)
print(
    f"Replay Memory Distribution: {bucket_counts}"
)
