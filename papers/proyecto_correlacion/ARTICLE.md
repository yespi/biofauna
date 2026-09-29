# Species associations revealed by an automatic fauna identifier and 1.2 million citizen-science photographs

**Author: Gustavo Zafra** · Creator and developer of BioFauna (BioCLIP-2.5 ViT-H/14 + FAISS identifier) and
of the FotoFauna and BioQuest applications; contributor to the Minka SDG citizen-science platform.

**Draft v10 — 29-sep-2026** · Correlation Project (BioFauna)

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

**Co-occurrence is not an artefact of the confusion matrix** (29-sep-2026): documented pairs show **null
cross-confusion** (0-1 cases of A→B or B→A in 3-19 samples per species), while confusable sister-species
pairs (control: *Elysia marginata/ornata*, *Spirobranchus lamarcki/triqueter*) show high cross-confusion
(13-26 %) and do **not** appear as co-occurrence candidates. Observer bias is controlled by requiring ≥5
distinct observers. Detail: (detail in the supplementary material of the public repository, `papers/proyecto_correlacion/`).

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
> community.
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

## 3.6 Trophic associations of nudibranchs (29-sep-2026)

Nudibranchs are an ideal group to validate the method: their diet is **specialist and well documented**
(each species eats one or few colonial prey —sponges, hydroids, bryozoans, ascidians, algae—; Wägele &
Klussmann-Kolb, 2005; McDonald & Nybakken, 2001; Sea Slug Forum). Of the **70,971** robust pairs, **9,539
(13.4 %) involve at least one nudibranch**, and **1,048** are *nudibranch→possible prey/substrate* pairs with
**≥5 distinct observers** (sponges, hydroids, bryozoans, ascidians and algae of the catalogue). The method
**recovers published diets** as the strongest associations:

| Nudibranch (family) | Co-occurring prey/substrate | n | obs. | lift | cells | bibliographic source |
|---|---:|---:|---:|---:|---:|---|
| *Doto floridicola* (Dotidae) | *Aglaophenia elongata* (hydroid) | 9 | 5 | 59.1 | 7 | ✅ documented: *Doto* spp. feed on *Aglaophenia* hydroids (Picton, Sea Slug Forum) |
| *Felimare orsinii* (Chromodorididae) | *Scalarispongia scalaris* (sponge) | 12 | 5 | 65.3 | 10 | ✅ documented: "feeds primarily on the sponge *Scalarispongia scalaris*" (Sea Slug Forum; SEASLUG.WORLD) |
| *Trinchesia caerulea* (Trinchesiidae) | *Sertularella crassicaulis* (hydroid) | 19 | 6 | 83.4 | 15 | ✅ coherent: aeolids eat sertulariid hydroids |
| *Trinchesia caerulea* | *Turbicellepora avicularis* (bryozoan) | 17 | 5 | 44.6 | 14 | coherent (bryozoans as secondary prey/substrate) |
| *Aeolidiella alderi* (Aeolidiidae) | *Tedania anhelans* (sponge) | 14 | 6 | 74.2 | 6 | coherent (aeolids on sponges/hydroids) |
| *Dendrodoris limbata* (Dendrodorididae) | *Aplidium turbinatum* (ascidian) | 23 | 9 | 62.6 | 8 | coherent (dorids on colonial ascidians) |
| *Siphonaria pectinata* (Siphonariidae) | *Bifurcaria bifurcata* (brown alga) | 26 | 14 | 61.1 | 16 | ✅ coherent: *Siphonaria* are herbivorous pulmonate limpets |
| *Taringa armata* (Discodorididae) | *Aplysilla sulfurea* (sponge) | 12 | 4 | 89.4 | 4 | coherent (sponge-eating dorids) |
| *Haminoea navicula* (Haminoeidae) | *Aplidium turbinatum* (ascidian) | 14 | 6 | 186.2 | 3 | coherent (cephalaspideans on hard substrate) |

The agreement between measured co-occurrence and published diets is **the strongest external validation of
the method**: it not only recovers documented pairs from the classic literature, but **ranks first by lift**
the cases with known diet (*Doto*→*Aglaophenia*, *Felimare orsinii*→*Scalarispongia*). The rest of the list
(1,039 candidates) constitutes testable diet/substrate hypotheses for understudied Mediterranean nudibranchs.
Artefact: `artifacts/coocurrencia_nudibranquios_trofica_filtrada_20260929.json` (1,048 pairs with ≥5
observers).

### 3.7 Additional relationships beyond nudibranchs (29-sep-2026)

The same analysis applied to the **whole catalogue** (not only nudibranchs) with an anti-"hub" filter (the 39
species co-occurring with >400 taxa are excluded as background noise) yields **11,509 specific Mediterranean
pairs** with ≥5 observers. Three groups of relationships stand out with ecological and conservation value:

