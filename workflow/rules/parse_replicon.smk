if MODE == "genbank":

    rule genbank_to_replicon:
        input:
            genbank=config["input"]["genbank"],
        output:
            fasta=f"results/replicon/{CONTIG_NAME}.fasta",
            genes_gff=f"results/replicon/{CONTIG_NAME}.genes.gff3",
            transcripts_gff=f"results/replicon/{CONTIG_NAME}.transcripts.gff3",
        params:
            contig_name=CONTIG_NAME,
            genes=config["input"]["genes"],
        log:
            "logs/genbank_to_replicon/genbank_to_replicon.log",
        benchmark:
            "benchmarks/genbank_to_replicon/genbank_to_replicon.txt"
        conda:
            "../envs/genbank_to_replicon.yaml"
        script:
            "../scripts/genbank_to_replicon.py"

    REPLICON_RULE = "genbank_to_replicon"

elif MODE == "fasta_gff":

    rule fasta_gff3_to_replicon:
        input:
            fasta=config["input"]["fasta"],
            gff3=config["input"]["gff3"],
        output:
            fasta=f"results/replicon/{CONTIG_NAME}.fasta",
            genes_gff=f"results/replicon/{CONTIG_NAME}.genes.gff3",
            transcripts_gff=f"results/replicon/{CONTIG_NAME}.transcripts.gff3",
        params:
            contig_name=CONTIG_NAME,
        log:
            "logs/fasta_gff3_to_replicon/fasta_gff3_to_replicon.log",
        benchmark:
            "benchmarks/fasta_gff3_to_replicon/fasta_gff3_to_replicon.txt"
        conda:
            "../envs/genbank_to_replicon.yaml"
        script:
            "../scripts/fasta_gff3_to_replicon.py"

    REPLICON_RULE = "fasta_gff3_to_replicon"
