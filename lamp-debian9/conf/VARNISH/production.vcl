vcl 4.0;

import std;
import directors;

### {{{ PROBES, BACKENDS , ACLS , DIRECTORS
## Probes
include "includes/probes.vcl";

## Backends
include "includes/backends.vcl";

## ACLs
include "includes/acls.vcl";

## Directors ( vcl_init )
include "includes/directors.vcl";

### }}} PROBES, BACKENDS , ACLS , DIRECTORS

### {{{ RECV
sub vcl_recv {

    # Replace RealIP
    if (req.restarts == 0) {
       if (req.http.X-Forwarded-For) {
            set req.http.X-Forwarded-For = req.http.X-Forwarded-For + ", " + client.ip;
        } else {
            set req.http.X-Forwarded-For = client.ip;
        }
    }

    # Normalize the header, remove the port (in case you're testing this on various TCP ports)
    set req.http.Host = regsub(req.http.Host, ":[0-9]+", "");

    # Normalize the query arguments
    # Some issue with CMS
    # http://stackoverflow.com/questions/29929164/issue-with-wordpress-and-varnish-breaking-loadscript-php
    # set req.url = std.querysort(req.url);


    # Allow purging
    if (req.method == "PURGE") {
        if (!client.ip ~ purge) { # purge is the ACL defined at the begining
            # Not from an allowed IP? Then die with an error.
            return (synth(405, "This IP is not allowed to send PURGE requests."));
        }
        # If you got this stage (and didn't error out above), purge the cached result
        return (purge);
    }

    # Only deal with "normal" types
    if (req.method != "GET" &&
            req.method != "HEAD" &&
            req.method != "PUT" &&
            req.method != "POST" &&
            req.method != "TRACE" &&
            req.method != "OPTIONS" &&
            req.method != "PATCH" &&
            req.method != "DELETE") {
            /* Non-RFC2616 or CONNECT which is weird. */
        return (pipe);
    }

    # Only cache GET or HEAD requests. This makes sure the POST requests are always passed.
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }

    # Implementing websocket support # https://www.varnish-cache.org/docs/4.0/users-guide/vcl-example-websockets.html
    if (req.http.Upgrade ~ "(?i)websocket") {
            return (pipe);
    }

    # Some generic URL manipulation, useful for all templates that follow
    if (req.url ~ "(\?|&)(utm_source|utm_medium|utm_campaign|gclid|cx|ie|cof|siteurl)=") {
        set req.url = regsuball(req.url, "&(utm_source|utm_medium|utm_campaign|gclid|cx|ie|cof|siteurl)=([A-z0-9_\-\.%25]+)", "");
        set req.url = regsuball(req.url, "\?(utm_source|utm_medium|utm_campaign|gclid|cx|ie|cof|siteurl)=([A-z0-9_\-\.%25]+)", "?");
        set req.url = regsub(req.url, "\?&", "?");
        set req.url = regsub(req.url, "\?$", "");
    }

    # Strip hash, server doesn't need it.
    if (req.url ~ "\#") {
        set req.url = regsub(req.url, "\#.*$", "");
    }

    # Strip a trailing ? if it exists
    if (req.url ~ "\?$") {
        set req.url = regsub(req.url, "\?$", "");
    }


    # Some generic cookie manipulation, useful for all templates that follow
    # Remove the "has_js" cookie
    set req.http.Cookie = regsuball(req.http.Cookie, "has_js=[^;]+(; )?", "");

    # Remove any Google Analytics based cookies
    set req.http.Cookie = regsuball(req.http.Cookie, "__utm.=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "_ga=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "utmctr=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "utmcmd.=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "utmccn.=[^;]+(; )?", "");

    # Remove DoubleClick offensive cookies
    set req.http.Cookie = regsuball(req.http.Cookie, "__gads=[^;]+(; )?", "");

    # Remove the Quant Capital cookies (added by some plugin, all __qca)
    set req.http.Cookie = regsuball(req.http.Cookie, "__qc.=[^;]+(; )?", "");

    # Remove the AddThis cookies
    set req.http.Cookie = regsuball(req.http.Cookie, "__atuvc=[^;]+(; )?", "");

    # Remove a ";" prefix in the cookie if present
    set req.http.Cookie = regsuball(req.http.Cookie, "^;\s*", "");

    # Are there cookies left with only spaces or that are empty?
    if (req.http.cookie ~ "^\s*$") {
        unset req.http.cookie;
    }

    # Normalisation Accept-Encoding header
    if (req.http.Accept-Encoding) {
        if (req.url ~ "\.(jpg|png|gif|gz|tgz|bz2|tbz|mp3|ogg)$") {
            unset req.http.Accept-Encoding;
        } elsif (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elsif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {
            # algorithm non connu
            unset req.http.Accept-Encoding;
        }
    }

    # Large static files are delivered directly to the end-user without
    # waiting for Varnish to fully read the file first.
     if (req.url ~ "^[^?]*\.(7z|avi|bz2|flac|flv|gz|mka|mkv|mov|mp3|mp4|mpeg|mpg|ogg|ogm|opus|rar|tar|tgz|tbz|txz|wav|webm|xz|zip)(\?.*)?$") {
        unset req.http.Cookie;
        return (hash);
    }

    # Remove all cookies for static files
    if (req.url ~ "^[^?]*\.(bmp|bz2|css|doc|eot|flv|gif|gz|ico|jpeg|jpg|js|less|pdf|png|rtf|swf|txt|woff|xml)(\?.*)?$") {
        unset req.http.Cookie;
        return (hash);
    }

    # Send Surrogate-Capability headers to announce ESI support to backend
    set req.http.Surrogate-Capability = "key=ESI/1.0";

    if (req.http.Authorization) {
        # Not cacheable by default (security)
        return (pass);
    }

    return (hash);
}
### }}} RECV