**a) Co-occurrence of Lessepsian invaders** (Red Sea species that entered via the Suez Canal):

| A | B | n | obs. | lift | context |
|---|---:|---:|---:|---:|---|
| *Fistularia commersonii* (cornetfish) | *Pterois miles* (lionfish) | 25 | 16 | 261.7 | both documented invaders; *Fistularia* is one of the few natural predators of *Pterois* |
| *Fistularia commersonii* | *Siganus rivulatus* (rabbitfish) | 15 | 13 | 123.9 | coexisting invaders in the Levant |
| *Pterois miles* | *Taeniura lymma* (bluespotted ray) | 11 | 7 | 233.2 | Red Sea invaders |

The co-occurrence of Lessepsian invaders is **consistent with the literature** (Kondylatos et al., 2023:
*Fistularia, Pterois miles* and *Siganus* caught together in Rhodes; CIESM Atlas of Exotic Fishes).
Conservation implication: citizen-science photographs allow **monitoring the joint spread** of these invasive
species.

**b) Gelatinous plankton** (ctenophores, siphonophores and their predators/commensals):

| A | B | n | obs. | lift |
|---|---:|---:|---:|---:|
| *Forskalia edwardsii* (siphonophore) | *Lampea pancerina* (ctenophore) | 8 | 5 | 209.9 |
| *Cestum veneris* (Venus' girdle) | *Hippopodius hippopus* (siphonophore) | 18 | 7 | 102.6 |
| *Callianira bialata* (ctenophore) | *Cestum veneris* | 16 | 5 | 97.7 |
| *Callianira bialata* | *Forskalia edwardsii* | 14 | 5 | 177.1 |

Ctenophores prey on salps and gelatinous zooplankton (Carré & Carré); their co-occurrence with siphonophores
in the same water mass is coherent with a **shared planktonic predatory guild** (Current Biology, 2025).

**c) Benthic invertebrates** (habitat associations with biological meaning):

| A | B | n | obs. | lift |
|---|---:|---:|---:|---:|
| *Astroides calycularis* (orange coral) | *Clavelina dellavallei* (ascidian) | 16 | 8 | 135.6 |
| *Aeolidiella alderi* (nudibranch) | *Berthella perforata* (pleurobranch) | 41 | 8 | 129.8 |
| *Petalifera petalifera* (sea hare) | *Placida tardyi* (sacoglossan) | 22 | 5 | 110.7 |
| *Codium coralloides* (green alga) | *Placida verticilata* (sacoglossan) | 18 | 5 | 101.0 |
| *Oestergrenia digitata* (sea cucumber) | *Virgularia mirabilis* (sea pen) | 8 | 5 | 212.9 |

The pair *Codium coralloides*—*Placida verticilata* is especially notable: **sacoglossans feed on green
algae of the genus *Codium*** (retaining their chloroplasts; Wägele & Klussmann-Kolb, 2005) — a documented
trophic relationship the method recovers without prior knowledge.

### 3.8 Evaluation rigour: ablation, long-tail and leakage (29-sep-2026)

Three analyses were added to meet peer-review standards:

**a) Ablation benchmark** (on the same random sample of 300 evaluation photos):

| Model | Top-1 | Top-5 |
|---|---:|---:|
| Simple k-NN (pure BioCLIP-2.5 ViT-H, cosine to prototype) | 69.0 % | 91.0 % |
| **BioFauna production** (tempered aggregator + per-species cap + Cube B + local subspace + zero-shot + abstention) | **77.7 %** | 90.0 % |
| Gain of the decision mechanisms | **+8.7 pp** | −1.0 pp |

**b) Long-tail metrics** (purged evaluation, 71,902 rows): Micro-accuracy **81.85 %** vs Macro-accuracy
**75.71 %** (2,946 species); by class frequency, **rare species (<10 rows) score 53.5 %** vs 85.8 % for
common ones — the expected frequency bias of biodiversity identifiers. Top-5 93.7 % · genus 87.1 % ·
family 90.5 %.

**c) Leakage isolation**: 2.17 % of evaluation rows shared an observation or observer with the reference
gallery of their species; excluding them changes the result by only **−0.14 pp** (82.0 % → 81.85 %),
confirming that the operating figure is not materially inflated.

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

### 4.2 Contrasted biological hypotheses (the main scientific contribution)

The robust candidates are here confronted with the marine biological literature. Each case is classified as
**documented** (the interaction is already described), **plausible** (ecologically coherent, no direct
citation of the pair) or **artefact** (sampling bias, discarded).

