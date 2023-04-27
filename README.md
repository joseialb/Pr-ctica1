# Práctica 1

## Revisión de la corrección

En la primera corrección de la práctica 1, señalaba un error de mi código en la llamada a p.non_empty.release() de la linea 106, que realmente es correcto, aquí le añado la explicación:
Dentro de la función "consumir", se crea una lista de productos con el primer elemento del buffer de cada Productor. Para esto, es necesario que cada productor tenga al menos un elemento en su buffer.
Para asegurar esta condicion, hago una llamada a p.non_empty.acquire() por cada productor p, realizando un total de n_prods llamadas. Sin embargo, el consumidor solo necesita consumir 1 de los N elementos de la lista "productos", por lo que hasta este punto, se han hecho más acquires de los necesarios. 
Esta es la razón por la que, después de añadir el producto a la lista de productos, cada productor vuelve a llamar a su p.non_empty.release() (linea 106).
De esta manera se restablece el número de acquires hechos basándonos en el invariante de los semáforos. Finalmente, en la línea 107 se decide quién es el productor del que se va a consumir un objeto, ya que la función mínimo devuelve una tupla cuyo primer componente es el índice de dicho productor.
Posteriormente, en la línea 113 se hace la llamada de non_empty.acquire() para este productor, de manera que el numero de acquires para este semáforo es n_prods+1 y el numero de releases es n_prods, por lo que la diferencia es 1, que es lo esperable

Este resultado es correcto, más formalmente:
  Sea c el consumidor y p un productor
  Cuando en el consumidor, se hace la llamada a p.non_empty.acquire() pueden darse dos situaciones:
    - p.non_empty.V > 0, luego, hay elementos, y al hacer el acquire() hace p.non_empty.V -= 1, c no queda bloqueado y puede añadir a la lista de productos
      Finalmente, realiza la llamada a p.non_empty.release(), como el consumidor no quedó bloqueado en la última llamada a acquire, la lista de procesos
      bloqueados esta vacia, hace p.non_empty.V += 1, restaurando su valor original como p.non_empty.V = num_productos(p)
    - p.non_empty.V = 0, esto solo puede ocurrir si p no ha producido nada antes de que aparezca c, ya si termina de producir, se queda con el -1 hasta
      que c acabe. Por tanto, c queda bloqueado. Como al productor p le queda algo por producir, en algun momento este hará un p.non_empty.release(). 
      En ese momento, c podrá volver a actuar, y aunque el semáforo no ha sumado nada a p.non_empty.V cuando el productor llamo al release(),
      cuando c continue, c hará el release y añadira uno a este valor, restaurando p.non_empty.V al numero de productos de p


## Explicación del código

En esta práctica he implementado los productores y consumidores como clases para dejar más organizados las estructuras de datos necesarias.
Cada productor tiene un array circular iniciado todo a -2 con una capacidad variable que podemos asignar desde el main, su propio lock y sus propios semáforos non_empty y empty
Por cada productor, se inicializa un proceso "producir" que toma como parametro el productor y cada cierto tiempo, si hay capacidad libre, añade un 
elemento aleatorio de forma creciente al array circular y al terminar añade -1, llamando siempre al Lock desde la funcion almacenar de la propia clase
El consumidor es otra clase que contiene una lista de productores, de esta forma puede acceder a sus semaforos, y su propio almacen
Para el consumidor, se crea un proceso con la funcion consumir, que espera a que todos los productores tengan algun elemento, elige el minimo de todos
ellos (ignorando los -1, que corresponden a productores terminados) guardando el indice del productor, y consume este producto, eliminandolo del array del 
productor. Si todos los productores han terminado, esto es, todos los arrays devuelven un -1, entonces el consumidor los libera a todos y termina su bucle

El caso obligatorio en el que cada array tiene una unida de capacidad es un caso particular del código. La capacidad de cada productor puede definirse de 
forma independiente, asi como el numero de productos que produce cada uno
