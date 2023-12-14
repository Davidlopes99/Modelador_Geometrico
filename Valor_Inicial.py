import numpy as np
import json
import matplotlib.pyplot as plt

def main():
    # Carregando dados do arquivo JSON
    print("main")
    with open("input.json") as f: 
        model = json.load(f)
    print(model["coords"])
  
    # Extraindo coordenadas x e y do modelo
    x = np.array([e[0] for e in model["coords"]])
    print(x)
    y = np.array([e[1] for e in model["coords"]])
    print(y)

    # Carregando forças, restrições e mapa de conexão
    forcas = np.array(model["forces"])
    restrs = np.array(model["restrs"])
    connect = np.array(model["connection_map"])

    Np = x.shape[0]
    k = 210000000000
    m = 7850 
    r = 1
  
    # Configurando forças no formato adequado
    f = np.array([e for e in forcas])
    f = np.reshape(f, (2*Np))
    print(f)

    fi = np.zeros(2*Np)
    u = np.zeros(2*Np)
    v = np.zeros(2*Np)
    a = (1/m)*f
    N = 100
    h = 0.00004
    d = np.zeros(N)
  
    # Simulação do sistema dinâmico
    for i in range(N):
        fi *= 0
        v += a*h/2
        u += v*h
        
        # Contato entre nós
        for j in range(Np):
            if (restrs[j][0] == 1):
                u[2*j] = 0 
            if (restrs[j][1] == 1):
                u[2*j+1] = 0 
            Npc = connect[j][0]
            xj = x[j] + u[2*j]
            yj = y[j] + u[2*j+1]
            
            for ki in range(Npc-1):
                pk = connect[j][ki+1]-1
                xk = x[pk] + u[pk*2]
                yk = y[pk] + u[pk*2+1]
                dx = xj - xk
                dy = yj - yk
                di = (dx**2 + dy**2)**0.5
                d2 = di - 2*r
                dx = d2*dx/di
                dy = d2*dy/di
                fi[2*j] += k*dx
                fi[2*j+1] += k*dy

        a = (1./m)*(f-fi)
        v += a*h/2.
        fi *= 0.
        d[i] = u[17*2]  # Armazena a posição do 17º nó

    # Plotagem dos resultados
    plt.plot(d)
    plt.show()
  
if __name__ == "__main__":
    main()
