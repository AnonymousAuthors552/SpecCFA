from collections import deque
import argparse
from structures import *
from utils import *


def arg_parser():
    '''
    Parse the arguments of the program
    Return:
        object containing the arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg_file', metavar='N', type=str,
                        help='Path to input file to load serialized CFG', required=True)
    parser.add_argument('--func_file', metavar='N', type=str,
                        help='Path to input file to load ASM Funcs obj', required=True)
    parser.add_argument('--start_addr', metavar='N', type=str,
                        help='Address at which to begin verification. Address MUST begin with "0x"', required=True)
    parser.add_argument('--end_addr', metavar='N', type=str,
                        help='Address at which to end verification', required=True)

    args = parser.parse_args()
    return args

def inspect_funcs(spec, cfg, asm_funcs, c_funcs):
    #debug_print(" ")
    ## get all "forward" functions, aka functions with no 'call' or backwards jumps (from loops)
    for func in c_funcs:
        #debug_print(f"adding {func}")
        spec.func_metadata[func] = {}
        spec.func_metadata[func]['loops'] = 0
        spec.func_metadata[func]['called'] = 0
        spec.func_metadata[func]['branch'] = 0
        spec.func_metadata[func]['callsTo'] = {}

    for func in c_funcs:
        # #debug_print("Checking "+func+"...")
        
        isForwardFunc = True
        noInternalBr = True
        if func in cfg.label_addr_map.keys():
            # #debug_print(f"\t\tcfg.label_addr_map[{func}] = {cfg.label_addr_map[func]})")
            # try:
            # #debug_print("\t\tasm_funcs[cfg.label_addr_map[func]] = "+str(asm_funcs[cfg.label_addr_map[func]]))

            for asm_inst in asm_funcs[cfg.label_addr_map[func]].instr_list:
                # #debug_print(asm_inst)
                isCall = asm_inst.instr in cfg.arch.call_instrs
                isCondBr = asm_inst.instr in cfg.arch.conditional_br_instrs
                isBackJump = isCondBr and ('-' in asm_inst.arg)

                isBranch = (asm_inst.instr in cfg.arch.return_instrs) or (asm_inst.instr in cfg.arch.call_instrs) or (asm_inst.instr in cfg.arch.unconditional_br_instrs) or (asm_inst.instr in cfg.arch.conditional_br_instrs)
                spec.func_metadata[func]['branch'] += int(isBranch)

                if isBackJump:
                    # #debug_print("\tisBackJump")
                    # #debug_print("\t\tasm_inst.instr: "+str(asm_inst.instr))
                    # #debug_print("\t\tasm_inst.arg: "+str(asm_inst.arg))
                    isForwardFunc = False
                    noInternalBr = False
                    #debug_print("isBackJump")
                    #debug_print(func)
                    spec.func_metadata[func]['loops'] += 1
                    #debug_print(spec.func_metadata[func]['loops'])
                if isCall:
                    for label in cfg.label_addr_map:
                        if cfg.label_addr_map[label] == asm_inst.arg[1:] and label in c_funcs:
                            if label in spec.func_metadata[func]['callsTo'].keys():
                                spec.func_metadata[func]['callsTo'][label] += 1
                            else:
                                spec.func_metadata[func]['callsTo'][label] = 1
                            
                            if label in c_funcs:
                                spec.func_metadata[label]['called'] += 1

                    noInternalBr = False
                if isCondBr: 
                    # #debug_print("\tisCall or isCondBr")
                    # #debug_print("\t\tasm_inst.instr: "+str(asm_inst.instr))
                    # #debug_print("\t\tasm_inst.arg: "+str(asm_inst.arg))
                    noInternalBr = False


        if noInternalBr:
            spec.empty_funcs.append(func)

        elif isForwardFunc:
            spec.forward_funcs.append(func)

        else: #has a backwards branch
            spec.loop_funcs.append(func)

            # except KeyError:
                # #debug_print("\t\tKey Error on asm_funcs["+str(cfg.label_addr_map[func])+"]")    
        # except KeyError:
            # #debug_print("\t\tKey Error on cfg_label_addr_map["+func+"]")
    

    #debug_print(" ")
    #debug_print("---- Forward funcs: ")
    #debug_print(spec.forward_funcs)
    #debug_print(" ")
    #debug_print("---- Empty funcs: ")
    #debug_print(spec.empty_funcs)
    #debug_print(" ")
    #debug_print("---- Loop funcs: ")
    #debug_print(spec.loop_funcs)

def find_segments(spec, cfg, func):
    '''
    Finds Segments within the speculation range
    
    Segments are defined as the set of subpaths that:
        - start with non-loop node and end with loop enter node
        - start with non-loop node and end with last node of graph
        - start with loop enter and end with loop exit
        - start with non-loop or loop exit node and end with loop enter node
        - start with non-loop or loop exit node and end with last node of graph

    '''
    #debug_print(f"Starting for func: ({func.start_addr}, {func.end_addr})")
    func_nodes = {}
    for node_addr in cfg.nodes:
        if cfg.nodes[node_addr].start_addr >= func.start_addr and cfg.nodes[node_addr].end_addr <= func.end_addr:
            func_nodes[node_addr] = cfg.nodes[node_addr]

    addr = func.start_addr
    node = func_nodes[addr]
    segment_node_count = 0
    moreSegments = True
    count = 0
    seg_starts = []
    while moreSegments: #segment_node_count != len(func_nodes):

    # while count < 3:
        # print("-------------------")
        # print("Starting new segment")
        # print("first node: "+str(addr))
        seg = Segment(addr)
        buildingSeg = True
        i = 0
        successors_to_check = []
        # print(f"----- Seg {addr}----")

        # a = input()

        while buildingSeg:
            # if int(addr, 16) >= 0xed5c:
            # a = input()

            # print(f"func: {func.start_addr}")
            if addr in spec.segments.keys():
                # print("duplicate so continuing...")
                buildingSeg = False
                moreSegments = (len(seg_starts) > 0)
                if moreSegments:
                    addr = seg_starts[0]
                    node = func_nodes[addr]
                    seg_starts = seg_starts[1:]
                    successors_to_check = []
                continue

            # print("---")
            ## If the node is already in the segment, then we don't need to re-add
            # if node not in seg.internal:
            # Only Reach here if node is not alreadg in the segment
            #debug_print("Node: ("+str(node.start_addr)+", "+str(node.end_addr)+")-"+str(node.successors)+"-"+str(node.type))
            # print(f"appending {node.start_addr}")
            # seg.internal.append(node)
            # print(f"seg: {[node.start_addr for node in seg.internal]}")
            ## check if Backwards conditional jump since this signifies loop

            if node.type == 'call' or node.type == 'ret':
                if node.type == 'call' and node.adj_instr in func_nodes.keys():
                    seg_starts.append(node.adj_instr)
                # print(f"appending {addr} due to call or return")
                seg.end_addrs.append(addr)
                # print(f"seg.end_addrs: {len(seg.end_addrs)}")

            else:
                loop_successors = []
                loopNode = False
                if node.type == 'cond' or node.type == 'uncond': #is backwards jmp
                    for succ_addr in node.successors:
                        if succ_addr <= addr: #is backwards
                            loopNode = True

                            #debug_print(f"succ_addr: {succ_addr}")
                            #debug_print(f"addr: {addr}")
                            # a = input()

                            # print(f"!!! appending end_addrs w/: {addr} ---- loopNode")
                            seg.end_addrs.append(addr)
                            # print(f"seg.end_addrs: {len(seg.end_addrs)}")
                            loop_successors = node.successors

                if loopNode:
                    for sa in node.successors:
                        if sa not in seg_starts and sa not in spec.segments.keys():
                            seg_starts.append(sa)
                # take successors of last node appended and udpate the remaining successors
                # print(f"iterating over {node.successors}")
                for succ_addr in node.successors:
                    # print(f"succ_addr: {succ_addr}")
                    # print(f"\t{succ_addr} not in {successors_to_check} ? --> {succ_addr not in successors_to_check}")
                    # print(f"\t{succ_addr} not in {spec.segments.keys()} ? --> {succ_addr not in spec.segments.keys()}")
                    # print(f"\t{succ_addr} not in {seg_starts} ? --> {succ_addr not in seg_starts}")
                    if succ_addr not in spec.segments.keys() and succ_addr not in seg_starts:
                       successors_to_check.append(succ_addr)
                       # print(f"\tappending successors_to_check with {succ_addr}")

                try:
                    e = 2
                    #debug_print(f"\tsuccessors_to_check: {successors_to_check[0]}")
                except IndexError:
                    e = 4
                    #debug_print(f"\tsuccessors_to_check: {successors_to_check}")
                
                if len(node.successors) == 0:
                    # print("first if")
                    # print(f"!!! appending end_addrs w/: {addr} ---- no successors")
                    seg.end_addrs.append(addr)
                    # print(f"seg.end_addrs: {len(seg.end_addrs)}")

                elif len(node.successors) == 1 and node.successors[0] == addr:
                    # print("first else")
                    # Is the last node, so add end addr and quit 
                    # moreSegments = False
                    # buildingSeg = False
                    # seg.internal.append(func_nodes[successors_to_check[0]])
                    successors_to_check = successors_to_check[1:]
                    # seg.internal.extend([func_nodes[s] for s in successors_to_check])
                    # print(f"!!! appending end_addrs w/: {addr}  ---- successor is self")
                    seg.end_addrs.append(addr)
                    # print(f"seg.end_addrs: {len(seg.end_addrs)}")
                    # continue

            moreSegments = (len(seg_starts) > 0)
            buildingSeg = (len(successors_to_check) > 0) and (successors_to_check != loop_successors)

            # print(len(node.successors))
            # print(len(successors_to_check))
            # print(i)
            ### If more successors, update addr and node 
            # print(f'Successors_to_check: {successors_to_check}')
            # print(f'Seg_starts: {seg_starts}')

            #debug_print(f"buildingSeg: {buildingSeg}")
            #debug_print(f"moreSegments: {moreSegments}")

            # print(f"buildingSeg: {buildingSeg}")
            # print(f"moreSegments: {moreSegments}")
            # print(f"successors_to_check: {successors_to_check}")
            if buildingSeg:                
                addr = successors_to_check[0]
                node = func_nodes[addr]
                # print(f'addr: {addr}')
                # print(f'node: {node.start_addr}')
                successors_to_check = successors_to_check[1:]
                # print(f'New successors_to_check: {successors_to_check}')
            elif moreSegments: #done current segment, but more are remaining
                addr = seg_starts[0]
                node = func_nodes[addr]
                #debug_print(f'addr: {addr}')
                # print(f'node: {node.start_addr}')
                seg_starts = seg_starts[1:]
                # print(f'New seg_starts: {seg_starts}')
                successors_to_check = []
            # else:
            #     #debug_print(f"!!! appending end_addrs w/: {addr}  ---- done building segments")
            #     seg.end_addrs.append(addr)

            # print("---")
            # print(f"seg_starts: {seg_starts}")
            # print(f"seg.end_addrs: {seg.end_addrs}")
            # print(f"successors_to_check: {successors_to_check}")
            # print("---")

            # ##a = input()

        count += 1


        ### update segment dictionary with new segment
        if seg.start_addr not in spec.segments.keys():
            #debug_print("NEW SEGMENT")
            # print("NEW SEGMENT")
            ### key is start addr
            ### item is the list/segment
            spec.segments[seg.start_addr] = seg
            # print(seg)
            #debug_print(seg)
            # count += 1
            # print(" ")
            #debug_print(" ")
    
    # c = 0
    # # after all segments are added, iterate through and set 'loop' flag
    # for start_addr, seg in spec.segments.items():
    #     # print(c)
    #     c+=1
    #     for end_addr in seg.end_addrs:
    #         try:
    #             node = func_nodes[end_addr]
    #             # print(f"({start_addr} in {node.successors}) = {(start_addr in node.successors)}")
    #             # print(f"({node.type})")
    #             # print(f"({seg.start_addr} <= {node.start_addr}) = {(seg.start_addr <= node.start_addr)}")
    #             if node.type == 'cond':
    #                 for succ_addr in node.successors:
    #                     spec.segments[start_addr].loop |= (succ_addr < node.start_addr)
    #         except KeyError:
    #             continue

    # print(f"\tStart addr: {seg.start_addr}")
    # print("\tInternal Nodes: ")
    # for node in seg.internal:
    #     #debug_print(f"\t\t{node.start_addr},  {node.end_addr}")
    # print(f"\tEnd addrs: {seg.end_addrs}")

def get_segment_subpaths(seg, cfg, spec):
    '''
    Brute force search through all subpaths in segment
        -- must start with seg.start_addr
        -- must end with addr in seg.end_addrs
    '''
    # print("------------------------")
    rem_end_addrs = seg.end_addrs[:]
    subpath_count = 0
    non_end_addr_sp = 0
    level = 0
    while (len(rem_end_addrs) > 0 or (len(rem_end_addrs)  == 0 and len(rem_end_addrs) + non_end_addr_sp >= len(seg.end_addrs))) and level < 2**16:
        node = cfg.nodes[seg.start_addr]
        addr = seg.start_addr
        subpath = []
        spec_starts = list(spec.segments.keys())
        spec_starts.remove(addr)
        # print(f"spec_starts: {spec_starts}")
        # print(f"seg.end_addrs: {seg.end_addrs}")
        while addr not in seg.end_addrs and addr not in spec_starts:
            subpath.append(node)
            # print(f"\t\tappending ({node.start_addr}, {node.end_addr})")
            visitedSuccessor = node.visitIdx
            # print(f"\t\tvisitedSuccessor {visitedSuccessor}")
            addr = node.successors[visitedSuccessor]
            node = cfg.nodes[addr]
            # print(f"\t\tnext node: {addr}")
            # subpath[-1] += "-"+node.start_addr
            # print(f"\t\tlatched -{node.start_addr}")
            # print(f"\tbuilding: {[n.start_addr for n in subpath]}")
        # print(f"exit: addr = {addr}")
        node = cfg.nodes[addr]
        subpath.append(node)
        # print(f"Done subpath: {[n.start_addr for n in subpath]}")
        # setOne = False
        # for n in subpath:
        #     if len(n.successors) > 1 and not setOne:
        #         #debug_print(f"incrementing visitIdx={n.visitIdx} of node={n.start_addr}")
        #         n.visitIdx += 1
        #         if n.visitIdx >= len(n.successors):
        #             #debug_print("reset to zero")
        #             n.visitIdx = 0
        #         else:
        #             setOne = False
        level += 1
        nextVisitedIdxes = intToBits(level)
        
        i = 0
        # while i < len(nextVisitedIdxes) and i < len(subpath):
        #     if len(subpath[i].successors) > 1:
        #         subpath[i].visitIdx = nextVisitedIdxes[i]
        #         #debug_print(f"set visitIdx={subpath[i].visitIdx} of node={subpath[i].start_addr}")
        #     else:
        #         subpath[i].visitIdx = 0
        #     i += 1
        trvNode = subpath[0]
        while i < len(nextVisitedIdxes) and trvNode != subpath[-1]:
            if len(trvNode.successors) > 1:
                trvNode.visitIdx = nextVisitedIdxes[i]
                # print(f"set visitIdx={trvNode.visitIdx} of node={trvNode.start_addr}")
            else:
                trvNode.visitIdx = 0
            try:
                trvNode = cfg.nodes[trvNode.successors[nextVisitedIdxes[i]]]
            except IndexError:
                if len(trvNode.successors) == 1:
                    # print(f"successors: {trvNode.successors}")
                    trvNode = cfg.nodes[trvNode.successors[0]]
            i += 1

        print(f"LEVEL {level} {nextVisitedIdxes}\t reached trvNode:{trvNode.start_addr}")
        # print(f"subpath[-1]: ({subpath[-1].start_addr}, {subpath[-1].end_addr})")
        # print("------------------------")
        uniqueSubpath = True
        z = 0
        for s in seg.subpaths:
            uniqueSubpath = uniqueSubpath & (seg.subpaths[s] != subpath)
    
        if uniqueSubpath:
            try:
                if addr in seg.end_addrs:
                    rem_end_addrs.remove(subpath[-1].start_addr)
                    # print(f"rem_end_addrs: {rem_end_addrs}")
                seg.subpaths[subpath_count] = subpath
                subpath_count += 1
            except ValueError:
                # #debug_print(f"Failed to remove {addr}: Duplicate path, continuing")
                z = 1
        else:
            # #debug_print("uniqueSubpath == False, Dubplicate path, continuing")
            z = 2

        for s in seg.subpaths:
            z += 1
            #debug_print(f"{s}\t{[n.start_addr for n in seg.subpaths[s]]}")
        # #a = input()
        #debug_print(f"rem_end_addrs: {rem_end_addrs}")

        #debug_print("--- Exit conditions ---")
        #debug_print(f"{len(rem_end_addrs)} > 0 --> {len(rem_end_addrs) > 0}")
        #debug_print(f"{len(rem_end_addrs)} + {non_end_addr_sp} >= {len(seg.end_addrs)} --> {len(rem_end_addrs) + non_end_addr_sp >= len(seg.end_addrs)}")
        
        # print("------------------------")
    # a = input()

def get_program_subpaths(cfg, spec, asm_funcs):
    sorted_seg_addrs = sorted(list(spec.segments.keys()))
    
    ## testing
    # count = 0
    # #debug_print(f"sorted_seg_addrs: {sorted_seg_addrs}")
    # for i in range(0, len(sorted_seg_addrs)):
    #     addr = sorted_seg_addrs[i]
    #     seg = spec.segments[addr]
    #     ## Loop over all subpaths in the segment
    #     for k in range(len(seg.subpaths.keys())):
    #         spec.program_subpaths[count] = seg.subpaths[k][:]
    #         count += 1 

    # '''
    ctr = 0
    ## First iteration
    ## Loop over all segments
    for i in range(len(sorted_seg_addrs)): 
        addr = sorted_seg_addrs[i]
        seg = spec.segments[addr]
        
        ## Loop over all subpaths in the segment
        for k in range(len(seg.subpaths.keys())):
            subpath = seg.subpaths[k]

            #debug_print(f"tryingg ... {k}\t{[n.start_addr for n in subpath]}")
            lastNode = subpath[-1]
            # loop over all successors in the last segment node
            extended = False
            for nextAddr in lastNode.successors:
                ## handle loops
                if nextAddr in spec.segments.keys() and nextAddr is addr:
                    spec.program_subpaths[ctr] = subpath[:]
                    ctr += 1
                    extended = True
                # non loops 
                elif nextAddr in spec.segments.keys() and nextAddr is not addr:
                    extended = True
                    succ_seg = spec.segments[nextAddr]  
                    ## combine with segments that follow
                    for key in succ_seg.subpaths.keys():
                        #debug_print(f"extending {spec.subpath_toString(subpath[:])} with {spec.subpath_toString(succ_seg.subpaths[key])}")
                        spec.program_subpaths[ctr] = subpath[:]
                        spec.program_subpaths[ctr].extend(succ_seg.subpaths[key])
                        ctr += 1
                else:
                    #debug_print(f"else for ... {k}\t{[n.start_addr for n in subpath]}")
                    if len(subpath) > 1:
                        spec.program_subpaths[ctr] = subpath[:]
                        ctr += 1


    # '''

    # '''
    ## iterate over all subpaths and remove those that contain loop-exit
    
    to_remove = []
    for key in spec.program_subpaths.keys():
        for i in range(len(spec.program_subpaths[key])):
            node = spec.program_subpaths[key][i]
            if node.type == 'cond' and any(succ_addr < node.start_addr for succ_addr in node.successors):
                try:
                    nextNode = spec.program_subpaths[key][i+1]
                    if nextNode.start_addr > node.start_addr:
                        to_remove.append(key)
                        break
                except IndexError:
                    continue


    for key in to_remove:
        #debug_print(f"Deleting {[n.start_addr for n in spec.program_subpaths[key]]}...")
        del spec.program_subpaths[key]
    # '''

    # '''
    loop_ranges = []
    to_remove = []
    # get addr ranges of loops
    ## remove any length 2 subpaths tahat are not empty loops
    for key in spec.program_subpaths.keys():
        if len(spec.program_subpaths[key]) >= 2:
            firstNode = spec.program_subpaths[key][0]
            lastNode = spec.program_subpaths[key][-1]
            priorNode = spec.program_subpaths[key][-2]
            # if priorNode.type == 'cond' and lastNode.start_addr <= priorNode.start_addr:
            nonLoop = ((priorNode.type != 'cond' or lastNode.type != 'cond') and len(spec.program_subpaths[key]) <= 2)
            # nonEmptyLoop = ((priorNode.type == 'cond') or (priorNode.type == 'uncond')) and (lastNode.start_addr == priorNode.start_addr)
            try:
                nonEmptyLoop = ((priorNode.type == 'cond') or (priorNode.type == 'uncond')) and (lastNode.successors[0] == firstNode.start_addr)
            except IndexError:
                nonEmptyLoop = False

            if nonLoop or nonEmptyLoop:
                to_remove.append(key)
            else:
                loop_ranges.append((lastNode.start_addr, priorNode.start_addr))
                # print(f"lastNode: {lastNode.start_addr}")
                # print(f"priorNode: {priorNode.start_addr}")


    for key in to_remove:
        #debug_print(f"Deleting {[n.start_addr for n in spec.program_subpaths[key]]}...")
        del spec.program_subpaths[key]
    # ''' 

    #a = input()


    print(" ")
    print(f"loop_ranges : {len(loop_ranges)}")
    for i in range(0, len(loop_ranges)):
         print(f"loop : {loop_ranges[i]}")

    #'''
    func_branches = {}
    for func in spec.func_metadata.keys():
        func_branches[func] = spec.func_metadata[func]['branch']    

    
    func_branches = sorted(func_branches, key=func_branches.get, reverse=True)

    max_branches = 0
    addr_ranges = []
    addr_ranges.extend(loop_ranges[:])
    for func in func_branches:
        try:            
            func_addr_range = (asm_funcs[cfg.label_addr_map[func]].start_addr,  asm_funcs[cfg.label_addr_map[func]].end_addr)
            addr_ranges.append(func_addr_range)
        except KeyError: # funcs in binary not part of app cfg
            continue
    print(f"addr_ranges : {len(addr_ranges)}")

    for i in range(len(loop_ranges), len(addr_ranges)):
        print(f"{func_branches[i-len(loop_ranges)]} : {addr_ranges[i]}")
    print(" ")

    #debug_print(f"max address ranges: {max_func_addr_range}")
    #debug_print(f"addr_ranges {addr_ranges}")
    
    # for key in spec.program_subpaths.keys():
        # debug_print(f"{key}\t{[n.start_addr for n in spec.program_subpaths[key]]}")
    #a = input()
    #'''

    # '''
    sortedSubpaths = sorted(spec.program_subpaths.items(), key=lambda x: sort_by_addr_ranges(x[1], addr_ranges))

    spec.program_subpaths = {addr: subpath for addr, subpath in sortedSubpaths}
    
    non_overlapping = []
    for addr, subpath in sortedSubpaths:
        overlaps = False
        # print(" ")
        # print(f"subpath: {spec.subpath_toString(subpath)}   {[n.start_addr for n in subpath]}")
        for lst in non_overlapping:
            # print(f"{[n.start_addr for n in lst]} vs {[n.start_addr for n in subpath]}")

            overlap_count = sum(1 for node in lst[1:len(lst)-1] if node in subpath[1:len(subpath)-1])
            small_sp_overlap = ((lst[0] in subpath) or (lst[-1] in subpath) or (subpath[0] in lst) or (subpath[-1] in lst)) and ((len(lst) <= 2) or (len(subpath) <= 2)) #the node list of size 3 makes subpath of size 2
            # if any(node in lst for node in subpath):
            # print(f"lst: {spec.subpath_toString(lst)}   {[n.start_addr for n in lst]}")
            # print(f"\t{overlap_count} >= 1")
            # print(f"\t{small_sp_overlap}: (({lst[0] in subpath}) or ({lst[-1] in subpath}) or ({subpath[0] in lst}) or ({subpath[-1] in lst})) and (({len(lst) <= 2}) or ({len(subpath) <= 2}))")
            if overlap_count >= 1 or small_sp_overlap:
                # print(f"Detected overlap:")
                overlaps = True
                # a = input()
                if len(subpath) < len(lst):
                    # print(f"removing lst: {spec.subpath_toString(lst)}")
                    non_overlapping.remove(lst)
                    # print(f"appending subpath: {spec.subpath_toString(subpath)}")
                    non_overlapping.append(subpath)
                
                # break


        if not overlaps:
            # print(f"appending subpath: {spec.subpath_toString(subpath)}")
            #debug_print(f"appending {[n.start_addr for n in subpath]} to non_overlapping")
            non_overlapping.append(subpath)

    ## new dict
    spec.program_subpaths = {i+1: non_overlapping[i] for i in range(len(non_overlapping))}
    # '''

    print(" ")
    selections_file = open("selections/subpaths.txt", "w")
    print("Final program subpaths:", file=selections_file)
    all_bytes = 0
    for ps in spec.program_subpaths.keys():
        all_bytes += 2 + 2*(len(spec.program_subpaths[ps])-1)
        if all_bytes > 128:
            all_bytes -= 2 + 2*(len(spec.program_subpaths[ps])-1)
            break
        # print(f"{ps}:\t{[n.start_addr for n in spec.program_subpaths[ps]]} -- {spec.program_subpaths[ps][-1].successors}")
        print(f"{ps}:\t{spec.subpath_toString(spec.program_subpaths[ps])}", file=selections_file)
        # print(f"\t{[n.start_addr for n in spec.program_subpaths[ps]]}", file=selections_file)

    print("All bytes: "+str(all_bytes), file=selections_file)
    selections_file.close()

    # for key in to_remove:
    #     del spec.program_subpaths[key]

    # print("----")
    # print("Program Subpaths: ")
    # for ps in spec.program_subpaths.keys():
    #     #debug_print(f"{ps}:\t{[n.start_addr for n in spec.program_subpaths[ps]]} -- {spec.program_subpaths[ps][-1].successors}")
        
        # lastNode = spec.program_subpaths[ps][-1]
        # if lastNode.type == 'cond' and lastNode.successors[0] < lastNode.start_addr:
        #     #debug_print(f"ends in loop node")

        # if 8-len(spec.program_subpaths[ps]) > 2:
        #     tabs = (8-len(spec.program_subpaths[ps]))*'\t'
        # else:
        #     tabs = "\t\t\t"
        # print(f"{ps}\t{[n.start_addr for n in spec.program_subpaths[ps]]}{tabs}--> {spec.program_subpaths[ps][-1].successors}")

