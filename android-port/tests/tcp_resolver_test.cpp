// Tests the production resolver and socket-opening code on the host, with
// Android's stricter getaddrinfo flag validation. No emulator or remote joins.
#include "lib/framework/frame.h"
#include "lib/netplay/tcp/netsocket.h"
#include "lib/netplay/error_categories.h"

#include <cstdio>
#include <cstring>
#include <memory>
#include <poll.h>

// The test does not start the engine's logging / UI subsystem.
bool enabled_debug[LOG_LAST] = {};
bool assertEnabled = true;
char last_called_script_event[MAX_EVENT_NAME_LEN] = {};
void _debug(int, code_part, const char *, const char *, ...) {}

static unsigned checks = 0;
static int lastFamily = -1;
static void check(bool condition, const std::string &message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "FAIL: %s\n", message.c_str());
        std::exit(1);
    }
}

extern "C" int __real_getaddrinfo(const char *, const char *, const addrinfo *, addrinfo **);
extern "C" int __wrap_getaddrinfo(const char *host, const char *service, const addrinfo *hints, addrinfo **result)
{
    // This is the set accepted by Bionic's AI_MASK in the Android NDK netdb.h.
    // AI_V4MAPPED is declared there, but is NOT accepted by getaddrinfo().
    constexpr int allowed = AI_PASSIVE | AI_CANONNAME | AI_NUMERICHOST | AI_NUMERICSERV | AI_ADDRCONFIG;
    *result = nullptr;
    lastFamily = hints->ai_family;
    if ((hints->ai_flags & ~allowed) != 0) return EAI_BADFLAGS;
    if (std::strcmp(host, "missing.invalid") == 0) return EAI_NONAME;
    if (std::strcmp(host, "retry.invalid") == 0) return EAI_AGAIN;

    if (std::strcmp(host, "ipv6.fixture.test") == 0)
    {
        // Model an AAAA-only host on a network with IPv6 configured. The PC's
        // external interfaces must not suppress this loopback IPv6 fixture.
        addrinfo fixture = *hints;
        fixture.ai_flags = AI_NUMERICHOST | AI_NUMERICSERV;
        return __real_getaddrinfo("::1", service, &fixture, result);
    }
    if (std::strcmp(host, "failover.fixture.test") == 0)
    {
        // The first address has no listener; the second reaches our test server.
        addrinfo *second = nullptr;
        int err = __real_getaddrinfo("127.0.0.2", service, hints, result);
        if (err) return err;
        err = __real_getaddrinfo("127.0.0.1", service, hints, &second);
        if (err) { freeaddrinfo(*result); *result = nullptr; return err; }
        addrinfo *tail = *result;
        while (tail->ai_next) tail = tail->ai_next;
        tail->ai_next = second;
        return 0;
    }
    return __real_getaddrinfo(host, service, hints, result);
}

static void checkConnection(const char *host, int family)
{
    int listener = socket(family, SOCK_STREAM, IPPROTO_TCP);
    check(listener >= 0, "Create loopback listener");
    sockaddr_storage storage = {};
    socklen_t size;
    if (family == AF_INET6)
    {
        auto *address = reinterpret_cast<sockaddr_in6 *>(&storage);
        address->sin6_family = AF_INET6;
        address->sin6_addr = in6addr_loopback;
        size = sizeof(*address);
    }
    else
    {
        auto *address = reinterpret_cast<sockaddr_in *>(&storage);
        address->sin_family = AF_INET;
        address->sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        size = sizeof(*address);
    }
    check(bind(listener, reinterpret_cast<sockaddr *>(&storage), size) == 0, "Bind loopback listener");
    check(getsockname(listener, reinterpret_cast<sockaddr *>(&storage), &size) == 0, "Read ephemeral port");
    unsigned port = family == AF_INET6 ? ntohs(reinterpret_cast<sockaddr_in6 *>(&storage)->sin6_port)
                                      : ntohs(reinterpret_cast<sockaddr_in *>(&storage)->sin_port);
    check(listen(listener, 1) == 0, "Listen on loopback");

    auto resolved = tcp::resolveHost(host, port);
    check(resolved.has_value(), std::string("Resolve ") + host + (resolved ? "" : ": " + resolved.error().message()));
    std::unique_ptr<addrinfo, decltype(&freeaddrinfo)> addresses(resolved.value(), freeaddrinfo);
    check(lastFamily == AF_UNSPEC, "Keep IPv4 and IPv6 available");
    auto connected = tcp::socketOpenAny(addresses.get(), 2000);
    check(connected.has_value(), std::string("Open connection to ") + host);
    pollfd ready = {listener, POLLIN, 0};
    check(poll(&ready, 1, 2000) == 1 && (ready.revents & POLLIN), "Connection reached listener");
    int peer = accept(listener, nullptr, nullptr);
    check(peer >= 0, "Accept connection");
    timeval timeout = {2, 0};
    check(setsockopt(peer, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0, "Bound receive timeout");
    const char payload[] = "Warzone TCP";
    int client = tcp::getRawSocketFd(*connected.value());
    check(send(client, payload, sizeof(payload), MSG_NOSIGNAL) == sizeof(payload), "Send TCP data");
    char received[sizeof(payload)] = {};
    check(recv(peer, received, sizeof(received), MSG_WAITALL) == sizeof(payload), "Receive TCP data");
    check(std::memcmp(received, payload, sizeof(payload)) == 0, "TCP payload is intact");
    tcp::socketCloseNow(connected.value());
    close(peer);
    close(listener);
    std::printf("PASS: %s resolves and opens a TCP connection\n", host);
}

int main()
{
    tcp::SOCKETinit();
    checkConnection("127.0.0.1", AF_INET);
    checkConnection("localhost", AF_INET);
    checkConnection("failover.fixture.test", AF_INET);
    checkConnection("ipv6.fixture.test", AF_INET6);
    for (auto failure : {std::make_pair("missing.invalid", EAI_NONAME), std::make_pair("retry.invalid", EAI_AGAIN)})
    {
        auto result = tcp::resolveHost(failure.first, 2100);
        check(!result.has_value(), "DNS failure must remain a failure");
        check(result.error() == make_getaddrinfo_error_code(failure.second), "Preserve the real DNS error");
    }
    tcp::SOCKETshutdown();
    std::printf("PASS: %u checks; Android resolver flags, IPv4, IPv6 fixture, address failover, TCP data, DNS errors.\n", checks);
}
