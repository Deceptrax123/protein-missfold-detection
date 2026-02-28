from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
import torch
from transformers import T5Tokenizer, T5EncoderModel

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
                if residue.id[0] == " ":  # standard residue
                    residues.append(residue.resname)
            sequence += "".join([seq1(res) for res in residues])
        break  # first model only
    
    return sequence

sequence = extract_sequence_from_pdb(r"AlphaFold_model_PDBs\AlphaFold_model_PDBs\1A0N.pdb")
print(sequence)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = "Rostlab/prot_t5_xl_uniref50"

tokenizer = T5Tokenizer.from_pretrained(model_name, do_lower_case=False, use_fast=True).to(device)
model = T5EncoderModel.from_pretrained(model_name).to(device)
model.eval()

ids = tokenizer.batch_encode_plus(sequence, add_special_tokens=True, padding="longest",return_tensors='pt').to(device)
with torch.no_grad():
    embedding_rpr = model(
              ids.input_ids, 
              attention_mask=ids.attention_mask
              )

print(embedding_rpr[0])