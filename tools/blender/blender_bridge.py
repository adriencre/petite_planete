import socket, json, sys
code = open(sys.argv[1], encoding='utf-8').read() if len(sys.argv) > 1 else "import bpy; result = bpy.app.version_string + ' | objs: ' + str([o.name for o in bpy.data.objects])"
s = socket.create_connection(("127.0.0.1", 9876), timeout=300)
s.sendall(json.dumps({"type": "execute_code", "params": {"code": code}}).encode())
buf = b""
while True:
    chunk = s.recv(65536)
    if not chunk: break
    buf += chunk
    try:
        json.loads(buf); break
    except Exception: pass
d = buf.decode(); print(d[:300] + " ... " + d[-1500:] if len(d) > 2000 else d)
