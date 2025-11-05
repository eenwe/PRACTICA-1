import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

API_KEY_AV = "26D89FF9C6KRYKWO"



##### DESCARGA DE DATOS #####


def descargar_datos_yf(tickers, inicio, fin, guardar_csv=False):
    """
    DESCRIPCIÓN DE LA FUNCIÓN
    --------------------------
    Esta función accede a Yahoo Finance y descarga datos dando valores de inicio y fin
    PARÁMETROS
    ----------
        tickers
        inicio
        guardar_csv
    Return:
    -------
        Devuelve un dataframe con los datos descargados en las de que la descarga sea correcta
    """
    try:
        datos = yf.download(tickers, start=inicio, end=fin, group_by='ticker', progress=False)
        tickers_validos = []
        datos_filtrados = {}

        # Manejo de un solo ticker o múltiples
        for ticker in tickers:
            try:
                df = datos[ticker] if isinstance(datos.columns, pd.MultiIndex) else datos
                if df.empty:
                    print(f"No se encontraron datos válidos para {ticker}.")
                    continue
                tickers_validos.append(ticker)
                datos_filtrados[ticker] = df

                if guardar_csv:
                    nombre_archivo = f"{ticker}_yf.csv"
                    df.to_csv(nombre_archivo)
                    print(f"Datos guardados en: {nombre_archivo}")

            except Exception:
                print(f"Error al procesar datos de {ticker} (puede no existir en Yahoo Finance).")

        if not tickers_validos:
            print("No se encontraron datos válidos para ninguno de los tickers introducidos.")
            return None

        print(f"\nDatos descargados correctamente para: {', '.join(tickers_validos)}")
        return datos_filtrados

    except Exception as e:
        print(f"Error al descargar los datos: {e}")
        return None


# Esta función descarga los datos de AV
def descargar_datos_av(tickers, inicio, fin, guardar_csv=False, api_key=API_KEY_AV):
    """
    Descarga datos históricos desde la API de Alpha Vantage
    
    Se obtiene la información ajustada diaria de cada ticker solicitado y se procesan los datos en formato pandas
    Para mantener coherencia con otras fuentes se renombran las columnas a un formato estándar
    Además, se filtran los datos según el rango de fechas indicado y se incluye manejo de errores y validaciones
    
    """
    ts = TimeSeries(key=api_key, output_format='pandas')
    datos = {}
    tickers_validos = []

    try:
        for ticker in tickers:
            try:
                df, meta = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()

                if all(col in df.columns for col in [
                    '1. open', '2. high', '3. low', '4. close',
                    '5. adjusted close', '6. volume'
                ]):
                    df = df.rename(columns={
                        '1. open': 'Open',
                        '2. high': 'High',
                        '3. low': 'Low',
                        '4. close': 'Close',
                        '5. adjusted close': 'Adj Close',
                        '6. volume': 'Volume'
                    })
                else:
                    print(f" Formato inesperado en columnas para {ticker}: {df.columns.tolist()}")
                    continue

                df_filtrado = df.loc[inicio:fin]
                if df_filtrado.empty:
                    print(f"Sin datos en el rango seleccionado para {ticker}.")
                    continue

                datos[ticker] = df_filtrado
                tickers_validos.append(ticker)
                print(f"\nDatos Alpha Vantage descargados para: {ticker}")

                if guardar_csv:
                    nombre_archivo = f"{ticker}_av.csv"
                    df_filtrado.to_csv(nombre_archivo)
                    print(f"Datos guardados en: {nombre_archivo}")

            except Exception:
                print(f"Error al descargar datos de {ticker}. Puede no existir en Alpha Vantage.")

        if not tickers_validos:
            print("No se encontraron datos válidos para ninguno de los tickers introducidos.")
            return None

        return datos

    except Exception as e:
        print(f"Error al descargar datos Alpha Vantage: {e}")
        return None



##### CLASES #####


