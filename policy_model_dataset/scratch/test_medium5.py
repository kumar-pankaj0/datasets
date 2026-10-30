import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

p = {
    "raw_asr": "um message brokers halted publishing operations after five queue knowed partitions accumulated unacknowledged messages across twenty seconds wait forty seconds instead incident responders terminat blocked consumer threads buy purging queue underscore backlog before systems teams configur c p u threshold limits",
    "refined_text": "Message brokers halted publishing operations after 5 queue node partitions accumulated unacknowledged messages across 40 seconds instead.\n\nIncident responders terminate blocked consumer threads by purging queue_backlog before systems teams configure CPU threshold limits."
}

val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
nl = validator.get_noise_layer_count(p["raw_asr"])
words = len(p["refined_text"].split())
print(f"Medium 5: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