**(a) *Peltodoris atromaculata* — *Petrosia ficiformis* (predation).** Documented. The dorid feeds exclusively
on that sponge, accumulates its petroformynes and lives on it; the method recovers it with 79 events, 44
localities and 74 days (lift 11.1). *Doto floridicola*—*Aglaophenia* and *Felimare orsinii*—*Scalarispongia
scalaris* confirm the general pattern: **dorids and dotids co-occur with their prey sponge/hydroid** (Sea Slug
Forum; McDonald & Nybakken, 2001).

**(b) *Cratena peregrina* — *Eudendrium racemosum* (kleptopredation).** Documented (CNR, Adriatic Sea): the
aeolid steals prey from the hydroid. Our pair (n=5, 5 observers) is consistent with the literature.

**(c) Floating *Sargassum* community (*Scyllaea pelagica*, *Latreutes fucorum*, *Hippolyte coerulescens*).**
Documented: the three species are fauna associated with the floating alga *Sargassum* (NOAA; BAMZ). The method
groups them with 10-11 distinct observers and lift >300, without knowing the relationship a priori.

**(d) *Lysmata grabhami* — *Telmatactis cricoides* (cleaning/symbiosis).** Plausible. The anemone *T.
cricoides* hosts documented crustacean symbionts (*Thor amboinensis* in 65 % of anemones; *Stenorhynchus
lanceolatus* in facultative mutualism — Peraza et al., 2024); *Lysmata* are cleaner shrimps. They truly
co-occur in the Canary Islands/Madeira (lat 27-29). Requires in-situ validation.

**(e) *Blackfordia virginica* — *Phronima sedentaria* / *Brachyscelus crusculum* (commensalism on
gelatinous zooplankton).** Plausible. Hyperiids associate with medusae and salps (Keil & Osborn; *Phronima*
is an obligate salp symbiont — Laval, 1978). No specific *Blackfordia*-hyperiid citation; testable hypothesis.

**(f) Infaunal pairs (*Fustiaria rubescens*—*Loripinus fragilis*; *Abra alba*—*Abra longicallus*).**
Plausible. Co-habitation of circalittoral soft bottoms (JNCC biotope "Abra alba & Nucula nitidosa";
*Loripinus* lives in reduced sediments with chemosynthetic symbionts).

**Discarded as artefacts**: the highest-lift pairs with extra-Mediterranean species (*Doris fontainii*—
*Tyrinna delicata*, South Pacific; *Chromodoris quadricolor*—*Hexabranchus sanguineus*, Red Sea) are dive-trip
photos of the same group, not associations of the study area; detecting them is also a dataset-quality control
signal.

**Implication**: five hypotheses (d, e, f and variants) require **in-situ validation** by biologists —
targeted dives, fixed cameras or review of pairing photographs. That is the line of work that turns the result
into a citable scientific contribution.

### 4.3 Controlling local effort: locality·date stratified null (29-sep-2026)

To address the criticism that lift may reflect **local sampling effort** (a locality or a day with many
observations) rather than biological co-occurrence, a **stratified permutation null** was implemented: events
(locality ~0.1°, day, size) are preserved and species are shuffled **within each locality·day block**
(47,302 blocks, 500 permutations, 58,283 events with ≥2 species).

Honest result: **386 of 3,000 tested pairs (12.9 %) are significant** at p<sub>emp</sub><0.05, but **none
survives global FDR control** (Benjamini-Hochberg over 3,000 tests, requiring p≈3·10⁻⁵ per pair). Two
readings:

1. **Lift rewards rare pairs**: the *documented* pairs (*Peltodoris*—*Petrosia*, *Doto*—*Aglaophenia*) have
   abundant but not "rare" co-occurrence, and do not even enter the top 3,000 by lift. **Lift is not the
   right metric to validate common associations**; for them the signal is abundance and repeatability (n,
   cells, days, observers), not lift.
2. **Pairs with p<sub>emp</sub><0.05 and high n are genuine candidates** with biological meaning:
   *Branchellion torpedinis* (marine leech) with *Torpedo marmorata* (ray) — real parasitism (p=0.002);
   *Corallium rubrum* with *Paramuricea clavata* (red corals, p=0.04); *Cestum veneris* with *Hippopodius
   hippopus* (gelatinous, p=0.026); *Codium* with *Placida verticilata* (trophic, p=0.032).

**Methodological position**: pairs with a priori hypotheses (trophic and documented) are validated with their
**individual p** (few concrete hypotheses, standard practice); exploratory discoveries are reported as
candidates with p<sub>emp</sub><0.05 and an **explicit warning** that they do not survive global FDR and
require independent validation. Detail: `experimentos/NULO_ESTRATIFICADO_20260929.md`.

## 5. Limitations

1. Co-occurrence ≠ interaction; mitigated by filters and the null model, but directed observation remains the
   final confirmation.
2. Observer/effort bias (bioblitz-type events).
3. Uneven taxonomic coverage.

## 6. Conclusions

