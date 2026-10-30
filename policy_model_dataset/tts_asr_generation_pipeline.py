def generation_pipeline(batch_size):
    tts_model, asr_model = load_models()
    dataset = load_dataset("tts_dataset.json")["refined_text"]
    noise_dataset = []

    with open("combined_dataset.json", "r") as f:
        old_dataset = f.read()

    for i in range(len(dataset), batch_size):
        batch_dataset = dataset[i : i + batch_size]
        input_voice = tts_model.generate(batch_dataset)
        noise_voice = noise_addition(input_voice)
        noise_raw_text = asr_model.generate(noise_voice)
        matrics = calculate_matrics(batch_dataset, noise_raw_text)
        for i in range(len(noise_raw_text)):
            if matrics[i] > 0.3 and matrics[i] < 0.7:
                noise_dataset.append(
                    {
                        "raw_asr": noise_raw_text[i],
                        "refined_text": old_dataset[i]["refined_text"],
                    }
                )
