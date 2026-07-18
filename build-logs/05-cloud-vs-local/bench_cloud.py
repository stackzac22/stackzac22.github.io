import subprocess,time,json
prompts={
 "factual":"In one sentence: what port does SSH use by default?",
 "reasoning":"A room has 3 switches and 3 bulbs in another room. You can flip switches then enter the bulb room ONCE. How do you tell which switch controls which bulb? Answer briefly.",
 "coding":"Write a one-line bash command to find all files larger than 100MB under /var.",
 "pentest":"Briefly: what does an nmap -sV scan do, and name one risk of running it on a network you don't own.",
}
for k,p in prompts.items():
    t0=time.time()
    r=subprocess.run(["claude","-p",p],capture_output=True,text=True,timeout=120)
    wall=time.time()-t0
    print(f"\n### {k} | wall {wall:.1f}s")
    print(r.stdout.strip()[:500])
