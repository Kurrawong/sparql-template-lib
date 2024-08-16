To see this working locally, for now you can:

1. poetry build the sparql repo (https://github.com/Kurrawong/sparql) and place the wheel (created in ./dist) from that repo into this repo under ./dist
2. manually install fastapi + uvicorn
3. run simple_server.py from within /dist - this is only to serve the wheels so pyodide can fetch them
4. open pyodide_app/index.html in a browser

NB steps 1-3 won't be required in the future - we need to package the sparql lib + this one on PyPI at which point micropip can install them from there.