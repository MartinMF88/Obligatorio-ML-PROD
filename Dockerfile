# imagen base
FROM python:3.9.6 as base

# crea y fija directorio de trabajo
WORKDIR /scrapers

COPY requirements.in requirements.in

RUN pip install -U pip
RUN pip install pip-tools
RUN pip-compile requirements.in

FROM python:3.9.6 as main
WORKDIR /scrapers
COPY --from=base /scrapers/requirements.txt /scrapers/requirements.txt

# instala las dependencias de nuestro proyecto
RUN pip install -r requirements.txt

# copia todo hacia el contenedor
COPY . .

# ejecuta bash para usar la línea de comandos
CMD ["bash"]

# docker build -t scrapy .
# docker run -it scrapy bash 
# scrapy crawl gallito
