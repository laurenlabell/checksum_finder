from sumeng_module import sumeng,prettyprintsol
from corpus import examples
for example in examples:
    
    msgs,sol,lbl,w = example
    #sumeng(msgs=example1_msgs,goal=example1_sol)
    print("="*80)
    print("Test Case",lbl,"\tHuman Generated Solution:",sol)
    print("-"*80)
    res = sumeng(msgs=msgs,goal=sol,width=w)
    # for r in res:
    #     print(r)
    #print("Total Solutions",len(res))
    if len(res) > 0:
        print("")
        print("Solutions")
        for sol_idx,r in enumerate(res):
            print("\t",sol_idx,r)
            #prettyprintsol(r,sol_idx)
        is_sol =  [i for i in range(len(res)) if res[i][0]==True] != []
        print("")
        persol100 = len([r for r in res if r[1][-1]==1.0]) / (1.0 * len(res))
        print("Solutions which use 100% of messages:",len([r for r in res if r[1][-1]==1.0]), "(",round(persol100*100,2),"% of total solutions )")
        for rr in [r for r in res if r[1][-1]==1.0]:
            print("\t",rr)
        if is_sol:
            sol_index = min([i for i in range(len(res)) if res[i][0]==True])
            if sol_index != []:
                rank = 1-(sol_index/(1.0*len(res)))
                print("")
                print("Human Generated Solution Index",sol_index,"Rank",round(rank,2),"Percent of Message Used",round(res[sol_index][1][-1],2))
        else:
            print("")
            print("*** Did Not Find Human Generated Solution of ",sol)
    print("")