package com.example.mystarsapp;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        WebView webView = findViewById(R.id.webview);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true); // если нужен JS
        webView.setWebViewClient(new WebViewClient()); // открывать ссылки внутри WebView

        // Загружаем локальный HTML-файл из папки assets
        webView.loadUrl("file:///android_asset/index.html");
    }
}
