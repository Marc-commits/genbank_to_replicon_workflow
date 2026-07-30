# TODOs

- `fasta_gff` mode's synthesized transcripts (1:1 gene-span mirror) could
  be replaced with real transcript parsing if a caller ever provides a
  GFF3 with actual `mRNA`/`transcript` feature rows — currently only
  `gene` rows are read. See `workflow/scripts/fasta_gff3_to_replicon_README.md`.
- `combine_annotations.py` does not check for contig-ID collisions between
  the base genome and the replicon; consider adding a fail-fast check if
  this workflow is ever used with a base genome whose contig names aren't
  controlled by the same caller as the replicon's `contig_name`.
- The pytest module-basename collision (`tests/test_X.py` vs
  `.tests/unit/test_X.py` needing `__init__.py` files to collect together)
  is a latent bug in the parent `CyanoBulkRNAseq_SE_workflow` repo too —
  consider backporting the `__init__.py` fix there.
