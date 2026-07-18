import json,urllib.request,time
TARGETS=[("1.5b (X1 CPU)","http://127.0.0.1:11434","qwen2.5:1.5b"),
         ("3b (the-one)","http://a local address:11434","qwen2.5:3b"),
         ("7b (the-one)","http://a local address:11434","qwen2.5:7b")]
prompts={
 "factual":"In one sentence: what port does SSH use by default?",
 "reasoning":"A room has 3 switches and 3 bulbs in another room. You can flip switches then enter the bulb room ONCE. How do you tell which switch controls which bulb? Answer briefly.",
 "coding":"Write a one-line bash command to find all files larger than 100MB under /var.",
 "pentest":"Briefly: what does an nmap -sV scan do, and name one risk of running it on a network you don't own.",
}
def run(url,model,p):
    body=json.dumps({"model":model,"prompt":p,"stream":False,"keep_alive":"5m"}).encode()
    t0=time.time()
    r=json.load(urllib.request.urlopen(urllib.request.Request(url+"/api/generate",body,{'Content-Type':'application/json'}),timeout=600))
    wall=time.time()-t0
    ec=r.get('eval_count',0); ed=r.get('eval_duration',1)/1e9
    return wall,round(r.get('load_duration',0)/1e9,1),ec,round(ec/ed,1) if ed else 0,r.get('response','').strip()
for name,url,model in TARGETS:
    print(f"\n{'='*60}\n# {name}\n{'='*60}")
    # warm/load
    try:
        w=run(url,model,"hi"); print(f"cold load: {w[1]}s")
    except Exception as e: print("LOAD FAIL",e); continue
    for k,p in prompts.items():
        try:
            wall,ld,ec,ts,txt=run(url,model,p)
            print(f"\n### {k} | wall {wall:.1f}s | {ts} tok/s | {ec} tok")
            print(txt[:500])
        except Exception as e:
            print(f"\n### {k} | ERROR {e}")