class Report:
    """
    Descripción de la clase:
    ------------------------
    Dado un ticker, permite aplicar ciertos métodos para luego obetner datos y gráficas
    Atributos:
    -----------
        ticker
        dataframe
    Métodos:
    --------
    fechas() -> obtiene fechas   
    cierre() -> devuelve los precios de cierre ajustados o normales
    retornos_diarios() -> calcula los retornos porcentuales diarios
    media_retorno() -> calcula el retorno medio diario
    desviacion_tipica() -> calcula la desviación estándar de los retornos diarios
    retorno_acumulado() -> devuelve el rendimiento total en el periodo analizado
    volatilidad_anualizada() -> estima la volatilidad anual asumiendo 252 días de mercado
    retorno_anualizado() -> calcula el retorno anualizado a partir del retorno acumulado
    max_drawdown() -> determina la máxima caída desde un pico histórico
    ratio_sharpe(rf=0.0) -> calcula el ratio Sharpe ajustado por el tipo libre de riesgo
    graficar_precios(): muestra la evolución del precio en el tiempo
    graficar_retornos(): muestra los retornos diarios en una serie temporal
    graficar_hist_retornos(): representa un histograma de la distribución de retornos diarios

    """
    def __init__(self, ticker: str, dataframe: pd.DataFrame):
        self.ticker = ticker
        self.data = dataframe
        self.columna_cierre = 'Adj Close' if 'Adj Close' in dataframe.columns else 'Close'
        self._retornos = self.data[self.columna_cierre].pct_change().dropna()
        self._media = self._retornos.mean()
        self._std = self._retornos.std()

    def fechas(self):
        return self.data.index

    def cierre(self):
        return self.data[self.columna_cierre]

    def retornos_diarios(self):
        return self._retornos

    def media_retorno(self):
        return self._media

    def desviacion_tipica(self):
        return self._std

    def retorno_acumulado(self):
        return (self.cierre().iloc[-1] / self.cierre().iloc[0]) - 1

    def volatilidad_anualizada(self):
        return self._std * np.sqrt(252)

    def retorno_anualizado(self):
        n_dias = (self.fechas()[-1] - self.fechas()[0]).days
        return ((1 + self.retorno_acumulado()) ** (252 / n_dias)) - 1

    def max_drawdown(self):
        acumulado = (1 + self._retornos).cumprod()
        pico = acumulado.cummax()
        drawdown = (acumulado - pico) / pico
        return drawdown.min()

    def ratio_sharpe(self, rf=0.0):
        exceso = self._retornos - rf / 252
        return exceso.mean() / exceso.std() * np.sqrt(252)

    def graficar_precios(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.data.index, self.cierre(), label=f"{self.ticker}")
        plt.title(f" Evolución del precio - {self.ticker}")
        plt.xlabel("Fecha")
        plt.ylabel("Precio")
        plt.legend()
        plt.grid(True)
        plt.show()

    def graficar_retornos(self):
        plt.figure(figsize=(10, 4))
        plt.plot(self._retornos, color='orange')
        plt.title(f" Retornos diarios - {self.ticker}")
        plt.xlabel("Fecha")
        plt.ylabel("Retorno diario (%)")
        plt.grid(True)
        plt.show()

    def graficar_hist_retornos(self):
        plt.figure(figsize=(8, 4))
        plt.hist(self._retornos * 100, bins=30, color='purple', alpha=0.7)
        plt.title(f" Distribución de retornos - {self.ticker}")
        plt.xlabel("Retorno diario (%)")
        plt.ylabel("Frecuencia")
        plt.grid(True)
        plt.show()

    def simular_montecarlo(self, n_paths=1000, n_dias=252):
        mu = self.media_retorno() * 252
        sigma = self.desviacion_tipica() * np.sqrt(252)
        S0 = self.cierre().iloc[-1]
        dt = 1 / 252
        precios = np.zeros((n_dias, n_paths))
        precios[0] = S0

        for t in range(1, n_dias):
            rand = np.random.normal(0, 1, n_paths)
            precios[t] = precios[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rand)

        plt.figure(figsize=(10, 6))
        plt.plot(precios, alpha=0.1, color='blue')
        plt.title(f"Simulación Monte Carlo Normal - {self.ticker}")
        plt.xlabel("Días")
        plt.ylabel("Precio simulado")
        plt.grid(True)
        plt.show()



class Datosprint(Report):
    def resumen(self):
        print(f"\nResumen para {self.ticker}")
        print(f"Fechas: {self.fechas()[0].date()} → {self.fechas()[-1].date()}")
        print(f"Retorno acumulado: {self.retorno_acumulado() * 100:.2f}%")
        print(f"Retorno anualizado: {self.retorno_anualizado() * 100:.2f}%")
        print(f"Volatilidad anualizada: {self.volatilidad_anualizada() * 100:.2f}%")
        print(f"Sharpe ratio: {self.ratio_sharpe():.2f}")
        print(f"Máx. drawdown: {self.max_drawdown() * 100:.2f}%")
        print(f"Último cierre: {self.cierre().iloc[-1]:.2f}")



