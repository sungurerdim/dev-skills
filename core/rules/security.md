# Sec — secrets, transport, injection, exposure, resilience bounds, app hardening, billing integrity

Applies to every project type. OWASP Top 10 IDs are the 2025 edition (owasp.org/Top10/2025); ASVS is 5.0.0 — label a tool's output with the ASVS version the tool itself cites. Secret file names and content regexes live once in [../secret-patterns.md](../secret-patterns.md). Dependency audit, lockfiles, pinning, licences and SBOM are the `ci` area (DOP-06, DOP-11, DOP-14, DOP-17); sessions and object-level access are AUTH-02, AUTH-11; SQL is DB-01.

### SEC-01 [CRITICAL] Secret in source or a tracked file
- **Detect:** a tracked file from the filename set or a content-regex match in [../secret-patterns.md](../secret-patterns.md); credentials in config (`settings.py`, `application.yml`, `config/*.json`), Dockerfile `ENV` or a connection string. Skip `*.example`, documented placeholders and test fixtures with dummy values; every hit gets the history check from that file.
- **Mech:** T `git ls-files | grep -E '(^|/)(\.env(\.[^/]*)?|credentials\.[^/]*|secrets\.[^/]*|id_rsa|id_ed25519)$|\.(pem|key|p12|pfx|jks|keystore)$' | grep -vE '\.(example|sample|template)$'` · `git grep -nIE 'AKIA[0-9A-Z]{16}|-----BEGIN ([A-Z]+ )?PRIVATE KEY-----|sk_live_[A-Za-z0-9]{10,}|gh[pousr]_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|glpat-[A-Za-z0-9_-]{20,}|npm_[A-Za-z0-9]{36}' -- . ':!*.lock' ':!*lock.json'` · `gitleaks dir . --no-banner --no-color --redact -v | grep '^Fingerprint:'` · `gitleaks git --no-banner --no-color --redact -v | grep '^Fingerprint:'`
- **Fix:** never auto-fixed — rotate the credential first, then load it at runtime from the environment or a secret manager, ignore the file and keep a placeholder in `.env.example`; a third-party key a client must not hold moves behind a server-side proxy.
- **Impact:** a committed secret reaches every clone, fork, build artefact and the git history; removing the line does not revoke it.
- **Source:** Twelve-Factor; OWASP A07:2025; CWE-798; Gitleaks (github.com/gitleaks/gitleaks).

### SEC-25 [HIGH] Firebase API key unrestricted or bound to the wrong app
applies_when: platforms∋android
- **Detect:** a committed `google-services.json` whose API key has no Android restriction (package name plus SHA-1) in the Google Cloud console; its `package_name` unequal to the build's `applicationId`; a debug or release variant pointing at the wrong Firebase project or missing its SHA-1. The key restriction is console state: name it as the owner's check.
- **Mech:** T `git ls-files '*google-services.json'` · `git grep -nIE 'applicationId|package_name' -- '*.gradle' '*.gradle.kts' '*google-services.json'`
- **Fix:** restrict the key to the app's package name, its SHA-1 fingerprints and the APIs it calls; match `package_name` to `applicationId`; one config per variant with its fingerprint registered.
- **Impact:** a key lifted from the APK calls the project's Google APIs on the owner's bill; a mismatch silently breaks sign-in or push for that build.
- **Source:** Least privilege; Firebase, Learn about using and managing API keys for Firebase; Google Cloud, API key best practices.

### SEC-04 [CRITICAL] Cleartext transport
applies_when: api≠none or deploy≠none or mobile≠none
- **Detect:** `http://` endpoints in source or config other than loopback, private ranges and XML/schema namespaces; no HTTP→HTTPS redirect; Android `usesCleartextTraffic="true"` or a network security config permitting cleartext; iOS `NSAllowsArbitraryLoads` true.
- **Mech:** T `git grep -nIE 'http://' -- ':!*.md' ':!*test*' ':!*.lock' | grep -vE 'http://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|\[::1\]|www\.w3\.org|schemas\.|json-schema\.org|xmlns)'` · `git grep -nIE 'usesCleartextTraffic="true"|cleartextTrafficPermitted="true"|NSAllowsArbitraryLoads' -- ':!*.md'`
- **Fix:** HTTPS everywhere outside loopback; redirect HTTP to HTTPS and send HSTS (NWK-03); remove platform cleartext exceptions or scope them to a named debug domain.
- **Impact:** any network intermediary reads or alters credentials, tokens and personal data in transit.
- **Source:** Secure / private by default; OWASP A04:2025; OWASP MASVS-NETWORK-1; CWE-319.

