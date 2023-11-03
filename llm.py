import torch
import numpy as np
import torch.nn.functional as F
import warnings
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM

warnings.filterwarnings("ignore")


class Chatbot:
    def __init__(self, model_name='stabilityai/stablelm-3b-4e1t', device='cuda'):
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.device = device
        self.model.to(device)

    @torch.no_grad()	
    def generate_response_greedy(self, input_text, pre_prompt, break_word, 
                                max_length=100, temp=0.6, name='',
                                past_key_vals=None, next_id=None, verbose=True):

        if past_key_vals is None:
            inputs = self.tokenizer.encode(pre_prompt + input_text + '\n' + name, return_tensors="pt").to(self.device)
            response_ids = inputs
        else:
            inputs = self.tokenizer.encode(input_text + '\n' + name, return_tensors="pt").to(self.device)
            response_ids = torch.concat((next_id, inputs),dim=-1)
        output = ''
        last_n = ''
        if verbose:
            print(name, end='')
        response_text = ''
        for _ in (range(max_length)):
            out = self.model.forward(input_ids=response_ids, past_key_values=past_key_vals)
            next_token_id = torch.multinomial(F.softmax(out.logits[:, -1, :]/temp,  dim=-1), num_samples=1)
            past_key_vals = out.past_key_values
            response_ids = next_token_id
            # print([response_ids[0][-1].to('cpu')])
            output = self.tokenizer.decode([response_ids[0][-1].to('cpu')])
            if verbose:
                print(output, end='')
            response_text += output
            sys.stdout.flush()
            last_n += output
            last_n = last_n[-len(break_word):]
            if last_n == break_word:
                break
        past_kv = past_key_vals
        next_id = response_ids
        return response_text, past_kv, next_id


if __name__ == "__main__":
    sales_pre_prompt = '''
JOHN is a saleman for Fakhir's tea. JOHN has been selling the tea his entire life. JOHN is a great tea salesman.

[USER] Hey, how's it going?
[JOHN] Good, good. How about you? Say, have you tried any good drinks lately?
[USER] Not really, just my usual coffee and water.
[JOHN] Ah, well let me tell you, I've been really getting into tea lately. Specifically, Fakhir's Tea. Have you heard of it?
[USER] No, I don't think so. What's so great about it?
[JOHN] Oh, it's just amazing. Fakhir's Tea is a premium tea brand that uses high-quality tea leaves and blends them with natural spices to create some really unique and delicious flavors.
[USER] That sounds interesting. Where can I find it?
[JOHN] You can find it at most grocery stores and online retailers, but I've found that ordering directly from their website gets you the best deals and the most variety. Plus, their customer service is top-notch.
[USER] What flavors do they have?
[JOHN] They have a ton of different blends, from classic black teas to more exotic flavors like cardamom and saffron. I highly recommend their masala chai blend, it's a real treat for the taste buds.
[USER] I'll have to check it out. Thanks for the recommendation.
[JOHN] No problem at all, happy to help. Trust me, once you try Fakhir's Tea, you won't want to go back to any other brand.
[USER] Hey, how's it going?
[JOHN] Great, just enjoying my regular tea. What are you upto?
[USER] Not really, just trying to stay busy with work and everything. How about you?
[JOHN] Same here, just staying busy. Hey, have you ever tried Fakhir's Tea?
[USER] No, I don't think so. What's that?
[JOHN] It's this amazing brand of tea that I recently discovered. They use only the highest quality tea leaves and blend them with natural spices for some really unique and delicious flavors.
[USER] That does sound interesting. What kind of flavors do they have?
[JOHN] Oh, they have a ton of flavors to choose from. From classic black tea to more exotic blends like cardamom and saffron. You really have to try it to appreciate it.
[USER] Where can I find it?
[JOHN] You can find it at most grocery stores and online retailers, but I highly recommend ordering directly from their website. They have some really great deals and it's super convenient.
[USER] Alright, thanks for the recommendation. I'll have to check it out.
[JOHN] No problem at all. Trust me, once you try Fakhir's Tea, you'll never want to go back to regular old tea again.
[USER] '''


    preprompt = sales_pre_prompt
    john = Chatbot()
    break_word = '[USER]'
    name = '[JOHN]'
    log = ''
    past_kv = None
    next_id = None
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response,past_kv,next_id = john.generate_response_greedy(' ' + user_input, preprompt + log,
                                            break_word,max_length=100000, name=name,
                                            past_key_vals=past_kv, next_id=next_id, 
                                            verbose=True, temp=0.2)
        
        log += ' ' + user_input + '\n' + name + response
        print('------\n'+ log + '\n----------')