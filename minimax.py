import argparse

class Node:
    def __init__(self, name = "", val = None, ismax = True, par = None) -> None:
        self.name = name
        self.value = val
        self.parent = par
        self.children = []
        self.ismax = ismax
    def __repr__(self) -> str:
        return self.name
    def setParent(self, par) -> None:
        self.parent = par
    def setChildren(self, children) -> None:
        self.children = children

 
# Instantiate the parser
def parseArguments() -> tuple[bool, str, bool, bool, int]:
    parser = argparse.ArgumentParser(description ='Search some files')

    # python minimax.py [-v] [-ab] -range n min/max graph-file
    parser.add_argument('minormax')
    parser.add_argument(dest ='filenames', metavar ='filename', nargs ='*')

    parser.add_argument('-v', dest ='verbose', action ='store_true', help ='verbose mode')
    parser.add_argument('-ab', dest ='alpha_beta_pruning', action ='store_true', help ='alpha-beta mode')
    parser.add_argument('-range', dest ='range', action ='store', help ='range variable')
    args = parser.parse_args()
    
    if args.minormax == 'max':
        rootIsMaxPlayer = True
    elif args.minormax == 'min':
        rootIsMaxPlayer = False
    else:
        raise TypeError("Command Line Error: Did not use min or max in the correct position")
    
    return rootIsMaxPlayer, args.filenames[0], args.verbose, args.alpha_beta_pruning, int(args.range)

def parseGraphFile(filename: str) -> tuple[dict, set]:
    leaf: dict[str, int] = dict()
    nodes: str = []
    nodeSet: set[str] = set()
    nodeDict: dict[str, list[str]] = dict()
    file = open(filename, "r")
    while True:
        line = file.readline()
        if not line:
            break
        elif line[0] == '#':
            continue
        elif '=' in line:
            temp = line.split('=')
            key, val = temp[0].strip(), temp[1].strip()
            leaf[key] = int(val)
        elif ':' in line:
            nodes.append(line)
        else:
            continue
    file.close()
    internalNodeList: list[str] = []
    for node in nodes:
        nodeList = node.split(':')
        parent: str = nodeList[0].strip()
        firstBracket = nodeList[1].find('[')
        secondBracket = nodeList[1].rfind(']')
        if firstBracket == -1 or secondBracket == -1:
            raise IndexError("Did not find both sets of bracket []")
        children = nodeList[1][firstBracket + 1 : secondBracket].split(',')
        children = [s.strip() for s in children]
        nodeSet.add(parent)
        nodeSet.update(children)
        nodeDict[parent] = children

        internalNodeList.append(parent)
    return leaf,nodeSet, nodeDict, internalNodeList

def nonLeafNodes(leaf: dict, nodeSet: set) -> set[str]:
    nonLeafNodeSet = set()
    for name in nodeSet:
        if name not in leaf:
            nonLeafNodeSet.add(name)
    return nonLeafNodeSet

    # print(float('inf'), '\n', float('-inf'))
    # import math
    # math.isinf(a) # check if a is pos or neg inf