### NWK-01 [CRITICAL] TLS below 1.2 allowed
- **Detect:** TLS 1.0/1.1 or SSL enabled, or a minimum version left below 1.2, in code (`PROTOCOL_TLSv1`, `MinVersion: tls.VersionTLS10`, `SslProtocols.Tls`) or proxy config (`ssl_protocols`); weak cipher suites (RC4, 3DES, export) or OCSP stapling off in a hand-configured proxy.
- **Mech:** S `git grep -nIE 'TLSv1([^._0-9]|$)|TLSv1[._][01]([^0-9]|$)|VersionTLS1[01]([^0-9]|$)|SslProtocols\.Tls(11)?([^0-9]|$)|SSLv[23]' -- ':!*.md' | grep -viE 'NO_TLSv1|NO_SSLv|-TLSv1|!TLSv1'`
- **Fix:** minimum TLS 1.2 (1.3 preferred) through the platform default client or an explicit minimum; drop legacy protocols from proxy config; a hand-configured proxy takes the Mozilla SSL Configuration Generator Intermediate profile.
- **Impact:** downgradable connections expose traffic to known protocol attacks.
- **Source:** Secure / private by default; RFC 8996 (deprecating TLS 1.0 and 1.1); NIST SP 800-52 Rev. 2; Mozilla Server Side TLS (ssl-config.mozilla.org).

### NWK-02 [CRITICAL] Certificate verification disabled
- **Detect:** verification turned off in shipped code or config: `verify=False`, `InsecureSkipVerify: true`, `NODE_TLS_REJECT_UNAUTHORIZED=0`, `rejectUnauthorized: false`, `CURLOPT_SSL_VERIFYPEER` false, `danger_accept_invalid_certs(true)`, a trust-all `TrustManager` or `ServerCertificateValidationCallback` returning true.
- **Mech:** S `git grep -nIE 'verify[[:space:]]*=[[:space:]]*False|InsecureSkipVerify[[:space:]]*:[[:space:]]*true|NODE_TLS_REJECT_UNAUTHORIZED[[:space:]]*=?[[:space:]]*.?0|rejectUnauthorized[[:space:]]*:[[:space:]]*false|CURLOPT_SSL_VERIFYPEER[[:space:]]*(=>|,)[[:space:]]*(false|0)|danger_accept_invalid_certs\(true\)|ServerCertificateValidationCallback[[:space:]]*=.*true' -- ':!*.md'`
- **Fix:** remove the bypass; trust a staging CA by adding it to the trust store, never by disabling checks.
- **Impact:** anyone on the path presents a forged certificate and reads or changes every request.
- **Source:** Secure / private by default; OWASP A02:2025; CWE-295.

### NWK-03 [HIGH] HSTS missing or weak
applies_when: ui∋web or api≠none
- **Detect:** HTTPS responses without `Strict-Transport-Security`, or `max-age` below 31536000 or without `includeSubDomains` where subdomains are served over HTTPS. Preload submission and rollout are DEP-25.
- **Mech:** T `git grep -qIiE 'Strict-Transport-Security|hsts' -- ':!*.md' || echo 'no HSTS header in tracked code'` · `git grep -nIiE 'max-age=([0-9]{1,7}|[0-2][0-9]{7})([^0-9]|$)' -- ':!*.md' | grep -i 'strict-transport'`
- **Fix:** `Strict-Transport-Security: max-age=31536000; includeSubDomains` at minimum (63072000 is the OWASP recommendation); ramp up from a short `max-age` on a first rollout.
- **Impact:** the first request, or any after a cleared cache, can be downgraded to HTTP and intercepted before the redirect.
- **Source:** Secure / private by default; RFC 6797; OWASP HTTP Strict Transport Security Cheat Sheet; hstspreload.org (preload needs max-age ≥ 31536000).

