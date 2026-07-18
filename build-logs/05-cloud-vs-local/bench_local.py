import json,urllib.request,time
URL="http://127.0.0.1:11434/api/generate"
prompts={
 "factual":"In one sentence: what port does SSH use by default?",
 "reasoning":"A room has 3 switches and 3 bulbs in another room. You can flip switches then enter the bulb room ONCE. How do you tell which switch controls which bulb? Answer briefly.",
 "coding":"Write a one-line bash command to find all files larger than 100MB under /var.",
 "pentest":"Briefly: what does an nmap -sV scan do, and name one risk of running it on a network you don't own.",
}
def run(p):
    body=json.dumps({"model":"qwen2.5:1.5b","prompt":p,"stream":False}).encode()
    t0=time.time()
    r=json.load(urllib.request.urlopen(urllib.request.Request(URL,body,{'Content-Type':'application/json'}),timeout=300))
    wall=time.time()-t0
    ec=r.get('eval_count',0); ed=r.get('eval_duration',1)/1e9
    return {"wall":round(wall,1),"load_s":round(r.get('load_duration',0)/1e9,1),
            "pe_s":round(r.get('prompt_eval_duration',0)/1e9,1),
            "out_tok":ec,"tok_s":round(ec/ed,1) if ed else 0,"text":r.get('response','').strip()}
print("== warming (cold load) ==")
w=run("hi"); print("cold load:",w['load_s'],"s  wall",w['wall'],"s")
for k,p in prompts.items():
    r=run(p)
    print(f"\n### {k}  | wall {r['wall']}s  load {r['load_s']}s  gen {r['tok_s']} tok/s  ({r['out_tok']} tok)")
    print(r['text'][:600])
