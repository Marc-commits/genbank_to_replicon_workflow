rule combine_annotations:
    input:
        unpack(combine_annotations_input),
    output:
        genes_gff=f"{OUTPUT_PREFIX}.genes.gff3",
        transcripts_gff=f"{OUTPUT_PREFIX}.transcripts.gff3",
    log:
        "logs/combine_annotations/combine_annotations.log",
    benchmark:
        "benchmarks/combine_annotations/combine_annotations.txt"
    conda:
        "../envs/genbank_to_replicon.yaml"
    script:
        "../scripts/combine_annotations.py"
