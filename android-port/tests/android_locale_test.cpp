#include "android_locale.h"

#include <cstdio>
#include <cstring>
#include <string>

static unsigned checks = 0;

static void expect(bool condition, const char *message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "FAIL: %s\n", message);
        std::exit(1);
    }
}

static void expectText(const char *actual, const char *expected)
{
    ++checks;
    if (std::strcmp(actual, expected) != 0)
    {
        std::fprintf(stderr, "FAIL: expected [%s], got [%s]\n", expected, actual);
        std::exit(1);
    }
}

int main(int argc, char **argv)
{
    expect(argc == 2, "Supply the real packaged locale directory");
    for (const char *domain : {"warzone2100", "warzone2100_guide"})
    {
        expect(bindtextdomain(domain, argv[1]) != nullptr, "Bind message catalog");
        expect(bind_textdomain_codeset(domain, "UTF-8") != nullptr, "Use UTF-8");
    }

    // Simulate Android's initial C locale, where gettext normally ignores LANGUAGE.
    setenv("LC_ALL", "C", 1);
    setlocale(LC_ALL, "C");
    struct Example { const char *language; const char *singlePlayer; };
    const Example examples[] = {
        {"id", "Pemain Tunggal"},
        {"fr", "Un joueur"},
        {"de", "Einzelspieler"},
        {"ru", "Одиночная игра"},
        {"zh_CN", "单人游戏"},
        {"en", "Single Player"},
        {"id", "Pemain Tunggal"},
    };
    // Repeating the same msgid across languages detects stale gettext caches.
    for (unsigned repeat = 0; repeat < 20; ++repeat)
    {
        for (const auto &example : examples)
        {
            expect(wz_android::setCatalogLanguage(example.language, "warzone2100"), "Switch language");
            expectText(gettext("Single Player"), example.singlePlayer);
            expectText(getenv("LC_ALL"), "C.UTF-8");
            expectText(localeconv()->decimal_point, ".");
            char *end = nullptr;
            expect(std::strtod("123.5", &end) == 123.5 && *end == '\0', "Portable numeric parsing");
        }
    }
    expectText(gettext("menu\004Return"), "Kembali");
    expectText(dgettext("warzone2100_guide", "## Present Day:"), "## Masa Kini:");
    expect(wz_android::setCatalogLanguage("ru", "warzone2100"), "Switch plural language");
    expectText(ngettext("%d player", "%d players", 1), "%d игрок");
    expectText(ngettext("%d player", "%d players", 2), "%d игрока");
    expectText(ngettext("%d player", "%d players", 5), "%d игроков");
    expect(wz_android::setCatalogLanguage("en", "warzone2100"), "Return to English");
    expectText(gettext("Single Player"), "Single Player");
    expectText(dgettext("warzone2100_guide", "## Present Day:"), "## Present Day:");
    expectText(gettext("A message missing from every catalog"), "A message missing from every catalog");
    std::printf("PASS: %u checks; 140 language changes, UTF-8, context, guide, plurals, numeric locale.\n", checks);
}