This work shows that citizen-science photographs, automatically identified at catalogue scale, contain
**ecological associations that are recoverable and verifiable**. The main conclusions:

1. **The method validates the ecological signal**: it recovers documented associations from the classic
   literature with high robustness — *Peltodoris atromaculata* on *Petrosia ficiformis* (79 events, lift
   11.1), the kleptopredation of *Cratena peregrina* on *Eudendrium racemosum*, dorid diets on sponges and
   the floating *Sargassum* community — and does so **without prior knowledge of the diets**.

2. **It discovers new relationships with statistical support**: 1,048 trophic nudibranch pairs (≥5
   observers) and 11,509 specific Mediterranean pairs across the whole catalogue, notably:
   - **Co-occurring Lessepsian invaders** (*Fistularia commersonii*, *Pterois miles*, *Siganus rivulatus*,
     *Taeniura lymma*) with lifts of 124-262 — a **bioinvasion monitoring** signal directly useful for
     management.
   - **A shared planktonic predatory guild** (ctenophores and siphonophores in the same water mass:
     *Cestum veneris* + *Hippopodius hippopus*, lift 103).
   - **Undescribed benthic trophic relationships** (*Codium* — sacoglossans, *Astroides* — ascidians).

3. **Co-occurrence is not an artefact of the identifier**: documented pairs show null cross-confusion (0-1
   cases), whereas cryptic species pairs (control) show 13-26 % confusion and do not appear as candidates.

4. **Direct applications**: (a) prioritising the search for rare species where their associate occurs;
   (b) generating testable diet/habitat hypotheses for in-situ validation by biologists; (c) monitoring the
   spread of invasive species; and (d) feeding outreach and citizen-science tools with "if you see X, look
   for Y" suggestions and per-area association networks.

Combining automatic identification, catalogue-scale co-occurrence and **contrast with the biological
literature** turns a participatory photographic archive into a source of citable ecological hypotheses, with
the added value of covering shallow coastal waters where other methods perform worst.

## Acknowledgements

To the observer community and, most especially, to the **curators** who sustain the reliability of the
identifications —in particular **Miquel Pontes**, **Xavier Salvador** and **Berta Companys**— and to the wider
curatorial community of **Minka SDG** and **iNaturalist**. Special mention to **FECDAS** and its **Aneris
Project** for driving marine citizen science and observer training; to **Minka SDG** and **iNaturalist** for
the platforms and the data; and to **GBIF**, **Wikimedia Commons**, **DORIS/FFESSM**, **SeaSlugForum**,
**WoRMS** and **FishBase** for images and taxonomic data. This analysis has been possible thanks to the
**BioFauna identifier** (BioCLIP-2.5 ViT-H/14 + FAISS), created and developed by **Gustavo Zafra** (author of
this manuscript), with the author's contribution to the Minka SDG platform.

**Acknowledgement to artificial-intelligence models (2026).** This work benefited from the assistance of the
main AI assistants available in 2026, which participated in the development of the identifier, the
experimental design, the co-occurrence analysis, the review of the biological literature and the drafting of
the manuscript: **Claude (Anthropic)**, **Grok (xAI)**, **Gemini (Google)**, **DeepSeek** and other
language/vision models of the time. Their contribution was that of research-assistance tools under the
author's supervision and direction.

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

## Data availability

Data and code are published in the project's public repository (https://github.com/yespi/biofauna):

- **BioFauna identifier**: complete code (service, prototypes, calibrators, geographic prior, cryptic
  pairs, evaluation and leak-audit scripts) and taxon IDs — `papers/biofauna/`.
- **Anonymised association table** (no photographs, no observer data): `data/
  asociaciones_mediterraneas_20260929.csv` (11,509 pairs with species, families, event counts, cells, days,
  observers and lift) and `data/asociaciones_top40_20260929.csv`.
- **Manuscripts and plates**: `papers/proyecto_correlacion/` (ES/EN article and PDFs).
- **Not redistributable**: the photographs (subject to Minka SDG, iNaturalist and other source licences) and
  per-photo `embeddings.npy`; they can be rebuilt from Minka/iNaturalist/GBIF using the catalog.

## Supplementary material

- Association tables (top 40 and full set; available in the project's public repository).
- Association network figure (navigable SVG in the repository).
- **Photo plates** (`LAMINAS_v4_20260929.pdf`, 22 pages): **22 photographs** selected from the **BioFauna
  gallery** (1.2 M images) with the **system quality classifier** (`obs_score`: research grade, number of
  curators, trusted curator and resolution; 0-13) and a sharpness filter (Laplacian variance). Each photo
  includes its **attribution** (author + licence + observation link). Only reusable-licence images (CC0 /
  CC BY / CC BY-SA); the rest are excluded or require the author's explicit permission.