### {{{ PIPE :: PASS
sub vcl_pipe {
    # Always send X-Forwarded-For
    set bereq.http.Connection = "Close";

     # Implementing websocket support
    if (req.http.upgrade) {
       set bereq.http.upgrade = req.http.upgrade;
    }
    return (pipe);
}

sub vcl_pass {
#    return (pass);
}

### }}} PIPE :: PASS

### {{{ HASH :: HIT :: MISS
sub vcl_hash {
    hash_data(req.url);

    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }

    # hash cookies for requests that have them
    if (req.http.Cookie) {
        hash_data(req.http.Cookie);
    }
}

sub vcl_hit {
    if (obj.ttl >= 0s) {
        return (deliver);
    }

    if (std.healthy(req.backend_hint)) {
       if (obj.ttl + 10s > 0s) {
           return (deliver);
       } else {
         return(miss);
      }
    } else {
        if (obj.ttl + obj.grace > 0s) {
            return (deliver);
        } else {
            return (miss);
        }
    }
    return (miss);
}

sub vcl_miss {
    return (fetch);
}
### }}} HASH :: HIT :: MISS

### {{{ BACKEND RESPONSE
sub vcl_backend_response {
    # Pause ESI request and remove Surrogate-Control header
    if (beresp.http.Surrogate-Control ~ "ESI/1.0") {
        unset beresp.http.Surrogate-Control;
        set beresp.do_esi = true;
    }


    # Enable cache for all static files
    # The same argument as the static caches from above: monitor your cache size, if you get data nuked out of it, consider giving up the static file cache.
    # Before you blindly enable this, have a read here: https://ma.ttias.be/stop-caching-static-files/
    if (bereq.url ~ "^[^?]*\.(7z|avi|bmp|bz2|css|csv|doc|docx|eot|flac|flv|gif|gz|ico|jpeg|jpg|js|less|mka|mkv|mov|mp3|mp4|mpeg|mpg|odt|otf|ogg|ogm|opus|pdf|png|ppt|pptx|rar|rtf|svg|svgz|swf|tar|tbz|tgz|ttf|txt|txz|wav|webm|webp|woff|woff2|xls|xlsx|xml|xz|zip)(\?.*)?$") {
        unset beresp.http.set-cookie;
    }

    # Large static files are delivered directly to the end-user without
    # waiting for Varnish to fully read the file first.
    # Varnish 4 fully supports Streaming, so use streaming here to avoid locking.
    if (bereq.url ~ "^[^?]*\.(7z|avi|bz2|flac|flv|gz|mka|mkv|mov|mp3|mp4|mpeg|mpg|ogg|ogm|opus|rar|tar|tgz|tbz|txz|wav|webm|xz|zip)(\?.*)?$") {
        unset beresp.http.set-cookie;
        set beresp.do_stream = true;
        set beresp.do_gzip = false;
    }

    # Sometimes, a 301 or 302 redirect formed via Apache's mod_rewrite can mess with the HTTP port that is being passed along.
    if (beresp.status == 301 || beresp.status == 302) {
        set beresp.http.Location = regsub(beresp.http.Location, ":[0-9]+", "");
    }

    # Set 2min cache if unset for static files
    if (beresp.ttl <= 0s || beresp.http.Set-Cookie || beresp.http.Vary == "*") {
        set beresp.ttl = 120s; # Important, you shouldn't rely on this, SET YOUR HEADERS in the backend
        set beresp.uncacheable = true;
        return (deliver);
    }

    # Don't cache 50x responses - varnish not cache 50x by default, it's just a security.
    if (beresp.status == 500 || beresp.status == 502 || beresp.status == 503 || beresp.status == 504) {
        return (abandon);
    }

    # Allow stale content, in case the backend goes down.
    # make Varnish keep all objects for 6 hours beyond their TTL
    set beresp.grace = 6h;

    return (deliver);
}

### }}} BACKEND RESPONSE

### {{{ DELIVER
sub vcl_deliver {

    if (obj.hits > 0) { # Add debug header to see if it's a HIT/MISS and the number of hits, disable when not needed
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }


    set resp.http.X-Cache-Hits = obj.hits;

    # Allow some information only if client.ip match for debug mode
    if (client.ip ~ debug) {
           set resp.http.X-Served-By = server.hostname;
           set resp.http.X-Varnish-Ip   = server.ip;
           set resp.http.X-Varnish-Port = std.port(server.ip);
    } else {
        unset resp.http.X-Powered-By;
        unset resp.http.X-Generator;
        unset resp.http.X-Drupal-Cache;
        unset resp.http.Server;
        unset resp.http.X-Varnish;
        unset resp.http.Via;
        unset resp.http.Link;
    }

    return (deliver);
}
### }}} DELIVER

### {{{ PURGE
sub vcl_purge {
  # Only handle actual PURGE HTTP methods, everything else is discarded
  if (req.method != "PURGE") {
    # restart request
    set req.http.X-Purge = "Yes";
    return(restart);
  }
}

### }}} PURGE

### {{{ SYNTH
sub vcl_synth {
    if (resp.status == 720) {
        set resp.http.Location = resp.reason;
        set resp.status = 301;
        set resp.reason = "Moved Permanently";
    } elseif (resp.status == 721) {
        set resp.http.Location = resp.reason;
        set resp.status = 302;
        set resp.reason = "Moved Temporary";
    }

    return (deliver);
}
### }}} SYNTH

### {{{ INIT
sub vcl_init {
    return (ok);
}

sub vcl_fini {
    return (ok);
}

### }}} INIT :: END