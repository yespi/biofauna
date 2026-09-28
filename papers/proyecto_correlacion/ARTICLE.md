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
|---|---:|---:|---:|---:|---:|
| commensalism on jellyfish | *Blackfordia virginica* — *Phronima sedentaria* | 19 | 653 | 6 | 15 |
| cleaning symbiosis | *Lysmata grabhami* — *Telmatactis cricoides* | 9 | 547 | 7 | 8 |
| infauna (same sediment) | *Fustiaria rubescens* — *Loripinus fragilis* | 16 | 892 | 7 | 15 |
| infauna | *Abra alba* — *Abra longicallus* | 9 | 534 | 7 | 9 |
| hard-substrate microhabitat | *Macrorhynchia philippina* — *Telmatactis cricoides* | 8 | 765 | 5 | 6 |
| gelatinous plankton | *Callianira bialata* — *Vanadis formosa* | 9 | 645 | 7 | 9 |

*(Full table: supplementary material; main figure: top-12 network.)*

### 3.4 Literature verification of the candidates

After reviewing public literature (WoRMS, Sea Slug Forum, FishBase, JNCC/MarLIN, peer-reviewed journals),
pairs are classified into three categories:

**Documented** (the interaction is already described): *Peltodoris atromaculata*—*Petrosia ficiformis*
(predation), *Felimare picta*—*Ircinia* spp. (diet), *Cratena peregrina*—*Eudendrium racemosum*
(kleptopredation), the floating **Sargassum community** (*Latreutes fucorum*, *Hippolyte coerulescens* and
*Scyllaea pelagica*), *Phronima sedentaria* as a salp symbiont and *Lampea pancerina* as a salp
predator/parasite.

**Plausible** (ecologically coherent, no direct citation of the pair): *Lysmata grabhami*—*Telmatactis
cricoides* (the anemone hosts documented crustacean symbionts —*Thor amboinensis* in 65 % of anemones and
*Stenorhynchus lanceolatus* in facultative mutualism— and both species truly co-occur in the Canary
Islands/Madeira), gelatinous-plankton pairs (ctenophores, hyperiids and medusae of the same water mass) and
infaunal sediment pairs (*Abra* spp.; *Fustiaria*—*Loripinus*, both typical of circalittoral soft bottoms).

**Dive-trip artefact** (species from other oceans photographed together by the same group in one immersion):
*Doris fontainii*—*Tyrinna delicata* (both from the **South Pacific**, lat −12…−55),
*Chromodoris quadricolor*—*Hexabranchus sanguineus* (Red Sea/Indo-Pacific), *Abudefduf saxatilis*—
*Kyphosus vaigiensis* (Atlantic vs. Indo-Pacific; they do not coexist in the Mediterranean). These pairs are
**excluded** from the ecological analysis of the study area; detecting them is also a useful dataset-quality
control signal.

**Taxonomic correction**: `loripinus_fragilis` (Philippi, 1836, **Lucinidae**) and `limaria_fragilis`
(Gmelin, 1791, **Limidae**) are distinct species; they are not synonyms (WoRMS AphiaID 718970 vs. 216644).

## 3.5 References supporting the associations

Sources verified during the literature review (28-sep-2026):

