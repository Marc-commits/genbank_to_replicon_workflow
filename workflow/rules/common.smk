validate(config, "../schemas/config.schema.yaml")

VALID_MODES = ("genbank", "fasta_gff")

if config["input"]["mode"] not in VALID_MODES:
    raise ValueError(
        f"config['input']['mode'] must be one of {VALID_MODES}, "
        f"got {repr(config['input']['mode'])}"
    )

MODE = config["input"]["mode"]
CONTIG_NAME = config["input"]["contig_name"]
OUTPUT_PREFIX = config["output_prefix"]

HAS_BASE_GENOME = bool(config.get("base_genome", {}).get("fasta"))


def replicon_output(name):
    return getattr(rules, REPLICON_RULE).output[name]


def combine_annotations_input(wildcards):
    inputs = {
        "replicon_genes_gff": replicon_output("genes_gff"),
        "replicon_transcripts_gff": replicon_output("transcripts_gff"),
    }
    if HAS_BASE_GENOME:
        inputs["base_genes_gff"] = config["base_genome"]["genes_gff"]
        inputs["base_transcripts_gff"] = config["base_genome"]["transcripts_gff"]
    return inputs
