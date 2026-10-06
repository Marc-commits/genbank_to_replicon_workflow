validate(config, "../schemas/config.schema.yaml")

VALID_MODES = ("genbank", "fasta_gff")

HAS_BASE_GENOME = bool(config.get("base_genome", {}).get("fasta"))

# `input` may be omitted for a base-genome-only build (no extra replicon):
# the index/IGV genome/annotations then come from base_genome alone.
HAS_REPLICON = bool(config.get("input"))

if HAS_REPLICON:
    if config["input"]["mode"] not in VALID_MODES:
        raise ValueError(
            f"config['input']['mode'] must be one of {VALID_MODES}, "
            f"got {repr(config['input']['mode'])}"
        )
    MODE = config["input"]["mode"]
    CONTIG_NAME = config["input"]["contig_name"]
elif HAS_BASE_GENOME:
    MODE = None
    CONTIG_NAME = None
    _missing = [
        k for k in ("genes_gff", "transcripts_gff") if not config["base_genome"].get(k)
    ]
    if _missing:
        raise ValueError(
            f"base-genome-only build (no config['input']) requires "
            f"config['base_genome'] keys {_missing}"
        )
else:
    raise ValueError(
        "config needs either 'input' (replicon) and/or 'base_genome.fasta'"
    )

OUTPUT_PREFIX = config["output_prefix"]


HAS_BASE_GENOME = bool(config.get("base_genome", {}).get("fasta"))


def replicon_output(name):
    return getattr(rules, REPLICON_RULE).output[name]


def combine_annotations_input(wildcards):
    inputs = {}
    if HAS_REPLICON:
        inputs["replicon_genes_gff"] = replicon_output("genes_gff")
        inputs["replicon_transcripts_gff"] = replicon_output("transcripts_gff")
    if HAS_BASE_GENOME:
        inputs["base_genes_gff"] = config["base_genome"]["genes_gff"]
        inputs["base_transcripts_gff"] = config["base_genome"]["transcripts_gff"]
    return inputs