| Association / claim | Source |
|---|---|
| *Peltodoris atromaculata* feeds on the sponge *Petrosia ficiformis* | trophic literature of dorid nudibranchs (diet review; petroformynes as chemical defence of the sponge) |
| *Felimare picta* (formerly *Hypselodoris*) feeds on sponges of the genus *Ircinia* | McDonald & Nybakken, 2001 — *A worldwide review of the food of nudibranch mollusks*; field observations (OPK) |
| *Cratena peregrina* practises kleptopredation on *Eudendrium racemosum* | Di Camillo et al. — *Eudendrium racemosum* as substrate/prey and prey theft (CNR, Adriatic Sea) |
| *Scyllaea pelagica*, *Latreutes fucorum* and *Hippolyte coerulescens* belong to the floating *Sargassum* fauna | literature of the pelagic Sargassum community (NOAA; BAMZ; Sea Slug Forum) |
| *Phronima sedentaria* is an obligate salp symbiont (lives in the "barrel") | Laval, 1978 — *The barrel of the pelagic amphipod Phronima sedentaria*; Diebel, 1988 — *Observations on the anatomy and behavior of Phronima sedentaria*; MBARI/Scripps |
| *Lampea pancerina* predates or parasitises salps | *The double life of the ctenophore Lampea pancerina*; ctenophore literature (Carré & Carré) |
| Hyperiids (*Brachyscelus*, *Phronima*) associate with gelatinous zooplankton (medusae, ctenophores, salps) | Keil & Osborn — *Associations between hyperiid amphipods and gelatinous zooplankton* (Smithsonian/MBARI, ROV) |
| *Telmatactis cricoides* hosts crustacean symbionts (*Thor amboinensis* in 65 % of anemones; *Stenorhynchus lanceolatus* in facultative mutualism) | *Crustacean symbionts of the sea anemone Telmatactis* (decapoda.nhm.org); Peraza et al., 2024 — *Exploring the association between Stenorhynchus lanceolatus and Telmatactis cricoides in the Canary Islands* (Regional Studies in Marine Science) |
| *Telmatactis cricoides* is a thermophilic species expanding in the western Mediterranean (Almería, Balearic Is.) | Cambridge, J. Mar. Biol. Assoc. UK 104 (2024) — *The thermophilic sea anemone Telmatactis cricoides in the western Mediterranean* |
| *Macrorhynchia philippina* is an invasive hydrozoan ("stinging bush hydroid") | Riera et al., 2016 — *Progressing the invasion of the hydrozoan Macrorhynchia philippina in Atlantic archipelagos* (Vieraea 44) |
| Soft-sediment communities with *Abra alba* and same-genus bivalves | JNCC Marine Habitat Classification (biotope SS.SSa.CMuSa.AalbNuc); MarLIN |
| *Loripinus fragilis* (Lucinidae, chemosymbiosis) ≠ *Limaria fragilis* (Limidae) | WoRMS AphiaID 718970 vs. 216644; Taylor & Glover, 2021 — *Biology, evolution and generic review of the Lucinidae* |
| *Abudefduf saxatilis* is strictly Atlantic (replaced by *A. vaigiensis* in the Indo-Pacific) | FishBase — *Abudefduf saxatilis* (Sergeant-major) |
| *Doris fontainii* (formerly *Anisodoris fontainei*) and *Tyrinna delicata* are South Pacific species | Sea Slug Forum (Australian Museum); Valdés & Muniain, 2002 |
| *Eurythoe complanata* is a complex of ≥3 cryptic species | Barroso et al., 2010 — *Eurythoe complanata, the 'cosmopolitan' fireworm, consists of at least three cryptic species* (Marine Biology) |

## 4. Discussion

### 4.1 Theoretical background: co-occurrence and citizen-science biases

Species co-occurrence is a classic ecological signal (shared habitat, predation, symbiosis, commensalism),
but reading it from citizen-science data requires controlling well-documented biases: **geographic bias**
(accessible areas are sampled more), **effort bias** (bioblitz-type events inflate certain localities),
**observer bias** (variable ability to detect and identify species) and **reporting bias** (preference for
charismatic species). Opportunistic data lack a sampling plan and explicit absences, so any inference must
explicitly mitigate these biases (Isaac et al., 2014; Johnston et al., 2018; Aceves-Bueno et al., 2017;
Boyd et al., 2021; Milanesi et al., 2020). Our design responds with: (1) *event* = effort unit per observer
and 3-h window (controls effort bias), (2) required repeatability across ≥3 localities, ≥3 days and **≥5
distinct observers** (controls observer and dive-trip bias), and (3) the **geographic-range filter** on
species (removes the dive-trip artefact found in this review). Geographic bias is addressed with the
locality·date stratified null currently under development (§6 of Methods).

Candidates fall into three interpretative classes: **commensalism/phoresy** (jellyfish—amphipod), **cleaning
symbiosis** (shrimp—anemone) and **substrate co-habitation** (infauna; hard bottoms; coralline algae). The
central methodological challenge is separating **interaction** from **coincidence** driven by habitat, season
or observer effort; hence the spatial/temporal repeatability requirement and the stratified null currently
under development.

