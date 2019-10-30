#from extratypes import Tree  # library with types used in the task


class T:
    def __init__(self, data):
        self.x = data
        self.l = self.r = None




def solution(T):
    if (not T):
        return 0
    hash = {}
    return distinctPath(T, hash)

def distinctPath(node, m):
    if (not node):
        return len(m)

    if node.x in m:
        return len(m)
    else:
        m[node.x] = 1

    print(node.r)
    max_path = max(distinctPath(node.l, m), distinctPath(node.r, m))
    m[node.x] -= 1

    if (m[node.x] == 0):
        del m[node.x]

    return max_path


if __name__ == '__main__':

    # Create binary tree shown
    # in above figure
    root = T(1)
    root.r = T(2)
    root.r.l = T(1)
    root.r.r = T(1)
    root.r.r.l = T(4)



print (solution(root))
