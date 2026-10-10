# Centimetre-scale proximity in the same photograph: screening for coexistence with an automatic identifier over 1.2 million marine citizen-science photographs

**Author: Gustavo Zafra** · Creator and developer of BioFauna (BioCLIP-2.5 ViT-H/14 + FAISS identifier) and of the FotoFauna and BioQuest applications; collaborator of the citizen-science platform Minka SDG.

**Version v24 — 10 Oct 2026** (v23: 9 Oct). P3/P4/P7/P9 advance: [`experimentos/AVANCE_v24_20261010.md`](experimentos/AVANCE_v24_20261010.md). · Correlation project (BioFauna). What is demonstrated is a **screening method** and a **set of pairs with visual evidence** (both species in the same photo), with partial validation; we do not claim ecological interaction or that “the method works” in general (P8).

---

## Abstract

Seeing two species on the same dive does not show they are related: a diver sees many different species in one outing, and spatial co-occurrence is not evidence of ecological interaction (Blanchet et al., 2020; Freilich et al., 2018). We therefore require a stricter, checkable criterion: **both species in the same photograph** (centimetre-scale proximity). We start from **1,222,170 photographs** and **759,207 geolocated observations** (Minka SDG, iNaturalist and other sources), identified by **BioFauna** (out-of-sample species accuracy **83.14 %** on the 78,145-row panel; source: `dataset/stats.json`, *all08it2* promote). A screening by *events* (observer × ~1 km cell × day × 3 h slot), with local effort controlled, serves only to **generate hypotheses**: 115,204 supported pairs, of which 51,401 are significant, so significance alone does not discriminate. For a shortlist of 138 pairs we searched the gallery for images where both species appear: 41 pairs had at least one candidate photo and 12 had three or more distinct observations; visual review showed **many false positives between look-alike species**. Pairs with both species visible were confirmed by eye (documented positive controls and level 1–2 candidates; Plates 1–9). Crossing the shortlist with GloBI does not validate the screening: without waterbirds there is no enrichment (Fisher p = 0.68; P1). Veech/Poisson/JSDM-lite proxies show weak or null GloBI enrichment (P3; no R/`cooccur` on this host). With accuracy 83.14 %, the probability that both IDs in a co-event are correct is ≈0.69 (P4). Proximity in a photo shows coexistence at centimetre scale, **not interaction**, and the second species is proposed by the identifier without curator confirmation.

**Keywords:** citizen science, coexistence, proximity, deep learning, Mediterranean, underwater photography, co-occurrence.

## 1. Introduction

Amateur underwater photography is a massive source of biodiversity data. Citizen-science platforms (**Minka SDG**, driven from the **FECDAS** ecosystem; **iNaturalist**; **GBIF**) accumulate millions of observations, but most analyses are limited to inventories and distribution maps. Inferring interactions from co-occurrence in participatory data has known effort and observer biases (Isaac et al., 2014; Johnston et al., 2018; Milanesi et al., 2020; Boyd et al., 2021) and, more fundamentally, spatial co-occurrence **is not evidence of ecological interaction** (Blanchet et al., 2020). In a marine intertidal system, networks built from co-occurrence alone poorly recover known interactions (sensitivity 0.469; specificity 0.527; Freilich et al., 2018). Probabilistic co-occurrence models (Veech, 2013; Griffith et al., 2016) and hierarchical community frameworks (Ovaskainen et al., 2017) formalise event screening but do not replace organism-scale verification. We propose a stricter criterion, and the only thing we count as **visual evidence of coexistence**: the appearance of both species in the same photograph, at centimetre scale.

## 2. Materials and methods

### 2.1 Data
1,222,170 photographs from the BioFauna gallery (Minka SDG 377,476; iNaturalist 779,411; GBIF, Wikimedia Commons, DORIS/FFESSM, SeaSlugForum, WoRMS, FishBase and others) and 759,207 observations with coordinates, date and (92 %) time. Catalogue of 2,985 Mediterranean taxa.

### 2.2 Identifier
BioFauna retrieves the most likely species of an image with k-NN over BioCLIP-2.5 ViT-H/14 embeddings in a FAISS index (k = 15, T = 0.05, at most 3 votes per species) and hierarchical calibration. On the out-of-sample field panel (78,145 rows; `dataset/stats.json`) it identifies **83.14 %** of species (0.8314; *all08it2* promote, 8 Oct 2026); accuracy increases with the species' reference photos (Figure 3). This conditions the study: species with few photos and small or camouflaged ones are recognised less well.

### 2.3 Event screening (hypothesis generation only)
An *event* is what the same observer recorded in the same ~1 km cell, on the same day and 3 h slot. For each pair with ≥5 shared events we test, with local effort controlled (null conditioned on the number and size of events per 0.1° cell·day block, Benjamini–Hochberg over the whole family), whether they co-occur more than expected. **This result is not interpreted as association**; it only ranks pairs by effect size and replication (≥3 cells, ≥3 days, ≥5 observers) to choose which to verify. Details in the Supplement.

### 2.4 Verification by real proximity (main criterion)
For each pair (A, B) of the shortlist we analysed up to 60 gallery photos of A and of B. Each photo is split into five views (whole and four quadrants) and embedded; the live index is searched (300 neighbours) and a pair has a **candidate photo** if the other species appears in some view with similarity ≥ 0.82 (or as first choice with ≥ 0.86). The detector only proposes: **every candidate is checked by eye** and accepted only if both species are visible in the image. Look-alike pairs (same genus or family) produce false positives and are discarded in review.

### 2.5 Evidence levels
**Level 0:** event co-occurrence (a lead only). **Level 1:** both species in the same photo in ≥3 independent observations. **Level 2:** plus visible contact (on, inside, feeding). The absence of joint photos leaves the pair *unconfirmed*, not refuted: the gallery is mostly centred portraits of a single species.

### 2.6 Licences and attribution
We use CC0, CC BY, CC BY-SA and CC BY-NC / CC BY-NC-SA photographs; unlicensed and CC BY-NC-ND photos are excluded. Each photo states author, licence, local date and time, place and link to the observation. Those marked † (non-commercial) **must be replaced with CC0, CC BY or CC BY-SA photos, or used with the author's permission, if the article is published in a commercial journal**.

