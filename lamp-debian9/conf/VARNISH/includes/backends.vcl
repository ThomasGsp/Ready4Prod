backend default_backend {
  .host = "127.0.0.1";         # IP or Hostname of backend
  .port = "81";                # Port Apache or whatever is listening
  .connect_timeout = 5s;       # How long to wait for a backend connection?
  .first_byte_timeout = 30s;   # How long to wait before we receive a first byte from our backend?
  .between_bytes_timeout = 2s; # How long to wait between bytes received from our backend?
  .probe = default_probe;      # Use probes.vlc
  # .max_connections = 400;
}