def initTree(leaf: dict[str,int], nodeSet: set[str], nodeDict: dict[str, list[str]]) ->\
    tuple[dict, dict, dict, dict]:
    # nodeclassSet = set() # keep track of already created node
    classNodeDict: dict[Node, list[Node | int]] = dict() # convert node dict to node class dict
    nodeNameToObj: dict[str, Node | int] = dict() # name: Node() | int

    classNodeDictNoInt: dict[Node, list[Node]] = dict()
    nodeNameToObjNoInt: dict[str, Node] = dict()

    for name in nodeSet:
        nodeObj = Node(name=name)
        nodeNameToObjNoInt[name] = nodeObj  # V: without leaf Node converted into int
        if name not in leaf:
            nodeNameToObj[name] = nodeObj
        else:
            nodeNameToObj[name] = leaf[name]
    
    for parentName in nodeDict:
        parentObj = nodeNameToObj[parentName]
        parentObjNoInt = nodeNameToObjNoInt[parentName] # V: without leaf Node converted into int

        # connect parent - children
        children: list[Node | int] = []
        childrenNoInt: list[Node] = []  # V: without leaf Node converted into int
        for childName in nodeDict[parentName]:
            childrenNoInt.append(nodeNameToObjNoInt[childName]) # V: without leaf Node converted into int
            if childName in leaf:
                children.append(leaf[childName])
            else:
                childObj = nodeNameToObj[childName]
                childObj.setParent(parentObj)
                children.append(childObj)
        parentObj.setChildren(children)
        # update the dict[parentNode : list[childNodes]]
        classNodeDict[parentObj] = children
        classNodeDictNoInt[parentObjNoInt] = childrenNoInt # V: without leaf Node converted into int

    return nodeNameToObj, classNodeDict, nodeNameToObjNoInt, classNodeDictNoInt

# def checkError(classNodeDict: dict[Node, list[Node | int]], nodeDict: dict[str, list[str]], leaf: dict[str, int]) -> str:
def checkError(classNodeDict: dict[Node, list[Node , int]], nodeDict: dict[str, list[str]], leaf: dict[str, int]) -> str:
    # Output 4: missing leafs
    # if it's not a leaf(int) and not an internal node
    # Output 5: copy nodeDict
    # look at all the name of all child Node. 
    #   If all non-Leaf child are in nodeDict.keys(), it is true
    #   If some keys are missing, Output 5 error - missing internal node
    # Output 6: choose 1 node, look at which parent nodes are missing from the nodeDict.values (children)
    # if there is only 1 parent node missing from children, then OK
    # if there are >= 2 parent missing from the values, the Output 6 error - multiple roots
    # example2: parents with the same children are fine. No error. Valid DAG
    allChildNodes = set()
    for key in classNodeDict.keys():
        children = classNodeDict[key]
        allChildNodes.update(children)
        
        for child in children:
            if type(child) == int: # leaf node
                continue
            elif repr(child) not in nodeDict: # if the non Leaf child node is not a parent
                # output 4 and 5. Missing leaf or missing internal node
                error = 'child node "' + repr(child) + '" of "' + repr(key) + '" not found'
                raise ValueError(error)
    
    countRootKey = []
    for key in classNodeDict.keys():
        if key not in allChildNodes:
            countRootKey.append(key)
    if len(countRootKey) > 1:
        # output 6: no root node, multiple nodes are without parent
        error = 'multiple roots: ' + str(countRootKey)
        raise ValueError(error)
    
    return countRootKey[0]  # root node

# def minimax(root: Node, isMaxPlayer: bool, rangeNum: int, nodeDict: dict[str, list[str]], 
#             classNodeDict: dict[Node, list[Node | int]]) -> int:
def minimax(root: Node, isMaxPlayer: bool, rangeNum: int, nodeDict: dict[str, list[str]], 
            classNodeDict: dict[Node, list[Node , int]]) -> int:
    if isMaxPlayer:
        res = -rangeNum
        for child in classNodeDict[root]:
            # base case: leaf node
            if type(child) == int:
                res = max(res, child)
            else:
                # keep going down
                res = max(res, minimax(child, not isMaxPlayer, rangeNum, nodeDict, classNodeDict))
        
        return res
    else:
        res = rangeNum
        for child in classNodeDict[root]:
            # base case: leaf node
            if type(child) == int:
                res = min(res, child)
            else:
                # keep going down
                res = min(res, minimax(child, not isMaxPlayer, rangeNum, nodeDict, classNodeDict))

        return res