### NWK-04 [HIGH] No certificate pinning where the threat model needs it
applies_when: mobile≠none or ui∋desktop
- **Detect:** a native app handling payments, health or account credentials calling its own API with no pin set (`network_security_config.xml` `<pin-set>`, OkHttp `CertificatePinner`, iOS `NSPinnedDomains` or a `URLSession` delegate); a pin set with a single pin and no backup.
- **Mech:** T `git grep -qIE 'pin-set|CertificatePinner|NSPinnedDomains|TrustKit|evaluateServerTrust' -- ':!*.md' || echo 'no certificate pinning in tracked code'`
- **Fix:** pin the public-key hash of the leaf or intermediate with at least one backup pin and an expiry; ship a pin update before rotating keys.
- **Impact:** a coerced CA or a user-installed root lets an attacker read sensitive API traffic undetected.
- **Source:** Defense in depth; OWASP MASVS-NETWORK-2; Android, Network security configuration.

### SEC-05 [CRITICAL] Input reaches an interpreter or business logic unchecked
- **Detect:** request, file, webhook, queue, CLI or environment input passed to business logic without a schema check (type, format, range, length, allowed values), or checked only in the client (form, app) and not again on the server; input concatenated into a shell command (`os.system`, `subprocess` with `shell=True`, `child_process.exec`, `Runtime.exec` with a single string, `shell_exec`), `eval`/`new Function`, HTML sinks (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `|safe`, `mark_safe`, Angular `bypassSecurityTrust*`), LDAP or XPath queries, template source. SQL is DB-01.
- **Mech:** T `git grep -nIE 'os\.system\(|shell[[:space:]]*=[[:space:]]*True|child_process|\.exec(Sync)?\(|Runtime\.getRuntime\(\)\.exec|shell_exec\(|passthru\(|eval\(|new Function\(|innerHTML[[:space:]]*=|dangerouslySetInnerHTML|v-html|\|[[:space:]]*safe|mark_safe\(|bypassSecurityTrust|render_template_string\(' -- ':!*test*' ':!*.md'`
- **Fix:** validate at the boundary with the stack's schema library and reject invalid input (400) rather than repairing it; pass arguments as an array, never through a shell; encode on output with the template engine's auto-escaping, and sanitize with DOMPurify where raw HTML must render; never evaluate input.
- **Impact:** one unchecked path to an interpreter gives an attacker code execution or another user's session.
- **Source:** Fail fast; Defense in depth; OWASP A05:2025; OWASP Input Validation and XSS Prevention Cheat Sheets; CWE-20/77/78/79/94.

### SEC-18 [CRITICAL] Untrusted data deserialized into objects
- **Detect:** native object deserialization of data that crosses a trust boundary (request, cookie, cache, queue, upload): Python `pickle`/`marshal`/`shelve`, `yaml.load` without a safe loader, Java `ObjectInputStream`, .NET `BinaryFormatter`/`NetDataContractSerializer`, PHP `unserialize`, Ruby `Marshal.load`/`YAML.load`, JSON libraries with polymorphic type handling enabled (`TypeNameHandling`, `enableDefaultTyping`).
- **Mech:** T `git grep -nIE 'pickle\.loads?\(|marshal\.loads?\(|shelve\.open\(|yaml\.load\(|ObjectInputStream|BinaryFormatter|NetDataContractSerializer|unserialize\(|Marshal\.load|YAML\.load\(|TypeNameHandling\.(All|Auto|Objects)|enableDefaultTyping|activateDefaultTyping' -- ':!*test*' ':!*.md'`
- **Fix:** exchange plain data formats (JSON, protobuf) mapped onto explicit types; `yaml.safe_load`; an allow-list of types where polymorphism is unavoidable; sign data that must round-trip through a client and verify before reading it.
- **Impact:** deserializing attacker-controlled bytes runs attacker-chosen code in the process.
- **Source:** Secure / private by default; OWASP A08:2025; OWASP Deserialization Cheat Sheet; CWE-502.

### SEC-19 [HIGH] Uploaded files and archives trusted by name or path
applies_when: api≠none or ui≠none
- **Detect:** an upload stored under the client's file name or inside the web root; type decided by extension or `Content-Type` alone; no size limit per endpoint; archive extraction (`extractall`, `ZipFile`, `ZipInputStream`, `archive/zip`, `tar`) or a user-supplied path joined to a base directory with no check that the resolved path stays inside it (`..`, absolute paths, symlinks).
- **Mech:** T `git grep -nIE 'extractall\(|extractfile\(|ZipFile|ZipInputStream|ZipArchive|archive/(zip|tar)|tarfile\.open|multer|UploadFile|MultipartFile|FormFile\(|move_uploaded_file|send_?[Ff]ile\(' -- ':!*test*' ':!*.md'`
- **Fix:** store under a generated name outside the web root (or in object storage) with the size capped (NWK-06); check content type by magic bytes against an allow-list; resolve every extracted or joined path and reject it unless it stays under the target directory; cap the extracted total size and entry count.
- **Impact:** a crafted file overwrites code or config (zip-slip), is served back as executable content, or a zip bomb fills the disk.
- **Source:** Fail fast; OWASP File Upload Cheat Sheet; CWE-22, CWE-434, CWE-409.