### 2.7 Co-occurrence baselines (P3) and software limitation
The required comparison with Veech's (2013) probabilistic model and the R package `cooccur` (Griffith et al., 2016), a Deutsch-style spatial Poisson null, and a JSDM/HMSC with environmental covariates (Ovaskainen et al., 2017) **was not run with R here**: this host has neither R nor the `cooccur` package. As a CPU proxy on the 3,108 already measured robust pairs (q ≤ 0.05 and observed/expected ratio ≥ 3): (i) all meet the Veech/cooccur-style filter used in screening; (ii) Poisson z = (n−λ)/√λ has median 6.36 and p90 11.12; (iii) JSDM-lite residual = log(n/expected) **without environmental covariates** (stated limitation). GloBI enrichment of the top-k by z versus random (200 resamples) is weak (e.g. k = 100: precision 9.00 % vs 2.03 % random; enrichment 4.43) and **JSDM-lite does not beat z**. Artefact: `experimentos/AVANCE_P3_P4_P1_P9_20261009.md`. A full P3 with `cooccur` and covariate JSDM remains pending.

### 2.8 Identifier error propagation (P4)
With species accuracy p = 0.8314, the probability that both species in a co-event are correctly identified is p² ≈ 0.691 under independence. On the 138-pair shortlist, using per-species accuracies when available: mean P(both OK) = **71.51 %**; 138/138 have E[clean events] ≥ 3 and 134/138 ≥ 8; none of the 138 appear as a direct A↔B confusion in the top-50 of the 25-Sep eval. Before visual review, about **~31 %** of co-events are lost to ID error.

### 2.9 GloBI cross-check (P1)
Each pair was queried against the GloBI API (Poelen et al., 2014). The shortlist has 9/138 documented (6.52 %), but 7 of them are waterbirds with generic type “interactsWith”. **Without birds:** shortlist 2/130 (1.54 %) versus events-only sample 5/395 (1.27 %); odds ratio 1.219, p = 0.6849 (Fisher) → **no enrichment**. Genus-level hits (≥3 pairs) concentrate in *Anas*, *Gallinula* and *Ardea*; outside birds there is no cluster signal.

## 3. Results

### 3.1 From event screening to the shortlist
Of 115,204 pairs with ≥5 events, 51,401 are significant with effort controlled and 3,108 combine replication and an observed/expected ratio ≥3 (Figure 1). Since almost half of the supported pairs are "significant", significance does not discriminate and is not used as a conclusion.

<figure class="fig"><img src="figuras/fig1_cribado_hasta_misma_foto.png" alt="Figure 1. From event screening to pairs with a joint photogr"><figcaption><b>Figure 1. From event screening to pairs with a joint photograph.</b> Number of pairs passing each filter (logarithmic scale). Grey: event screening (hypotheses); blue: shortlist of 138 pairs (the 70 highest-scoring and the 70 highest-scoring among different taxonomic groups, with n ≥ 15 events and ≥ 8 observers), pairs with at least one candidate photo and pairs with three or more distinct observations. Data: <code>data/</code> and <a href="https://github.com/yespi/biofauna/blob/master/data/copresencia_pares_20261006.csv">data/copresencia_pares_20261006.csv</a>.</figcaption></figure>

### 3.2 Detecting both species in the same photo
Of the 138 pairs, 41 had at least one candidate photo and 12 three or more distinct observations (Figure 2). Visual review of the first ones showed **false positives between look-alike species** (e.g. two clams, *Polititapes aureus* and *Ruditapes decussatus*, or two nudibranchs, *Caloria quatrefagesi* and *Luisella babai*): the identifier recognises the look-alike species in another region of the image. This confirms that automatic detection only proposes and that many "significant" coincidences do not survive review.

<figure class="fig"><img src="figuras/fig2_candidatas_por_pareja.png" alt="Figure 2. Candidate photos per pair and visual review outcom"><figcaption><b>Figure 2. Candidate photos per pair and visual review outcome.</b> Distinct observations with a candidate photo of both species for the 14 pairs with most candidates. Green: confirmed by eye with both species visible; red: false positive due to look-alike species; grey: not reviewed or to be confirmed (<i>Echinolittorina</i>–<i>Melarhaphe</i>, <i>Cliona</i>/<i>Clavularia</i>–<i>Rocellaria</i>, <i>Anas</i>–<i>Gallinula</i>).</figcaption></figure>

