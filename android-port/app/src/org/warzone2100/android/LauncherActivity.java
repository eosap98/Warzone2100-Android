package org.warzone2100.android;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;

/** Installs and verifies bundled release data before starting the native engine. */
public final class LauncherActivity extends Activity {
    private static final int GOLD = 0xFFEDBD68;
    private static final int TEXT = 0xFFF0F3F7;
    private static final int MUTED = 0xFF9CAFC2;
    private static final String GITHUB_URL = "https://github.com/eosap98/Warzone2100-Android";
    private TextView status;
    private ProgressBar progress;
    private Button start;
    private volatile boolean cancelled;
    private boolean ready;
    private Thread installer;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().getDecorView().setSystemUiVisibility(5894);

        LinearLayout hero = column();
        TextView eyebrow = text("STRATEGI REAL-TIME", 10, MUTED);
        eyebrow.setLetterSpacing(0.22f);
        hero.addView(eyebrow);
        TextView title = text("", 48, TEXT);
        SpannableString titleText = new SpannableString("WARZONE 2100");
        titleText.setSpan(new ForegroundColorSpan(GOLD), 8, 12, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        title.setText(titleText);
        title.setTypeface(Typeface.create("sans-serif-condensed", Typeface.BOLD));
        title.setLetterSpacing(0.055f);
        title.setMaxLines(1);
        title.setAutoSizeTextTypeUniformWithConfiguration(26, 48, 1, TypedValue.COMPLEX_UNIT_SP);
        hero.addView(title, new LinearLayout.LayoutParams(-1, dp(66)));
        hero.addView(text("Bangun markas. Pimpin pasukan. Kuasai medan.", 12, MUTED));

        LinearLayout actions = column();
        start = new Button(this);
        start.setText("MULAI GAME");
        start.setTextSize(14);
        start.setLetterSpacing(0.1f);
        start.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        start.setTextColor(0xFF141D29);
        start.setBackground(ripple(GOLD, 14));
        start.setElevation(dp(4));
        start.setStateListAnimator(null);
        start.setOnClickListener(v -> {
            if (ready) {
                startActivity(new Intent(this, GameActivity.class));
                finish();
            } else beginInstall();
        });
        actions.addView(start, new LinearLayout.LayoutParams(-1, dp(52)));
        status = text("Menyiapkan data game…", 12, MUTED);
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        LinearLayout.LayoutParams statusParams = new LinearLayout.LayoutParams(-1, -2);
        statusParams.topMargin = dp(14);
        actions.addView(status, statusParams);
        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);
        progress.setProgressTintList(ColorStateList.valueOf(GOLD));
        progress.setProgressBackgroundTintList(ColorStateList.valueOf(0xFF253343));
        LinearLayout.LayoutParams progressParams = new LinearLayout.LayoutParams(-1, dp(3));
        progressParams.setMargins(dp(24), dp(10), dp(24), 0);
        actions.addView(progress, progressParams);

