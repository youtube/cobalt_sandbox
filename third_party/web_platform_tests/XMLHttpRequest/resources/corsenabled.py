import time

def main(request, response):
    headers = [("Access-Control-Allow-Origin", "*"),
               ("Access-Control-Allow-Credentials", "true"),
               ("Access-Control-Allow-Methods", "GET, POST, PUT, FOO"),
               ("Access-Control-Allow-Headers", "x-test, x-foo"),
               ("Access-Control-Expose-Headers", "x-request-method, x-request-content-type, x-request-query, x-request-content-length, x-request-data")]

    if "delay" in request.GET:
        delay = int(request.GET.first("delay"))
        time.sleep(delay)

    if "safelist_content_type" in request.GET:
        headers.append(("Access-Control-Allow-Headers", "content-type"))

    headers.append(("X-Request-Method", request.method))
    headers.append(("X-Request-Query", request.url_parts.query if request.url_parts.query else "NO"))
    headers.append(("X-Request-Content-Length", request.headers.get("Content-Length", "NO")))
    headers.append(("X-Request-Content-Type", request.headers.get("Content-Type", "NO")))
    headers.append(("X-Request-Data", request.body))

    return headers, "Test"