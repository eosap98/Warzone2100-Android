package org.warzone2100.android;

import android.os.Bundle;
import android.view.KeyEvent;
import java.io.File;
import java.util.Locale;
import org.libsdl.app.SDLActivity;

/** Full-screen native game; touch gestures are handled by the engine. */
public final class GameActivity extends SDLActivity {
    private static native void nativePauseAudio(boolean paused);
    private boolean librariesReady;
    @Override protected String[] getLibraries() { return new String[]{"c++_shared", "SDL3", "warzone2100"}; }
    @Override protected String[] getArguments() {
        nativeSetenv("WZ_LOCALEDIR", new File(getFilesDir(), "data/locale").getAbsolutePath());
        Locale locale = getResources().getConfiguration().getLocales().get(0);
        String language = locale.getLanguage();
        if ("in".equals(language)) language = "id";
        String country = locale.getCountry();
        if ("zh".equals(language)) {
            country = "Hant".equals(locale.getScript()) || "TW".equals(country) || "HK".equals(country) || "MO".equals(country) ? "TW" : "CN";
        }
        nativeSetenv("WZ_ANDROID_LOCALE", language + (country.isEmpty() ? "" : "_" + country));
        return new String[]{"--datadir=" + new File(getFilesDir(), "data"), "--configdir=" + new File(getFilesDir(), "config"), "--gfxbackend=opengles", "--fullscreen"};
    }
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        librariesReady = mLayout != null;
    }
    @Override public void onBackPressed() {
        if (librariesReady) { onNativeKeyDown(KeyEvent.KEYCODE_ESCAPE); onNativeKeyUp(KeyEvent.KEYCODE_ESCAPE); }
        else super.onBackPressed();
    }
    @Override protected void onPause() {
        if (librariesReady) nativePauseAudio(true);
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume();
        if (librariesReady) nativePauseAudio(false);
    }
}
