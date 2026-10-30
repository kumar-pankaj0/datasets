import re

with open('prompt/subagent_dataset_generator.md', 'r') as f:
    content = f.read()

# The clean original text had: Zero '---' dividers.
# Let's fix lines where 'Zero `### 4.2' occurred
cleaned = re.sub(
    r'Zero `### 4\.2.*?\n---\` dividers\.',
    "Zero '---' dividers.",
    content,
    flags=re.DOTALL
)

# And remove any stray ### 4.2 block at the end of section 3
cleaned = re.sub(
    r'\n+### 4\.2 Calibrated Noise Density & Count Distribution Sampling Protocol\n+To prevent low-count noise collapse.*?(?=\n## 4\. Acoustic Noise)',
    '\n\n---\n\n',
    cleaned,
    flags=re.DOTALL
)

# Remove any duplicate 4.2 blocks if multiple exist
parts = cleaned.split('### 4.2 Calibrated Noise Density & Count Distribution Sampling Protocol')
if len(parts) > 2:
    # keep only the last one
    cleaned = parts[0] + '### 4.2 Calibrated Noise Density & Count Distribution Sampling Protocol' + parts[-1]

with open('prompt/subagent_dataset_generator.md', 'w') as f:
    f.write(cleaned)

print('Cleaned prompt/subagent_dataset_generator.md successfully.')
