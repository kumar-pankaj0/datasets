import re

HOMOPHONES = [
    (r"\bright\b", "write"),
    (r"\bbuy\b", "by"),
    (r"\bfour\b", "for"),
    (r"\btwo\b", "to"),
    (r"\bknowed\b", "node"),
    (r"\broot\b", "route"),
]

PHONETIC_TERMS = [
    ("cube ctl", "kubectl"), ("cube see tee ell", "kubectl"), ("cube sea tea ell", "kubectl"),
    ("cube cuddle", "kubectl"), ("coober netties", "kubernetes"), ("cube let", "kubelet"),
    ("cube adm", "kubeadm"), ("post gres", "postgres"), ("free are toss", "freertos"),
    ("open see vee", "opencv"), ("wi re shark", "wireshark"), ("c group v two", "cgroupv2"),
    ("c group", "cgroup"), ("c n i", "cni"), ("slash", " "), ("dot", " "),
    ("dash", " "), ("minus", "-"), ("negative", "-"), ("colon", ":"), ("equals", "="),
    ("zero x", "0x"), ("a sink i o", "asyncio"), ("a sink", "async"),
]

# Spoken number conversion
ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}

TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
}

def parse_spoken_number_phrases(text: str) -> str:
    """Converts phrases like 'two hundred fifty six' to '256', and 'one three seven' to '137'."""
    tokens = text.lower().split()
    out = []
    i = 0
    while i < len(tokens):
        # Check compound like "two hundred fifty six"
        if (i + 3 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred" 
            and tokens[i+2] in TENS and tokens[i+3] in ONES):
            val = ONES[tokens[i]] * 100 + TENS[tokens[i+2]] + ONES[tokens[i+3]]
            out.append(str(val))
            i += 4
        # "two hundred fifty"
        elif (i + 2 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred" and tokens[i+2] in TENS):
            val = ONES[tokens[i]] * 100 + TENS[tokens[i+2]]
            out.append(str(val))
            i += 3
        # "two hundred six"
        elif (i + 2 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred" and tokens[i+2] in ONES):
            val = ONES[tokens[i]] * 100 + ONES[tokens[i+2]]
            out.append(str(val))
            i += 3
        # "one hundred"
        elif (i + 1 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred"):
            val = ONES[tokens[i]] * 100
            out.append(str(val))
            i += 2
        # "twenty six"
        elif (i + 1 < len(tokens) and tokens[i] in TENS and tokens[i+1] in ONES):
            val = TENS[tokens[i]] + ONES[tokens[i+1]]
            out.append(str(val))
            i += 2
        elif tokens[i] in TENS:
            out.append(str(TENS[tokens[i]]))
            i += 1
        elif tokens[i] in ONES:
            out.append(str(ONES[tokens[i]]))
            i += 1
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)

print("Test compound 1:", parse_spoken_number_phrases("exit code one three seven because limit two hundred fifty six megabytes"))
print("Test compound 2:", parse_spoken_number_phrases("block size twenty six and port eight zero eight zero"))
