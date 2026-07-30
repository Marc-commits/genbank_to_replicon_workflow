from snakemake.utils import validate


configfile: "config/config.yaml"


include: "workflow/rules/common.smk"
include: "workflow/rules/parse_replicon.smk"
include: "workflow/rules/combine.smk"


_bowtie2_sequences = [replicon_output("fasta")]
if HAS_BASE_GENOME:
    _bowtie2_sequences.append(config["base_genome"]["fasta"])

_bowtie2_module_config = {
    "sequences": _bowtie2_sequences,
    "index_name": OUTPUT_PREFIX,
}


module bowtie2:
    snakefile:
        "submodules/bowtie2_build_index_workflow/Snakefile"
    config:
        _bowtie2_module_config


use rule * from bowtie2 as bowtie2_*


_igv_module_config = {
    "fasta": rules.bowtie2_combine_sequences.output.fasta,
    "genefile": rules.combine_annotations.output.genes_gff,
    "genome_id": config["igv_genome"]["id"],
    "genome_name": config["igv_genome"]["name"],
    "output": f"{OUTPUT_PREFIX}.genome",
}


module igv:
    snakefile:
        "submodules/make_IGV_genome_workflow/Snakefile"
    config:
        _igv_module_config


use rule * from igv as igv_*


rule all:
    input:
        rules.bowtie2_bowtie2_build.output,
        rules.igv_make_igv_genome.output,
    default_target: True
