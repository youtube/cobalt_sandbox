import time

def main(request, response):
    delay = float(request.GET.first("ms", 500)) / 1E3
    count = int(request.GET.first("count", 50))
    # Read request body
    request.body
    time.sleep(delay)
    response.headers.set("Content-type", "text/plain")
    response.write_status_headers()
    time.sleep(delay)
    for i in range(count):
        response.writer.write_content("TEST_TRICKLE\n")
        time.sleep(delay)