##### CLASE DE CARTERA #####


class Cartera:
    """
    Descripción de la clase:
    ------------------------
    Clase que representa una cartera de inversión formada por varios activos y sus pesos asociados

    Atributos:
    -----------
        activos
        pesos
        retorno_df
        retorno_cartera

    Métodos:
    --------
        _construir_retorno_df() -> construye el DataFrame con los retornos diarios de cada activo
        _retorno_cartera() -> calcula el retorno diario total de la cartera
        retorno_esperado() -> devuelve el retorno medio diario de la cartera
        volatilidad_estimada() -> calcula la desviación estándar del retorno diario de la cartera
        retorno_anualizado() -> estima el retorno anualizado según el retorno medio diario
        volatilidad_anualizada() ->  estima la volatilidad anualizada de la cartera
        sharpe_ratio(rf=0.0) ->  calcula el ratio Sharpe ajustado por el tipo libre de riesgo
        max_drawdown() -> determina la máxima pérdida desde un pico histórico de valor
        resumen(): muestra en consola las métricas principales de la cartera
        graficar_pesos(): muestra un gráfico circular con la distribución de los pesos
        graficar_evolucion(): muestra la evolución temporal del valor total de la cartera

    """
    def __init__(self, activos: list, pesos: dict):
        self.activos = activos
        self.pesos = pesos
        self.retorno_df = self._construir_retorno_df()
        self.retorno_cartera = self._retorno_cartera()

    def _construir_retorno_df(self):
        retornos = pd.concat({a.ticker: a.retornos_diarios() for a in self.activos}, axis=1).dropna()
        return retornos

    def _retorno_cartera(self):
        pesos_vector = np.array([self.pesos[a.ticker] for a in self.activos])
        retorno_port = self.retorno_df.dot(pesos_vector)
        return retorno_port

    def retorno_esperado(self):
        return self.retorno_cartera.mean()

    def volatilidad_estimada(self):
        cov = self.retorno_df.cov()
        w = np.array([self.pesos[a.ticker] for a in self.activos])
        return np.sqrt(np.dot(w.T, np.dot(cov, w)))

    def retorno_anualizado(self):
        return (1 + self.retorno_esperado()) ** 252 - 1

    def volatilidad_anualizada(self):
        return self.volatilidad_estimada() * np.sqrt(252)

    def sharpe_ratio(self, rf=0.0):
        exceso = self.retorno_cartera - rf / 252
        return exceso.mean() / exceso.std() * np.sqrt(252)

    def max_drawdown(self):
        acumulado = (1 + self.retorno_cartera).cumprod()
        pico = acumulado.cummax()
        drawdown = (acumulado - pico) / pico
        return drawdown.min()

    def resumen(self):
        print("\n Resumen de cartera:")
        for a in self.activos:
            peso = self.pesos.get(a.ticker, 0)
            print(f" - {a.ticker}: peso {peso:.2f}")
        print(f"\n Retorno esperado diario: {self.retorno_esperado() * 100:.3f}%")
        print(f"Retorno anualizado: {self.retorno_anualizado() * 100:.2f}%")
        print(f"Volatilidad anualizada: {self.volatilidad_anualizada() * 100:.2f}%")
        print(f"Sharpe ratio: {self.sharpe_ratio():.2f}")
        print(f"Máx. drawdown: {self.max_drawdown() * 100:.2f}%")

    def graficar_pesos(self):
        etiquetas = list(self.pesos.keys())
        valores = list(self.pesos.values())
        plt.figure(figsize=(6, 6))
        plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90)
        plt.title("Distribución de pesos de la cartera")
        plt.show()

    def graficar_evolucion(self):
        plt.figure(figsize=(10, 5))
        valor_cartera = (1 + self.retorno_cartera).cumprod()
        plt.plot(valor_cartera, color="black")
        plt.title("Evolución histórica del valor de la cartera")
        plt.xlabel("Fecha")
        plt.ylabel("Valor normalizado (inicio = 1)")
        plt.grid(True)
        plt.show()

    def simular_montecarlo(self, n_paths=1000, n_dias=252):
        mu = self.retorno_esperado() * 252
        sigma = self.volatilidad_estimada() * np.sqrt(252)
        S0 = 1
        dt = 1 / 252
        precios = np.zeros((n_dias, n_paths))
        precios[0] = S0

        for t in range(1, n_dias):
            rand = np.random.normal(0, 1, n_paths)
            precios[t] = precios[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rand)

        plt.figure(figsize=(10, 6))
        plt.plot(precios, alpha=0.1, color='red')
        plt.title("Simulación Monte Carlo Normal - Cartera")
        plt.xlabel("Días")
        plt.ylabel("Valor simulado")
        plt.grid(True)
        plt.show()


