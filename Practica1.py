"""
Practica 1: Problema del productor/consumidor

Jose Ignacio Alba Rodriguez
"""


# Posibles cambios: Consumidor().storage a Array

from multiprocessing import Process, BoundedSemaphore, Semaphore, Lock, Value, Array, Manager
from random import randint
import time

# Por comodidad en las llamadas a las funciones, recogo todos los datos asociados a cada productor y consumidor en clases
# He implementado los buffer de los productores como Arrays circulares, por ello, debemos de guardar los datos de la posicion del valor inicial y final
# Estos ultimos son de la clase Value pues deben ser compartidos y modificados con el consumidor, mientras que cap puede ser entero de Python ya que es constante
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
    
    def __repr__(self):
        s = f"Productor {self.indice}: ["
        for i in range(self.cap):
            a = self.storage[(self.inicial.value + i)% self.cap]
            if a == -2:
                s+= " _ "
            else: s+= f" {a} "
            if(i< self.cap -1): s+= ","
        return s+"]"
    
    def almacenar(self, dato):
        self.lock.acquire()
        print(f"El Productor {self.indice} entra a su seccion critica", flush = True)
        try:
            self.storage[self.final.value] = dato
            self.final.value = (self.final.value + 1) % self.cap        
        finally:
            self.lock.release()
            print(f"El Productor {self.indice} sale de su seccion critica", flush = True)
    
    # Aunque quitar sea un metodo de la clase productor, sera llamado desde el proceso consumidor, por lo que necesitamos los Locks
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


def minimo(productos):
    l = list(filter(lambda x: x[1]>=0 , productos))
    if l == [] : return -1
    m = l[0]
    for a in l:
        if(a[1] < m[1]): m = a
    return m


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
            for p in c.prods:    # Para que "liberen" el -1 y asi todos los procesos terminen para el join()
                p.empty.release()
        else:
            c.prods[ mini[0] ].non_empty.acquire()
            print(f"Elementos escogidos: {productos}\nEl Consumidor consume {mini[1]} del Productor {mini[0]}\n", flush = True)            
            c.prods[mini[0]].quitar()
            c.prods[mini[0]].empty.release()
            c.storage.append(mini)
            print(f"Estado Actual del Consumidor: {c}")
    print(f"Los productos consumidos por c en orden de consumicion: {c.storage}", flush = True)



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
        
    #print(c.storage) c.storage no ha cambiado por que era una copia y la memoria no era compartida!!! Para que sea memo compartida: c.storage = Array('i', sum(N))
    for p in c.prods: print(p)


if __name__ == '__main__':
    n_prods = 5 #Numero de productores
    cap = [2 for _ in range(n_prods)] #Capacidad de cada productor (no todos tienen por que tener la misma)
    N = [3  for _ in range(n_prods)] # Numero de productos que produce cada productor (no todos tienen por que producir los mismos elementos)
    
    """ No tienen por que tener todos los productores la misma capacidad ni el mismo numero de producciones"""    
    cap = [5,6,2,8,10]
    N = [8,7,3,9,15]
    m = Manager()
    l = m.list()

    main()
    time.sleep(1000)
        
        