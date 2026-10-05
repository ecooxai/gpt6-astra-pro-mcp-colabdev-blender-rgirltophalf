"""Serve the portable studio without requiring filesystem symlinks."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.glb':'model/gltf-binary','.wasm':'application/wasm','.js':'text/javascript; charset=utf-8','.blend':'application/octet-stream'}
    def translate_path(self,path):
        url=unquote(urlsplit(path).path)
        routes={'/artifacts/':ROOT/'build','/reference/':ROOT/'reference','/history/':ROOT/'progress'}
        base=ROOT/'preview';tail=url.lstrip('/')
        for prefix,directory in routes.items():
            if url.startswith(prefix):base=directory;tail=url[len(prefix):];break
        resolved=(base/tail).resolve()
        if not resolved.is_relative_to(base.resolve()):return str(ROOT/'__invalid_request__')
        return str(resolved)
    def list_directory(self,path):
        self.send_error(403,'Directory listing is disabled; use the studio file links.')
        return None
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','same-origin')
        if urlsplit(self.path).path.endswith('status.json'):self.send_header('Cache-Control','no-store')
        super().end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8776);parser.add_argument('--host',default='0.0.0.0');args=parser.parse_args()
    server=ThreadingHTTPServer((args.host,args.port),Handler)
    print(f'Studio: http://{args.host}:{args.port}/ · {ROOT}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