The literature review yields two results of general interest. First, **the method recovers already documented
associations** (dorid predation, the Sargassum community, gelatinous-zooplankton symbionts), validating the
ecological signal against effort noise. Second, classifying the top pairs by the geographic range of their
species reveals a **systematic citizen-science artefact**: the highest-lift pairs with extra-Mediterranean
species (*Doris fontainii*—*Tyrinna delicata*; *Chromodoris quadricolor*—*Hexabranchus sanguineus*)
correspond to **dive trips** by the same group rather than to ecological interactions in the study area.
Cross-checking each taxon's geographic range is therefore a necessary quality filter before interpreting any
candidate as an ecological association.

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

## References

- Aceves-Bueno, E., Adeleye, A. S., Feraud, M., Huang, Y., Tao, M., Yang, Y., & Anderson, S. E. (2017). The
  accuracy of citizen science data: a quantitative review. *The Bulletin of the Ecological Society of
  America*, 98(4), 278–290.
- Avila, C. (1996). The growth of *Peltodoris atromaculata* Bergh, 1880 (Gastropoda, Nudibranchia) in the
  laboratory. *Journal of Molluscan Studies*, 62, 151–157. — exclusive diet on *Petrosia ficiformis*;
  petroformyne accumulation.
- Barroso, R., Klautau, M., Solé-Cava, A. M., & Paiva, P. C. (2010). *Eurythoe complanata* (Polychaeta:
  Amphinomidae), the 'cosmopolitan' fireworm, consists of at least three cryptic species. *Marine Biology*,
  157(1), 69–80.
- Boyd, R. J., Powers, M., & Pescott, O. L. (2021). occAssess: an R package for assessing potential biases in
  species occurrence data. *Ecology and Evolution*, 11(22).
- Diebel, C. E. (1988). Observations on the anatomy and behavior of *Phronima sedentaria* (Forskål)
  (Amphipoda: Hyperiidea). *Journal of Crustacean Biology*, 8(1), 79–90.
- Isaac, N. J. B., van Strien, A. J., August, T. A., de Zeeuw, M. P., & Roy, D. B. (2014). Statistics for
  citizen science: extracting signals of change from noisy ecological data. *Methods in Ecology and
  Evolution*, 5(10), 1052–1060.
- Johnston, A., Fink, D., Hochachka, W. M., & Kelling, S. (2018). Estimates of observer expertise improve
  species distributions from citizen science data. *Methods in Ecology and Evolution*, 9(4), 880–890.
- Keil, K. E., & Osborn, K. J. Associations between hyperiid amphipods and gelatinous zooplankton
  (Smithsonian Institution, NMNH; MBARI ROV footage).
- Laval, P. (1978). The barrel of the pelagic amphipod *Phronima sedentaria* (Forsk.). *Journal of
  Experimental Marine Biology and Ecology*, 33(3), 187–211.
- McDonald, G. R., & Nybakken, J. W. (2001). A worldwide review of the food of nudibranch mollusks. II. The
  suborder Doridacea. *The Veliger*.
- Milanesi, P., Mori, E., & Menchetti, M. (2020). Observer-oriented approach improves species distribution
  models from citizen science data. *Ecology and Evolution*, 10(21), 12104–12114.
- Peraza, E., Pérez, J. A., Abdul-Jalbar, B., Chinea, J., & Clemente, S. (2024). Exploring the association
  between the arrow crab *Stenorhynchus lanceolatus* and the sea anemone *Telmatactis cricoides* in the
  Canary Islands. *Regional Studies in Marine Science*.
- Riera, R., Espina, F., & Moro, L. (2016). Progressing the invasion of the hydrozoan *Macrorhynchia
  philippina* (Kirchenpauer, 1872) in Atlantic archipelagos. *Vieraea*, 44, 117–120.
- Taylor, J., & Glover, E. (2021). *Biology, evolution and generic review of the chemosymbiotic bivalve
  family Lucinidae*. The Ray Society, London.
- Valdés, Á., & Muniain, C. (2002). Revision and taxonomic reassessment of Magellanic species assigned to
  *Anisodoris* Bergh, 1898 (Nudibranchia: Doridoidea). *Journal of Molluscan Studies*, 68, 345–351.


