import torch
from transformers import T5ForConditionalGeneration

model = T5ForConditionalGeneration.from_pretrained("/home/sbosisio486/dataflow_teaching/from_tutorial/t5_model", local_files_only=True)
print("passing model to cpu") 
model.to('cpu')
print("saving dictionary")
torch.save(model.state_dict(), "model/state_dict.pth")