### SEC-06 [CRITICAL] Weak cryptography or randomness
- **Detect:** MD5, SHA-1, DES, 3DES, RC4 or ECB used for security (signatures, password storage, tokens, integrity of untrusted data); a fixed or reused IV/nonce; hand-written crypto; tokens, IDs or codes from a non-cryptographic generator (`Math.random`, `random.random`, `rand()`, `java.util.Random`).
- **Mech:** T `git grep -nIwE 'md5|MD5|sha1|SHA1|SHA-1|DES|3DES|RC4|ECB' -- ':!*.md' ':!*lock*'` · `git grep -nIE 'Math\.random\(|random\.(random|randint|choice)\(|rand\(|new Random\(' -- ':!*test*' ':!*.md'`
- **Fix:** the platform's vetted library: AES-GCM or ChaCha20-Poly1305 with a random nonce per message; the OS CSPRNG (`secrets`, `crypto.getRandomValues`, `crypto/rand`, `SecureRandom`) for anything an attacker must not guess. A checksum of trusted data may stay non-cryptographic; password storage is AUTH-01.
- **Impact:** broken primitives and guessable tokens fall to known, cheap attacks.
- **Source:** OWASP A04:2025; OWASP Cryptographic Storage Cheat Sheet; CWE-327/328/330/338.

### SEC-07 [HIGH] Security response headers missing
applies_when: ui∋web or api≠none
- **Detect:** no header middleware or proxy config setting the baseline: `Content-Security-Policy` (strictness is SEC-20), `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy` and CSP `frame-ancestors` (or `X-Frame-Options`); authenticated or personal-data responses without `Cache-Control: no-store`. An API that returns only JSON needs `nosniff` and no framing, not a page CSP.
- **Mech:** T `git grep -qIE 'helmet|secure_headers' -- ':!*.md' || for h in Content-Security-Policy X-Content-Type-Options Referrer-Policy 'frame-ancestors|X-Frame-Options'; do git grep -qIiE "$h" -- ':!*.md' || echo "no $h in tracked code"; done`
- **Fix:** set the baseline once in middleware or at the proxy, with `Cache-Control: no-store` on every authenticated or personal response; add COOP/COEP/CORP only when cross-origin isolation is needed.
- **Impact:** missing headers turn an HTML injection into script execution, allow clickjacking and MIME sniffing, and leave private responses in shared caches and browser history.
- **Source:** Defense in depth; OWASP Secure Headers Project; OWASP HTTP Headers Cheat Sheet.

### SEC-20 [HIGH] Content Security Policy allows inline script or misses a fetched host
applies_when: ui∋web
- **Detect:** `script-src` with `'unsafe-inline'` or `'unsafe-eval'`, or a long host allow-list with no nonce or hash; no `object-src 'none'` or `base-uri`; a host the code calls (auth, identity, any third-party API) missing from `connect-src`, so the browser blocks it with no visible error.
- **Mech:** T `git grep -nIE 'unsafe-inline|unsafe-eval|script-src|connect-src' -- ':!*.md'` · `git grep -nIoE '(fetch|axios\.[a-z]+|new WebSocket)\([[:space:]]*.(https|wss)://[A-Za-z0-9.-]+' -- ':!*test*' ':!*.md'`
- **Fix:** strict CSP: `script-src 'nonce-{random}' 'strict-dynamic'; object-src 'none'; base-uri 'none'` with a fresh nonce per response; ship as `Content-Security-Policy-Report-Only` with a report endpoint and enforce once reports are quiet; build `connect-src` from the same host constants the calls use.
- **Impact:** an allow-list CSP is bypassed through JSONP or open redirects on an allowed host, so one injection still runs script; a host missing from `connect-src` breaks a feature silently.
- **Source:** Defense in depth; OWASP Content Security Policy Cheat Sheet; W3C Content Security Policy Level 3; CWE-79.

