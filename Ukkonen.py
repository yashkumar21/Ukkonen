import sys

class SuffixNode:
    # Each SuffixNode represents a suffix in the tree
    def __init__(self):
        # All characters are in the ASCII range [36, 126]
        self.children = [None] * 91
        # start and end denotes the edge, by storing indices.
        self.start = None
        self.end = None
        self.index = None
         # Suffix link to destination node 
        self.suffix_link = None

class End:
    def __init__(self, value):
        # global end to keep track of the end of leaf edge
        self.value = value

class ActivePoint:
    # Represents current active point while traversinf the tree 
    def __init__(self, node):
        self.node = node # Current node
        self.edge = 0 # Index of character from root
        self.length = 0 # Current length from the root

class SuffixTree:
    def __init__(self, data):
        # begin suffix tree with a root
        self.root = SuffixNode()
         # The input to construct the tree from
        self.data = data
        # Active point initially pointing to root
        self.active = ActivePoint(self.root)
        self.remaining_suffix_count = 0
        self.end = End(-1)
        # list to store the rank of each suffix
        self.rank = [] 
        self.build() # build tree

    # used to construct the Suffix tree
    def build(self):
         # Check for every character in the input string
        for i in range(len(self.data)):
            # Check if the input string ends with '$'
            if '$' != self.data[-1]:
                raise ValueError("Invalid input string, must end with '$'")
            # At every moment we are going to increment End point
            self.end.value = i
            self.remaining_suffix_count += 1
            # track the last node created
            last_new_node = None
            # Rule 1 
            while self.remaining_suffix_count > 0:
                if self.active.length == 0:
                    self.active.edge = i

                # Rule 2
                if self.active.node.children[ord(self.data[self.active.edge])-36] is None:
                    # Create a new leaf node  
                    new_leaf = SuffixNode()
                    new_leaf.start = i
                    new_leaf.end = self.end
                    # # Connect new_leaf to its parent active node
                    self.active.node.children[ord(self.data[self.active.edge])-36]= new_leaf 
                    # New internal node waiting for its suffix link
                    if last_new_node:
                        last_new_node.suffix_link = self.active.node
                    last_new_node = new_leaf
                # Rule 3
                else:
                    next_node = self.active.node.children[ord(self.data[self.active.edge])-36]  
                    if self.walk_down(next_node):
                        continue
                    # If the character already exists on the edge
                    if self.data[next_node.start + self.active.length] == self.data[i]:
                        if last_new_node and self.active.node != self.root:
                            last_new_node.suffix_link = self.active.node
                        self.active.length += 1
                        break
                    # If the character does not exist on the edge, Split the node and create a new internal node
                    split_node = SuffixNode()
                    split_node.start = next_node.start
                    next_node.start += self.active.length
                    split_node.end = End(next_node.start - 1)
                    split_node.children[ord(self.data[next_node.start])-36] = next_node 
                    split_node.children[ord(self.data[i])-36] = SuffixNode()  
                    split_node.children[ord(self.data[i])-36].start = i  
                    split_node.children[ord(self.data[i])-36].end = self.end 
                    self.active.node.children[ord(self.data[self.active.edge])-36] = split_node 
                    if last_new_node:
                        last_new_node.suffix_link = split_node
                    last_new_node = split_node
                # Decrement the remaining suffix count
                self.remaining_suffix_count -= 1
                # Rule 1 extension
                if self.active.node == self.root and self.active.length > 0:
                    self.active.length -= 1
                    self.active.edge = i - self.remaining_suffix_count + 1
                # Rule 3 extension
                else:
                    self.active.node = self.active.node.suffix_link if self.active.node.suffix_link else self.root

        self.set_suffix_indices(self.root, 0)

    # Walk down the tree, rule 3 extension
    def walk_down(self, next_node):
        edge_length = next_node.end.value - next_node.start + 1
        # If the active length is greater than the edge length, walk down the tree so change active point
        if self.active.length >= edge_length:
            self.active.edge += edge_length
            self.active.length -= edge_length
            self.active.node = next_node
            return True
        return False

    # Set the suffix indices for each node
    def set_suffix_indices(self, node, path_length):
        if node is None:
            return
        leaf = True
        # Recursively set the suffix indices for each child node
        for child in node.children:
            if child is not None:
                leaf = False
                self.set_suffix_indices(child, path_length + (child.end.value - child.start + 1))
        # If the node is a leaf, set the index of the node
        if leaf:
            node.index = len(self.data) - path_length
            # Store the rank of the suffix
            self.rank.append(node.index)

    def suffixArray(self):
        # Get the suffix array of the tree
        suffixes = []
        self.suffixArrayRec(self.root, suffixes)
        return suffixes

    def suffixArrayReccursive(self, node, suffixes):
        # Recursively get the suffix array of the tree
        if node is None:
            return
        if node.index is not None:
            suffixes.append(node.index)
        # for each child node, get the suffix array
        for child in node.children:
            self.suffixArrayReccursive(child, suffixes)
    
    # Get the rank of the suffix
    def get_rank(self, suffix):
        index = len(self.data) - len(suffix)
        return self.rank.index(index)
    
    # Get the suffix from the index
    def get_suffix(self, idx):
        if idx >= len(self.data):
            return None
        suffix_start = idx
        return self.data[suffix_start:]

if __name__ == '__main__':
    # Ensure the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python q1.py <stringFileName> <positionsFileName>")
        sys.exit(1)
    stringFileName = sys.argv[1]
    positionsFileName = sys.argv[2]

    # if correct number of arguments are provided, read the string and positions from the files
    with open(stringFileName, 'r') as file:
        string = file.read().strip()
    with open(positionsFileName, 'r') as file:
        positions = [int(line.strip()) for line in file]

    # Create a suffix tree from the string
    tree = SuffixTree(string)
    # Get the ranks of the suffixes from the positions
    ranks = [tree.get_rank(tree.get_suffix(pos-1))+1 for pos in positions]

    # Write the ranks to the output file
    with open('output_q1.txt', 'w') as file:
        for rank in ranks:
            file.write(str(rank) + '\n')