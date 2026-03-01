import os
import torch
import glob


def fit_latent_space_baseline(embed_folder="AlphaFold_model_embeds"):
    print("Loading baseline embeddings...")
    embed_files = glob.glob(os.path.join(embed_folder, "*.embed"))

    if not embed_files:
        raise ValueError(
            "No .embed files found! Run the embedding script first.")

    embeddings_list = []
    for file in embed_files:
        emb = torch.load(file, map_location="cpu").squeeze()
        embeddings_list.append(emb)

    X = torch.stack(embeddings_list)

    centroid = X.mean(dim=0)

    distances = torch.linalg.norm(X - centroid, dim=1)

    mean_distance = distances.mean()
    std_distance = distances.std()

    baseline_metrics = {
        "centroid": centroid,
        "mean_dist": mean_distance,
        "std_dist": std_distance
    }
    torch.save(baseline_metrics, "latent_space_baseline.pt")

    print(f"Baseline fitted! Analyzed {len(embeddings_list)} proteins.")
    print(f"Mean Distance from Center: {mean_distance:.4f}")
    print(f"Standard Deviation of Spread: {std_distance:.4f}\n")

    return baseline_metrics


def calculate_z_score(new_embedding_path, baseline_metrics_path="latent_space_baseline.pt"):
    if not os.path.exists(baseline_metrics_path):
        raise FileNotFoundError(
            "Baseline not found! Run fit_latent_space_baseline() first.")

    baseline = torch.load(baseline_metrics_path)
    centroid = baseline["centroid"]
    mean_dist = baseline["mean_dist"]
    std_dist = baseline["std_dist"]

    new_emb = torch.load(new_embedding_path, map_location="cpu").squeeze()

    distance = torch.linalg.norm(new_emb - centroid)

    z_score = (distance - mean_dist) / std_dist

    return z_score.item()


if __name__ == "__main__":
    fit_latent_space_baseline(embed_folder="AlphaFold_model_embeds")