### SAR-06 [CRITICAL] Debug mode or internals exposed in production
- **Detect:** debug switches on in a production config or build (`DEBUG = True`, `FLASK_DEBUG=1`, `APP_DEBUG=true`, PHP `display_errors=On`, ASP.NET `UseDeveloperExceptionPage` outside a development branch, Spring `debug=true`, Android `android:debuggable="true"`, Rust/C++ release builds with debug assertions or symbols shipped by accident, desktop builds with devtools enabled); error responses or crash dialogs carrying stack traces, SQL, file paths or framework versions; framework default error pages.
- **Mech:** T `git grep -nIE 'DEBUG[[:space:]]*=[[:space:]]*True|FLASK_DEBUG[[:space:]]*=[[:space:]]*1|APP_DEBUG[[:space:]]*=[[:space:]]*true|display_errors[[:space:]]*=[[:space:]]*(On|1)|UseDeveloperExceptionPage|^debug[[:space:]]*=[[:space:]]*true|android:debuggable="true"|traceback\.(print_exc|format_exc)\(|(^|[^[:alnum:]_])(err|error|e|ex|exc|exception)\.stack([^[:alnum:]_]|$)|openDevTools\(' -- ':!*test*' ':!*.md'`
- **Fix:** debug from the environment, off by default; one error handler returns a generic body with a correlation ID (RFC 9457 shape for HTTP APIs, API-02) and logs the detail server-side.
- **Impact:** internals hand an attacker the layout and versions needed for a targeted exploit; some debug modes expose a live code console.
- **Source:** Secure / private by default; OWASP A02:2025; OWASP Error Handling Cheat Sheet; CWE-209, CWE-489.

### SEC-22 [CRITICAL] Hybrid shell loads a remote origin or a debuggable WebView
applies_when: mobile=capacitor
- **Detect:** the committed `capacitor.config.*` sets `server.url` (Capacitor marks it not for production), `server.cleartext: true`, a wildcard or broad `server.allowNavigation`, or `webContentsDebuggingEnabled: true` for release; one config file with no dev/release split.
- **Mech:** T `git grep -nIE '(url|cleartext|allowNavigation|webContentsDebuggingEnabled)"?[[:space:]]*:' -- 'capacitor.config.*'`
- **Fix:** keep `server.url` and `cleartext` in a dev-only override the dev script applies; `allowNavigation` empty or exact hosts; WebView debugging off for release; read the generated native config of the release build.
- **Impact:** with a remote origin loaded, one XSS on that origin drives every registered native plugin (camera, files, contacts, secure storage).
- **Source:** Secure / private by default; Capacitor, Configuration (`server.url`, `server.cleartext`, `server.allowNavigation`); OWASP MASVS-PLATFORM-2.

### SEC-23 [HIGH] Release build not shrunk or obfuscated
applies_when: mobile≠none
- **Detect:** an Android release `buildType` with minify or resource shrinking off or absent (R8 off); a Flutter release build without `--obfuscate --split-debug-info`; React Native without Hermes bytecode; an iOS release binary keeping debug symbols.
- **Mech:** T `git grep -nIE '(is)?[mM]inifyEnabled[[:space:]]*(=[[:space:]]*)?false|(is)?[sS]hrinkResources[[:space:]]*(=[[:space:]]*)?false' -- '*.gradle' '*.gradle.kts'` · `git grep -nIE 'flutter build (apk|appbundle|ipa|ios)' -- ':!*.md' | grep -v -- '--obfuscate'`
- **Fix:** R8 minify and resource shrinking on, with keep rules for reflection-loaded classes; `flutter build <target> --obfuscate --split-debug-info=<dir>` with the symbols uploaded for crash reports (OBS-03); strip debug symbols from the iOS release binary.
- **Impact:** an unshrunk release is larger and hands a reverse engineer near-source names for logic, checks and endpoints.
- **Source:** Defense in depth; OWASP MASVS-RESILIENCE-3; Android, Shrink, obfuscate, and optimize your app; Flutter, Obfuscate Dart code.

### SEC-24 [HIGH] App data copied out through OS backup
applies_when: platforms∋android
- **Detect:** `android:allowBackup="true"`, or the attribute missing (default true), with no `dataExtractionRules` or `fullBackupContent` excluding tokens, keys and personal data.
- **Mech:** T `git grep -nIE 'android:allowBackup="true"' -- '*AndroidManifest.xml'` · `git grep -L 'allowBackup' -- '*AndroidManifest.xml'`
- **Fix:** `android:allowBackup="false"`, or keep backup and exclude sensitive files with `dataExtractionRules` (Android 12+) and `fullBackupContent`.
- **Impact:** ADB or cloud backup lifts the app's private storage, tokens included, off the device without root.
- **Source:** Secure / private by default; OWASP MASVS-STORAGE-2; Android, Back up user data with Auto Backup.

