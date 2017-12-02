probe default_probe {
  .request =
      "HEAD / HTTP/1.1"
      "Host: localhost"
      "Connection: close"
       "User-Agent: Varnish Health Probe";

  .expected_response  = 200;
  .timeout            = 1s;  # timing out after 1 second.
  .interval           = 5s;  # check the health of each backend every 5 seconds
  .window             = 5;   # If 3 out of the last 5 polls succeeded the backend is considered healthy, otherwise it will be marked as sick
  .threshold          = 3;
}