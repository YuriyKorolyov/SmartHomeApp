package com.example.smarthomeapp;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.google.gson.JsonObject;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    private TextView statusText;
    private EditText editTimer;

    private final String SERVER_URL = "http://192.168.1.100:5000/device";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        statusText = findViewById(R.id.statusText);
        editTimer = findViewById(R.id.editTimer);

        Button btnOn = findViewById(R.id.btnOn);
        Button btnOff = findViewById(R.id.btnOff);
        Button btnSetTimer = findViewById(R.id.btnSetTimer);

        btnOn.setOnClickListener(v -> sendCommand("on", 0, false));
        btnOff.setOnClickListener(v -> sendCommand("off", 0, false));
        btnSetTimer.setOnClickListener(v -> {
            int duration = Integer.parseInt(editTimer.getText().toString());
            sendCommand("timer", duration, true);
        });
    }

    private void sendCommand(String action, int duration, boolean state) {
        new Thread(() -> {
            try {
                OkHttpClient client = new OkHttpClient();

                JsonObject json = new JsonObject();
                json.addProperty("action", action);
                if (action.equals("timer")) {
                    json.addProperty("duration", duration);
                    json.addProperty("state", state);
                }

                RequestBody body = RequestBody.create(
                        MediaType.parse("application/json"), json.toString());

                Request request = new Request.Builder()
                        .url(SERVER_URL)
                        .post(body)
                        .build();

                Response response = client.newCall(request).execute();
                String responseBody = response.body().string();

                runOnUiThread(() -> statusText.setText("Status: " + responseBody));
            } catch (Exception e) {
                Log.e("MainActivity", "Error: " + e.getMessage());
                runOnUiThread(() -> statusText.setText("Error: " + e.getMessage()));
            }
        }).start();
    }
}
