import os
import re
import pickle
import torch
from pathlib import Path
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from transformers import AutoTokenizer, AutoModel

PDB_FOLDER = r"AlphaFold_model_PDBs\AlphaFold_model_PDBs" 
OUTPUT_FOLDER = r"AlphaFold_model_PDBs\AlphaFold_model_embeds"
MODEL_NAME = "facebook/esm2_t33_650M_UR50D"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, do_lower_case=False, use_fast=True)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

parser = PDBParser(QUIET=True)

def extract_sequence_from_pdb(pdb_path, chain_id=None):
    structure = parser.get_structure("protein", pdb_path)
    
    sequence = ""
    for model in structure:
        for chain in model:
            if chain_id and chain.id != chain_id:
                continue
            residues = []
            for residue in chain:
                if residue.id[0] == " ":
                    residues.append(residue.resname)
            sequence += "".join([seq1(res) for res in residues])
        break 
    
    return sequence

pdb_files = os.listdir(PDB_FOLDER)
pkl_files = [i.replace(".pdb", ".pkl") for i in pdb_files] #Respective pkl file names

for x in range(len(pdb_files)):
    fname = pdb_files[x]
    sequence = extract_sequence_from_pdb(str(os.path.join(PDB_FOLDER, fname)))
    sequence = sequence.upper()
    sequence = re.sub(r"[UZOB]", "X", sequence)
    if len(sequence) == 0:
            print(f"Skipping empty sequence: {fname}")
            continue

    inputs = tokenizer(sequence, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)

    token_embeddings = outputs.last_hidden_state[0][1:-1]
    attention_mask = inputs["attention_mask"][0][1:-1].unsqueeze(-1)

    protein_embedding = (token_embeddings * attention_mask).sum(dim=0) / attention_mask.sum()

    protein_embedding = protein_embedding.cpu().float()

    output_path = os.path.join(OUTPUT_FOLDER, pkl_files[x])
    with open(output_path, "wb") as f:
        pickle.dump(protein_embedding, f)

    torch.cuda.empty_cache()