### SAR-07 [CRITICAL] Authorization fails open or lives outside the server boundary
applies_when: auth≠none or billing≠none
- **Detect:** a protected route or handler with no server-side check; a role, permission or paid entitlement taken from the client (body, header, unverified token claim) or checked only in client code; authorization enforced only at an API gateway, proxy or UI route guard while the service behind it is reachable directly; paid data readable without passing the server check; auth middleware that continues on error or timeout; a role switch whose default allows; `catch` blocks that proceed after an auth failure; permission checks scattered through business code instead of one boundary. Object ownership is AUTH-11.
- **Mech:** T `git grep -nIE 'catch[[:space:]]*(\([^)]*\))?[[:space:]]*\{[[:space:]]*(return[[:space:]]+)?next\(\)|except[^:]*:[[:space:]]*(pass|return True)|default:[[:space:]]*return[[:space:]]+true|isAdmin[[:space:]]*=[[:space:]]*req\.(body|query|headers)' -- ':!*test*' ':!*.md'`
- **Fix:** deny by default: every route passes one central policy layer (middleware, decorator, interceptor) that returns 401/403 on any error; roles and entitlements come from the server-side session or a verified token, and the route serving a paid capability checks the entitlement (a client check is display only); allow-list roles; a test lists every route and asserts each is protected or on an explicit public list.
- **Impact:** any bug, timeout or forged claim in the auth path becomes an access-control bypass.
- **Source:** Secure / private by default; Defense in depth; OWASP A01:2025, A10:2025; OWASP API5:2023 Broken Function Level Authorization; OWASP Authorization Cheat Sheet; CWE-285, CWE-636.

### SAR-01 [HIGH] Security-relevant events not audit-logged
applies_when: auth≠none or billing≠none or pii=yes
- **Detect:** login, logout, failed login, MFA and password changes, permission or role changes, admin actions, data export and deletion, consent changes and payment events produce no structured record of who, what, when, from where and the outcome; audit records writable or deletable by the application role.
- **Mech:** M (list the sensitive handlers; check each emits an audit event)
- **Fix:** one audit helper called from each sensitive path, writing `{time, actor, action, resource, source, result}` to an append-only store separate from application logs; alert on repeated failures.
- **Impact:** incident response and regulators cannot reconstruct who did what, and attacks go unnoticed.
- **Source:** OWASP A09:2025; OWASP Logging Cheat Sheet; GDPR Art. 30 and 33(5).

### SAR-02 [CRITICAL] Secrets or personal data written to logs
- **Detect:** log, print or crash-report calls emitting passwords, tokens, API keys, session IDs, card data, full request or response bodies, whole user objects, or PII fields (email, phone, address, government ID, health data); error trackers sending request bodies or user context without scrubbing. A log line naming a field (`password reset sent`) is not a hit.
- **Mech:** T `git grep -nIiE '(log|logger|console|print|debug|info|warn|error)[[:alnum:]_]*[.(].*(password|passwd|secret|token|api_?key|authorization|cookie|ssn|card_?number|req\.body|request\.body)' -- ':!*test*' ':!*.md'`
- **Fix:** log an allow-list of known-safe fields; redact or hash identifiers at one logging boundary; configure error trackers to scrub bodies and headers; a test asserts a known secret never appears in captured output.
- **Impact:** logs reach aggregators, dashboards, support staff and vendors; a log leak becomes a credential and personal-data breach.
- **Source:** Secure / private by default; OWASP Logging Cheat Sheet; CWE-532; GDPR Art. 5(1)(c) and 32.

### SAR-11 [MEDIUM] Dependency with supply-chain risk
- **Detect:** a direct dependency that is archived, unmaintained (no release for years with open security issues), has a single anonymous maintainer and install scripts, or pulls a large transitive tree for a small job. Whether it earns its place is LEAN-06; advisories are DOP-06.
- **Mech:** M (manifest plus registry metadata read at run time)
- **Fix:** replace with a maintained alternative or the standard library; vendor and pin a small abandoned piece; disable install scripts where the package manager allows.
- **Impact:** an abandoned or takeover-prone package is the cheapest path into every build.
- **Source:** OWASP A03:2025; NIST SSDF (SP 800-218) PW.4; OpenSSF Scorecard.

