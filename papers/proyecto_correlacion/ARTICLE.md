# Species associations revealed by an automatic fauna identifier and 1.2 million citizen-science photographs

**Draft v1 — 28-sep-2026** · Correlation Project (BioFauna)

---

## Abstract

Marine citizen science has produced photographic observation datasets that are rarely exploited beyond species
distributions. We analyse **1,222,170 photographs** and **759,207 geolocated, dated observations** (Minka SDG,
iNaturalist and other public sources), automatically identified by **BioFauna** —a k-NN retriever over
BioCLIP-2.5 ViT-H/14 embeddings with hierarchical calibration— to uncover **species associations**. We define a
sampling *event* (observer × ~1 km cell × day × 3-h window) and evaluate pair co-occurrence with support,
spatial and temporal repeatability, finding **70,971 significant pairs**. The method **recovers known,
documented associations** with high robustness —e.g. *Peltodoris atromaculata* on the sponge *Petrosia
ficiformis* (79 events, lift 11.1, 44 localities, 74 days)— and reveals **undescribed candidates** with
plausible biological interpretation, such as jellyfish with commensal hyperiid amphipods, cleaner shrimps with
anemones and infaunal species pairs. The work highlights the role of human curators in verifying cryptic
species and outlines applications for conservation and outreach.

**Keywords:** citizen science, interspecific associations, habitat use, deep learning, Mediterranean,
underwater photography.

## 1. Introduction

Amateur underwater photography has become a massive source of biodiversity data. Citizen-science platforms
(**Minka SDG**, driven by the **FECDAS** ecosystem; **iNaturalist**; **GBIF**) accumulate millions of verified
observations, and automatic identifiers can consolidate that archive at catalogue scale. Yet most analyses
stop at inventories and distribution maps. Photographs also carry **ecological context**: which species occur
together, on what substrate and under which conditions. This work explores that latent information.

## 2. Material and methods

Summary (details in [`METODOS.md`](METODOS.md) and supplementary material):

- **Data**: 1,222,170 photographs; 759,207 observations with coordinates, date and (92 %) time; a curated
  catalogue of 2,985 Mediterranean taxa.
- **Identification**: BioFauna (BioCLIP-2.5 ViT-H/14 + FAISS k-NN, k=15, T=0.05 aggregator with a cap of 3
  votes per species, hierarchical calibration), with publication guards and leak auditing.
- **Unit of analysis**: *event* = (observer × ~1.1 km cell × day × 3-h window); the set of species seen
  together.
- **Filters**: catalogue-only; support ≥8 events; repeatability across **≥3 localities, ≥3 days and ≥5 distinct observers** (the latter added after finding that a single dive trip generates false associations).
- **Metrics**: observed co-occurrence `n`, expected from marginals and **lift**; Poisson p for screening.
- **Internal validation**: blind search for documented associations (§3.1).

## 3. Results

### 3.1 Method validation (documented associations recovered)

| association | n | lift | localities | days | source |
|---|---:|---:|---:|---:|---|
| *Peltodoris atromaculata* — *Petrosia ficiformis* | 79 | 11.1 | 44 | 74 | classic literature |
| *Felimare picta* — *Ircinia oros* | 29 | 4.1 | 20 | 28 | host sponge |
| *Cratena peregrina* — *Eudendrium racemosum* | 5 | 10.5 | — | — | prey hydroid |
| ~~*Doto paulinae* — *Sertularella mediterranea*~~ | 5 | 48.3 | — | — | ❌ **discarded**: single observer (expert-review correction) |

### 3.2 Taxonomic groups

Pairs concentrate in the photographically best-represented families (sparids, blenniids, gobiids, labrids,
coralline algae, didemnids, holothurians, actiniids, trochids, dictyotaceans, facelinids, serpulids,
sabellids, irciniids). **98 % of pairs are inter-family**, as expected for habitat or trophic associations.

### 3.3 New candidates (pending expert review)

| functional group | A — B | n | lift | localities | days |
|---|---|---:|---:|---:|---:|
| commensalism on jellyfish | *Blackfordia virginica* — *Phronima sedentaria* | 19 | 653 | 6 | 15 |
| cleaning symbiosis | *Lysmata grabhami* — *Telmatactis cricoides* | 9 | 547 | 7 | 8 |
| infauna (same sediment) | *Fustiaria rubescens* — *Loripinus fragilis* | 16 | 892 | 7 | 15 |
| infauna | *Abra alba* — *Abra longicallus* | 9 | 534 | 7 | 9 |
| hard-substrate microhabitat | *Macrorhynchia philippina* — *Telmatactis cricoides* | 8 | 765 | 5 | 6 |
| gelatinous plankton | *Callianira bialata* — *Vanadis formosa* | 9 | 645 | 7 | 9 |
| co-occurring nudibranchs | *Doris fontainii* — *Tyrinna delicata* | 14 | 1,277 | 9 | 12 |

*(Full table: supplementary material; main figure: top-12 network.)*

## 4. Discussion

Candidates fall into three interpretative classes: **commensalism/phoresy** (jellyfish—amphipod), **cleaning
symbiosis** (shrimp—anemone) and **substrate co-habitation** (infauna; hard bottoms; coralline algae). The
central methodological challenge is separating **interaction** from **coincidence** driven by habitat, season
or observer effort; hence the spatial/temporal repeatability requirement and the stratified null currently
under development.

## 5. Limitations

1. Co-occurrence ≠ interaction; mitigated by filters and the null model, but directed observation remains the
   final confirmation.
2. Observer/effort bias (bioblitz-type events).
3. Uneven taxonomic coverage.

## 6. Conclusions and applications

Citizen-science photographs contain ecological associations retrievable at catalogue scale. Results enable
(a) **prioritising** the search for rare species where their associate occurs, (b) **enriching BioQuest** with
"if you see X, look for Y" suggestions and per-area association networks, and (c) generating **testable
hypotheses** for marine research, with the added value of covering shallow coastal waters where satellites
perform worst.

## Acknowledgements

To the observer community and, most especially, to the **curators** who sustain the reliability of the
identifications —in particular **Miquel Pontes**, **Xavier Salvador** and **Berta Companys**— and to the wider
curatorial community of **Minka SDG** and **iNaturalist**. Special mention to **FECDAS** and its **Aneris
Project** for driving marine citizen science and observer training; to **Minka SDG** and **iNaturalist** for
the platforms and the data; and to **GBIF**, **Wikimedia Commons**, **DORIS/FFESSM**, **SeaSlugForum**,
**WoRMS** and **FishBase** for images and taxonomic data. This analysis has been possible thanks to the
**BioFauna identifier** (BioCLIP-2.5 ViT-H/14 + FAISS) developed in the project.


