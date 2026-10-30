import json
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
    # 1. Short (<25w, 1 sentence, 0 newlines)
    {
        "raw_asr": "basically routing client reads two the primary database four twenty seconds after right operat eliminates stale replica reads",
        "refined_text": "Routing client reads to the primary database for 20 seconds after write operations eliminates stale replica reads."
    },
    # 2. Short (<25w, 1 sentence, 0 newlines)
    {
        "raw_asr": "um deploying an s f u architecture cuts server c p u load buy forwarding media packets without transcod",
        "refined_text": "Deploying an SFU architecture cuts server CPU load by forwarding media packets without transcoding."
    },
    # 3. Medium (25-90w, 1-3 sentences, \n\n)
    {
        "raw_asr": "basically our zero trust architecture r f c evaluat s p i f f e and s p i r e four automated m t l s certificate rotat across four wait across eight service clusters uh issuing short lived x five zero nine s v i d credentials with one hour validity eliminated vault token renewal overhead and reduced secret revocat latency",
        "refined_text": "Our zero-trust architecture RFC evaluated SPIFFE and SPIRE for automated mTLS certificate rotation across 8 service clusters.\n\nIssuing short-lived X.509 SVID credentials with 1 hour validity eliminated Vault token renewal overhead and reduced secret revocation latency."
    },
    # 4. Medium (25-90w, 1-3 sentences, \n\n)
    {
        "raw_asr": "um the click house storage r f c defined tiered volume lifecycles moving analyt logs from local n v m e drives two s three object storage after fourteen wait after seven days basically configur storage policies with background merge operat preserved fast query performance four hot partitions while cutting cold data retent costs",
        "refined_text": "The ClickHouse storage RFC defined tiered volume lifecycles moving analytical logs from local NVMe drives to S3 object storage after 7 days.\n\nConfiguring storage policies with background merge operations preserved fast query performance for hot partitions while cutting cold data retention costs."
    },
    # 5. Medium (25-90w, 1-3 sentences, \n\n)
    {
        "raw_asr": "our database replicat r f c implemented primary pin routing two guarantee read after right consistency four active user sessions um setting a sticky session cookie that pins web requests two the primary writer four fifteen wait four thirty seconds completely masks asynchron replicat lag across four read replicas",
        "refined_text": "Our database replication RFC implemented primary pin routing to guarantee read-after-write consistency for active user sessions.\n\nSetting a sticky session cookie that pins web requests to the primary writer for 30 seconds completely masks asynchronous replication lag across 4 read replicas."
    },
    # 6. Long (90+w, multi-paragraph \n\n)
    {
        "raw_asr": "basically the database infrastructure r f c evaluat read after right consistency trade offs across our distribut billing services our legacy architecture routed all read traffic randomly across eight read replicas which exposed user workflows two asynchron replicat lag of up two two seconds after order submissions customers frequently observed stale invoice balances immediately after completing checkouts um we compared monotonic client session tokens against gateway level primary pin routing pinning subsequent read requests two the primary database writer four five seconds following any right mutat eliminated stale reads however during flash sales primary c p u utiliz surged two seventy percent because checkout confirmat polling pinned thirty wait pinned forty thousand read queries per second two the writer okay so the r f c committee adopted a hybrid causal consistency strategy using replicat lag watermarks the gateway inspects replicat log sequence numbers across read replicas and routes read requests two any replica that has caught up with the transact commit timestamp this relieved primary database pressure and kept replica query latency below twelve milliseconds",
        "refined_text": "The database infrastructure RFC evaluated read-after-write consistency trade-offs across our distributed billing services. Our legacy architecture routed all read traffic randomly across 8 read replicas, which exposed user workflows to asynchronous replication lag of up to 2 seconds after order submissions. Customers frequently observed stale invoice balances immediately after completing checkouts.\n\nWe compared monotonic client session tokens against gateway-level primary pin routing. Pinning subsequent read requests to the primary database writer for 5 seconds following any write mutation eliminated stale reads. However, during flash sales, primary CPU utilization surged to 70% because checkout confirmation polling pinned 40000 read queries per second to the writer.\n\nThe RFC committee adopted a hybrid causal consistency strategy using replication lag watermarks. The gateway inspects replication log sequence numbers across read replicas and routes read requests to any replica that has caught up with the transaction commit timestamp. This relieved primary database pressure and kept replica query latency below 12 milliseconds."
    },
    # 7. Long (90+w, multi-paragraph \n\n)
    {
        "raw_asr": "basically our web r t c gateway architecture a d r resolved server scaling bottlenecks across interactive video conferencing rooms the existing media platform deployed m c u knowed instances that decoded composited and re encoded video streams four every participant centralized m c u mixing consumed excessive c p u resources capping knowed density at sixteen concurrent streams per media instance uh we benchmarked s f u selective packet forwarding against m c u centralized transcod across fifty participant video rooms in the s f u architecture media servers forward raw s r t p packets directly without transcod video payloads shifting encoding workloads two client devices while server c p u utiliz dropped from ninety percent two fifteen percent downstream client egress bandwidth expanded linearly with room attendance um the architectural board approved migrating two an s f u design with simulcast and selective forwarding layers clients publish three distinct spatial resolut layers allowing the media gateway two selectively forward lower bitrate video tracks two bandwidth constrained participants this architecture scales video conferences two sixty wait two one hundred participants while maintaining end two end packet latency under eighty milliseconds",
        "refined_text": "Our WebRTC gateway architecture ADR resolved server scaling bottlenecks across interactive video conferencing rooms. The existing media platform deployed MCU node instances that decoded, composited, and re-encoded video streams for every participant. Centralized MCU mixing consumed excessive CPU resources, capping node density at 16 concurrent streams per media instance.\n\nWe benchmarked SFU selective packet forwarding against MCU centralized transcoding across 50 participant video rooms. In the SFU architecture, media servers forward raw SRTP packets directly without transcoding video payloads, shifting encoding workloads to client devices. While server CPU utilization dropped from 90% to 15%, downstream client egress bandwidth expanded linearly with room attendance.\n\nThe architectural board approved migrating to an SFU design with simulcast and selective forwarding layers. Clients publish 3 distinct spatial resolution layers, allowing the media gateway to selectively forward lower bitrate video tracks to bandwidth-constrained participants. This architecture scales video conferences to 100 participants while maintaining end-to-end packet latency under 80 milliseconds."
    },
    # 8. Long (90+w, multi-paragraph \n\n)
    {
        "raw_asr": "um our infrastructure security r f c evaluat automated m t l s certificate rotat across twenty thousand microservice workloads the existing implement used vault app role authenticat with short lived tokens two fetch t l s certificates under cluster churn ninety service instances simultaneously re authenticating against vault triggered severe a p i rate limiting and delayed pod startup times buy thirty wait buy forty seconds basically we benchmarked s p i f f e and s p i r e workload identity attestat against the centralized vault model buy deploying the s p i r e agent as a daemon set on each coober netties knowed workloads authenticate locally using unix domain socket attestat without transmitting long lived secrets the s p i r e server rotates x five zero nine s v i d credentials every six hours through e n v o y secret discovery service dynamic updates okay so the security review committee approved deploying s p i r e four service mesh identity management workloads perform cryptographic attestat using kernel attributes and c group membership completely eliminating secret zero bootstrapping vulnerabilities the automated rotat pipeline maintains continuous m t l s communicat without dropping active t c p connections across ninety six knowed clusters",
        "refined_text": "Our infrastructure security RFC evaluated automated mTLS certificate rotation across 20000 microservice workloads. The existing implementation used Vault AppRole authentication with short-lived tokens to fetch TLS certificates. Under cluster churn, 90 service instances simultaneously re-authenticating against Vault triggered severe API rate limiting and delayed pod startup times by 40 seconds.\n\nWe benchmarked SPIFFE and SPIRE workload identity attestation against the centralized Vault model by deploying the SPIRE agent as a daemonset on each Kubernetes node. Workloads authenticate locally using UNIX domain socket attestation without transmitting long-lived secrets. The SPIRE server rotates X.509 SVID credentials every 6 hours through Envoy Secret Discovery Service dynamic updates.\n\nThe security review committee approved deploying SPIRE for service mesh identity management. Workloads perform cryptographic attestation using kernel attributes and cgroup membership, completely eliminating secret 0 bootstrapping vulnerabilities. The automated rotation pipeline maintains continuous mTLS communication without dropping active TCP connections across 96 node clusters."
    },
    # 9. Long (90+w, multi-paragraph \n\n)
    {
        "raw_asr": "basically our log analytics r f c redesigned tiered storage lifecycle policies across a seventy knowed click house cluster the platform ingests fifty terabytes of log data daily consuming six hundred terabytes of raw storage monthly retaining all historical logs on local n v m e solid state disks exceeded budget ceilings and saturated hardware storage controllers um we benchmarked click house tiered storage disks configur with volume t t l move policies against monolithic disk architectures under the new policy the merge tree storage engine retains incoming partit parts on local n v m e arrays four twenty wait four fourteen days before background worker threads migrate inactive parts two cold s three object storage s three offloading reduced n v m e disk consumpt buy sixty five percent okay so analyt queries targeting historical logs over thirty days old experienced an acceptable read latency increase from two hundred milliseconds two eight hundred milliseconds buy configur local metadata caching and aggressive columnar mark caches the cluster avoids repetitive s three get requests during log aggregat the committee adopted the tiered storage policy across all product analyt clusters",
        "refined_text": "Our log analytics RFC redesigned tiered storage lifecycle policies across a 70 node ClickHouse cluster. The platform ingests 50 terabytes of log data daily, consuming 600 terabytes of raw storage monthly. Retaining all historical logs on local NVMe solid-state disks exceeded budget ceilings and saturated hardware storage controllers.\n\nWe benchmarked ClickHouse tiered storage disks configured with volume TTL move policies against monolithic disk architectures. Under the new policy, the MergeTree storage engine retains incoming partition parts on local NVMe arrays for 14 days before background worker threads migrate inactive parts to cold S3 object storage. S3 offloading reduced NVMe disk consumption by 65%.\n\nAnalytical queries targeting historical logs over 30 days old experienced an acceptable read latency increase from 200 milliseconds to 800 milliseconds. By configuring local metadata caching and aggressive columnar mark caches, the cluster avoids repetitive S3 GET requests during log aggregations. The committee adopted the tiered storage policy across all production analytical clusters."
    },
    # 10. Long (90+w, multi-paragraph \n\n)
    {
        "raw_asr": "basically our real time communicat r f c evaluat multi region s f u cascading architectures four global video conferences the previous monolithic deployment routed all participant media streams two a single media cluster in north america international participants in europe and asia experienced over three hundred milliseconds of round trip latency and severe packet loss um we benchmarked edge s f u ingest proxies against direct origin connections across ten wait across twenty thousand concurrent video sessions in the cascaded s f u topology edge media gateways terminate local web r t c connections and forward a single muxed video stream over dedicated backbone links two origin media clusters this proxy relay design reduced egress bandwidth across regional backbones buy sixty percent okay so the r f c committee approved cascading s f u media clusters across six cloud regions edge gateways utilize adaptive bit rate renegotiat and forward n a c k repair requests locally preventing packet retransmiss requests from traversing transoceanic routes this distribut routing keeps global audio jitter below twenty milliseconds and stabilizes video delivery across thirty two participant conference rooms",
        "refined_text": "Our real-time communications RFC evaluated multi-region SFU cascading architectures for global video conferences. The previous monolithic deployment routed all participant media streams to a single media cluster in North America. International participants in Europe and Asia experienced over 300 milliseconds of round-trip latency and severe packet loss.\n\nWe benchmarked edge SFU ingestion proxies against direct origin connections across 20000 concurrent video sessions. In the cascaded SFU topology, edge media gateways terminate local WebRTC connections and forward a single muxed video stream over dedicated backbone links to origin media clusters. This proxy relay design reduced egress bandwidth across regional backbones by 60%.\n\nThe RFC committee approved cascading SFU media clusters across 6 cloud regions. Edge gateways utilize adaptive bit rate renegotiation and forward NACK repair requests locally, preventing packet retransmission requests from traversing transoceanic routes. This distributed routing keeps global audio jitter below 20 milliseconds and stabilizes video delivery across 32 participant conference rooms."
    }
]

def run():
    print(f"Auditing {len(samples)} candidate samples...\n")
    all_ok = True
    for i, s in enumerate(samples, 1):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])

        ref_words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = ref_words / max(1, raw_words)

        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"Sample {i:02d}: [{status}] ({ref_words}w ref, {raw_words}w raw, ratio {ratio:.2f})")
        if not v_ok:
            print(f"  Validator failure: {v_reason}")
        if c_res is None:
            print(f"  Cleaner failure: {c_reason}")

    b_ok, b_reason, b_counts = validate_batch(samples, min_short=2, min_medium=3, min_long=5)
    print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
    print(f"Tier counts: {b_counts}")
    print(f"Overall status: {'ALL PASS (10/10)' if all_ok and b_ok else 'AUDIT FAILED'}")

    if all_ok and b_ok:
        with open("scratch/subagent_batch_23.json", "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2, ensure_ascii=False)
        print("\nWrote verified batch to scratch/subagent_batch_23.json")

if __name__ == "__main__":
    run()
