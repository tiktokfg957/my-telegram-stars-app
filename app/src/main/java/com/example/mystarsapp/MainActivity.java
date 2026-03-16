package com.example.mystarsapp;

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        WebView webView = findViewById(R.id.webview);
        // Включаем JavaScript
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        // Чтобы ссылки открывались внутри WebView (а не в браузере)
        webView.setWebViewClient(new WebViewClient());
        // Загружаем локальный HTML
        webView.loadUrl("file:///android_asset/index.html");
    }
}
