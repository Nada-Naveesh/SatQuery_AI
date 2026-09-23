#!/usr/bin/env python3
"""
Reproducible Training & Fine-Tuning Script for Remote-Sensing Adapter (SIH 2026 PS 26167).
Trains MultimodalRSAdapter on paired Sentinel-1 SAR + Sentinel-2 Optical data from BigEarthNet.txt.
Produces verifiable model weights: backend/app/models/adaptation/bigearthnet_adapter.pt.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim

from backend.app.models.adaptation.adapter import MultimodalRSAdapter, BIGEARTHNET_19_CLASSES

def train_adapter():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data" / "bigearthnet"
    manifest_file = data_dir / "manifest.json"

    if not manifest_file.exists():
        print("Manifest not found. Running prepare_bigearthnet_adaptation.py first...")
        from scripts.prepare_bigearthnet_adaptation import generate_bigearthnet_dataset
        generate_bigearthnet_dataset()

    with open(manifest_file, "r") as f:
        manifest = json.load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Initializing MultimodalRSAdapter on device: {device}")

    model = MultimodalRSAdapter(embed_dim=256, num_classes=19).to(device)
    criterion_bce = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    # Prepare batches from training split
    train_records = manifest["splits"]["train"]
    print(f"Loaded {len(train_records)} training patches from BigEarthNet.txt manifest.")

    def load_tensors(records):
        opt_list = []
        sar_list = []
        label_list = []

        for rec in records:
            opt_path = root_dir / rec["optical_path"]
            sar_path = root_dir / rec["sar_path"]

            opt_img = Image.open(opt_path).convert("RGB")
            sar_img = Image.open(sar_path).convert("RGB")

            opt_tensor = torch.from_numpy(np.array(opt_img)).permute(2, 0, 1).float() / 255.0
            sar_arr = np.array(sar_img).astype(np.float32) / 255.0
            sar_tensor = torch.from_numpy(sar_arr[:, :, :2]).permute(2, 0, 1).float()

            target = torch.zeros(19, dtype=torch.float32)
            for c_idx in rec["labels"]:
                target[c_idx] = 1.0

            opt_list.append(opt_tensor)
            sar_list.append(sar_tensor)
            label_list.append(target)

        return (
            torch.stack(opt_list).to(device),
            torch.stack(sar_list).to(device),
            torch.stack(label_list).to(device)
        )

    x_opt, x_sar, y_labels = load_tensors(train_records)

    print("Beginning remote-sensing domain adaptation training...")
    start_t = time.perf_counter()
    epochs = 20

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        logits, emb = model(x_opt, x_sar)
        bce_loss = criterion_bce(logits, y_labels)

        # Contrastive alignment between optical and SAR branch embeddings
        f_opt = model.encode_optical(x_opt)
        f_sar = model.encode_sar(x_sar)
        sim_matrix = torch.matmul(f_opt, f_sar.T) / 0.1
        diag_labels = torch.arange(len(train_records), device=device)
        contrastive_loss = nn.functional.cross_entropy(sim_matrix, diag_labels)

        total_loss = bce_loss + 0.2 * contrastive_loss
        total_loss.backward()
        optimizer.step()

        if epoch % 5 == 0 or epoch == 1:
            preds = (torch.sigmoid(logits) > 0.5).float()
            correct = (preds == y_labels).float().mean().item()
            print(f"Epoch [{epoch:02d}/{epochs:02d}] Loss: {total_loss.item():.4f} (BCE: {bce_loss.item():.4f}, Align: {contrastive_loss.item():.4f}) Multi-label Acc: {correct*100:.1f}%")

    elapsed_s = time.perf_counter() - start_t
    print(f"Training completed in {elapsed_s:.2f}s.")

    # Save trained checkpoint
    save_dir = root_dir / "backend" / "app" / "models" / "adaptation"
    save_dir.mkdir(parents=True, exist_ok=True)
    weight_file = save_dir / "bigearthnet_adapter.pt"

    torch.save(model.state_dict(), weight_file)
    print(f"Adapter weights saved to: {weight_file}")

    # Evaluate on val set
    val_records = manifest["splits"]["val"]
    val_opt, val_sar, val_labels = load_tensors(val_records)
    model.eval()
    with torch.no_grad():
        val_logits, _ = model(val_opt, val_sar)
        val_loss = criterion_bce(val_logits, val_labels).item()
        val_preds = (torch.sigmoid(val_logits) > 0.5).float()
        val_acc = (val_preds == val_labels).float().mean().item() * 100.0

    print(f"Validation Evaluation: Loss={val_loss:.4f}, Accuracy={val_acc:.1f}%")
    return weight_file

if __name__ == "__main__":
    train_adapter()
