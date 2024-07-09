def swap(list, a, b):
    temp=a
    a=b
    b=temp

def heapifyUp(heap, pos):
    parent=int((pos-1)/2)
    if heap[parent] > heap[pos]:
        while pos!=0:
            swap(heap, pos, parent)
            heapifyUp(heap, parent)
    else:
        return
    

def insert(heap, k):
    heap.append(k)
    heapifyUp(heap, (len(heap)-1))


def heapifyDown(heap, pos):
    left_child= (pos*2)+1
    right_child=(pos+1)*2
    if pos < len(heap):
        if left_child < len(heap):
            if right_child >= len(heap):
                smaller_child=left_child
            elif heap[left_child]<heap[right_child]:
                smaller_child=left_child
            else:
                smaller_child=right_child
            if heap[smaller_child]<heap[pos]:
                swap(heap, pos, smaller_child)
                heapifyDown(heap, smaller_child)
            else:
                return
        else:
            return
            



minheap=[12,3,5,8,7,10,9]
print(minheap)
heapifyDown(minheap, 0)
print(minheap)
