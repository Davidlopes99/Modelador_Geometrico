import matplotlib.pyplot as plt
import json
import numpy as np

# Função para ler dados de um arquivo JSON
def read_json(_file):
    with open(_file, "r") as f:
        data = json.load(f)
        if "coords" in data:
            ne = len(data["coords"])
            x0 = np.zeros((ne, 1))
            y0 = np.zeros((ne, 1))
            for i in range(ne):
                x0[i] = float(data["coords"][i][0])
                y0[i] = float(data["coords"][i][1])
            forcas = np.array(data["forces"])
            restrs = np.array(data["restrs"])
            connect = np.array(data["connection_map"])
            return ne, x0, y0, forcas, restrs, connect

# Função principal de simulação
def main(_file):
    N = 600
    h = 0.00004
    ne, x0, y0, forcas, restrs, connect = read_json(_file)
    ndofs = 2 * ne
    raio = 1.0
    mass = 7850.0
    kspr = 210000000000.0
    forcas = forcas.flatten().reshape((ndofs, 1))
    restrs = restrs.flatten().reshape((ndofs, 1))

    u = np.zeros((ndofs, 1))
    v = np.zeros((ndofs, 1))
    a = np.zeros((ndofs, 1))
    res = np.zeros((N,))
    fi = np.zeros((ndofs, 1))

    a[:] = (forcas - fi) / mass

    # Loop de simulação
    for i in range(N):
        v += a * (0.5 * h)
        u += v * h
        fi[:] = 0.0
        # Atualiza posições e calcula forças entre nós
        for j in range(ne):
            if restrs[2 * j] == 1:
                u[2 * j] = 0.0
            if restrs[2 * j + 1] == 1:
                u[2 * j + 1] = 0.0
            xj = x0[j] + u[2 * j]
            yj = y0[j] + u[2 * j + 1]
            for index in range(1, connect[j, 0] + 1):
                k = connect[j, index]
                xk = x0[k - 1] + u[2 * k - 1]
                yk = y0[k - 1] + u[2 * k - 1]
                dX = xj - xk
                dY = yj - yk
                di = np.sqrt(dX * dX + dY * dY)
                d2 = (di - 2 * raio)
                dx = d2 * dX / di
                dy = d2 * dY / di
                fi[2 * j] += kspr * dx
                fi[2 * j + 1] += kspr * dy
        a[:] = (forcas - fi) / mass
        v += a * (0.5 * h)
        res[i] = u[32, 0]  # Supondo que u é uma matriz 2D

    # Plotagem dos resultados
    x = np.arange(1, N + 1)
    plt.plot(x, res)
    plt.show()

# Executa a função principal se este script for executado
if __name__ == "__main__":
    main("input.json")

