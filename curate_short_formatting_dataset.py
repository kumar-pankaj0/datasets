#!/usr/bin/env python3
import json
import random
import math
import re
from collections import Counter

INPUT_PATH = "/data/data/com.termux/files/home/project/dataset_generation_for_juage/second_face_dataset.json"
OUTPUT_PATH = "/data/data/com.termux/files/home/project/dataset_generation_for_juage/curated_short_formatting.json"

def pearson_r(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    vx = sum((xi - mx)**2 for xi in x)
    vy = sum((yi - my)**2 for yi in y)
    cov = sum((xi - mx)*(yi - my) for xi, yi in zip(x, y))
    denom = math.sqrt(vx * vy)
    return cov / denom if denom != 0 else 0

def generate_curated_dataset():
    with open(INPUT_PATH) as f:
        full_data = json.load(f)

    # Samples 150 to 299 (the short-text over-formatting shard)
    shard = full_data[150:300]
    assert len(shard) == 150, f"Expected 150 samples, got {len(shard)}"

    # Determine balanced orthogonal scores
    random.seed(42)

    # 4 severity tiers:
    # Tier 1 (fmt=1): 38 samples
    # Tier 2 (fmt=3): 37 samples
    # Tier 3 (fmt=5): 38 samples
    # Tier 4 (fmt=7): 37 samples

    def build_tier_scores(n, f_dist, nr_dist, ef_dist):
        f_list = [7]*f_dist[7] + [9]*f_dist[9]
        nr_list = [7]*nr_dist[7] + [9]*nr_dist[9]
        ef_list = [5]*ef_dist[5] + [7]*ef_dist[7] + [9]*ef_dist[9]
        best = None
        min_corr = 999
        for _ in range(5000):
            random.shuffle(f_list)
            random.shuffle(nr_list)
            random.shuffle(ef_list)
            c1 = abs(pearson_r(f_list, nr_list))
            c2 = abs(pearson_r(f_list, ef_list))
            c3 = abs(pearson_r(nr_list, ef_list))
            sc = max(c1, c2, c3)
            if sc < min_corr:
                min_corr = sc
                best = (list(f_list), list(nr_list), list(ef_list))
                if min_corr < 0.03:
                    break
        return best

    t1_f, t1_nr, t1_ef = build_tier_scores(38, {7: 19, 9: 19}, {7: 19, 9: 19}, {5: 13, 7: 13, 9: 12})
    t2_f, t2_nr, t2_ef = build_tier_scores(37, {7: 18, 9: 19}, {7: 18, 9: 19}, {5: 12, 7: 12, 9: 13})
    t3_f, t3_nr, t3_ef = build_tier_scores(38, {7: 19, 9: 19}, {7: 19, 9: 19}, {5: 13, 7: 12, 9: 13})
    t4_f, t4_nr, t4_ef = build_tier_scores(37, {7: 19, 9: 18}, {7: 19, 9: 18}, {5: 12, 7: 13, 9: 12})

    f_all = t1_f + t2_f + t3_f + t4_f
    nr_all = t1_nr + t2_nr + t3_nr + t4_nr
    ef_all = t1_ef + t2_ef + t3_ef + t4_ef
    fmt_all = [1]*38 + [3]*37 + [5]*38 + [7]*37

    # Verify distribution targets
    assert Counter(fmt_all) == {1: 38, 5: 38, 3: 37, 7: 37}
    assert Counter(f_all) == {7: 75, 9: 75}
    assert Counter(nr_all) == {7: 75, 9: 75}
    assert Counter(ef_all) == {5: 50, 7: 50, 9: 50}

    # Now define refined text generator
    def craft_refined_text(idx, raw, f, nr, ef, fmt):
        text = raw.strip()

        # 1. Fillers handling (noise_removed)
        # raw fillers: 'uh', 'um', 'like', 'just', 'ah', 'can you like', 'can you please'
        filler_prefixes = [
            ('ah just ', 'Just ' if nr == 7 else ''),
            ('uh restart the um ', 'Please restart the ' if nr == 7 else 'Restart the '),
            ('uh apply the ', 'Just apply the ' if nr == 7 else 'Apply the '),
            ('uh configure the ', 'Please configure the ' if nr == 7 else 'Configure the '),
            ('uh list all ', 'Just list all ' if nr == 7 else 'List all '),
            ('uh provision a ', 'Please provision a ' if nr == 7 else 'Provision a '),
            ('um update the ', 'Just update the ' if nr == 7 else 'Update the '),
            ('like update the ', 'Like, update the ' if nr == 7 else 'Update the '),
            ('can you like flush the ', 'Can you flush the ' if nr == 7 else 'Flush the '),
            ('can you please check the ', 'Can you please check the ' if nr == 7 else 'Check the '),
            ('just clear the ', 'Just clear the ' if nr == 7 else 'Clear the '),
            ('just tail the ', 'Just tail the ' if nr == 7 else 'Tail the '),
        ]
        
        cleaned = None
        for prefix, repl in filler_prefixes:
            if text.startswith(prefix):
                cleaned = repl + text[len(prefix):]
                break
        if cleaned is None:
            cleaned = text[0].upper() + text[1:]

        # 2. Faithfulness variations (f == 7: slight synonym/paraphrase while preserving 100% meaning)
        if f == 7:
            paraphrases = [
                ("and deploy it now", "and deploy it right away"),
                ("so we can access internal tools", "to access internal tools"),
                ("to fix the stale data issue", "to resolve the stale data issue"),
                ("before the backup window closes", "prior to the backup window closing"),
                ("for the billing service", "associated with the billing service"),
                ("on the read replica database", "for the read replica database"),
                ("and report the results", "and provide the test results"),
                ("that started yesterday", "which began yesterday"),
                ("to troubleshoot the failed transactions", "to diagnose the failed transactions"),
                ("it seems to be hanging", "it appears to be hanging"),
                ("in the dev cluster", "within the dev cluster"),
                ("it is completely unresponsive", "it has become completely unresponsive"),
                ("immediately to prevent abuse", "right away to prevent unauthorized access"),
                ("before it crashes", "prior to crashing"),
                ("to localhost", "directly to localhost"),
                ("and upgrade the release", "and proceed with the release upgrade"),
                ("immediately before it locks the table", "promptly before the table gets locked"),
                ("so we can test the changes", "to test the upcoming changes"),
                ("and filter by ip", "and filter them by ip"),
                ("with multi az enabled", "with Multi-AZ active"),
                ("over the last hour", "during the past hour"),
                ("right now", "immediately"),
                ("to block http traffic", "to deny incoming http traffic"),
                ("to previous version as soon as possible", "to the previous version as soon as possible"),
                ("because of the high traffic", "due to the high traffic load"),
                ("it is running out of heap", "it is exhausting its heap memory"),
                ("in the us east region", "within the us east region"),
                ("for the new domain", "on the new domain name"),
                ("expiration date on the main load balancer", "expiry date on the primary load balancer"),
                ("it is resolving incorrectly", "it is resolving improper addresses"),
                ("for the new microservices", "across the new microservices"),
                ("for the new release", "for the upcoming release"),
                ("on the staging server", "across the staging environment"),
                ("to save some money on aws", "to reduce storage expenses on aws"),
            ]
            for orig, para in paraphrases:
                if orig in cleaned:
                    cleaned = cleaned.replace(orig, para)
                    break

        # 3. Technical entities casing & grammar (errors_fixed)
        if ef == 9:
            # Full capitalization of technical entities
            casing_replacements = [
                (r'\becr\b', 'ECR'),
                (r'\bvpn\b', 'VPN'),
                (r'\bredis\b', 'Redis'),
                (r'\bs3\b', 'S3'),
                (r'\bjava\b', 'Java'),
                (r'\bdocker\b', 'Docker'),
                (r'\bec2\b', 'EC2'),
                (r'\brds\b', 'RDS'),
                (r'\bkubernetes\b', 'Kubernetes'),
                (r'\bssh\b', 'SSH'),
                (r'\bdns\b', 'DNS'),
                (r'\bpostgres\b', 'PostgreSQL'),
                (r'\bapi\b', 'API'),
                (r'\bssl\b', 'SSL'),
                (r'\bkafka\b', 'Kafka'),
                (r'\bmemcached\b', 'Memcached'),
                (r'\bgrafana\b', 'Grafana'),
                (r'\blinux\b', 'Linux'),
                (r'\bcpu\b', 'CPU'),
                (r'\bhelm\b', 'Helm'),
                (r'\bterraform\b', 'Terraform'),
                (r'\bhttps\b', 'HTTPS'),
                (r'\bhttp\b', 'HTTP'),
                (r'\bip\b', 'IP'),
                (r'\bqa\b', 'QA'),
                (r'\baws\b', 'AWS'),
                (r'\bglacier\b', 'Glacier'),
                (r'\belasticsearch\b', 'Elasticsearch'),
                (r'\bmulti az\b', 'Multi-AZ'),
                (r'\bus east one\b', 'us-east-1'),
                (r'\bus east\b', 'us-east'),
                (r'\bnode three\b', 'node-3'),
            ]
            for pat, rep in casing_replacements:
                cleaned = re.sub(pat, rep, cleaned, flags=re.IGNORECASE)
            
            # Clause fixes (run-ons)
            if "node-3 it" in cleaned:
                cleaned = cleaned.replace("node-3 it", "node-3; it")
            if "us-east-1 it" in cleaned:
                cleaned = cleaned.replace("us-east-1 it", "us-east-1; it")
            if "cluster it" in cleaned:
                cleaned = cleaned.replace("cluster it", "cluster, it")
            if "server it" in cleaned:
                cleaned = cleaned.replace("server it", "server; it")
            if "previous version" in cleaned and "to previous" in cleaned:
                cleaned = cleaned.replace("to previous", "to the previous")

        elif ef == 7:
            # Standard capitalization and clean grammar, but keep some acronyms lowercase or standard
            casing_replacements = [
                (r'\bredis\b', 'Redis'),
                (r'\bjava\b', 'Java'),
                (r'\bdocker\b', 'Docker'),
                (r'\bkubernetes\b', 'Kubernetes'),
                (r'\bpostgres\b', 'Postgres'),
                (r'\bssl\b', 'SSL'),
                (r'\bkafka\b', 'Kafka'),
                (r'\bmemcached\b', 'Memcached'),
                (r'\bgrafana\b', 'Grafana'),
                (r'\blinux\b', 'Linux'),
                (r'\bhelm\b', 'Helm'),
                (r'\bterraform\b', 'Terraform'),
                (r'\belasticsearch\b', 'Elasticsearch'),
            ]
            for pat, rep in casing_replacements:
                cleaned = re.sub(pat, rep, cleaned, flags=re.IGNORECASE)
            # Add comma for compound sentence
            if "node three it" in cleaned:
                cleaned = cleaned.replace("node three it", "node three, it")
            if "us east one it" in cleaned:
                cleaned = cleaned.replace("us east one it", "us east one, it")
            if "cluster it" in cleaned:
                cleaned = cleaned.replace("cluster it", "cluster, it")

        elif ef == 5:
            # Minor casing/grammar flaws left unfixed: lowercase tech acronyms and run-ons without comma
            pass

        # Ensure sentence capitalization
        cleaned = cleaned[0].upper() + cleaned[1:]
        cleaned = cleaned.rstrip('.!?;:, ')

        # 4. Formatting severity tiers (TARGETED METRIC)
        if fmt == 1:
            # Severe over-formatting:
            # Short sentence with ---, \n\n, !!!!, and markdown headers all combined
            header_styles = [
                "### Alert: Urgent Execution Required ###",
                "## Priority Command Directive ##",
                "### System Maintenance Notice ###",
                "## Critical Action Item ##",
                "### Execution Notice ###"
            ]
            hdr = header_styles[idx % len(header_styles)]
            emphasis = f"**{cleaned}!!!!**" if idx % 2 == 0 else f"_{cleaned}!!!!_"
            refined = f"{hdr}\n\n---\n\n{emphasis}\n\n---\n\n"

        elif fmt == 3:
            # Moderate over-formatting:
            # Short sentence with forced --- divider OR ## header (only one type!)
            if idx % 2 == 0:
                headers = ["## Task", "## Command", "## Action", "## Notice"]
                hdr = headers[(idx // 2) % len(headers)]
                refined = f"{hdr}\n\n{cleaned}."
            else:
                refined = f"{cleaned}.\n\n---"

        elif fmt == 5:
            # Mild over-formatting:
            # Short sentence with unnecessary !! or extra punctuation
            if cleaned.lower().startswith("can you"):
                refined = f"{cleaned}??"
            else:
                refined = f"{cleaned}!!"

        elif fmt == 7:
            # Minor formatting issue:
            # Clean sentence with technical styling, but missing a single backtick on a tech term or slight quote inconsistency
            # Identify tech terms in the text to format authentically
            tech_terms = [
                'ECR', 'ecr', 'VPN', 'vpn', 'Redis', 'redis', 'S3', 's3',
                'Java', 'java', 'Docker', 'docker', 'EC2', 'ec2', 'RDS', 'rds',
                'Kubernetes', 'kubernetes', 'SSH', 'ssh', 'DNS', 'dns',
                'PostgreSQL', 'Postgres', 'postgres', 'API', 'api', 'SSL', 'ssl',
                'Kafka', 'kafka', 'Memcached', 'memcached', 'Grafana', 'grafana',
                'Linux', 'linux', 'CPU', 'cpu', 'Helm', 'helm', 'Terraform', 'terraform',
                'HTTPS', 'https', 'HTTP', 'http', 'IP', 'ip', 'QA', 'qa',
                'AWS', 'aws', 'Glacier', 'glacier', 'Elasticsearch', 'elasticsearch',
                'us-east-1', 'us-east', 'node-3', 'dev', 'staging', 'main'
            ]
            found_terms = [t for t in tech_terms if re.search(r'\b' + re.escape(t) + r'\b', cleaned)]

            if found_terms:
                t0 = found_terms[0]
                if idx % 3 == 0:
                    # Missing backtick on primary tech term (clean sentence, just missing backtick)
                    # e.g. `Restart the docker daemon on node-3.`
                    refined = f"{cleaned}."
                elif idx % 3 == 1:
                    # Inconsistent quote/tick style: backtick on one term, single quote on another
                    if len(found_terms) > 1:
                        t1 = found_terms[1]
                        mod = re.sub(r'\b' + re.escape(t0) + r'\b', f'`{t0}`', cleaned, count=1)
                        mod = re.sub(r'\b' + re.escape(t1) + r'\b', f"'{t1}'", mod, count=1)
                        refined = f"{mod}."
                    else:
                        # Backtick on tech term, single quotes on action or modifier
                        words = cleaned.split()
                        if len(words) > 3:
                            mod = re.sub(r'\b' + re.escape(t0) + r'\b', f'`{t0}`', cleaned, count=1)
                            # add single quote around last word
                            words_mod = mod.split()
                            words_mod[-1] = f"'{words_mod[-1]}'"
                            refined = " ".join(words_mod) + "."
                        else:
                            refined = f"{cleaned}."
                else:
                    # Backtick on one tech term, but missing backtick on secondary term
                    if len(found_terms) > 1:
                        t1 = found_terms[1]
                        mod = re.sub(r'\b' + re.escape(t0) + r'\b', f'`{t0}`', cleaned, count=1)
                        # t1 remains unbackticked
                        refined = f"{mod}."
                    else:
                        refined = f"{cleaned}."
            else:
                # No tech term found: slight quote inconsistency on branch or parameter
                if "'main'" in cleaned or "main" in cleaned:
                    mod = cleaned.replace("main", "'main'").replace("results", '"results"')
                    refined = f"{mod}."
                else:
                    refined = f"{cleaned}."

        return refined

    # Construct the curated 150 samples
    curated_samples = []
    for i in range(150):
        raw = shard[i]["input"]["raw_asr"]
        f = f_all[i]
        nr = nr_all[i]
        ef = ef_all[i]
        fmt = fmt_all[i]

        ref = craft_refined_text(i, raw, f, nr, ef, fmt)

        curated_samples.append({
            "input": {
                "raw_asr": raw,
                "refined_text": ref
            },
            "output": {
                "faithfulness": f,
                "noise_removed": nr,
                "errors_fixed": ef,
                "formatting": fmt
            }
        })

    # Save to curated_short_formatting.json
    with open(OUTPUT_PATH, "w") as f:
        json.dump(curated_samples, f, indent=2)

    print(f"Successfully saved {len(curated_samples)} samples to {OUTPUT_PATH}")

    # Audit & report distributions
    required_dims = ['faithfulness', 'noise_removed', 'errors_fixed', 'formatting']
    print("\n" + "=" * 68)
    print("      CURATED SHORT FORMATTING DATASET AUDIT REPORT")
    print("=" * 68)
    print(f"Total Curated Samples: {len(curated_samples)}\n")

    print("--- SCORE DISTRIBUTIONS ACROSS 4 METRICS ---")
    print(f"{'Metric':<16} | {'Score 1':<9} | {'Score 3':<9} | {'Score 5':<9} | {'Score 7':<9} | {'Score 9':<9}")
    print("-" * 68)
    for dim in required_dims:
        counts = Counter(s['output'][dim] for s in curated_samples)
        row = [f"{counts[k]} ({counts[k]/len(curated_samples)*100:.1f}%)" for k in [1, 3, 5, 7, 9]]
        print(f"{dim:<16} | {row[0]:<9} | {row[1]:<9} | {row[2]:<9} | {row[3]:<9} | {row[4]:<9}")
    print("-" * 68)

    print("\n--- METRIC ORTHOGONALITY MATRIX (PEARSON r) ---")
    vals = {d: [s['output'][d] for s in curated_samples] for d in required_dims}
    print(f"{'Metric':<16} | {'faithfulness':<12} | {'noise_removed':<13} | {'errors_fixed':<12} | {'formatting':<10}")
    print("-" * 68)
    for d1 in required_dims:
        row = [f"{pearson_r(vals[d1], vals[d2]):6.3f}" for d2 in required_dims]
        print(f"{d1:<16} | {row[0]:<12} | {row[1]:<13} | {row[2]:<12} | {row[3]:<10}")

if __name__ == "__main__":
    generate_curated_dataset()