### 3.3 Pairs with both species visible
Table 2 lists the pairs confirmed by eye and Plates 1–9 show the photographs. *Peltodoris atromaculata* on *Petrosia ficiformis* (Avila, 1996) and *Cratena peregrina* on hydroids serve as **positive controls**: they are documented relations and the method finds photos with both visible. *Condylactis aurantiaca* with *Periclimenes scriptus* (the shrimp among the anemone's tentacles) came from the shortlist; it is consistent with the known commensalism of *Periclimenes* with anemones, although pair-specific literature has not been checked. *Lysmata grabhami* with *Telmatactis cricoides* (cleaner shrimp and anemone) and *Electra posidoniae* with *Tridentata perpusilla* (bryozoan and hydroid on the same *Posidonia* leaf) show real proximity, but the latter is **shared microhabitat, not demonstrated interaction**. The second species in each photo is identified by BioFauna and is **not confirmed by curators**.

| Table 2. Pairs with photographs of both species in the same image | Level | Photos (distinct obs.) | Origin |
|---|---|---:|---|
| *Peltodoris atromaculata* on *Petrosia ficiformis* (predation) | 2 | 4 (4) | positive control (documented relation) |
| *Cratena peregrina* on hydroid colonies (*Eudendrium racemosum*; kleptoparasitism) | 2 | 4 (4) | positive control (documented relation) |
| *Condylactis aurantiaca* with the shrimp *Periclimenes scriptus* (commensalism) | 2 | 4 (4) | screening shortlist |
| *Lysmata grabhami* and *Telmatactis cricoides* (cleaning) | 1 | 4 (4) | earlier selection (cleaner) |
| *Scyllaea pelagica* on floating *Sargassum* | 0–1 | 1 (1) | earlier selection |
| *Electra posidoniae* and *Tridentata perpusilla* on *Posidonia* leaves (shared microhabitat) | 1 | 4 (4) | screening shortlist |
| *Felimare orsinii* on a dark sponge (*Scalarispongia scalaris*) | 1 | 4 (4) | same-photo pairs (visual review 8 Oct) |
| *Parazoanthus axinellae* next to *Spongia lamella* | 1 | 2 (2) | same-photo pairs (visual review 8 Oct) |
| *Echinolittorina punctata* and *Melarhaphe neritoides* (splash zone) | 0–1 | 3 (3) | same-photo pairs (with caution) |

### 3.4 Pairs without a joint photo
No photo with both species was found for *Felimare picta*–*Ircinia oros*, *Muraena helena*–*Ophidiaster ophidianus* or *Fistularia commersonii*–*Pterois miles*. This does not show they do not coexist and does not allow any relation to be claimed: they remain *unconfirmed*.
### 3.5 Other detected relations (screening candidates)
The screening left 41 pairs with at least one candidate photo (including 8 waterbird pairs from the 138-pair shortlist: the same-photo criterion does not depend on the taxonomic group; waterbirds from the shortlist are listed as not reviewed by eye). Table 3 lists them with their review status; those marked 'not reviewed by eye' are hypotheses awaiting visual checking, not results. The pairs in plates 7–9 were added in v22.

Table 3. Candidate pairs with a photo of both species according to the detector

| Pair | Distinct obs. with candidate photo | Status |
|---|---:|---|
| *Electra posidoniae* – *Tridentata perpusilla* | 43 | plate 6 |
| *Polititapes aureus* – *Ruditapes decussatus* | 31 | false positive (look-alikes) |
| *Condylactis aurantiaca* – *Periclimenes scriptus* | 31 | plate 3 |
| *Caloria quatrefagesi* – *Luisella babai* | 24 | false positive (look-alikes) |
| *Echinolittorina punctata* – *Melarhaphe neritoides* | 15 | plate 9, with caution |
| *Anas platyrhynchos* – *Gallinula chloropus* | 14 | waterbirds; not reviewed by eye |
| *Cliona rhodensis* – *Rocellaria dubia* | 14 | discarded (bivalve not visible) |
| *Clavularia crassa* – *Rocellaria dubia* | 13 | not reviewed by eye |
| *Clavelina lepadiformis* – *Echinaster sepositus* | 6 | weak (ascidian unconfirmed) |
| *Eryngium maritimum* – *Pancratium maritimum* | 4 | unconfirmed (*Eryngium* not distinguishable) |
| *Calystegia soldanella* – *Medicago marina* | 3 | 1 obs.; undecided |
| *Mactra corallina* – *Peronaea planata* | 3 | not reviewed by eye |
| *Chamelea gallina* – *Glycymeris glycymeris* | 2 | not reviewed by eye |
| *Chamelea gallina* – *Spisula subtruncata* | 2 | not reviewed by eye |
| *Donax trunculus* – *Spisula subtruncata* | 2 | not reviewed by eye |
| *Sicyonia carinata* – *Synodus saurus* | 2 | not reviewed by eye |
| *Ophidiaster ophidianus* – *Tripterygion delaisi* | 2 | not reviewed by eye |
| *Holothuria forskali* – *Reptadeonella violacea* | 2 | not reviewed by eye |
| *Columbella rustica* – *Conus ventricosus* | 1 | not reviewed by eye |
| *Chroicocephalus ridibundus* – *Gallinula chloropus* | 1 | waterbirds; not reviewed by eye |
| *Ardea cinerea* – *Gallinula chloropus* | 1 | waterbirds; not reviewed by eye |
| *Diaphorodoris alba* – *Luisella babai* | 1 | not reviewed by eye |
| *Mactra corallina* – *Turritellinella tricarinata* | 1 | not reviewed by eye |
| *Donax semistriatus* – *Spisula subtruncata* | 1 | not reviewed by eye |
| *Barbatia barbata* – *Limaria tuberculata* | 1 | not reviewed by eye |
| *Chamelea gallina* – *Mactra corallina* | 1 | not reviewed by eye |
| *Anas platyrhynchos* – *Phalacrocorax carbo* | 1 | waterbirds; not reviewed by eye |
| *Chamelea gallina* – *Ensis minor* | 1 | not reviewed by eye |
| *Fistularia commersonii* – *Siganus rivulatus* | 1 | not reviewed by eye |
| *Cotylorhiza tuberculata* – *Diplodus vulgaris* | 1 | not reviewed by eye |
| *Acanthocardia tuberculata* – *Cymodocea nodosa* | 1 | not reviewed by eye |
| *Chthamalus stellatus* – *Echinolittorina punctata* | 1 | not reviewed by eye |
| *Semicassis undulata* – *Synodus saurus* | 1 | not reviewed by eye |
| *Ophisurus serpens* – *Sicyonia carinata* | 1 | not reviewed by eye |
| *Condylactis aurantiaca* – *Gobius geniporus* | 1 | not reviewed by eye |
| *Holothuria forskali* – *Pleraplysilla spinifera* | 1 | not reviewed by eye |
| *Epinephelus costae* – *Pinna rudis* | 1 | not reviewed by eye |
| *Muraena helena* – *Octopus vulgaris* | 1 | not reviewed by eye |
| *Chthamalus stellatus* – *Cystoseira compressa* | 1 | not reviewed by eye |
| *Conger conger* – *Galathea strigosa* | 1 | not reviewed by eye |
| *Bispira volutacornis* – *Phycis phycis* | 1 | not reviewed by eye |


<div class="lamina">
<p class="lt"><b>Plate 1. <i>Peltodoris atromaculata</i> on <i>Petrosia ficiformis</i> (predation).</b> <i>Sponge identified by BioFauna as <i>Petrosia ficiformis</i> (purple, reddish and cream variants); not confirmed by curators.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par1__peltodoris_atromaculata__petrosia_ficiformis__1.jpg" alt="Plate 1.1"><figcaption>Plate 1.1: Pau Pagès Jaén · CC BY · 2024-08-06 12:08 (Europe/Madrid) · Empordà Marítim, Girona, Cataluña; España · 42.0999° N, 3.1866° E (±36 m) · Minka obs 324790.</figcaption></figure>
<figure><img src="lamina_fotos/par1__peltodoris_atromaculata__petrosia_ficiformis__2.jpg" alt="Plate 1.2"><figcaption>Plate 1.2: Dean Zagorac · CC BY-NC † · 2023-08-07 16:40 (Europe/Zagreb) · Rožići, Kostrena, Općina Kostrena, Primorsko-goranska županija, Croacia; Dolina Ričine, Bakar, Primorsko-Goranska · 45.3024° N, 14.4878° E · iNaturalist obs 184319097.</figcaption></figure>
<figure><img src="lamina_fotos/par1__peltodoris_atromaculata__petrosia_ficiformis__3.jpg" alt="Plate 1.3"><figcaption>Plate 1.3: jmturon · CC BY-NC † · 2022-07-23 10:16 (Europe/Madrid) · Empordà Marítim, Girona, Cataluña; España · 42.0860° N, 3.1988° E (±287 m) · Minka obs 205860.</figcaption></figure>
<figure><img src="lamina_fotos/par1__peltodoris_atromaculata__petrosia_ficiformis__4.jpg" alt="Plate 1.4"><figcaption>Plate 1.4: Óscar Comellas Garcia · CC BY-NC † · 2023-11-11 11:43 (Europe/Madrid) · Girona, España; Empordà Marítim, Girona, Cataluña · 42.0736° N, 3.2055° E (±55 m) · Minka obs 203388.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 2. <i>Cratena peregrina</i> on hydroid colonies (<i>Eudendrium racemosum</i>; kleptoparasitism).</b> <i>Hydroid identified by BioFauna as <i>Eudendrium racemosum</i>; not confirmed by curators.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par2__cratena_peregrina__eudendrium_racemosum__1.jpg" alt="Plate 2.1"><figcaption>Plate 2.1: xavi salvador costa · CC BY-NC † · 2024-11-02 22:52 (Europe/Paris) · La Peyrade, Frontignan, Montpellier, Hérault, Francia; ABC de la Lagune, Hérault, Languedoc-Roussillon · 43.4247° N, 3.7000° E (±88 m) · Minka obs 392849.</figcaption></figure>
<figure><img src="lamina_fotos/par2__cratena_peregrina__eudendrium_racemosum__2.jpg" alt="Plate 2.2"><figcaption>Plate 2.2: xatrac · CC BY-NC † · 2022-08-27 10:08 (Europe/Paris) · Venta de Goya, Lloret de Mar, la Selva, Cataluña, España; Comarca de la Selva, Girona, Cataluña · 41.6913° N, 2.8299° E (±183 m) · Minka obs 88838.</figcaption></figure>
<figure><img src="lamina_fotos/par2__cratena_peregrina__eudendrium_racemosum__3.jpg" alt="Plate 2.3"><figcaption>Plate 2.3: xatrac · CC BY-NC † · 2022-08-10 09:42 (Europe/Paris) · Venta de Goya, Lloret de Mar, la Selva, Cataluña, España; Comarca de la Selva, Girona, Cataluña · 41.6913° N, 2.8299° E (±183 m) · Minka obs 88546.</figcaption></figure>
<figure><img src="lamina_fotos/par2__cratena_peregrina__eudendrium_racemosum__4.jpg" alt="Plate 2.4"><figcaption>Plate 2.4: xatrac · CC BY-NC † · 2022-08-07 09:16 (Europe/Paris) · Venta de Goya, Lloret de Mar, la Selva, Cataluña, España; Comarca de la Selva, Girona, Cataluña · 41.6913° N, 2.8299° E (±183 m) · Minka obs 88528.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 3. <i>Condylactis aurantiaca</i> with the shrimp <i>Periclimenes scriptus</i> (commensalism).</b> <i>Shrimp identified by BioFauna as <i>Periclimenes scriptus</i>; not confirmed by curators.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__1.jpg" alt="Plate 3.1"><figcaption>Plate 3.1: xavi salvador costa · CC BY-NC † · 2016-09-10 22:07 (Europe/Paris) · Begur, Bajo Ampurdán, Cataluña, España; Empordà Marítim, Girona, Cataluña · 41.9355° N, 3.2176° E (±185 m) · Minka obs 28492.</figcaption></figure>
<figure><img src="lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__2.jpg" alt="Plate 3.2"><figcaption>Plate 3.2: Sylvain Le Bris · CC BY-NC † · 2026-04-08 22:17 (Europe/Paris) · Montredon, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur; Francia · 43.2325° N, 5.3502° E (±101 m) · iNaturalist obs 348576200.</figcaption></figure>
<figure><img src="lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__3.jpg" alt="Plate 3.3"><figcaption>Plate 3.3: xavi salvador costa · CC BY-NC † · 2016-07-09 22:18 (Europe/Paris) · Begur, Bajo Ampurdán, Cataluña, España; Empordà Marítim, Girona, Cataluña · 41.9366° N, 3.2201° E (±185 m) · Minka obs 28862.</figcaption></figure>
<figure><img src="lamina_fotos/par3__condylactis_aurantiaca__periclimenes_scriptus__4.jpg" alt="Plate 3.4"><figcaption>Plate 3.4: xavi salvador costa · CC BY-NC † · 2018-09-01 16:03 (Europe/Paris) · Begur, Bajo Ampurdán, Cataluña, España; Empordà Marítim, Girona, Cataluña · 41.9357° N, 3.2176° E (±142 m) · Minka obs 35885.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 4. <i>Lysmata grabhami</i> and <i>Telmatactis cricoides</i> (cleaning).</b> <i>Cleaner shrimp and anemone identified by BioFauna; the shrimp is small in two photos.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__1.jpg" alt="Plate 4.1"><figcaption>Plate 4.1: jmturon · CC BY-NC † · 2023-12-05 10:57 (Atlantic/Canary) · Las Coloradas; LANZAROTE with iselets and seashore, Las Palmas, Islas Canarias; España · 28.8506° N, 13.7995° W (±662 m) · Minka obs 210346.</figcaption></figure>
<figure><img src="lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__2.jpg" alt="Plate 4.2"><figcaption>Plate 4.2: jmturon · CC BY-NC † · 2023-12-06 20:06 (Atlantic/Canary) · Playa Flamingo; LANZAROTE with iselets and seashore, Las Palmas, Islas Canarias; España · 28.8552° N, 13.8439° W (±361 m) · Minka obs 210532.</figcaption></figure>
<figure><img src="lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__3.jpg" alt="Plate 4.3"><figcaption>Plate 4.3: phil_newman · CC BY-NC † · 2025-11-22 11:50 (Atlantic/Canary) · Playa Flamingo Playa Blanca Lanzarote; LANZAROTE with iselets and seashore, Las Palmas, Islas Canarias; España · 28.8568° N, 13.8428° W (±100 m) · iNaturalist obs 329826704.</figcaption></figure>
<figure><img src="lamina_fotos/par4__lysmata_grabhami__telmatactis_cricoides__4.jpg" alt="Plate 4.4"><figcaption>Plate 4.4: whodden · CC BY-NC † · 2007-04-04 00:00 (Europe/Madrid) · Punta Prieta, Güímar, Canarias, España; TENERIFE with seashore, Santa Cruz de Tenerife, Islas Canarias · 28.2660° N, 16.3869° W (±14 m) · iNaturalist obs 2354980.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 5. <i>Scyllaea pelagica</i> on floating <i>Sargassum</i>.</b> <i>Only the camouflaged nudibranch is clearly visible; <i>Latreutes</i> and <i>Hippolyte</i> cannot be told apart by eye.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par5__scyllaea_pelagica__latreutes_fucorum__1.jpg" alt="Plate 5.1"><figcaption>Plate 5.1: Ben Eddy · CC BY-NC † · 2023-06-27 13:52 (Atlantic/Bermuda) · Southampton, BM; Bermuda Marine, Sandys; Bermudas · 32.2556° N, 64.8742° W (±105 m) · iNaturalist obs 170761288.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 6. <i>Electra posidoniae</i> and <i>Tridentata perpusilla</i> on <i>Posidonia</i> leaves (shared microhabitat).</b> <i>Encrusting bryozoan and hydroid on the same leaf; shared microhabitat, interaction not demonstrated.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__1.jpg" alt="Plate 6.1"><figcaption>Plate 6.1: xavi salvador costa · CC BY-NC † · 2023-08-09 11:01 (Europe/Madrid) · Vegueria de Barcelona, Barcelona, Cataluña; España · 41.3957° N, 2.2114° E (±115 m) · Minka obs 153028.</figcaption></figure>
<figure><img src="lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__2.jpg" alt="Plate 6.2"><figcaption>Plate 6.2: conxi · CC BY-NC † · 2025-05-31 11:48 (Europe/Madrid) · Valldolig, Blanes, la Selva, Cataluña, España; Vegueria de Barcelona, Barcelona, Cataluña · 41.6732° N, 2.8022° E (±178 m) · Minka obs 511234.</figcaption></figure>
<figure><img src="lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__3.jpg" alt="Plate 6.3"><figcaption>Plate 6.3: ester serrao · CC BY · 2024-06-30 07:17 (America/Costa_Rica) · Esterillos Oeste, Parrita, Puntarenas, Costa Rica · 9.5237° N, 84.5099° W · Minka obs 629063.</figcaption></figure>
<figure><img src="lamina_fotos/par6__electra_posidoniae__tridentata_perpusilla__4.jpg" alt="Plate 6.4"><figcaption>Plate 6.4: Manel Ortega · CC BY · 2025-08-10 10:13 (Europe/Madrid) · Llançà, Alto Ampurdán, Cataluña, España; Orientales, Girona, Cataluña · 42.3875° N, 3.1612° E (±622 m) · Minka obs 544263.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 7. <i>Felimare orsinii</i> on a dark sponge (<i>Scalarispongia scalaris</i>).</b> <i>Sponge identified only by BioFauna from the photo (not confirmed by curators): level 1 (appears on it); predation is not claimed.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par7__felimare_orsinii__scalarispongia_scalaris__1.jpg" alt="Plate 7.1"><figcaption>Plate 7.1: motalec · CC BY-NC † · 2026-08-02 14:01 (Europe/Paris) · 8e Arrondissement, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur · 43.1907° N, 5.3827° E · iNaturalist obs 389401988.</figcaption></figure>
<figure><img src="lamina_fotos/par7__felimare_orsinii__scalarispongia_scalaris__2.jpg" alt="Plate 7.2"><figcaption>Plate 7.2: xavi salvador costa · CC BY-NC † · 2016-07-25 23:04 (Europe/Madrid) · Empordà Marítim, Girona, Cataluña · 41.7658° N, 3.0026° E · Minka obs 418034.</figcaption></figure>
<figure><img src="lamina_fotos/par7__felimare_orsinii__scalarispongia_scalaris__3.jpg" alt="Plate 7.3"><figcaption>Plate 7.3: motalec · CC BY-NC † · 2025-04-26 09:37 (Europe/Paris) · Impérial du Milieu; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur · 43.1716° N, 5.3938° E · iNaturalist obs 275056747.</figcaption></figure>
<figure><img src="lamina_fotos/par7__felimare_orsinii__scalarispongia_scalaris__4.jpg" alt="Plate 7.4"><figcaption>Plate 7.4: Alessandro Diotallevi · CC BY-NC † · 2024-04-28 10:06 (Etc/GMT-1) · lugar no indicado · 41.2450° N, 12.3467° E · iNaturalist obs 212560581.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 8. <i>Parazoanthus axinellae</i> next to <i>Spongia lamella</i>.</b> <i>Grey laminar sponge next to <i>Parazoanthus</i> colonies: coexistence in the same frame, interaction not demonstrated.</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par8__parazoanthus_axinellae__spongia_lamella__1.jpg" alt="Plate 8.1"><figcaption>Plate 8.1: Sylvain Le Bris · CC BY-NC † · 2025-08-15 10:55 (Europe/Paris) · Pierre à Joseph, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur · 43.1851° N, 5.3894° E · iNaturalist obs 307095607.</figcaption></figure>
<figure><img src="lamina_fotos/par8__parazoanthus_axinellae__spongia_lamella__2.jpg" alt="Plate 8.2"><figcaption>Plate 8.2: Sylvain Le Bris · CC BY-NC † · 2026-05-17 09:42 (Europe/Paris) · Pharillons, Marseille, France; Bouches-Du-Rhône, Bouches-du-Rhône, Provence-Alpes-Côte d'Azur · 43.2074° N, 5.3380° E · iNaturalist obs 362838925.</figcaption></figure>
</div>
</div>

<div class="lamina">
<p class="lt"><b>Plate 9. <i>Echinolittorina punctata</i> and <i>Melarhaphe neritoides</i> (splash zone).</b> <i>Splash-zone snails on the same rock. The two species look very alike: their separation relies on BioFauna and needs expert confirmation (level 0–1).</i></p>
<div class="grid">
<figure><img src="lamina_fotos/par9__echinolittorina_punctata__melarhaphe_neritoides__1.jpg" alt="Plate 9.1"><figcaption>Plate 9.1: Golfopolikayak · CC BY · 2020-06-19 16:58 (Europe/Paris) · 87029 Scalea CS, Italia; Pollino, Cosenza, Calabria · 39.8191° N, 15.7775° E · iNaturalist obs 56350676.</figcaption></figure>
<figure><img src="lamina_fotos/par9__echinolittorina_punctata__melarhaphe_neritoides__2.jpg" alt="Plate 9.2"><figcaption>Plate 9.2: Mar Humet Caballero · CC BY-NC † · 2026-08-03 17:51 (Europe/Madrid) · Camping Cases, Carrer a l'Ombra del Montsià, les Cases d'Alcanar, Alcanar, Montsià, Tarragona, Catalunya, 43530, Espanya; RB ESP 44. Reserva de la Biosfera.Terras de L’Ebre. Cataluña. España., Castellón, Cataluña · 40.5557° N, 0.5335° E · Minka obs 834586.</figcaption></figure>
<figure><img src="lamina_fotos/par9__echinolittorina_punctata__melarhaphe_neritoides__3.jpg" alt="Plate 9.3"><figcaption>Plate 9.3: Calum McLennan · CC BY-NC † · 2021-08-25 11:24 (Europe/London) · Alicante, Spain; Javea - Xabia, Alicante, Comunidad Valenciana · 38.8169° N, 0.1688° E · iNaturalist obs 92485321.</figcaption></figure>
</div>
</div>


### 3.6 Baselines and GloBI enrichment (P3, proxy)
On the 3,108 robust pairs, GloBI enrichment of the ranking by z (versus 200 random resamples) is:

| k | top-z precision | random precision | enrichment |
|---:|---:|---:|---:|
| 50 | 6.00 % | 1.75 % | 3.43 |
| 100 | 9.00 % | 2.03 % | 4.43 |
| 200 | 7.50 % | 1.96 % | 3.84 |
| 500 | 3.60 % | 1.90 % | 1.90 |

On the shortlist: GloBI precision 25 % (top-20), 14 % (top-50), 6.52 % (138). The JSDM-lite residual does not beat z. **Reading:** the value of the work is not in event screening but in the same-photo criterion. Limitation: `cooccur` (R) and a covariate JSDM (Ovaskainen et al., 2017) were not run.

### 3.7 Error propagation (P4)
With OOS = 83.14 %, P(both OK) ≈ 0.69–0.72 on the shortlist. That bounds how many event coincidences can be doubly correct IDs **before** visual review; it does not replace that review.

### 3.8 Literature review of confirmed pairs (P9)
|*Peltodoris atromaculata*–*Petrosia ficiformis*|documented predation (Avila, 1996); positive control|
|*Cratena peregrina*–hydroids|classic Mediterranean relation; primary DOI missing in this version|
|*Condylactis aurantiaca*–*Periclimenes scriptus*|genus-level commensalism; pair-specific citation pending|
|*Lysmata grabhami*–*Telmatactis cricoides*|cleaning documented in *Lysmata*; E Atlantic / Canary literature pending|
|*Electra posidoniae*–*Tridentata perpusilla*|shared *Posidonia* microhabitat, not demonstrated interaction|
|*Felimare orsinii*–*Scalarispongia scalaris*|level 1 (appears on); **do not** claim predation|
|*Parazoanthus axinellae*–*Spongia lamella*|coexistence in the same frame; interaction not demonstrated|
|*Calystegia soldanella*–*Medicago marina*|shared dune habitat (terrestrial)|

Curators (Pontes, Salvador, Companys): formal sending of v10 plates for review is pending.

## 4. Discussion

**What this shows and what it does not.** A photo with both species shows proximity at centimetre scale at one instant; it does not show that they seek, avoid or interact with each other (Blanchet et al., 2020). Freilich et al. (2018) show that even with exhaustive field sampling, co-occurrence poorly recovers interactions; our event screening fits that caution. Three or more independent observations with both visible give replication, and visible contact (on, inside, feeding) points to a relation that must be confirmed with curators and literature. Event co-occurrence, by contrast, only flags species that share place and date and is **not used as a result**: requiring the same photo removes most coincidences.

**Biases.** The gallery consists mostly of centred portraits of one species, which underestimates the share of photos with a second species; the identifier recognises small or camouflaged species less well and confuses look-alike species (false positives); only the first candidates have been reviewed by eye; and the photographs come with very diverse licences, which limits the plates.

## 5. Limitations

**Identifier accuracy.** The **83.14 %** (0.8314; `dataset/stats.json`, 78,145-row panel after *all08it2*) is the current out-of-sample species accuracy; the panel may still contain rows with high gallery similarity, so it may be somewhat optimistic. **Incomplete P3.** There is no R/`cooccur` on this host: Veech (2013) / Griffith et al. (2016) baselines and a covariate JSDM (Ovaskainen et al., 2017) remain a limitation; only CPU proxies exist (P3). **External validation (P1).** GloBI does not validate the shortlist: without birds, Fisher p = 0.68; the API cannot separate iNaturalist-derived records (possible circularity). **P4.** With p = 0.8314, about ~31 % of co-events are lost to ID error before visual review. Proximity in a photo is not interaction. The identity of the second species is a proposal by the identifier. The shortlist was chosen by effect size and support, not at random. Pair literature (P9) and curator review remain pending. CC BY-NC photos must be replaced in a commercial journal. P2 (detector precision on ~200 photos) and P5 (≥5 new pairs with photo) are still open.

## 6. Conclusions

1. Event co-occurrence screening, even with effort controlled, is not evidence of association: it generates thousands of coincidences of which only a small part survives review by real proximity.
2. Real proximity (both species in the same photograph) is a criterion any reader can verify; with it, a few pairs have been confirmed by eye (documented positive controls and level 1–2 candidates in Plates 1–9); that is a base of visual evidence, not proof that screening “works” in general.
3. The method serves to propose pairs and photographs that curators can verify; it does not replace their judgement.

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

- Aceves-Bueno, E., Adeleye, A. S., Feraud, M., Huang, Y., Tao, M., Yang, Y., & Anderson, S. E. (2017). The accuracy of citizen science data: a quantitative review. *The Bulletin of the Ecological Society of America*, 98(4), 278–290.
- Avila, C. (1996). The growth of *Peltodoris atromaculata* Bergh, 1880 (Gastropoda, Nudibranchia) in the laboratory. *Journal of Molluscan Studies*, 62, 151–157. — diet exclusively on *Petrosia ficiformis*.
- Blanchet, F. G., Cazelles, K., & Gravel, D. (2020). Co-occurrence is not evidence of ecological interactions. *Ecology Letters*, 23(7), 1050–1063. https://doi.org/10.1111/ele.13525
- Freilich, M. A., Wieters, E., Broitman, B. R., Marquet, P. A., & Navarrete, S. A. (2018). Species co-occurrence networks: Can they reveal trophic and non-trophic interactions in ecological communities? *Ecology*, 99(3), 690–699. https://doi.org/10.1002/ecy.2142
- Griffith, D. M., Veech, J. A., & Marsh, C. J. (2016). cooccur: Probabilistic species co-occurrence analysis in R. *Journal of Statistical Software*, 69(Code Snippet 2). https://doi.org/10.18637/jss.v069.c02
- Boyd, R. J., Powers, M., & Pescott, O. L. (2021). occAssess: an R package for assessing potential biases in species occurrence data. *Ecology and Evolution*, 11(22).
- Isaac, N. J. B., van Strien, A. J., August, T. A., de Zeeuw, M. P., & Roy, D. B. (2014). Statistics for citizen science: extracting signals of change from noisy ecological data. *Methods in Ecology and Evolution*, 5(10), 1052–1060.
- Johnston, A., Fink, D., Hochachka, W. M., & Kelling, S. (2018). Estimates of observer expertise improve species distributions from citizen science data. *Methods in Ecology and Evolution*, 9(4), 880–890.
- McDonald, G. R., & Nybakken, J. W. (2001). A worldwide review of the food of nudibranch mollusks. II. The suborder Doridacea. *The Veliger*.
- Milanesi, P., Mori, E., & Menchetti, M. (2020). Observer-oriented approach improves species distribution models from citizen science data. *Ecology and Evolution*, 10(21), 12104–12114.
- Ovaskainen, O., Tikhonov, G., Norberg, A., Guillaume Blanchet, F., Duan, L., Dunson, D., Roslin, T., & Abrego, N. (2017). How to make more out of community data? A conceptual framework and its implementation as models and software. *Ecology Letters*, 20(5), 561–576. https://doi.org/10.1111/ele.12757
- Poelen, J. H., Simons, J. D., & Mungall, C. J. (2014). Global biotic interactions: An open infrastructure to share and analyze species-interaction datasets. *Ecological Informatics*, 24, 148–159.
- Veech, J. A. (2013). A probabilistic model for analysing species co-occurrence. *Global Ecology and Biogeography*, 22(2), 252–260. https://doi.org/10.1111/j.1466-8238.2012.00789.x
- Peraza, E., Pérez, J. A., Abdul-Jalbar, B., Chinea, J., & Clemente, S. (2024). Exploring the association between the arrow crab *Stenorhynchus lanceolatus* and the sea anemone *Telmatactis cricoides* in the Canary Islands. *Regional Studies in Marine Science*.

## Data availability

**All material is in the public GitHub repository: https://github.com/yespi/biofauna** (branch `master`). Full paths:
- Shortlist pairs and their candidate photos: [`data/copresencia_pares_20261006.csv`](https://github.com/yespi/biofauna/blob/master/data/copresencia_pares_20261006.csv) and [`data/copresencia_hits_20261006.jsonl`](https://github.com/yespi/biofauna/blob/master/data/copresencia_hits_20261006.jsonl).
- Plate manifest with author, licence, date and time, place and link for each photo: [`papers/proyecto_correlacion/lamina_fotos/lamina_manifest_20261008.json`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/lamina_fotos/lamina_manifest_20261008.json).
- Event-screening lists (hypotheses only) and their description: [`data/README_correlacion.md`](https://github.com/yespi/biofauna/blob/master/data/README_correlacion.md) and the files `data/nulo_exacto_pares_*.csv` and `data/pares_*_20261005.csv`.
- Extended methods and results, figures and plates: folder [`papers/proyecto_correlacion/`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/) (article in Spanish and English, `LAMINAS`, `METODOS.md`, `RESULTADOS.md`, `figuras/`, `lamina_fotos/`). The unnumbered versions (`ARTICULO_ES_latest.pdf`, `ARTICLE_EN_latest.pdf`, `LAMINAS_latest.pdf`) are always updated; numbered versions are kept (v22 and v23). P1/P3/P4/P9 detail: [`experimentos/AVANCE_P3_P4_P1_P9_20261009.md`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/experimentos/AVANCE_P3_P4_P1_P9_20261009.md).
- BioFauna identifier (code, prototypes, calibrators, evaluation scripts): folders [`src/`](https://github.com/yespi/biofauna/blob/master/src/), [`scripts/`](https://github.com/yespi/biofauna/blob/master/scripts/), [`data/`](https://github.com/yespi/biofauna/blob/master/data/) and [`papers/biofauna/`](https://github.com/yespi/biofauna/blob/master/papers/biofauna/).
- **Not redistributable**: gallery photographs (Minka SDG, iNaturalist and other licences; those in the plates are included with attribution) and per-photo embeddings.


## Supplementary material

**Supplement S1. Event screening (hypotheses).** Description of the effort-controlled test and full lists in [`NULO_EXACTO_TODOS_PARES_20261005.md`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/NULO_EXACTO_TODOS_PARES_20261005.md). Figures S1 and S2 in [`papers/proyecto_correlacion/figuras/`](https://github.com/yespi/biofauna/blob/master/papers/proyecto_correlacion/figuras/).


**Table S1. The 30 pairs with the highest z among the 3,108 robust pairs of the event screening (observed/expected ratio ≥ 3, ≥ 5 observers).** These are **hypotheses, not results**: a high z means they co-occur far more than local effort predicts, but it does not separate interaction from shared habitat (e.g. two beach species), from species planted or kept together (*Phoenix*–*Washingtonia*) or from species so alike that the observer assigns one or the other (*Nembrotha cristata*–*N. milleri*). The full list of 3,108 and of the 2,312 Mediterranean pairs of different genera is in `data/`.

| Pair | Same genus | Groups | Shared events | Expected (effort) | Ratio | z | Observers |
|---|:-:|---|---:|---:|---:|---:|---:|
| *Limacia clavigera* – *Polycera quadrilineata* | no | Mollusca | 66 | 2.0 | 33.1 | 54.6 | 19 |
| *Cephalopholis miniata* – *Pseudanthias squamipinnis* | no | Actinopterygii | 102 | 4.6 | 22.3 | 54.5 | 55 |
| *Phoenix canariensis* – *Washingtonia robusta* | no | Plantae | 31 | 0.6 | 55.8 | 51.8 | 21 |
| *Limacia clavigera* – *Okenia nodosa* | no | Mollusca | 75 | 2.8 | 26.7 | 49.1 | 15 |
| *Chamelea striatula* – *Donax vittatus* | no | Mollusca | 80 | 4.0 | 19.8 | 45.4 | 57 |
| *Okenia nodosa* – *Polycera quadrilineata* | no | Mollusca | 38 | 0.9 | 41.0 | 44.1 | 8 |
| *Candiella lineata* – *Limacia clavigera* | no | Mollusca | 35 | 0.7 | 48.5 | 41.6 | 9 |
| *Nembrotha cristata* – *Nembrotha milleri* | yes | Mollusca | 76 | 6.3 | 12.2 | 40.7 | 57 |
| *Clibanarius aequabilis* – *Columbella adansoni* | no | Malacostraca / Mollusca | 34 | 1.1 | 32.2 | 38.8 | 30 |
| *Archidoris pseudoargus* – *Limacia clavigera* | no | Mollusca | 43 | 3.2 | 13.2 | 37.0 | 10 |
| *Sambucus nigra* – *Urtica dioica* | no | Plantae | 55 | 2.9 | 18.8 | 35.1 | 52 |
| *Sargassum muticum* – *Zostera marina* | no |  / Plantae | 37 | 1.3 | 27.7 | 34.6 | 29 |
| *Chthamalus stellatus* – *Tectarius striatus* | no | Crustacea / Mollusca | 44 | 2.4 | 18.4 | 34.4 | 34 |
| *Chthamalus stellatus* – *Clibanarius aequabilis* | no | Crustacea / Malacostraca | 38 | 1.8 | 20.9 | 33.2 | 32 |
| *Donax vittatus* – *Spisula subtruncata* | no | Mollusca | 20 | 0.4 | 53.1 | 33.1 | 14 |
| *Donax vittatus* – *Lutraria lutraria* | no | Mollusca | 50 | 2.9 | 17.3 | 32.1 | 35 |
| *Flexopecten glaber* – *Tritia nitida* | no | Mollusca | 18 | 0.4 | 47.3 | 30.5 | 5 |
| *Acanthurus dussumieri* – *Arothron hispidus* | no | Actinopterygii | 11 | 0.1 | 72.6 | 28.4 | 10 |
| *Solatopupa similis* – *Zonites algirus* | no | Mollusca | 18 | 0.8 | 22.1 | 26.7 | 12 |
| *Echium vulgare* – *Hypericum perforatum* | no | Plantae | 19 | 0.7 | 27.1 | 25.9 | 14 |
| *Cochlicella acuta* – *Trochoidea elegans* | no | Mollusca | 32 | 2.4 | 13.2 | 25.7 | 25 |
| *Helicodonta obvoluta* – *Solatopupa similis* | no | Mollusca | 14 | 0.8 | 17.7 | 25.3 | 6 |
| *Clibanarius aequabilis* – *Tectarius striatus* | no | Malacostraca / Mollusca | 28 | 1.8 | 15.7 | 24.4 | 24 |
| *Limacia clavigera* – *Trapania lineata* | no | Mollusca | 15 | 0.5 | 28.9 | 24.0 | 7 |
| *Chamelea striatula* – *Mactra stultorum* | no | Mollusca | 13 | 0.7 | 19.1 | 23.8 | 13 |
| *Solatopupa similis* – *Xerosecta cespitum* | no | Mollusca | 16 | 0.8 | 19.6 | 23.6 | 9 |
| *Chthamalus stellatus* – *Columbella adansoni* | no | Crustacea / Mollusca | 21 | 1.1 | 19.9 | 23.5 | 19 |
| *Acanthurus dussumieri* – *Cephalopholis miniata* | no | Actinopterygii | 9 | 0.1 | 59.4 | 23.1 | 9 |
| *Rocellaria dubia* – *Vermetus triquetrus* | no | Mollusca | 83 | 16.5 | 5.0 | 23.1 | 11 |
| *Donax vittatus* – *Turritellinella tricarinata* | no | Mollusca | 26 | 1.9 | 13.6 | 22.5 | 16 |

<figure class="fig"><img src="figuras/supl_S1_distribucion_efecto.png" alt="Figure S1. Effect-size distribution. Ratio of observed to ef"><figcaption><b>Figure S1. Effect-size distribution.</b> Ratio of observed to effort-expected events for pairs with q ≤ 0.05 (grey) and replicated pairs (blue); logarithmic axes and lines at 2, 3, 5 and 10. A large part of the significant pairs have low ratios.</figcaption></figure>
<figure class="fig"><img src="figuras/supl_S2_soporte_vs_efecto.png" alt="Figure S2. Support versus effect in replicated pairs. Each p"><figcaption><b>Figure S2. Support versus effect in replicated pairs.</b> Each point is a pair: events with both species (n) against observed/expected ratio, coloured by distinct observers; the red line marks ratio 3.</figcaption></figure>

**Photo plates** (`LAMINAS_latest.pdf`): the same plates as section 3.3, with full attribution.