### SEC-21 [HIGH] Third-party script or frame loaded without integrity or sandbox
applies_when: ui∋web
- **Detect:** a `<script src>` or stylesheet `<link>` from another origin without `integrity` and `crossorigin`; a third-party `<iframe>` without `sandbox`. Assets that change per request (hosted font CSS) cannot carry a hash.
- **Mech:** T `git grep -nIE '<script[^>]*src="https?://|<link[^>]*href="https?://' -- ':!*.md' | grep -v 'integrity='` · `git grep -nIE '<iframe' -- ':!*.md' | grep -v 'sandbox'`
- **Fix:** `integrity="sha384-…" crossorigin="anonymous"` on every third-party script and stylesheet, regenerated with each version bump; self-host what cannot carry a hash; `sandbox` with only the capabilities the frame needs.
- **Impact:** a compromised CDN or vendor injects script into every page; with a hash the load fails instead.
- **Source:** Least privilege; Defense in depth; W3C Subresource Integrity; OWASP Third Party JavaScript Management Cheat Sheet; CWE-829.

### NWK-06 [HIGH] Request body or message size unbounded
applies_when: api≠none
- **Detect:** no body-size limit in the framework or proxy (`express.json` without `limit`, `client_max_body_size` absent, `DATA_UPLOAD_MAX_MEMORY_SIZE`, `MaxRequestBodySize`, `http.MaxBytesReader` absent), no per-endpoint upload cap, no WebSocket message size limit; an app limit above the fronting proxy or CDN's documented limit.
- **Mech:** T `git grep -qIE 'client_max_body_size|LimitRequestBody|DATA_UPLOAD_MAX_MEMORY_SIZE|MaxRequestBodySize|MaxBytesReader|maxPayload|max_size|MAX_CONTENT_LENGTH|limit:[[:space:]]*.?[0-9]+[kKmM]?b' -- ':!*.md' || echo 'no request body size limit in tracked code'`
- **Fix:** an explicit small default for JSON, a larger explicit cap per upload endpoint with streaming, a WebSocket message cap; check the proxy's current documented limit when setting the app limit.
- **Impact:** one oversized request exhausts memory and takes the process down.
- **Source:** Fail fast; OWASP API4:2023 Unrestricted Resource Consumption; CWE-770.

### NWK-07 [HIGH] Outbound call without a timeout
- **Detect:** HTTP, RPC, database or queue clients with no connect and read timeout: `requests.*(` without `timeout=`, `fetch` without an abort signal, Go `http.Client{}` without `Timeout` or context deadline, JDBC or driver defaults left infinite, no statement timeout.
- **Mech:** T `git grep -nIE 'requests\.(get|post|put|patch|delete|request)\(' -- ':!*test*' ':!*.md' | grep -v 'timeout'` · `git grep -nIE 'http\.Client\{\}|new HttpClient\(\)|(^|[^[:alnum:]_])fetch\(' -- ':!*test*' ':!*.md' ':!*.py'`
- **Fix:** explicit connect and overall timeouts on every client, sized under the caller's own deadline; a statement timeout on the database role.
- **Impact:** one slow peer holds threads and connections until the whole service stops answering.
- **Source:** Fail fast; Nygard, *Release It!* (timeouts); CWE-400.

