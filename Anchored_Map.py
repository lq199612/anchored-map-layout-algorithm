# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx
from numpy.random.mtrand import RandomState as rdm
import random
import math 
import matplotlib.pyplot as plt
import os
import json
random.seed(10)

# 生成图
def generate_graph(A, B, edges):
    nodes = A.copy()
    nodes.extend(B)
    nodes.sort()  # 排序
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    return g

# 生成锚点坐标
def anchored_pos_init( achored, center=(0.5,0.5), r = 0.5):
    n = len(achored)
    theta = [360/n*i for i in range(n)]
    pos = []
    for idx, i in enumerate(theta):
        pos.append((center[0]+r*math.cos(i * math.pi / 180), center[1]+r*math.sin(i * math.pi / 180)))
    return pos

# 自由节点-锚点链接表
def connect_map(g,A):
    connect_A_edges =  g.edges(A)
    m = {}
    for edge in connect_A_edges:
        if edge[0] in A:
            if edge[1] not in m:
                m[edge[1]] = [edge[0]]
            else:
                m[edge[1]].append(edge[0])
        if edge[1] in A:
            if edge[0] not in m:
                m[edge[0]] = [edge[1]]
            else:
                m[edge[0]].append(edge[1])    
    return m
        
# 计算 Penalty
def caculate_penalty(A, m, q=2):
    total = 0
    k = len(A)
    for node in m:
        l = m[node]
        pos = [A.index(i)+1 for i in l]
        for idx, i in enumerate(pos):
            if idx +1 < len(pos):
                total += ((pos[idx+1] - i + k) % k) ** q
    return total
  
def searching_optimal_order(A_, m):
    A = A_.copy()
    p0 = caculate_penalty(A, m)
    k = len(A)
    d = math.ceil(k /2 )
    while d>0:
        print('d',d)
        c = True
        while c:
            c = False
            for i in range(d):
                j = (i+d) % k
                A[i], A[j] = A[j], A[i]
                p1 = caculate_penalty(A, m)
                if p1 < p0:
                    p0 = p1
                    c = True
                else:
                    A[i], A[j] = A[j], A[i]   
        d = math.floor(d/2)
    return A

def pos_init(g, A, anchored_pos):
    anchored_pos_ = {}   
    for idx, i in enumerate(A):
        anchored_pos_[i] = anchored_pos[idx]
    random_pos = rdm().rand(len(g),2)
    anchored_pos_sorted = {}
    for k in anchored_pos_:
        random_pos[k] = anchored_pos_[k]
    return anchored_pos_sorted, random_pos

# 随机扰动
def get_random_disturb():
    return random.random()

def fruchterman_reingold_init(
   G, A, pos=None, fixed=None, iterations=100, threshold=1e-4, dim=2, seed=None,center=[0.5,0.5], r=0.5, inner = False, k=5
):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    nnodes, _ = A.shape
    # 位置初始化
    if pos is None:
        seed = rdm()
        pos = np.asarray(seed.rand(nnodes, dim), dtype=A.dtype)
    else:
        pos = pos.astype(A.dtype)
    # 初始化k
    # if k is None:
        # k = np.sqrt(5.0 / nnodes)
    k = np.sqrt(k / nnodes)
    # 初始化t
    t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1])) * 0.1
    dt = t / float(iterations + 1)
    # 初始化 距离表  
    delta = np.zeros((pos.shape[0], pos.shape[0], pos.shape[1]), dtype=A.dtype)
    for iteration in range(iterations):
        # 计算每个点之间的距离
        delta = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]  
        distance = np.linalg.norm(delta, axis=-1)  # 求范数 默认二范数 可以求出不同点之间的距离   
        # 制大小 最小为0.01    out：可以指定输出矩阵的对象，shape与a相同
        np.clip(distance, 0.01, None, out=distance) # 限
        # 计算x,y方向上的累计位移
        a = (k * k / distance ** 2  - A * distance / k)
        displacement = np.einsum(
            "ijk,ij->ik", delta, (k * k / distance ** 2  - A * distance / k)        # 在不同维度上产生的合力 = 1 / distance (k * k / distance ** 2  - A * distance / k), "ijk,ij->ik" 点乘再累加
        )
        # 更新
        length = np.linalg.norm(displacement, axis=-1)            
        length = np.where(length < 0.01, 0.1, length)
        delta_pos = np.einsum("ij,i->ij", displacement, t / length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed] = 0.0
        pos += delta_pos 
        # 施加约束 使得自由节点都落入圆内
        if inner:
            centripetal_distance = np.linalg.norm(pos - center, axis=-1)
            for idx, n in enumerate(centripetal_distance):
                if n > r + 0.01 * get_random_disturb():
                    pos[idx] = r/n * (pos[idx] + center) + (center - pos[idx]) * (r / 8)
        # 模拟降温
        t -= dt
        err = np.linalg.norm(delta_pos) / nnodes
        if err < threshold:
            break
    pos = dict(zip(G, pos))
