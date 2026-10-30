import json
import re

SYMBOL_MAP = {
    "/": " slash ",
    "\\": " backslash ",
    ".": " dot ",
    "-": " dash ",
    "_": " underscore ",
    "=": " equals ",
    ":": " colon ",
    "*": " star ",
    "@": " at ",
    "&": " and ",
    "+": " plus ",
    "%": " percent ",
    "#": " hash ",
    "~": " tilde ",
}

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TENS = [
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]
TEENS = [
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
DIGITS = {str(i): w for i, w in enumerate(ONES)}


def int2words(n):
    if n < 0:
        return "minus " + int2words(-n)
    if n < 10:
        return ONES[n]
    if n < 20:
        return TEENS[n - 10]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        return (
            ONES[n // 100]
            + " hundred"
            + ("" if n % 100 == 0 else " " + int2words(n % 100))
        )
    for mag, word in ((10**9, "billion"), (10**6, "million"), (10**3, "thousand")):
        if n >= mag:
            return (
                int2words(n // mag)
                + " "
                + word
                + ("" if n % mag == 0 else " " + int2words(n % mag))
            )
    return str(n)


def spell(s):
    out = []
    for c in s:
        if c.isdigit():
            out.append(DIGITS[c])
        elif c.isalpha():
            out.append(c.lower())
        else:
            out.append(c)
    return " ".join(out)


def remove_headers(refined_text):
    t = refined_text
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"(?<!\w)[*_]{1,3}([^*_]+)[*_]{1,3}(?!\w)", r"\1", t)
    t = re.sub(r"^\s*#{1,6}\s*", "", t, flags=re.M)
    t = re.sub(r"^\s*[-*+]\s+", "", t, flags=re.M)
    t = re.sub(r"^\s*-{3,}\s*$", "", t, flags=re.M)
    t = re.sub(r"[\[\]()]", "", t)
    return t


def _expand_token(tok):
    if not tok:
        return tok
    if re.fullmatch(r"0[xX][0-9a-fA-F]+", tok):
        return "zero x " + spell(tok[2:])
    m = re.fullmatch(r"(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?", tok)
    if m:
        ip = " dot ".join(spell(p) for p in m.group(1).split("."))
        return ip + (" colon " + spell(m.group(2)) if m.group(2) else "")
    m = re.fullmatch(r"(v?)(\d+(?:\.\d+)+)", tok)
    if m:
        prefix = m.group(1)
        parts = " point ".join(
            spell(p) if len(p) > 1 else int2words(int(p)) for p in m.group(2).split(".")
        )
        return (prefix + " " + parts) if prefix else parts
    m = re.fullmatch(r"(\d+)(%|ms|s|kb|mb|gb|tb|k|m)?", tok, re.I)
    if m:
        n = int2words(int(m.group(1)))
        unit = m.group(2)
        if unit is None:
            return n
        return (
            n
            + " "
            + {"%": "percent", "k": "thousand", "m": "million"}.get(unit.lower(), unit)
        )
    if "=" in tok and re.fullmatch(r"[A-Za-z0-9_./:=-]+", tok):
        left, right = tok.split("=", 1)
        return _expand_token(left) + " equals " + _expand_token(right)
    if re.fullmatch(r"--[A-Za-z0-9_-]+", tok):
        return "dash dash " + tok[2:].replace("-", " ").lower()
    if re.fullmatch(r"-[A-Za-z0-9]", tok):
        return "dash " + tok[1].lower()
    if "/" in tok or "\\" in tok:
        s = tok.replace("\\", " backslash ").replace("/", " slash ")
        s = s.replace(".", " dot ").replace("-", " dash ").replace("_", " underscore ")
        return re.sub(r"\s+", " ", s).strip()
    if "_" in tok:
        return tok.replace("_", " ")
    if re.search(r"[a-z0-9][A-Z]", tok) or re.search(r"[A-Z]{2,}[a-z]", tok):
        tok = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", tok)
        tok = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", tok)
        return " ".join(_expand_token(p) for p in tok.split())
    if re.fullmatch(r"[A-Za-z]+(?:-[A-Za-z]+)+", tok):
        return " ".join(_expand_token(p) for p in tok.split("-"))
    return tok


def map_dot_to_dot_dash_to_dash_etc(refined_text):
    out = []
    for raw in refined_text.split():
        m = re.match(r"^(.*?)([.,;:!?]+)?$", raw)
        core, punct = m.group(1), (m.group(2) or "")
        out.append((_expand_token(core) if core else "") + punct)
    t = " ".join(out)
    t = re.sub(r"\s+([,;:!?])", r"\1", t)
    t = re.sub(r"\s*\.\s*", ". ", t).strip()
    return re.sub(r"\s{2,}", " ", t).lower()


cleanup_func = [remove_headers, map_dot_to_dot_dash_to_dash_etc]

dataset_tts = {"refined_text": []}


def iter_records(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            yield from data
            return
        if isinstance(data, dict):
            yield data
            return
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        obj, i = decoder.raw_decode(text, i)
        yield obj


def tts_ready(path: str = "combined_dataset.json"):
    dataset_tts["refined_text"].clear()
    for item in iter_records(path):
        refined_text = item["refined_text"]
        for func in cleanup_func:
            refined_text = func(refined_text)
        dataset_tts["refined_text"].append(refined_text)
    return dataset_tts


if __name__ == "__main__":
    data = tts_ready()
    with open("tts_input_dataset.json", "w", encoding="utf-8") as f:
        json.dump(data, f)
