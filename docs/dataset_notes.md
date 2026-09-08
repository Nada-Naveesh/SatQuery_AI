# Dataset Adaptation & Evaluation Guide (PS 26167)

This document provides specifications on data preparation, domain adaptation, and benchmark splits for **SatQuery AI**.

---

## 1. Primary Adaptation Dataset: BigEarthNet.txt

Problem Statement 26167 explicitly requires remote-sensing adaptation using **BigEarthNet.txt** or equivalent multimodal open data.

### 1.1 Dataset Architecture
BigEarthNet contains 590,326 pairs of Sentinel-2 (multispectral optical) and Sentinel-1 (C-band dual-pol SAR) image patches:
- **Sentinel-2 Bands:** 12 spectral bands (B01–B12) covering VNIR and SWIR at 10m, 20m, and 60m Ground Sampling Distances.
- **Sentinel-1 Bands:** 2 SAR polarimetric channels:
  - $VV$ (Vertical transmit, Vertical receive)
  - $VH$ (Vertical transmit, Horizontal receive)
- **Annotations:** Multi-label CORINE land cover classification classes plus generated text descriptions (`BigEarthNet.txt`).

### 1.2 Domain Adaptation Strategy
1. **Multimodal Dual-Encoder Feature Alignment:**
   - Optical branch: Vision Transformer (ViT-B/16) initialized from remote-sensing weights.
   - SAR branch: Convolutional or lightweight ViT backbone converting decibel backscatter ($\sigma^0_{\text{dB}}$) into structural feature maps.
2. **Text-Image Contrastive Fine-Tuning (RemoteCLIP / LoRA):**
   - Injected Low-Rank Adaptation (LoRA) matrices into the attention projection layers (`q_proj`, `v_proj`).
   - Rank $r=8$, $\alpha=16$, dropout $p=0.05$.
   - Objective function combines cross-entropy for categorical tags with symmetric InfoNCE contrastive loss:
     $$\mathcal{L}_{\text{InfoNCE}} = -\log \frac{\exp(\text{sim}(u_i, v_i)/\tau)}{\sum_j \exp(\text{sim}(u_i, v_j)/\tau)}$$

---

## 2. Evaluation Benchmarks

| Task Domain | Benchmark Dataset | Metrics Tracked |
| :--- | :--- | :--- |
| **Single-Image RS-VQA** | **RSVQA-LR / RSVQA-HR** | Accuracy (Top-1 QA Match), Macro F1, Confidence Calibration Error |
| **Text-Guided Grounding** | **VRSBench** | Mean Intersection-over-Union (mIoU), Precision@0.5 IoU |
| **Bi-Temporal Change Analysis** | **CDVQA** & **LEVIR-CD** | Change Detection F1 score, IoU of altered mask, BLEU-4 on text summary |
| **Optical-SAR Fusion** | **ISRO Cartosat-2S + RISAT Pairs** | Cloud-penetration structural recovery, Mean IoU across Land-Use classes |

---

## 3. Evaluation Scripts

To reproduce benchmark results locally:
```bash
# Run automated benchmark evaluation harness
python scripts/run_benchmarks.py --benchmark rsvqa --split val_subset
python scripts/run_benchmarks.py --benchmark cdvqa --split test_pairs
```
