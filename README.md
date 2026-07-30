# genbank_to_replicon_workflow

A Snakemake workflow: parse a replicon (plasmid, phage, small extra
chromosome, ...) from either a GenBank record or a FASTA+GFF3 pair, select
named genes of interest, optionally combine it with an existing base
genome, and produce a bowtie2 index plus an IGV `.genome` archive ready for
downstream RNA-seq analysis. Composes two smaller reusable modules
(included as git submodules) rather than reimplementing indexing/IGV logic.

## What it does

1. **Parse** the replicon into a FASTA + genes GFF + transcripts GFF,
   using one of two mutually exclusive input modes
   (`config["input"]["mode"]`):
   - `genbank` — `genbank_to_replicon` rule: parses a `.gb`/`.gbk` record
     with Biopython, matching `gene`/`CDS` features by a `/label`
     substring against `config["input"]["genes"]`
     (output-name → substring, e.g. `GFP: "GFPMUT2"`).
   - `fasta_gff` — `fasta_gff3_to_replicon` rule: takes a FASTA + GFF3 pair
     directly (no GenBank parsing). See **Limitations** below.
2. **Combine** (`combine_annotations` rule) the replicon's genes/transcripts
   GFFs with an optional existing base genome's GFFs
   (`config["base_genome"]`) into one combined annotation set.
3. **Index** (`bowtie2_build_index_workflow` submodule, prefixed
   `bowtie2_*`) — concatenates the replicon FASTA (+ base genome FASTA, if
   configured) and builds a bowtie2 index.
4. **IGV genome** (`make_IGV_genome_workflow` submodule, prefixed `igv_*`)
   — packages the combined FASTA + combined genes GFF into an IGV
   `.genome` archive.

## Usage as a standalone workflow

```bash
git submodule update --init --recursive
snakemake --use-conda --latency-wait 30 all
```

Edit `config/config.yaml` first: set `input.mode`, the paths for that mode,
`input.contig_name`, `input.genes` (genbank mode only), optionally
`base_genome`, and `igv_genome`/`output_prefix`.

## Usage as a Snakemake module (git submodule)

```python
_replicon_module_config = {
    "input": {
        "mode": "genbank",
        "genbank": "resources/pSAM301.gb",
        "contig_name": "pSAM301",
        "genes": {
            "GFP": "GFPMUT2",
            "SmSpR": "AadA",
            "rop": "rop gene",
            "bla": "bla gene",
        },
    },
    "igv_genome": {"id": "pSAM301", "name": "pSAM301 plasmid"},
    "output_prefix": "results/bowtie2_index/combined",
}

module replicon:
    snakefile:
        "submodules/genbank_to_replicon_workflow/Snakefile"
    config:
        _replicon_module_config

use rule * from replicon as replicon_*
```

## Limitations

- **`fasta_gff` mode only supports genes, not real transcripts.** The
  input GFF3 is parsed for `gene` feature rows only;
  `fasta_gff3_to_replicon.py` synthesizes a `transcripts_gff` that is a
  1:1 mirror of each gene span
  (one transcript per gene, identical coordinates) rather than real
  transcript/mRNA/exon annotation. If the source GFF3 encodes UTRs,
  multi-exon structure, or alternate isoforms at the transcript level,
  none of that is represented in this mode's output. A
  `logging.warning(...)` is emitted every time this happens (see
  `logs/fasta_gff3_to_replicon/fasta_gff3_to_replicon.log`); details in
  `workflow/scripts/fasta_gff3_to_replicon_README.md`.
- `genbank` mode's gene matching is a case-insensitive substring match
  against each feature's `/label` qualifier — a substring shared between
  two features' labels (e.g. `"AmpR"` vs `"AmpR promoter"`) can
  over-match; the first feature found in file order wins.
- `combine_annotations` is plain concatenation, not a coordinate-aware
  merge; it assumes the replicon's `contig_name` doesn't collide with any
  contig already present in the base genome.

## Tests

- `tests/` — pytest unit tests for the pure functions in
  `workflow/scripts/{genbank_to_replicon,fasta_gff3_to_replicon,combine_annotations}.py`.
- `.tests/unit/` — Snakemake rule-level integration tests
  (`pytest .tests/unit`), generated/maintained following
  `snakemake --generate-unit-tests` conventions.