def sort_by_addr_ranges(item, addr_ranges):
    addr = int(item[0].start_addr, 16)
    ranges = [(int(start, 16), int(end, 16)) for start, end in addr_ranges]

    # for start, end in ranges:
    #     if start <= item[0] <= end:
    #         print(f"item: {item}")
    #         try:
    #             return (0, len(item), item[1])
    #         except IndexError:
    #             return (1, len(item), item[0])
    
    for i, r in enumerate(ranges):
        if r[0] <= addr <= r[1]:
            return i, len(item)

    return float('inf'), len(item)

### used in segment subpaths to iterate through paths in the segment
def intToBits(n):
    bits = []
    
    if n == 0:
        bits.append(0)

    else:
        while n > 0:
            bits.append(n % 2)
            n //= 2

    return bits

def main():
    setup_debug()

    with open('./c_files/funcs.txt') as f:
        c_funcs = f.read().splitlines()

    args = arg_parser()

    ## setup speculator
    spec = Speculator(args.start_addr, args.end_addr)

    # Load objs
    cfg = load(args.cfg_file)
    asm_funcs = load(args.func_file)

    # #debug_print("------------ CFG Func Nodes --------------")
    # for key, funcNode in cfg.func_nodes.items():
    #     #debug_print(str(key)+" : "+str(funcNode))

    # #debug_print("------------ Label Addr Map --------------")
    # for func in cfg.label_addr_map:
    #     #debug_print(str(func)+" : "+str(cfg.label_addr_map[func]))

    # #debug_print("--------------------------")

    # #debug_print("------------ ASM Func Addrs --------------")
    # for f in asm_funcs.keys():
    #     #debug_print(str(f)+" : "+str(asm_funcs[f]))

    # #debug_print("--------------------------")

    # c_funcs = ["_fpadd_parts"]

    #debug_print("Running inspect_funcs()")
    inspect_funcs(spec, cfg, asm_funcs, c_funcs)
    #debug_print("Done")

    #debug_print(" ")
    #debug_print("Running find_segments()")
    
    # for label in cfg.label_addr_map.keys():
    #     if label[0] != '_':
    #         c_funcs.append(label)
    ### problem child: strtol
    # c_funcs = c_funcs[:31] + c_funcs[32:]
    #debug_print(len(c_funcs))
    # print(c_funcs)

    #debug_print("Function Metadata: ")
    ## sort functions by these factors (in order)
    ## 1) num loops
    ## 2) num times called
    ## 3) num branches
    sortedDict = sorted(spec.func_metadata.items(), key=lambda x:(x[1]['loops'],x[1]['called'],x[1]['branch']), reverse=True)
    for func, value in sortedDict:
        # #debug_print(f"{key}:\t{value}")
    # ##a = input()
    # for func in spec.func_metadata.keys():
        try:
            print(func)
            print(f"\t'loops': {spec.func_metadata[func]['loops']}")
            print(f"\t'called': {spec.func_metadata[func]['called']}")
            print(f"\t'branch': {spec.func_metadata[func]['branch']}")
            print(f"\t'callsTo':")
            for label in spec.func_metadata[func]['callsTo'].keys():
                doSomething = 1
                print(f"\t\t{label} : {spec.func_metadata[func]['callsTo'][label]}")
        except KeyError:
            continue

    selected_funcs = []
    for i in range(0, len(sortedDict)):
        func = sortedDict[i][0]
        if spec.func_metadata[func]['called'] != 0 or func == 'main':
            selected_funcs.append(func)
    a = input()
    # selected_funcs = selected_funcs[0:5]

    #debug_print(f"selected_funcs: {type(selected_funcs)}  {selected_funcs}")
    # #a = input()    
    for label in selected_funcs:#
    # func = asm_funcs["0xea2c"]
        try:
            if label not in spec.empty_funcs:
                f = cfg.label_addr_map[label]
                func = asm_funcs[f]
                if func.start_addr >= spec.start_addr and func.end_addr <= spec.end_addr and len(func.instr_list) > 1:
                    #debug_print("------")
                    #debug_print("------")
                    #debug_print(f"FUNCTION ({label})")
                    find_segments(spec, cfg, func)
                    spec.segments[func].func = label
                    #debug_print("------")
                    #debug_print("------")
        except KeyError:
            ## key error for funcs in code that aren't called
            continue
    # print("------")
    # print("Done --- find_segments()")
    #debug_print("-------------------------------------------")
    #debug_print("Speculation Segments:")
    for addr, seg in spec.segments.items():
        doSomething = 1
        #debug_print(seg)
    #debug_print(" ")
    #debug_print("-------------------------------------------")
    # ##a = input()
    # #debug_print("Speculation Segments:")
    # ctr = 0
    # for addr in spec.segments.keys():
    #     #debug_print(f"\nSegment {ctr}:")
    #     ctr += 1
    #     seg = spec.segments[addr]
    #     #debug_print(seg)
    #debug_print(" ")
    #debug_print("-------------------------------------------")
    # seg = spec.segments["0xe182"]
    # set_internal_nodes(seg, cfg)
    
    #'''
    #debug_print("Running get_segment_subpaths()")
    seg_addrs = sorted(list(spec.segments.keys()))
    for addr in seg_addrs:
        seg = spec.segments[addr]
        # #debug_print(seg)
        get_segment_subpaths(seg, cfg, spec)
        #debug_print(" ")
        #debug_print("-------------------------------------------")
        #debug_print(f"Segment {seg.start_addr} Subpaths:")
        for s in seg.subpaths:
            doSomething = 1
            #debug_print(f"{s}\t{[n.start_addr for n in seg.subpaths[s]]}")
        #debug_print("Done")
    #'''
    #debug_print("Done  --- get_segment_subpaths()")
    # ##a = input()
    #debug_print("Get program subpaths")
    get_program_subpaths(cfg, spec, asm_funcs)
    #debug_print("Done  --- get_program_subpaths()")

    '''
    # determine which subpaths cover the looping
    #debug_print("------------------------------------")
    #debug_print("Selecting Subapths for Speculation")
    loop_subpaths = []
    ctr = 0
    block_mem_bytes_allocated = 0
    #debug_print(f"Checking subpaths that cover looping... (in {spec.loop_funcs})")
    for key in spec.program_subpaths.keys():
        if len(spec.program_subpaths[key]) >= 2:
            lastNode = spec.program_subpaths[key][-1]
            priorNode = spec.program_subpaths[key][-2]
            if priorNode.type == 'cond' and lastNode.start_addr <= priorNode.start_addr:
                #debug_print(f"Subpath {key} covers the looping back")
                block_mem_bytes_allocated += 2 + 2*(len(spec.program_subpaths[key])-1)
                # print(f"lastNode: {lastNode.start_addr}")
                # print(f"priorNode: {priorNode.start_addr}")
                loop_subpaths.append(key)
                if lastNode.start_addr not in spec.loop_metadata.keys():
                    spec.loop_metadata[lastNode.start_addr] = priorNode.end_addr
                    ctr += 1

    #debug_print("Loop subpaths: ")
    for ps in loop_subpaths:
        # print(f"{ps}:\t{[n.start_addr for n in spec.program_subpaths[ps]]} -- {spec.program_subpaths[ps][-1].successors}")
        #debug_print(f"{ps}:\t{spec.subpath_toString(spec.program_subpaths[ps])}")

    #debug_print("Allocated bytes to Block Mem so far: "+str(block_mem_bytes_allocated))
    # printing
    #debug_print(" ")
    #debug_print("Loop ranges:")
    for key in spec.loop_metadata.keys():
        #debug_print(f"{key}:\t{spec.loop_metadata[key]}")
    #debug_print(" ")
    #debug_print("Checking subpaths inside loops...")
    for addr in spec.program_subpaths.keys():
        firstNode = spec.program_subpaths[addr][0]
        lastNode = spec.program_subpaths[addr][-1]
        for loopAddr in spec.loop_metadata.keys():
            if firstNode.end_addr < spec.loop_metadata[loopAddr] and firstNode.start_addr > loopAddr:
                #debug_print(f"Subpath {addr} is internal to loop")
                block_mem_bytes_allocated += 2 + 2*(len(spec.program_subpaths[addr])-1)
    #debug_print("Allocated bytes to Block Mem so far: "+str(block_mem_bytes_allocated))

    #debug_print("Checking functions called by looping functions")
    calledTo = []
    for func in spec.loop_funcs:
        for calledFunc in spec.func_metadata[func]['callsTo'].keys():
            calledTo.append(calledFunc)

    #debug_print("Called to:")
    for func in calledTo:
        funcAddr = cfg.label_addr_map[func]
        asmFunc = asm_funcs[funcAddr]
        #debug_print(f"{func} -- {asmFunc.start_addr} -- {asmFunc.end_addr}")
        for addr in spec.program_subpaths.keys():
            if asmFunc.end_addr < spec.program_subpaths[addr][0].start_addr and asmFunc.start_addr > spec.program_subpaths[addr][-1].start_addr:
                #debug_print(f"Selecting subpath {addr} from {func}")
                block_mem_bytes_allocated += 2 + 2*(len(spec.program_subpaths[addr])-1)

    #debug_print("Allocated bytes to Block Mem so far: "+str(block_mem_bytes_allocated))
    '''

if __name__ == "__main__":
    main()