<<<<<<< HEAD
    
    return pos          
=======
    return pos           
>>>>>>> ccbccd220cd9e90764690586c13b6895d517f168

def FR(g, A, random_pos,iterations,center,r,inner,show_img):
    matri = nx.to_numpy_array(g, weight='weight')
    B = np.array(A)
    pos = fruchterman_reingold_init(g,matri,pos=random_pos,fixed=B,center=center,r=r,inner=inner,iterations=iterations)
    if show_img:
        node_color = ['blue' if i in B else 'black' for i in g.nodes]
        plt.figure(figsize=(100,100))
        ax = plt.subplot(4,5,1)
        ax.set_aspect('equal')
        nx.draw(g,pos=pos,node_size =55,font_size=20,ax=ax,node_color=node_color,with_labels=True)
        plt.show()
    return pos

def read_json_file(file_path):
    with open(file_path,'r',encoding='utf8')as fp:
        json_data = json.load(fp)
        return json_data

def write_dict(d, file_path):
    jsObj = json.dumps(d)    
    fileObject = open(file_path, 'w')  
    fileObject.write(jsObj)  
    
def Anchored_Map(json_file, anchor_nodes=[], choose='left', r=3, center=(0.5,0.5), iterations=150, inner=False, show_img=True): 
    data = read_json_file(json_file)
    # 锚点
    A = []
    # 自由节点
    B = []
    if not anchor_nodes:
        [A.append(n['id_']) if n['location'] == choose else  B.append(n['id_']) for n in data['nodes']]
    # 指定锚点
    else:
        A = anchor_nodes
        [B.append(n['id_']) if n['id_'] not in A else None  for n in data['nodes']]
    # 边
    E = [(i['source_'],i['target_']) for i in data['links']]
    # 生成图和锚点初始坐标
    g = generate_graph(A, B, E)
    anchored_pos =  anchored_pos_init(A,center=center, r = r)
    # 得到自由节点-锚点链接表
    m = connect_map(g, A)
    print('pre',A) 
    # 优化顺序
    A = searching_optimal_order(A, m)
    print('lat',A)
    # 初始布局
    anchored_pos_sorted, random_pos = pos_init(g, A, anchored_pos)
    # 力导布局
    pos_res = FR(g, A, random_pos,iterations=iterations,center=center,r=r,inner=inner,show_img=show_img)
    # 返回pos
    for n in data['nodes']: 
        n['pos'] = pos_res[n['id_']]
    return pos_res
<<<<<<< HEAD
#%%
json_file = './test.json'  
pos_res1 = Anchored_Map(json_file)
#%%
pos_res2 = Anchored_Map(json_file,inner=True) 
#%%
anchor_nodes = [0,1,2,3,4,5,6,7,8,9,10]
pos_res1 = Anchored_Map(json_file,anchor_nodes=anchor_nodes)
=======
 
json_file = './data/test.json'  
pos_res = Anchored_Map(json_file)
 
    
  
    
>>>>>>> ccbccd220cd9e90764690586c13b6895d517f168
