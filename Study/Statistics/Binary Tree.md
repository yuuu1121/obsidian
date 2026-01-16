# Binary Tree (이진 트리)

## 개요
Binary Tree(이진 트리)는 각 노드가 최대 두 개의 자식 노드를 가지는 트리 자료구조이다. 왼쪽 자식(left child)과 오른쪽 자식(right child)으로 구분된다.

## 용어

- **Root**: 최상위 노드
- **Leaf**: 자식이 없는 노드
- **Height**: 루트에서 가장 깊은 리프까지의 거리
- **Depth**: 루트에서 해당 노드까지의 거리
- **Level**: 같은 깊이의 노드 집합

## 종류

### Full Binary Tree
모든 노드가 0개 또는 2개의 자식을 가짐

### Complete Binary Tree
마지막 레벨을 제외하고 모든 레벨이 채워져 있고, 마지막 레벨은 왼쪽부터 채워짐

### Perfect Binary Tree
모든 내부 노드가 2개의 자식을 가지고, 모든 리프가 같은 레벨

### Binary Search Tree (BST)
왼쪽 서브트리 < 부모 < 오른쪽 서브트리

## 순회 방법

### 전위 순회 (Preorder)
Root → Left → Right
```python
def preorder(node):
    if node:
        print(node.val)
        preorder(node.left)
        preorder(node.right)
```

### 중위 순회 (Inorder)
Left → Root → Right (BST에서 정렬된 순서)
```python
def inorder(node):
    if node:
        inorder(node.left)
        print(node.val)
        inorder(node.right)
```

### 후위 순회 (Postorder)
Left → Right → Root
```python
def postorder(node):
    if node:
        postorder(node.left)
        postorder(node.right)
        print(node.val)
```

### 레벨 순회 (Level-order)
BFS 방식, 같은 레벨 먼저

## 시간 복잡도 (BST)

| 연산 | 평균 | 최악 |
|------|------|------|
| 탐색 | O(log n) | O(n) |
| 삽입 | O(log n) | O(n) |
| 삭제 | O(log n) | O(n) |

## 응용

### Machine Learning
- Decision Tree
- Random Forest
- [[KDTree]]

### 자료구조
- Heap (Priority Queue)
- Huffman Coding

## 관련 개념
- [[KDTree]]
- [[Decision Tree]]
- [[Graph]]
