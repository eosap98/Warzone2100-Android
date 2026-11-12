#include "touch_gestures.h"
#include <cstdlib>
#include <iostream>
#include <vector>
#include <random>
using namespace wz::touch;
static int scenarios = 0;
static const char *scenarioName = "";
static constexpr float Pi = 3.14159265358979323846f;
struct Test {
    explicit Test(const char *name = "existing controls") { ++scenarios; scenarioName = name; }
    std::vector<Action> actions;
    Gestures g{[this](const Action &a) { actions.push_back(a); }};
    Point first{}, second{};
    Gestures::FingerId firstId = 1, secondId = 2;
    int count(Kind k) const { int n = 0; for (const auto &a : actions) if (a.kind == k) ++n; return n; }
    float rotation() const { float value = 0; for (const auto &a : actions) if (a.kind == Kind::Rotate) value += a.radians; return value; }
    float scale() const { float value = 1; for (const auto &a : actions) if (a.kind == Kind::Pinch) value *= a.scale; return value; }
    void tap(float x, uint64_t time) { g.down(1, {x,100}, time); g.up(1, {x,100}, time+50); }
    void setPair(Point center, float span, float degrees) {
        const float x = std::cos(degrees * Pi / 180) * span / 2;
        const float y = std::sin(degrees * Pi / 180) * span / 2;
        first = {center.x - x, center.y - y}; second = {center.x + x, center.y + y};
    }
    void beginPair(Point center, float span, float degrees = 0, uint64_t now = 0) {
        setPair(center, span, degrees);
        g.down(firstId, first, now); g.down(secondId, second, now + 10);
    }
    void movePair(Point center, float span, float degrees, uint64_t now, bool reverse = false, bool flush = true) {
        setPair(center, span, degrees);
        if (reverse) { g.motion(secondId, second, now); g.motion(firstId, first, now); }
        else { g.motion(firstId, first, now); g.motion(secondId, second, now); }
        if (flush) g.tick(now);
    }
    void endPair(uint64_t now) {
        g.up(firstId, first, now); g.up(secondId, second, now + 5); g.tick(now + 1000);
    }
};
#define CHECK(x) do { if (!(x)) { std::cerr << "FAIL " << scenarioName << " line " << __LINE__ << ": " #x "\n"; std::exit(1); } } while (0)
int main() {
    { Test t; t.tap(100,0); t.g.tick(349); CHECK(t.actions.empty()); t.g.tick(351); CHECK(t.count(Kind::Tap)==1); t.g.tick(9999); CHECK(t.actions.size()==1); }
    { Test t; t.tap(100,0); t.tap(103,150); t.g.tick(1000); CHECK(t.count(Kind::DoubleTap)==1); CHECK(t.actions.size()==1); }
    { Test t; t.g.down(1,{100,100},0); t.g.motion(1,{150,130},80); t.g.motion(1,{180,150},100); t.g.up(1,{180,150},140); t.g.tick(1000); CHECK(t.count(Kind::Pan)>=2); CHECK(t.count(Kind::Tap)==0); CHECK(t.count(Kind::BoxBegin)==0); }
    { Test t; t.g.down(1,{100,100},0); t.g.tick(419); CHECK(t.actions.empty()); t.g.tick(420); t.g.motion(1,{200,180},500); t.g.up(1,{250,200},600); CHECK(t.count(Kind::BoxBegin)==1); CHECK(t.count(Kind::BoxEnd)==1); CHECK(t.actions.back().from.x==100); CHECK(t.actions.back().at.x==250); CHECK(t.count(Kind::Pan)==0); }
    { Test t; t.g.down(1,{100,100},0); t.g.tick(500); t.g.up(1,{102,100},600); CHECK(t.count(Kind::BoxCancel)==1); CHECK(t.count(Kind::BoxEnd)==0); }
    { Test t; t.g.down(1,{100,100},0); t.g.down(2,{200,100},20); t.g.up(2,{200,100},100); t.g.up(1,{100,100},130); t.g.tick(1000); CHECK(t.count(Kind::Deselect)==1); CHECK(t.actions.size()==1); }
    { Test t; t.g.down(1,{100,100},0); t.g.down(2,{200,100},20); t.g.motion(1,{80,100},60); t.g.motion(2,{220,100},65); t.g.up(1,{80,100},80); t.g.motion(2,{250,100},120); t.g.up(2,{250,100},140); t.g.tick(1000); float scale=1; for (auto a:t.actions) { CHECK(a.kind==Kind::Pinch); scale*=a.scale; } CHECK(std::abs(scale-100.f/140.f)<0.001f); }
    { Test t; t.g.down(1,{50,100},0); t.g.down(2,{250,100},20); t.g.motion(2,{150,100},90); t.g.tick(90); CHECK(t.count(Kind::Pinch)==1); CHECK(t.actions[0].scale>1); t.g.up(1,{50,100},100); t.g.up(2,{150,100},150); CHECK(t.count(Kind::Deselect)==0); }
    { Test t; t.g.down(1,{100,100},0); t.g.down(2,{200,100},20); t.g.motion(1,{100,130},80); t.g.motion(2,{200,130},90); t.g.up(1,{100,130},110); t.g.up(2,{200,130},130); CHECK(t.count(Kind::Deselect)==0); CHECK(t.count(Kind::Tap)==0); }
    { Test t; t.g.down(1,{100,100},0); t.g.down(2,{200,100},20); t.g.down(3,{300,100},30); t.g.up(1,{100,100},70); t.g.up(2,{200,100},80); t.g.up(3,{300,100},90); t.g.tick(1000); CHECK(t.actions.empty()); }
    { Test t; t.tap(100,0); t.g.cancel(); t.g.tick(1000); CHECK(t.actions.empty()); t.g.down(1,{100,100},2000); t.g.tick(2500); t.g.cancel(); CHECK(t.count(Kind::BoxCancel)==1); }
    { Test t; t.tap(100,0); t.g.down(1,{103,100},150); t.g.motion(1,{200,100},200); t.g.up(1,{200,100},230); t.g.tick(1000); CHECK(t.count(Kind::Tap)==0); CHECK(t.count(Kind::DoubleTap)==0); }
    { Test t; t.g.down(1,{100,100},0); t.g.tick(500); t.g.down(2,{200,100},510); t.g.up(1,{100,100},530); t.g.up(2,{200,100},540); CHECK(t.count(Kind::BoxCancel)==1); CHECK(t.count(Kind::BoxEnd)==0); CHECK(t.count(Kind::Deselect)==0); }
    { Test t; t.g.motion(99,{3,4},0); t.g.up(99,{3,4},100); CHECK(t.actions.empty()); }
    { Test t; t.g.down(1,{100,100},0); t.g.motion(1,{200,150},500); t.g.up(1,{220,150},550); CHECK(t.count(Kind::BoxBegin)==1); CHECK(t.count(Kind::BoxEnd)==1); CHECK(t.count(Kind::Pan)==0); }
    {
        Test t("clockwise twist");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 15, 50);
        t.movePair({300,300}, 240, 45, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - Pi / 4) < 0.001f);
        CHECK(t.count(Kind::Rotate) == 2);
        CHECK(t.actions.size() == 2);
    }
    {
        Test t("counterclockwise twist");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, -45, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() + Pi / 4) < 0.001f);
        CHECK(t.actions.size() == 1);
    }
    {
        Test t("twist reverses without lifting");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 30, 50);
        t.movePair({300,300}, 240, 10, 100);
        t.movePair({300,300}, 240, -20, 150);
        t.endPair(180);
        CHECK(std::abs(t.rotation() + Pi / 9) < 0.001f);
        CHECK(t.count(Kind::Rotate) == 3);
        CHECK(t.count(Kind::Deselect) == 0);
    }
    for (const float direction : {-1.f, 1.f}) {
        Test t("twist crosses the atan2 wrap in either direction");
        t.beginPair({300,300}, 240, direction * 170);
        t.movePair({300,300}, 240, -direction * 170, 50);
        t.movePair({300,300}, 240, -direction * 150, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - direction * 40 * Pi / 180) < 0.001f);
        for (const auto &a : t.actions) CHECK(std::abs(a.radians) < Pi / 4);
    }
    {
        Test t("two full revolutions");
        t.beginPair({300,300}, 240);
        for (int step = 1; step <= 24; ++step) t.movePair({300,300}, 240, step * 30.f, step * 20);
        t.endPair(500);
        CHECK(std::abs(t.rotation() - 4 * Pi) < 0.001f);
        CHECK(t.count(Kind::Pinch) == 0);
        CHECK(t.count(Kind::Tap) == 0);
    }
    {
        Test t("finger IDs and event order do not reverse rotation");
        t.firstId = 9876543210LL; t.secondId = -23;
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 30, 70, true);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - Pi / 6) < 0.001f);
        CHECK(t.actions.size() == 1);
    }
    {
        Test t("pinch and twist together");
        t.beginPair({300,300}, 200);
        t.movePair({300,300}, 280, 30, 80);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - Pi / 6) < 0.001f);
        CHECK(std::abs(t.scale() - 200.f / 280) < 0.001f);
        CHECK(t.count(Kind::Deselect) == 0);
        CHECK(t.count(Kind::Pan) == 0);
    }
    {
        Test t("pinch can begin after twisting");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 15, 50);
        t.movePair({300,300}, 360, 15, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - Pi / 12) < 0.001f);
        CHECK(std::abs(t.scale() - 2.f / 3) < 0.001f);
    }
    {
        Test t("twist can begin after pinching");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 300, 0, 50);
        t.movePair({300,300}, 300, 30, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - Pi / 6) < 0.001f);
        CHECK(std::abs(t.scale() - 0.8f) < 0.001f);
    }
    {
        Test t("tap jitter does not rotate or zoom");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 242, 2, 40);
        t.movePair({300,300}, 238, -2, 70);
        t.movePair({300,300}, 240, 1, 100);
        t.endPair(140);
        CHECK(t.count(Kind::Deselect) == 1);
        CHECK(t.actions.size() == 1);
    }
    {
        Test t("slow twist accumulates below-threshold samples");
        t.beginPair({300,300}, 240);
        for (int step = 1; step <= 30; ++step) t.movePair({300,300}, 240, float(step), 20 + step * 10);
        t.endPair(350);
        CHECK(std::abs(t.rotation() - Pi / 6) < 0.001f);
        CHECK(t.count(Kind::Pinch) == 0);
    }
    {
        Test t("overlapping fingers rebase before rotation");
        t.beginPair({300,300}, 0);
        t.movePair({300,300}, 240, 90, 50);
        CHECK(t.count(Kind::Rotate) == 0);
        t.movePair({300,300}, 240, 120, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - Pi / 6) < 0.001f);
        CHECK(std::isfinite(t.scale()) && t.scale() > 0);
    }
    {
        Test t("fingers crossing during a pinch do not flip the camera");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 20, 0, 50);
        t.movePair({300,300}, 240, 180, 100);
        t.endPair(140);
        CHECK(t.count(Kind::Rotate) == 0);
        CHECK(std::abs(t.scale() - 1) < 0.001f);
    }
    {
        Test t("an ambiguous half-turn between samples is ignored");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 180, 70);
        t.endPair(140);
        CHECK(t.actions.empty());
    }
    for (const float direction : {-1.f, 1.f}) {
        Test t("horizontal swipe rotates left and right");
        t.beginPair({300,300}, 200);
        t.movePair({300 + direction * 60,300}, 200, 0, 70);
        t.movePair({300 + direction * 100,300}, 200, 0, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - direction * 25 * Pi / 180) < 0.001f);
        CHECK(t.actions.size() == 2);
    }
    {
        Test t("vertical finger layout still supports horizontal swipes");
        t.beginPair({300,300}, 200, 90);
        t.movePair({380,300}, 200, 90, 70, false, false);
        CHECK(t.actions.empty()); // Wait for both SDL finger events before classifying.
        t.g.tick(70);
        t.endPair(140);
        CHECK(std::abs(t.rotation() - 20 * Pi / 180) < 0.001f);
        CHECK(t.actions.size() == 1);
    }
    {
        Test t("diagonal finger layout and reversed events support swipes");
        t.beginPair({300,300}, 200, 45);
        t.movePair({220,300}, 200, 45, 70, true);
        t.endPair(140);
        CHECK(std::abs(t.rotation() + 20 * Pi / 180) < 0.001f);
        CHECK(t.actions.size() == 1);
    }
    {
        Test t("swipe reverses while both fingers remain down");
        t.beginPair({300,300}, 200);
        t.movePair({360,300}, 200, 0, 70);
        t.movePair({240,300}, 200, 0, 100);
        t.endPair(140);
        CHECK(std::abs(t.rotation() + Pi / 12) < 0.001f);
        CHECK(t.count(Kind::Pinch) == 0);
    }
    {
        Test t("small differences in parallel finger travel do not start zoom");
        t.beginPair({300,300}, 200);
        t.g.motion(1, {240,300}, 70);
        t.g.motion(2, {460,300}, 70);
        t.g.tick(70);
        CHECK(std::abs(t.rotation() - 12.5f * Pi / 180) < 0.001f);
        CHECK(t.count(Kind::Pinch) == 0);
    }
    {
        Test t("an anchored pinch does not rotate when its midpoint moves");
        t.beginPair({300,300}, 200);
        t.g.motion(2, {500,300}, 70);
        t.g.tick(70);
        CHECK(t.count(Kind::Rotate) == 0);
        CHECK(std::abs(t.scale() - 2.f / 3) < 0.001f);
    }
    {
        Test t("an asymmetric pinch does not become a horizontal rotation");
        t.beginPair({300,300}, 200);
        t.g.motion(1, {160,300}, 70);
        t.g.motion(2, {460,300}, 70);
        t.g.tick(70);
        CHECK(t.count(Kind::Rotate) == 0);
        CHECK(std::abs(t.scale() - 2.f / 3) < 0.001f);
    }
    {
        Test t("parallel vertical movement does not rotate or zoom");
        t.beginPair({300,300}, 200, 90);
        t.movePair({300,360}, 200, 90, 70);
        t.endPair(140);
        CHECK(t.actions.empty());
    }
    {
        Test t("lifting one finger ends rotation without issuing orders");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 30, 70);
        t.g.up(1, t.first, 90);
        const auto count = t.actions.size();
        t.g.motion(2, {600,450}, 110); t.g.tick(120);
        t.g.up(2, {600,450}, 140); t.g.tick(1000);
        CHECK(t.actions.size() == count);
        CHECK(t.count(Kind::Rotate) == 1);
        CHECK(t.count(Kind::Deselect) == 0);
    }
    {
        Test t("third finger blocks further rotation until all fingers lift");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 30, 70);
        t.g.down(3, {500,500}, 90);
        const auto count = t.actions.size();
        t.movePair({300,300}, 240, 60, 110);
        t.g.up(3, {500,500}, 130); t.endPair(140);
        CHECK(t.actions.size() == count);
        CHECK(!t.g.touching());
    }
    {
        Test t("cancellation discards pending motion and resets the next gesture");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 30, 70, false, false);
        t.g.cancel(); t.g.tick(1000);
        CHECK(t.actions.empty());
        t.beginPair({300,300}, 240, 0, 1200); t.endPair(1300);
        CHECK(t.actions.size() == 1);
        CHECK(t.count(Kind::Deselect) == 1);
    }
    {
        Test t("starting rotation cancels an earlier pending single tap");
        t.tap(100, 0);
        t.beginPair({200,100}, 200, 0, 150);
        t.movePair({200,100}, 200, 30, 210);
        t.endPair(240);
        CHECK(t.count(Kind::Rotate) == 1);
        CHECK(t.count(Kind::Tap) == 0);
        CHECK(t.count(Kind::DoubleTap) == 0);
        CHECK(t.count(Kind::Deselect) == 0);
    }
    {
        Test t("a second finger can change an existing pan into rotation");
        t.g.down(1, {100,100}, 0);
        t.g.motion(1, {150,100}, 70);
        t.g.down(2, {350,100}, 90);
        t.g.motion(1, {190,100}, 110); t.g.motion(2, {390,100}, 110); t.g.tick(110);
        CHECK(t.count(Kind::Pan) == 1);
        CHECK(std::abs(t.rotation() - 10 * Pi / 180) < 0.001f);
        CHECK(t.count(Kind::Pinch) == 0);
    }
    {
        Test t("a replacement finger starts from a fresh rotation baseline");
        t.beginPair({300,300}, 240);
        t.movePair({300,300}, 240, 30, 70);
        t.g.up(2, t.second, 90);
        const auto count = t.actions.size();
        t.g.down(3, {500,400}, 110); t.g.tick(120);
        CHECK(t.actions.size() == count);
        t.g.up(1, t.first, 130); t.g.up(3, {500,400}, 140); t.g.tick(1000);
        CHECK(t.actions.size() == count);
    }
    {
        Test t("lifting fingers flushes a final unrendered swipe");
        t.beginPair({300,300}, 200);
        t.movePair({380,300}, 200, 0, 70, false, false);
        CHECK(t.actions.empty());
        t.endPair(140);
        CHECK(std::abs(t.rotation() - 20 * Pi / 180) < 0.001f);
        CHECK(t.actions.size() == 1);
    }
    {
        Test t("holding two fingers before swiping does not select units");
        t.beginPair({300,300}, 200);
        t.g.tick(1000);
        CHECK(t.actions.empty());
        t.movePair({380,300}, 200, 0, 1200);
        t.endPair(1500);
        CHECK(std::abs(t.rotation() - 20 * Pi / 180) < 0.001f);
        CHECK(t.actions.size() == 1);
    }
    { Test t("10,000 mixed events"); std::mt19937 rng(2100); uint64_t now=0; for (int n=0;n<10000;n++) { now+=rng()%30; auto id=rng()%4; Point p{float(rng()%500),float(rng()%400)}; switch(rng()%5) { case 0:t.g.down(id,p,now);break;case 1:t.g.motion(id,p,now);break;case 2:t.g.up(id,p,now);break;case 3:t.g.tick(now);break;default:t.g.cancel(); } } for(auto a:t.actions) CHECK(std::isfinite(a.scale)&&a.scale>0&&std::isfinite(a.radians)); t.g.cancel(); auto count=t.actions.size(); t.g.tick(now+10000); CHECK(t.actions.size()==count); }
    std::cout << "PASS: " << scenarios << " gesture scenarios, including two-finger rotation, cancellation and 10,000 mixed events\n";
}
