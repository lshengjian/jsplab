import numpy as np
N=20 # 狮子总数
M=N//4 #母狮数量
D=2 # dimension of the problem
T=400


gBest=float("inf")
gBestX=np.random.randn(D)
pBest=np.array([float("inf")]*N)
pBestX=np.random.randn(N,D)


def fitness(x):
    return (x*x).sum(axis=-1)

def update(i,idx,x,f):
    global gBest
    y=fitness(x)
    if(y<f):
        pBest[idx]=y
        pBestX[idx,:]=x
        if y<gBest:
            gBest=y
            gBestX[:]=x
            print(f'M:{y}') if i==0  else \
                print(f'C:{y}') if i>M else print(f'F:{y}')
    return y

def train(steps,dt=5):
    I=pBest.argsort()
    for t in range(steps):
        for i,idx in enumerate(I):
            ds=(steps-t)/steps*np.random.randn(D)*0.01
            x=(pBestX[I[i%M+1]]+pBestX[idx])/2+ds
            if i==0 :
                x=gBestX+0.001*ds
            elif i<=M:
                x=(pBestX[idx]+pBestX[I[np.random.choice(range(1,M+1))]])/2+ds*0.1
            update(i,idx,x,pBest[idx])
        if t%dt==0:
            I=pBest.argsort()
            #print(I)

    return gBest,gBestX
    

if __name__ == '__main__':
    gBest,gBestX=train(T)
    #print(gBest)
    print(gBestX)