# def minimaxab(root: Node, isMaxPlayer: bool, rangeNum: int, nodeDict: dict[str, list[str]], 
#             classNodeDict: dict[Node, list[Node | int]], alpha: int, beta: int) -> int:
def minimaxab(root: Node, isMaxPlayer: bool, rangeNum: int, nodeDict: dict[str, list[str]], 
            classNodeDict: dict[Node, list[Node , int]], alpha: int, beta: int) -> int:
    # alpha = MIN: best choice along path to root for MAXimizer player
    # beta = MAX: best choice along path to root for MINimizer
    if isMaxPlayer:
        res = -rangeNum
        for child in classNodeDict[root]:
            if type(child) == int:
                val = child
            else:
                val = minimaxab(child, not isMaxPlayer, rangeNum, nodeDict, classNodeDict, alpha, beta)
            res = max(res, val)

            # alpha pruning
            alpha = max(alpha, res)
            if beta <= alpha:
                break
        
        return res

    else:
        res = rangeNum
        for child in classNodeDict[root]:
            if type(child) == int:
                val = child
            else:
                val = minimaxab(child, not isMaxPlayer, rangeNum, nodeDict, classNodeDict, alpha, beta)
            res = min(res, val)
            
            # beta pruning
            beta = min(beta, res)
            if beta <= alpha:
                break
    
        return res

# def minimaxabgame(root: Node, isMaxPlayer: bool, ab: bool, rangeNum: int, nodeDict: dict[str, list[str]], 
#             classNodeDict: dict[Node, list[Node | int]], classNodeDictNoInt: dict[Node, list[Node]],
#             nodeNameToObj: dict[str, Node | int],
#             alpha: int, beta: int,
#             verboseList: list[tuple[str | int]]) -> int:
def minimaxabgame(root: Node, isMaxPlayer: bool, ab: bool, rangeNum: int, nodeDict: dict[str, list[str]], 
            classNodeDict: dict[Node, list[Node , int]], classNodeDictNoInt: dict[Node, list[Node]],
            nodeNameToObj: dict[str, Node , int],
            alpha: int, beta: int,
            verboseList: list[tuple[str , int]]) -> int:
    chooseBetterOption = False
    bestChoice: tuple[str | int] = ()
    if isMaxPlayer:
        res: int = -rangeNum
        for node in classNodeDictNoInt[root]:
            child: Node | int = nodeNameToObj[repr(node)]
            if type(child) == int:
                val: int = child
            else:
                val: int = minimaxabgame(child, not isMaxPlayer, ab, rangeNum, nodeDict, classNodeDict, classNodeDictNoInt, nodeNameToObj, alpha, beta, verboseList)
            
            if val < -rangeNum or val > rangeNum:
                raise ValueError("The value " + str(val) + " is out of range.")
            # if val >= res: # Edge Case for output3 (# max -ab -v) - want earlist (leftmost) node choice
            if val > res:
                chooseBetterOption = True
            res = max(res, val)

            if ab:
                # alpha pruning
                alpha = max(alpha, res)
                if beta <= alpha:
                    if res == rangeNum:    # edge case: put value at limit into verbose List
                        bestChoice = ('max', repr(root), repr(node), val)
                        break
                    # print("pruned: ", res)
                    return res  # don't append to verboseList if pruned
            
            # changed res so add remark about choosing a node
            if chooseBetterOption:
                chooseBetterOption = False
                bestChoice = ('max', repr(root), repr(node), val)
                # verboseList.append(bestChoice) # show all choices

        verboseList.append(bestChoice)
        return res

    else:
        res = rangeNum
        for node in classNodeDictNoInt[root]:
            child: Node | int = nodeNameToObj[repr(node)]
            if type(child) == int:
                val = child
            else:
                val: int = minimaxabgame(child, not isMaxPlayer, ab, rangeNum, nodeDict, classNodeDict, classNodeDictNoInt, nodeNameToObj, alpha, beta, verboseList)
            
            if val < -rangeNum or val > rangeNum:
                raise ValueError("The value " + str(val) + " is out of range.")
            # if val <= res: # Edge Case for output3 (# max -ab -v)
            if val < res:
                chooseBetterOption = True
            res = min(res, val)
            
            if ab:
                # beta pruning
                beta = min(beta, res)
                
                if beta <= alpha:
                    if res == -rangeNum:   # edge case: put value at limit into verbose List
                        bestChoice = ('min', repr(root), repr(node), val)
                        break
                    # print("pruned: ", res)
                    return res  # don't append to verboseList if pruned
            
            # changed res so add remark about choosing a node
            if chooseBetterOption:
                chooseBetterOption = False
                bestChoice = ('min', repr(root), repr(node), val)
                # verboseList.append(bestChoice) # show all choices
        
        verboseList.append(bestChoice)
        return res

