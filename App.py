from GestorArchivos import GestorArchivos
from API import API

class App:
    """
    Coordina la aplicacion MeteoCaracas: prepara los datos a partir del archivo
    de zonas, presenta el menu y atiende las consultas de clima en tiempo real,
    ya sea navegando por municipio o buscando la localidad por su nombre.

    Atributos:
        gestorArchivos (GestorArchivos): Encargado de leer el archivo de zonas.
        municipios (list): Municipios cargados en memoria.
        api (API): Cliente para consultar Open-Meteo.
    """

    def __init__(self):
        """
        Deja la aplicacion lista para iniciar, con sus colaboradores creados y la
        lista de municipios todavia vacia.
        """
        self.gestorArchivos = GestorArchivos()
        self.municipios = []
        self.api = API()

    def iniciar(self):
        """
        Pone en marcha la aplicacion: carga los datos, muestra el reporte de
        carga y repite el menu leyendo la opcion del usuario hasta que se decide
        salir. Si la carga falla, termina sin abrir el menu.
        """
        self.cargarDatos()
        if len(self.municipios) == 0:
            return
        self.mostrarReporteCarga()
        self.menu()


    def cargarDatos(self):
        """
        Solicita al gestor la lista de municipios y avisa si el archivo no pudo
        leerse. Ademas prueba la conexion con Open-Meteo para informar si se
        podran hacer consultas.
        """
        print("Cargando zonas de Caracas...")
        self.municipios = self.gestorArchivos.leerZonas()
        if len(self.municipios) == 0:
            print("No se pudo cargar el archivo zonas_caracas.json.")
            return
        print("Se cargaron", len(self.municipios), "municipios.")
        if self.api.conectar():
            print("Open-Meteo disponible.")
        else:
            print("Sin conexion con Open-Meteo; podra ver los datos pero no consultar el clima.")

    def mostrarReporteCarga(self):
        """
        Recorre los municipios y muestra, para cada uno, cuantas localidades se
        cargaron, cuantas tienen coordenadas, cuantas no, y el porcentaje que si
        las tiene.
        """
        print("\n===== REPORTE DE CARGA =====")
        for municipio in self.municipios:
            cargadas = municipio.contarLocalidades()
            conCoord = municipio.contarConCoordenadas()
            sinCoord = municipio.contarSinCoordenadas()
            porcentaje = round(municipio.porcentajeConCoordenadas(), 2)
            print(municipio.nombre + ":")
            print("   cargadas =", cargadas, "| con coord =", conCoord, "| sin coord =", sinCoord, "| % con coord =", porcentaje)

    def menu(self):
        """
        Imprime las opciones disponibles del menu principal.
        """
        while True:
            print("\n===== METEOCARACAS =====")
            print("1) Clima por municipio y localidad")
            print("2) Buscar localidad por nombre")
            print("3) Ver reporte de carga")
            print("4) Salir")

            opcion = input("Ingrese la opcion que desea ejecutar: ")
            while not opcion.isdigit() or not int(opcion) in range(1,5):
                print("Opción inválida. Intente nuevamente.")
                opcion = input("Ingrese la opcion que desea ejecutar: ")

            if opcion == "1":
                self.consultarPorMunicipio()
            elif opcion == "2":
                self.buscarPorNombre()
            elif opcion == "3":
                self.mostrarReporteCarga()
            else:
                print("Hasta pronto")
                break

    def consultarPorMunicipio(self):
        pass
        """
        Permite seleccionar un municipio y luego una localidad geolocalizada
        para consultar su clima actual.
        """
        if len(self.municipios) == 0:
            print("No hay municipios cargados.")
            return

        print("\n===== CONSULTA POR MUNICIPIO =====")
        for indice, municipio in enumerate(self.municipios, start=1):
            print(f"{indice}) {municipio.nombre} ({municipio.contarLocalidades()} localidades)")

        opcion = input("Seleccione el número de municipio: ")
        while not opcion.isdigit() or int(opcion) not in range(1, len(self.municipios) + 1):
            print("Opción inválida. Intente nuevamente.")
            opcion = input("Seleccione el número de municipio: ")

        municipio = self.municipios[int(opcion) - 1]
        localidades = municipio.localidadesConCoordenadas()

        if len(localidades) == 0:
            print(f"El municipio {municipio.nombre} no tiene localidades con coordenadas.")
            return

        print(f"\nLocalidades de {municipio.nombre} con coordenadas:")
        for indice, localidad in enumerate(localidades, start=1):
            print(f"{indice}) {localidad.nombre} ({localidad.latitud}, {localidad.longitud})")

        opcion = input("Seleccione el número de localidad: ")
        while not opcion.isdigit() or int(opcion) not in range(1, len(localidades) + 1):
            print("Opción inválida. Intente nuevamente.")
            opcion = input("Seleccione el número de localidad: ")

        localidad = localidades[int(opcion) - 1]
        self.mostrarClimaLocalidad(localidad)

    def buscarPorNombre(self):
        pass
        """
        Busca localidades por nombre en todos los municipios y permite consultar
        el clima de la localidad seleccionada.
        """
        if len(self.municipios) == 0:
            print("No hay municipios cargados.")
            return

    def mostrarReporteCarga(self):
        pass
        texto = input("Ingrese el nombre o fragmento de localidad: ").strip()
        if texto == "":
            print("Debe ingresar un texto para buscar.")
            return

        resultados = []
        for municipio in self.municipios:
            coincidencias = municipio.buscarPorNombre(texto)
            for localidad in coincidencias:
                resultados.append((municipio, localidad))

        if len(resultados) == 0:
            print("No se encontraron localidades con ese nombre.")
            return

        print("\nResultados de búsqueda:")
        for indice, (municipio, localidad) in enumerate(resultados, start=1):
            coordenadas = "sin coordenadas" if not localidad.tieneCoordenadas() else f"({localidad.latitud}, {localidad.longitud})"
            print(f"{indice}) {municipio.nombre} - {localidad.nombre} {coordenadas}")

        opcion = input("Seleccione el número de localidad para ver el clima: ")
        while not opcion.isdigit() or int(opcion) not in range(1, len(resultados) + 1):
            print("Opción inválida. Intente nuevamente.")
            opcion = input("Seleccione el número de localidad para ver el clima: ")

        municipio, localidad = resultados[int(opcion) - 1]
        if not localidad.tieneCoordenadas():
            print(f"La localidad {localidad.nombre} en {municipio.nombre} no tiene coordenadas registradas.")
            return

        self.mostrarClimaLocalidad(localidad)

    def mostrarClimaLocalidad(self, localidad):
        """
        Consulta el clima de una localidad y muestra sus datos.
        """
        if not self.api.hayConexion():
            print("No hay conexión con Open-Meteo. No se puede consultar el clima.")
            return

        clima = self.api.consultarClimaActual(localidad.latitud, localidad.longitud)
        if clima is None:
            print("No se pudo obtener el clima actual para esta localidad.")
            return

        print(f"\nClima actual en {localidad.nombre}:")
        print(f"  Temperatura: {clima.temperatura} °C")
        print(f"  Humedad: {clima.humedad} %")
        print(f"  Viento: {clima.viento} km/h")
        print(f"  Estado: {clima.estado}")

    