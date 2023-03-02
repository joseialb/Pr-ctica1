"""
Practica 1: Problema del productor/consumidor

Jose Ignacio Alba Rodriguez
"""


from multiprocessing import Process, BoundedSemaphore, Semaphore, Lock, Value, Array, Manager
from random import randint
import time

# Por comodidad en las llamadas a las funciones, recogo todos los datos asociados a cada productor y consumidor en clases
# He implementado los buffer de los productores como Arrays circulares, por ello, se deben guardar los datos de la posicion del valor inicial y final
# Estos ultimos son de la clase Value pues deben ser compartidos y modificados con el consumidor, mientras que cap puede ser entero de Python ya que es constante
# Tambien, el codigo admite que cada productor tenga una capacidad y numero de producciones distintos

class Productor():
    def __init__(self ,cap, indice):
        self.cap = cap
        self.indice = indice
        self.inicial = Value('i',0)
        self.final = Value('i',0)
        self.storage = Array('i', cap)
        for i in range(cap):
            self.storage[i] = -2
        self.non_empty = Semaphore(0)
        self.empty = BoundedSemaphore(cap)
        self.lock = Lock()

    # La funcion __repr__ devolvera un string con el identificador del productor y su almacen, sustituyendo los -2 por _
    def __repr__(self):
        s = f"Productor {self.indice}: ["
        for i in range(self.cap):
            a = self.storage[(self.inicial.value + i)% self.cap]
            if a == -2:
                s+= " _ "
            else: s+= f" {a} "
            if(i< self.cap -1): s+= ","
        return s+"]"

    # La funcion almacenar espera para entrar en la seccion critica y añade un elemento al almacen, desplazando el valor final
    def almacenar(self, dato):
        self.lock.acquire()
        print(f"El Productor {self.indice} entra a su seccion critica", flush = True)
        try:
            self.storage[self.final.value] = dato
            self.final.value = (self.final.value + 1) % self.cap        
        finally:
            self.lock.release()
            print(f"El Productor {self.indice} sale de su seccion critica", flush = True)

    # La funcion quitar sustituye el primer elemento por -2 y reduce el valor inicial
    # Aunque quitar sea un metodo de la clase Productor, sera llamado desde el proceso consumidor, por lo que necesitamos los Locks para asegurar que no se almacena y se quita al mismo tiempo
    def quitar(self):
        print(f"El Consumidor entra en la seccion critica del Producto {self.indice}", flush = True)
        self.lock.acquire()
        try:
            data = self.storage[self.inicial.value]
            self.storage[self.inicial.value] = -2
            self.inicial.value = (self.inicial.value+1)%self.cap
        finally:
            self.lock.release()
            print(f"El Consumidor sale de la seccion critica del Producto {self.indice}", flush = True)
        return data


class Consumidor():
    def __init__(self, n, productores, storage):
        self.n = n
        self.prods = productores
        self.storage = storage
    
    def __repr__(self):
        return str(self.storage)

# Cada proceso Productor añade a su almacen elementos aleatorios de forma creciente siempre que tenga capacidad suficiente, y si no, espera
def producir(prod, N):
    producto = 0
    for v in list(range(N)) + [-1]:
        producto += randint(1,10) 
        if v == -1: producto = -1
        prod.empty.acquire()
        prod.almacenar(producto)
        prod.non_empty.release()
        print(f"El productor {prod.indice} ha producido:\n{prod}\n", flush = True)
    print(f"El productor {prod.indice} ha terminado", flush = True)

# La funcion minimo decuelve una tupla con el segundo elemento correspondiente al producto menor y el primer elemento correspondiente al indice del productor del que viene dicho elemento
# Si todos los procesos han acabado (todos tienen -1) entonces devuelve -1
def minimo(productos):
    l = list(filter(lambda x: x[1]>=0 , productos))
    if l == [] : return -1
    m = l[0]
    for a in l:
        if(a[1] < m[1]): m = a
    return m

# Calcula el minimo y lo consume. Para cuando minimo devuelve -1, es decir, cuando consume todos los elementos producidos de cada productor
def consumir(c):
    alguien_no_terminado = True,
    while alguien_no_terminado:
        productos = []
        for i, p in enumerate(c.prods):
            p.non_empty.acquire()
            productos.append( (i,p.storage[p.inicial.value]) )
            p.non_empty.release()
        mini = minimo(productos)
        if (mini ==-1) :
            alguien_no_terminado = False
            for p in c.prods:    # Para que "liberen" el -1 y asi todos los procesos terminen y puedan acceder al join()
                p.empty.release()
        else:
            c.prods[ mini[0] ].non_empty.acquire()
            print(f"Elementos escogidos: {productos}\nEl Consumidor consume {mini[1]} del Productor {mini[0]}\n", flush = True)            
            c.prods[mini[0]].quitar()
            c.prods[mini[0]].empty.release()
            c.storage.append(mini)
            print(f"Estado Actual del Consumidor: {c}")


def main():
    prods = [Productor(cap[i], i) for i in range(n_prods)]
    c = Consumidor(n_prods, prods, l)
    procesos = []
    for i, p in enumerate(c.prods):
        procesos.append(Process( target = producir, args = (p, N[i]), name = f'Productor {i}'))

    proc_c = Process( target = consumir, args =(c,) , name = "Consumidor")
                
    for p in (procesos + [proc_c]):
        p.start()

    for p in (procesos + [proc_c]):
        p.join()
    for p in c.prods: print(p)


if __name__ == '__main__':
    # No es necesario que todos los productores tengan la misma capacidad o numero de producciones

    n_prods = 5         # Numero de productores    
    cap = [5,6,2,8,10]  # Capacidad de cada productor
    N = [8,7,3,9,15]    # Numero de producciones que realiza cada productor
    m = Manager()
    l = m.list()        # Lista compartida del Consumidor

    main()

    # El primer indice indica el Productor del que proviene cada producto, y el segundo es el propio producto
    print(f"El resultado de la lista del consumidor: {l}")
