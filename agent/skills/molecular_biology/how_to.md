# Molecular Biology

分子生物学工具集。

## 可用工具

- **annotate_open_reading_frames**: Find all Open Reading Frames (ORFs) in a DNA sequence using Biopython, searching
- **annotate_plasmid**: Annotate a DNA sequence using pLannotate's command-line interface
- **get_gene_coding_sequence**: Retrieves the coding sequence(s) of a specified gene from NCBI Entrez
- **get_plasmid_sequence**: Unified function to retrieve plasmid sequences from either Addgene or NCBI. If i
- **align_sequences**: Align short sequences (primers) to a longer sequence, allowing for one mismatch
- **pcr_simple**: Simulate PCR amplification with given primers and sequence
- **digest_sequence**: Simulates restriction enzyme digestion of a DNA sequence and returns the resulti
- **find_restriction_sites**: Identifies restriction enzyme sites in a given DNA sequence for specified enzyme
- **find_restriction_enzymes**: Finds common restriction enzyme sites in a DNA sequence and returns their cut po
- **find_sequence_mutations**: Compare query sequence against reference sequence to identify mutations
- **design_knockout_sgrna**: Design sgRNAs for CRISPR knockout by searching pre-computed sgRNA libraries. Ret
- **get_oligo_annealing_protocol**: Return a standard protocol for annealing oligonucleotides without phosphorylatio
- **get_golden_gate_assembly_protocol**: Return a customized protocol for Golden Gate assembly based on the number of ins
- **get_bacterial_transformation_protocol**: Return a standard protocol for bacterial transformation
- **design_primer**: Design a single primer within the given sequence window
- **design_verification_primers**: Design Sanger sequencing primers to verify a specific region in a plasmid. First
- **design_golden_gate_oligos**: Design complementary oligonucleotides with Type IIS restriction enzyme overhangs
- **golden_gate_assembly**: Simulate Golden Gate assembly to predict final construct sequences from backbone

## 使用示例

调用 `annotate_open_reading_frames` 进行分子生物学相关分析。
