from __future__ import annotations
import re
from pathlib import Path

class ScienceWorldQwenPolicy:
    def __init__(self,model_path:Path,device:str='cuda:0',max_history:int=6):
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        self.torch=torch; self.tokenizer=AutoTokenizer.from_pretrained(str(model_path),local_files_only=True)
        self.model=AutoModelForCausalLM.from_pretrained(str(model_path),local_files_only=True,torch_dtype='auto').to(device).eval(); self.device=device; self.max_history=max_history; self.calls=0; self.input_tokens=0; self.output_tokens=0
    def _prompt(self,task_desc,obs,inventory,history,templates,objects):
        hist='\n'.join(f'Action: {a}\nObservation: {o}' for a,o in history[-self.max_history:]) or '(none)'
        tm='\n'.join(f'- {x}' for x in templates); ob=', '.join(objects)
        system=("You are a ScienceWorld text agent. Choose exactly one concrete environment action. "
                "Use the task, current observation, inventory, recent history, action templates, and currently observable objects. "
                "Do not explain. End with exactly `Action: <concrete action>`. Never mention action template IDs or variation IDs.")
        user=(f'Task:\n{task_desc}\n\nCurrent observation:\n{obs}\n\nInventory:\n{inventory}\n\nRecent history:\n{hist}\n\n'
              f'Action templates:\n{tm}\n\nObservable objects:\n{ob}\n\nChoose one concrete next action.')
        return [{'role':'system','content':system},{'role':'user','content':user}]
    def choose(self,task_desc,obs,inventory,history,templates,objects):
        msgs=self._prompt(task_desc,obs,inventory,history,templates,objects); prompt=self.tokenizer.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True); inputs=self.tokenizer(prompt,return_tensors='pt').to(self.device)
        with self.torch.no_grad():
            g=self.model.generate(**inputs,max_new_tokens=40,do_sample=False,pad_token_id=self.tokenizer.eos_token_id)
        suf=g[0,inputs['input_ids'].shape[1]:]; raw=self.tokenizer.decode(suf,skip_special_tokens=True).strip(); self.calls+=1; self.input_tokens+=int(inputs['input_ids'].numel()); self.output_tokens+=int(suf.numel())
        m=re.search(r'(?im)^\s*Action\s*:\s*(.+?)\s*$',raw); action=(m.group(1) if m else next((x.strip() for x in raw.splitlines() if x.strip()),raw)).strip().strip('`"\'')
        action=re.sub(r'\s+',' ',action); return action,raw
    def usage(self):return {'generation_calls':self.calls,'input_tokens':self.input_tokens,'output_tokens':self.output_tokens,'tokens':self.input_tokens+self.output_tokens}
    def close(self):
        try: del self.model
        except Exception: pass
        try:
            if self.torch.cuda.is_available(): self.torch.cuda.empty_cache()
        except Exception: pass

def normalize_action(x:str)->str:return re.sub(r'\s+',' ',str(x).strip().lower())
def substantive_gold_action(x:str)->bool:return normalize_action(x) not in {'look around','inventory','task','wait','wait1'}
