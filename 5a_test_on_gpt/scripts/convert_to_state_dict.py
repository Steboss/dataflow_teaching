import torch
from transformers import GPT2Model
import sys

model = GPT2Model.from_pretrained(sys.argv[1], local_files_only=True)
print("passing model to cpu")
model.to('cpu')
print("saving dictionary")
torch.save(model.state_dict(), "model/gpt2.pth")