##### MONTE CARLO #####


"""
Se definen tres clases para realizar simulaciones Monte Carlo aplicadas a una cartera de inversión

La clase MonteCarloSimulador actúa como clase base y permite simular trayectorias bajo una distribución normal
A partir de ella se heredan dos clases:
    - MonteCarloTStudent: utiliza la distribución t-Student para capturar colas más pesadas
    - MonteCarloEmpirico: genera trayectorias mediante muestreo bootstrap de retornos históricos

El método __init__ define los parámetros principales de la simulación:
    - cartera: instancia de la clase Cartera
    - n_paths: número de trayectorias simuladas
    - n_dias: horizonte temporal en días

Cada clase incluye un método simular() para generar las trayectorias y graficar() para visualizar los resultados
"""

class MonteCarloSimulador:
    def __init__(self, cartera: Cartera, n_paths=1000, n_dias=252):
        self.cartera = cartera
        self.n_paths = n_paths
        self.n_dias = n_dias

    def simular(self):
        mu = self.cartera.retorno_esperado() * 252
        sigma = self.cartera.volatilidad_estimada() * np.sqrt(252)
        S0 = 1
        dt = 1 / 252
        precios = np.zeros((self.n_dias, self.n_paths))
        precios[0] = S0

        for t in range(1, self.n_dias):
            rand = np.random.normal(0, 1, self.n_paths)
            precios[t] = precios[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rand)

        self.precios = precios
        return precios

    def graficar(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.precios, alpha=0.1, color='blue')
        plt.title("Simulación Monte Carlo (Normal)")
        plt.xlabel("Días")
        plt.ylabel("Valor simulado")
        plt.grid(True)
        plt.show()


class MonteCarloTStudent(MonteCarloSimulador):
    def __init__(self, cartera: Cartera, n_paths=1000, n_dias=252, df=5):
        super().__init__(cartera, n_paths, n_dias)
        self.df = df

    def simular(self):
        mu = self.cartera.retorno_esperado() * 252
        sigma = self.cartera.volatilidad_estimada() * np.sqrt(252)
        S0 = 1
        dt = 1 / 252
        precios = np.zeros((self.n_dias, self.n_paths))
        precios[0] = S0

        for t in range(1, self.n_dias):
            rand_t = np.random.standard_t(df=self.df, size=self.n_paths)
            rand_t = rand_t / np.sqrt(self.df / (self.df - 2))
            precios[t] = precios[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rand_t)

        self.precios = precios
        return precios

    def graficar(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.precios, alpha=0.1, color='green')
        plt.title(f"Simulación Monte Carlo (t-Student, df={self.df})")
        plt.xlabel("Días")
        plt.ylabel("Valor simulado")
        plt.grid(True)
        plt.show()


class MonteCarloEmpirico(MonteCarloSimulador):
    def simular(self):
        retornos_hist = self.cartera.retorno_cartera.values
        S0 = 1
        precios = np.zeros((self.n_dias, self.n_paths))
        precios[0] = S0

        for t in range(1, self.n_dias):
            rand_emp = np.random.choice(retornos_hist, size=self.n_paths, replace=True)
            precios[t] = precios[t - 1] * (1 + rand_emp)

        self.precios = precios
        return precios

    def graficar(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.precios, alpha=0.1, color='orange')
        plt.title("Simulación Monte Carlo (Distribución Empírica - Bootstrap)")
        plt.xlabel("Días")
        plt.ylabel("Valor simulado")
        plt.grid(True)
        plt.show()



##### INPUTS #####