        LinearLayout footer = new LinearLayout(this);
        footer.setOrientation(LinearLayout.HORIZONTAL);
        footer.setBaselineAligned(false);
        footer.setGravity(Gravity.CENTER);
        TextView help = text("Panduan kontrol", 12, MUTED);
        help.setMinHeight(dp(48));
        help.setPadding(dp(12), dp(8), dp(12), dp(8));
        help.setBackground(ripple(0x00000000, 12));
        help.setFocusable(true);
        help.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("Kontrol sentuh")
                .setMessage("Geser 1 jari  —  Geser kamera\n\n"
                        + "Tap 1 jari  —  Arahkan unit terpilih\n\n"
                        + "Tap 2 jari  —  Lepas pilihan\n\n"
                        + "Geser 2 jari ke kiri / kanan  —  Putar kamera\n\n"
                        + "Putar 2 jari melingkar  —  Putar kamera\n\n"
                        + "Tahan lalu seret  —  Buat kotak seleksi\n\n"
                        + "Tap 2 kali pada unit  —  Pilih unit\n\n"
                        + "Cubit  —  Zoom masuk / keluar\n\n"
                        + "Tombol kembali  —  Buka menu game\n\n"
                        + "Simpan permainan melalui menu sebelum keluar.")
                .setPositiveButton("MENGERTI", null).show());
        // Equal-width cells keep the divider at the exact horizontal center.
        footer.addView(help, new LinearLayout.LayoutParams(0, -2, 1));
        View divider = new View(this);
        divider.setBackgroundColor(0xFF314052);
        footer.addView(divider, new LinearLayout.LayoutParams(dp(1), dp(24)));

        LinearLayout credit = new LinearLayout(this);
        credit.setBaselineAligned(false);
        credit.setGravity(Gravity.CENTER);
        credit.setPadding(dp(12), dp(6), dp(12), dp(6));
        credit.setMinimumHeight(dp(48));
        credit.setBackground(ripple(0x00000000, 12));
        credit.setFocusable(true);
        credit.setContentDescription("Port by EosAP98 (aka AsfatreHilmi). Buka proyek di GitHub.");
        credit.setOnClickListener(v -> openGitHub());
        TextView by = text("Port by", 11, MUTED);
        LinearLayout.LayoutParams byParams = new LinearLayout.LayoutParams(-2, -2);
        byParams.rightMargin = dp(8);
        credit.addView(by, byParams);
        ImageView github = new ImageView(this);
        github.setImageResource(getResources().getIdentifier("github_mark", "drawable", getPackageName()));
        github.setColorFilter(TEXT);
        github.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        credit.addView(github, new LinearLayout.LayoutParams(dp(22), dp(22)));
        LinearLayout author = column();
        author.setPadding(dp(10), 0, 0, 0);
        author.addView(text("EosAP98  ↗", 13, TEXT));
        author.addView(text("(aka AsfatreHilmi)", 10, MUTED));
        credit.addView(author, new LinearLayout.LayoutParams(-2, -2));
        footer.addView(credit, new LinearLayout.LayoutParams(0, -2, 1));

        LauncherScene scene = new LauncherScene(this, hero, actions, footer);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);
        scroll.setBackgroundColor(0xFF0B121C);
        scroll.addView(scene, new ScrollView.LayoutParams(-1, -2));
        if (Build.VERSION.SDK_INT >= 28) {
            scroll.setOnApplyWindowInsetsListener((view, insets) -> {
                android.view.DisplayCutout cutout = insets.getDisplayCutout();
                view.setPadding(cutout == null ? 0 : cutout.getSafeInsetLeft(),
                        cutout == null ? 0 : cutout.getSafeInsetTop(),
                        cutout == null ? 0 : cutout.getSafeInsetRight(),
                        cutout == null ? 0 : cutout.getSafeInsetBottom());
                return insets;
            });
        }
        setContentView(scroll);
        beginInstall();
    }

    private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }

    private LinearLayout column() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        return layout;
    }

    private TextView text(String value, int size, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        view.setGravity(Gravity.CENTER);
        view.setIncludeFontPadding(false);
        return view;
    }

    private RippleDrawable ripple(int color, int radius) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(color);
        shape.setCornerRadius(dp(radius));
        GradientDrawable mask = new GradientDrawable();
        mask.setColor(0xFFFFFFFF);
        mask.setCornerRadius(dp(radius));
        return new RippleDrawable(ColorStateList.valueOf(0x30FFFFFF), shape, mask);
    }

    private void openGitHub() {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(GITHUB_URL));
            intent.addCategory(Intent.CATEGORY_BROWSABLE);
            startActivity(intent);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "Pasang browser untuk membuka tautan GitHub.", Toast.LENGTH_LONG).show();
        }
    }

    private void enableStart(boolean enabled) {
        start.setEnabled(enabled);
        start.setAlpha(enabled ? 1f : 0.45f);
    }

    private void beginInstall() {
        if (installer != null && installer.isAlive()) return;
        ready = false;
        enableStart(false);
        progress.setProgress(0);
        status.setTextColor(MUTED);
        status.setText("Menyiapkan data game…");
        installer = new Thread(() -> {
            try {
                installData();
                if (!cancelled) runOnUiThread(() -> {
                    if (cancelled) return;
                    ready = true; progress.setProgress(100);
                    status.setText("Siap bermain");
                    status.setTextColor(0xFF94D5BA);
                    start.setText("MULAI GAME"); enableStart(true);
                });
            } catch (Exception e) {
                android.util.Log.e("Warzone2100", "Data installation failed", e);
                if (!cancelled) runOnUiThread(() -> {
                    if (cancelled) return;
                    status.setTextColor(0xFFFFAAA0);
                    status.setText("Gagal menyiapkan data: " + e.getMessage());
                    start.setText("COBA LAGI"); enableStart(true);
                });
            }
        }, "WarzoneDataInstaller");
        installer.start();
    }
    private static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream(); byte[] buffer = new byte[65536]; int n;
        while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
        return out.toByteArray();
    }
    private void installData() throws Exception {
        byte[] manifestBytes;
        try (InputStream in = getAssets().open("data-manifest.json")) { manifestBytes = readAll(in); }
        JSONObject manifest = new JSONObject(new String(manifestBytes, StandardCharsets.UTF_8));
        JSONArray files = manifest.getJSONArray("files");
        File base = new File(getFilesDir(), "data");
        if (!base.isDirectory() && !base.mkdirs()) throw new IOException("Folder data tidak dapat dibuat");
        File stamp = new File(base, ".manifest");
        boolean sameVersion = stamp.isFile() && java.util.Arrays.equals(Files.readAllBytes(stamp.toPath()), manifestBytes);
        long missingBytes = 0;
        for (int i = 0; i < files.length(); i++) {
            JSONObject item = files.getJSONObject(i); File target = new File(base, item.getString("path"));
            if (!sameVersion || !target.isFile() || target.length() != item.getLong("size")) missingBytes += item.getLong("size");
        }
        if (base.getUsableSpace() < missingBytes + 64L * 1024 * 1024) throw new IOException("Ruang penyimpanan tidak cukup (perlu " + (missingBytes / 1048576 + 64) + " MB)");
        for (int i = 0; i < files.length(); i++) {
            if (cancelled) return;
            JSONObject item = files.getJSONObject(i); String path = item.getString("path"); File target = new File(base, path);
            if (!target.getCanonicalPath().startsWith(base.getCanonicalPath() + File.separator)) throw new IOException("Path data tidak valid");
            if (!sameVersion || !target.isFile() || target.length() != item.getLong("size")) {
                File parent = target.getParentFile();
                if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException("Gagal membuat " + parent);
                File temp = new File(parent, target.getName() + ".tmp");
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                try (InputStream in = getAssets().open("data/" + path); FileOutputStream out = new FileOutputStream(temp)) {
                    byte[] buffer = new byte[262144]; int n;
                    while ((n = in.read(buffer)) != -1) { if (cancelled) return; out.write(buffer, 0, n); digest.update(buffer, 0, n); }
                    out.getFD().sync();
                }
                StringBuilder hash = new StringBuilder(); for (byte b : digest.digest()) hash.append(String.format(java.util.Locale.ROOT, "%02x", b & 255));
                if (temp.length() != item.getLong("size") || !hash.toString().equals(item.getString("sha256"))) { temp.delete(); throw new IOException("Verifikasi gagal: " + path); }
                Files.move(temp.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            }
            final int percent = (i + 1) * 100 / files.length();
            runOnUiThread(() -> {
                if (cancelled) return;
                progress.setProgress(percent);
                status.setText("Menyiapkan data game… " + percent + "%");
            });
        }
        File configDir = new File(getFilesDir(), "config");
        if (!configDir.isDirectory() && !configDir.mkdirs()) throw new IOException("Folder konfigurasi tidak dapat dibuat");
        File config = new File(configDir, "config");
        if (!config.exists()) {
            android.util.DisplayMetrics metrics = new android.util.DisplayMetrics(); getWindowManager().getDefaultDisplay().getRealMetrics(metrics);
            int height = Math.min(metrics.widthPixels, metrics.heightPixels);
            int scale = Math.max(100, Math.min(200, (height / 6 / 25) * 25));
            String initial = "[General]\nconfigVersion=4\ngfxbackend=opengles\nfullscreen=1\nwidth=1280\nheight=720\ndisplayScale=" + scale + "\nantialiasing=0\nshadows=false\nterrainShadows=false\nterrainMode=0\ntextureSize=1024\nvsync=1\nRightClickOrders=true\nPauseOnFocusLoss=true\ntrapCursor=0\n";
            Files.write(config.toPath(), initial.getBytes(StandardCharsets.UTF_8));
        }
        Files.write(stamp.toPath(), manifestBytes);
    }
    @Override protected void onResume() {
        super.onResume();
        getWindow().getDecorView().setSystemUiVisibility(5894);
    }
    @Override protected void onDestroy() { cancelled = true; super.onDestroy(); }
}