### NWK-09 [HIGH] Connection pool unbounded or unsized
applies_when: api≠none or db≠none
- **Detect:** database or HTTP pools with no maximum, no acquire timeout or idle and lifetime limits; a pool per request; the sum of max sizes across instances and workers above the server's connection limit (Postgres `max_connections`); serverless functions opening direct connections with no pooler.
- **Mech:** T `git grep -nIE 'pool_?size|max_?pool|maxPoolSize|MaxOpenConns|connectionLimit|max_connections|pool_max|maximumPoolSize|create_engine\(|new Pool\(' -- ':!*.md'`
- **Fix:** one pool per process with an explicit maximum derived from measured concurrency and the server limit divided by instances; acquire timeout and lifetime set; a pooler (PgBouncer, RDS Proxy, the provider's pooled endpoint) for serverless.
- **Impact:** a traffic spike exhausts the server's connections and every consumer of the database fails at once.
- **Source:** Fail fast; CWE-770; PostgreSQL, Connections and Authentication (`max_connections`); HikariCP, About Pool Sizing.

### NWK-10 [HIGH] Retry with no backoff
- **Detect:** retry loops with no delay, a fixed delay, no jitter or no attempt cap; retries of non-idempotent operations without an idempotency key (API-07); repeated calls to a failing dependency with no circuit breaker or fallback.
- **Mech:** T `git grep -nIiE 'retry|retries|backoff|while[[:space:]]*\([[:space:]]*![[:space:]]*[[:alnum:]_]*(success|ok|done)' -- ':!*test*' ':!*.md'`
- **Fix:** capped exponential backoff with full jitter and a small attempt limit, honouring `Retry-After`; retry only idempotent or keyed operations; a breaker that fails fast after a failure-rate threshold and probes recovery.
- **Impact:** synchronized retries multiply load exactly when the dependency is struggling and turn a blip into a cascade.
- **Source:** Idempotency; AWS Architecture Blog, "Exponential Backoff and Jitter"; Nygard, *Release It!* (circuit breaker).

### NWK-13 [HIGH] Client IP taken from a spoofable header
applies_when: api≠none
- **Detect:** `X-Forwarded-For`, `X-Real-IP` or `Forwarded` read unconditionally, or its leftmost value used, for rate limits, audit or access decisions; no setting stating which proxies are trusted.
- **Mech:** T `git grep -nIiE 'x-forwarded-for|x-real-ip|trust.?proxy|ProxyFix|ForwardedHeaders|RemoteIpValve' -- ':!*.md'`
- **Fix:** read forwarded headers only behind a configured trusted proxy and take the rightmost untrusted address (the framework's trusted-proxy setting); otherwise use the socket peer address.
- **Impact:** any client spoofs its IP with one header, defeating rate limits, audit trails and IP allow-lists.
- **Source:** MDN, X-Forwarded-For (security and privacy concerns); CWE-348.

## Billing integrity

Entitlement checks are SAR-07; webhook signatures and event dedupe API-20; outbound idempotency keys API-07.

### SEC-26 [CRITICAL] Card data passes through own servers
applies_when: billing≠none
- **Detect:** forms posting card number or CVC fields to own endpoints; request bodies, logs or columns shaped like card data (`card_number`, `cvc`, `cvv`) instead of a provider token.
- **Mech:** T `git grep -nIiE 'card_?number|cardnumber|cvc|cvv|cc_?num' -- ':!*.md' ':!*test*' ':!*lock*'`
- **Fix:** provider-hosted checkout or tokenizing fields, so card data goes from the browser or app straight to the provider; the server stores only the token.
- **Impact:** one card number on own infrastructure puts every system it touches in PCI DSS scope and turns a breach into a card-data breach.
- **Source:** Secure / private by default; PCI DSS v4.0.1, Self-Assessment Questionnaire A eligibility (PCI Security Standards Council).

### SEC-27 [CRITICAL] Undelivered paid work refunded from a cache, twice, or never
applies_when: billing≠none
- **Detect:** refund eligibility read from a cache or memory instead of the durable store; the refund and the mark that settles the work written in separate transactions, so a restart between them refunds twice; a failed refund logged at info and skipped; no sweep at start for work charged but never delivered.
- **Mech:** M (find the refund path; check where eligibility is read and what one transaction covers)
- **Fix:** at every start, read charged-but-undelivered records from the durable store; write the refund result and the settled mark in one transaction, with the provider's idempotency key (API-07); a failed refund alerts (OBS-03) and stays unsettled for the next start.
- **Impact:** users pay for work they never got, or are refunded twice; both end in chargebacks and store complaints.
- **Source:** Idempotency; Stripe, Idempotent requests; microservices.io, Pattern: Transactional outbox.

### SEC-28 [CRITICAL] In-app purchase credited on the client's word
applies_when: billing∋store-iap or billing∋revenuecat
- **Detect:** client code adding balance or unlocking content after a purchase callback; a server crediting a receipt or purchase token it has not verified with the store; no product-ID allow-list checked before verification.
- **Mech:** T `git grep -nIiE 'purchaseToken|verifyReceipt|appStoreReceipt|subscriptionsv2|purchases\.products|transactionId' -- ':!*.md' ':!*test*'`
- **Fix:** the client forwards only the store's verification data; the server rejects unknown product IDs, verifies with the store (App Store Server API, Google Play Developer API), computes the credit itself and records the transaction ID once (API-07).
- **Impact:** a patched client grants itself paid content; forged product IDs spend verification quota.
- **Source:** Apple, App Store Server API; Google Play, Fight fraud and abuse (verify purchases on a secure backend).
