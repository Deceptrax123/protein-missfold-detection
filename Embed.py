from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
import torch
from transformers import AutoTokenizer, AutoModel

def extract_sequence_from_pdb(pdb_path, chain_id=None):
    parser = PDBParser(QUIET=True)
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

sequence = extract_sequence_from_pdb(r"AlphaFold_model_PDBs\AlphaFold_model_PDBs\1A0N.pdb")
print(sequence)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

model_name = "facebook/esm2_t33_650M_UR50D"

tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=False, use_fast=True)
model = AutoModel.from_pretrained(model_name).to(device)
model.eval()

inputs = tokenizer(sequence, return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}
with torch.no_grad():
    outputs = model(**inputs)

embeddings = outputs.last_hidden_state

embeddings = embeddings[0]
embeddings = embeddings[1:-1]

print(embeddings)