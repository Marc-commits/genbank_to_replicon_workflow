# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] - 2026-07-30

### Added

- Initial release: `genbank_to_replicon` / `fasta_gff3_to_replicon` /
  `combine_annotations` rules, wiring `bowtie2_build_index_workflow` and
  `make_IGV_genome_workflow` as nested Snakemake `module:` submodules to
  produce a bowtie2 index and IGV `.genome` archive from a parsed
  replicon, optionally combined with an existing base genome.