def printLine(line: tuple) -> None:
    # example: min(a) chooses a1 for 3
    print(line[0] + '(' + line[1] + ') chooses ' + line[2] + ' for ' + str(line[3]))

# def printOutput(verboseList: list[tuple[str | int]]):
def printOutput(verboseList: list[tuple[str , int]], isVerbose: bool) -> None:
    if not isVerbose:
        printLine(verboseList[-1])
        return
    for line in verboseList:
        printLine(line)
    return

if __name__ == '__main__':
    # python minimax.py [-v] [-ab] -range n min/max graph-file
    rootIsMaxPlayer, filename, isVerbose, ab, rangeNum = parseArguments()
    # print(rootIsMaxPlayer, filename, isVerbose, ab, rangeNum)
    '''
    python minimax.py -range 1000 max ./examples/example1.txt
    python minimax.py -range 1000 min ./examples/example1.txt
    python minimax.py -v -range 1000 max ./examples/example1.txt
    python minimax.py -v -range 1000 min ./examples/example1.txt
    python minimax.py -v -ab -range 1000 max ./examples/example1.txt
    python minimax.py -v -ab -range 1000 min ./examples/example1.txt
    '''
    '''
    # python minimax.py -v -range 1000 max ./examples/example1.txt
    # MIN, MAX = -int(rangeNum), int(rangeNum)
    filename = "./examples/example1.txt"
    # max
    rootIsMaxPlayer = True
    ab= False
    # min
    # rootIsMaxPlayer = False
    # ab= False
    # max -ab
    # rootIsMaxPlayer = True
    # ab= True
    # min -ab
    # rootIsMaxPlayer = False
    # ab= True

    # rangeNum = 10
    rangeNum = 1000
    isVerbose = True
    '''

    leaf, nodeSet, nodeDict, internalNodeList = parseGraphFile(filename)
    # print(leaf)
    # print(nodeSet)
    # print(nodeDict)
    # print(internalNodeList) # non Leaf Nodes called in this order

    # nonLeafNodeSet = nonLeafNodes(leaf, nodeSet)
    # print(nonLeafNodeSet)

    nodeNameToObj, classNodeDict,  nodeNameToObjNoInt, classNodeDictNoInt = initTree(leaf, nodeSet, nodeDict)
    # print(nodeNameToObj)
    # print(classNodeDict)
    # print(nodeNameToObjNoInt)
    # print(classNodeDictNoInt)

    # print("Check Errors for " + filename)
    root = checkError(classNodeDict, nodeDict, leaf)
    # print("Result: No Errors")
    rootName = repr(root)
    # print(rootName)

    # print(minimax(root, rootIsMaxPlayer, rangeNum, nodeDict, classNodeDict))
    # print(minimaxab(root, rootIsMaxPlayer, rangeNum, nodeDict, classNodeDict, -rangeNum, rangeNum))

    # For an idea of the tree or graph:
    # print(classNodeDictNoInt)
    # print(classNodeDict)
    # print(rootName)

    # verboseList: list[tuple[str | int]] = []
    verboseList: list[tuple] = []
    output = minimaxabgame(root,rootIsMaxPlayer, ab, rangeNum, nodeDict, classNodeDict, classNodeDictNoInt, nodeNameToObj, -rangeNum, rangeNum, verboseList)
    # print(output)
    # print(verboseList)
    printOutput(verboseList, isVerbose)


    #'''



