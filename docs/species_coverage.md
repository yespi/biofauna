# Species Coverage — YOLOFauna (Updated 2026-08-06)

| Metric | Value |
|--------|-------|
| Species in model | 1,390 |
| With training images | 1371 |
| Total training images | 549,647 |
| Global accuracy (k-NN) | 63.4% |
| Weighted accuracy | 71.8% |
| AutoID threshold | p≥0.75 |
| Taxonomic exceptions | 7 pairs + 10 genera |

## New (Aug 6)
- +21 bird species embedded (Xavier Salvador guide)
- 361 pages scanned from "Guía fotografiar nudibranquios" (Xavier Salvador)
- 429 expert-labeled crops from Pontes/Ballesteros/Salvador PDFs
- NN classifier tested: 75.2% val (50% real — data leakage)
- Weighted k-NN implemented