try:
    """
    Bloque principal de ejecución del programa
    
    Solicita al usuario los parámetros de entrada (tickers, fechas, fuente de datos y pesos) y valida su formato
    Descarga los precios históricos desde la fuente seleccionada (Yahoo Finance o Alpha Vantage)
    Crea objetos de tipo Datosprint para cada activo y genera una cartera con los pesos definidos por el usuario
    Permite visualizar métricas, gráficos y realizar simulaciones Monte Carlo con diferentes distribuciones
    Incluye validaciones de errores y bucles interactivos para asegurar la coherencia de los datos ingresados
    
    """
    while True:
        tickers = input("Tickers separados por coma (ej: AAPL,MSFT): ").split(",")
        tickers = [t.strip().upper() for t in tickers if t.strip()]
        if not tickers:
            print("Debes introducir al menos un ticker.")
            continue

        inicio = input("Fecha inicio (YYYY-MM-DD): ")
        fin = input("Fecha fin (YYYY-MM-DD): ")
        guardar = input("¿Guardar CSV? (s/n): ").lower() == "s"
        fuente = input("Fuente de datos (yf/alpha): ").lower()

        activos = []

        if fuente == "yf":
            datos = descargar_datos_yf(tickers, inicio, fin, guardar)
        elif fuente == "alpha":
            datos = descargar_datos_av(tickers, inicio, fin, guardar, api_key=API_KEY_AV)
        else:
            print("Fuente no reconocida. Usa 'yf' o 'alpha'.")
            continue

        if datos is None:
            print("No se pudieron descargar datos válidos. Intenta nuevamente.")
            continue

        for ticker in datos:
            obj = Datosprint(ticker, datos[ticker])
            obj.resumen()
            activos.append(obj)

        if not activos:
            print("No hay activos válidos para crear la cartera. Reintenta.")
            continue

        while True:
            pesos = {}
            for ticker in [a.ticker for a in activos]:
                while True:
                    try:
                        peso = float(input(f"Peso para {ticker} (ej: 0.5): "))
                        if peso < 0:
                            print("El peso no puede ser negativo.")
                            continue
                        pesos[ticker] = peso
                        break
                    except ValueError:
                        print("Introduce un número válido.")

            suma_pesos = sum(pesos.values())
            if abs(suma_pesos - 1) > 1e-6:
                print(f"La suma de los pesos ({suma_pesos:.2f}) no es igual a 1. Reingrésalos.")
                continue
            break

        cartera = Cartera(activos, pesos)
        cartera.resumen()

        ver_graficos = input("\n ¿Deseas ver gráficos? (s/n): ").lower()
        if ver_graficos == "s":
            print("\nOpciones disponibles:")
            print("1 - Precio histórico")
            print("2 - Retornos diarios")
            print("3 - Histograma de retornos")
            print("4 - Pesos de cartera")
            print("5 - Evolución de la cartera")
            print("6 - Simulación Monte Carlo")

            opciones = input("Selecciona números separados por coma (ej: 1,3,4): ").split(",")
            opciones = [o.strip() for o in opciones]

            for activo in activos:
                if "1" in opciones:
                    activo.graficar_precios()
                if "2" in opciones:
                    activo.graficar_retornos()
                if "3" in opciones:
                    activo.graficar_hist_retornos()

            if "4" in opciones:
                cartera.graficar_pesos()

            if "5" in opciones:
                cartera.graficar_evolucion()

            if "6" in opciones:
                print("\n Selecciona tipo de distribución para la simulación Monte Carlo:")
                print("1 - Normal (por defecto)")
                print("2 - t-Student")
                print("3 - Empírica (bootstrap histórico)")

                tipo = input("Opción (1/2/3): ").strip()

                if tipo == "2":
                    df = int(input("Grados de libertad para t-Student (Por defecto: 5): ") or 5)
                    sim = MonteCarloTStudent(cartera, n_paths=1000, n_dias=252, df=df)
                elif tipo == "3":
                    sim = MonteCarloEmpirico(cartera, n_paths=1000, n_dias=252)
                else:
                    sim = MonteCarloSimulador(cartera, n_paths=1000, n_dias=252)
                sim.simular()
                sim.graficar()
                print("Simulación Monte Carlo completada.")
        
        ver_mc_directa = input("\n¿Deseas mostrar simulaciones Monte Carlo normales? (s/n): ").lower()
        if ver_mc_directa == "s":
            print("\n Opciones disponibles:")
            print("1 - Simulación Monte Carlo individual por activo (clase Report)")
            print("2 - Simulación Monte Carlo de la cartera completa")
            print("3 - Ambas simulaciones")

            opcion_mc = input("Selecciona una opción (1/2/3): ").strip()

            if opcion_mc in ["1", "3"]:
                print("\nSimulaciones Monte Carlo (activos individuales):")
                for activo in activos:
                    print(f" - {activo.ticker}")
                    activo.simular_montecarlo()

            if opcion_mc in ["2", "3"]:
                print("\n Simulación Monte Carlo Normal para la cartera completa...")
                cartera.simular_montecarlo()

            print("Simulaciones Monte Carlo completadas.")
        

        break  

except Exception as e:
    print("Error en la ejecución:", e)


