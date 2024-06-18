#!/usr/bin/env python3
import sys
import os
import zlib
from collections import deque

def topo_order_commits():
    branches = get_branches(get_path() + '/refs/heads')
    graph = build_graph(branches)
    topo_graph = topo_order(graph)
    topo_graph.reverse()
    ordered_print(branches, graph, topo_graph)
class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()
    
    def add_parent(self, parent_hash):
        self.parents.add(parent_hash)

    def add_child(self, child_hash):
        self.children.add(child_hash)

# Discover Git directory
# Determine where top level git directory is (containing .git)

def get_path():
    curr_dir = os.getcwd()
    while curr_dir != "":
        checkDir = os.path.join(curr_dir, ".git")
        if os.path.isdir(checkDir):
            return checkDir
        else:
            # Find index of last occurrence of / in string and then slice
            curr_dir = curr_dir[:curr_dir.rfind("/")]
    sys.stderr.write('Not inside a Git repository\n')
    exit(1)

# Returns dictionary w/hashkeys with list of branchnames associated with hash 
# Maps dictionary of commit hashes to branch names
# Keys: SHA-1 hash strings, Values: ./refs/heads/branch_name

def get_branches(path : str) -> list[(str, str)]:
    branches = {}
    for root, dirs, files in os.walk(path):
        for name in files:
            if os.path.isfile(os.path.join(root, name)):
                with open(os.path.join(root, name), 'r' ) as branch_file:
                    hash = branch_file.read().strip()
                if hash not in branches:
                    branches[hash] = [name]
                else:
                    branches[hash].append(name)
    return branches

def read_commit(commit_hash):
    # Locate git directory
    git_dir = get_path()
    # Get object path. Git stores objects in directory structure based on SHA-1 hash
    # First two characters form directory name, remaining form filename
    object_path = os.path.join(git_dir, 'objects', commit_hash[:2], commit_hash[2:])
    with open(object_path, 'rb') as f:
        compressed_data = f.read()
    decompressed_data = zlib.decompress(compressed_data)
    return decompressed_data.decode()

def parse_parents(commit_data):
    parents = []
    for line in commit_data.split('\n'):
        if line.startswith('parent'):
            parents.append(line.split()[1])
    return parents

def build_graph(branches):
    graph = {}
    visited = []
    hashes_to_process = []
    for i in branches:
        hashes_to_process.append(i)
    while len(hashes_to_process) != 0:
        curr_val = hashes_to_process.pop()
        if curr_val in visited:
            continue
        if curr_val not in graph:
            newNode = CommitNode(curr_val)
            graph[curr_val] = newNode
        parentHashes = parse_parents(read_commit(curr_val))
        for i in parentHashes:
            if i not in visited:
                hashes_to_process.append(i)
            if i not in graph:
                graph[i] = CommitNode(i)
            graph[i].children.add(curr_val)
            graph[curr_val].parents.add(i)
        visited.append(curr_val)
    return graph

def topo_order(graph):
    eList = []
    set2process=[]
    for i in graph:
        #if set of parents is empty
        if(len(graph[i].parents)==0):
            set2process.append(i)
    while len(set2process) != 0:
        #pop(0) pops the start of the list 
        currHash = set2process.pop(0)
        eList.append(currHash)
        for childHash in graph[currHash].children:
            #remove edges count parents
            #counting the matching parents
            matchPar = 0
            for parentHash in graph[childHash].parents:
                if parentHash in eList:
                    matchPar+= 1
            if matchPar == len(graph[childHash].parents):
                set2process.append(childHash)
    #at this pt set2process is empty
    return eList

def ordered_print(branches, graph, topo_eList):
    jumped = False
    #for currHash in topo_eList:
    for i in range(len(topo_eList)):
        currHash = topo_eList[i]
        if jumped:
            jumped = False
            print('=', end = '')
            print(" ".join(graph[currHash].children))
        print(currHash, end = '') 
        if(currHash in branches):
            for nameBranch in branches[currHash]:
                print(' ' + nameBranch, end = '')
        print('')
        if(i != len(topo_eList)-1): 
            if(topo_eList[i+1] not in graph[currHash].parents):
                print(" ".join(graph[currHash].parents), end = '')
                print("=\n")
                jumped = True
    
if __name__ == '__main__':
    topo_order_commits()
