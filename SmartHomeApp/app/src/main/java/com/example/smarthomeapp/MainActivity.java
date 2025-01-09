package com.example.smarthomeapp;

import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonSyntaxException;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import okhttp3.ResponseBody;

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
            OkHttpClient client = new OkHttpClient.Builder()
                    .addInterceptor(chain -> {
                        Response response = chain.proceed(chain.request());
                        if (response.body() == null) {
                            throw new IOException("Response empty");
                        }
                        if (response.body().contentLength() > 512) { // 512 B
                            throw new IOException("Response too large to handle");
                        }
                        return response;
                    })
                    .build();

            JsonObject json = new JsonObject();
            json.addProperty("action", action);
            if ("timer".equals(action)) {
                json.addProperty("duration", duration);
                json.addProperty("state", state);
            }

            RequestBody body = RequestBody.create(
                    json.toString(), MediaType.parse("application/json"));

            Request request = new Request.Builder()
                    .url(SERVER_URL)
                    .post(body)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    throw new IOException("Unexpected code " + response.code());
                }

                try (ResponseBody responseBody = response.body()) {
                    if (responseBody == null) {
                        throw new IOException("Response empty");
                    }
                    String responseBodyString = responseBody.string();
                    JsonElement jsonResponse = JsonParser.parseString(responseBodyString);

                    runOnUiThread(() -> statusText.setText("Status: " + jsonResponse.toString()));
                }
            } catch (JsonSyntaxException e) {
                Log.e("MainActivity", "Invalid JSON received: " + e.getMessage());
                runOnUiThread(() -> statusText.setText("Error: Invalid JSON received"));
            } catch (IOException e) {
                // Обработка ошибок сети или больших данных
                String errorMessage = e.getMessage();
                if (errorMessage != null) {
                    if (e.getMessage().contains("Response too large")) {
                        Log.e("MainActivity", "Response too large to handle: " + e.getMessage());
                        runOnUiThread(() -> statusText.setText("Error: Response too large"));
                    } else if (e.getMessage().contains("Response empty")) {
                        Log.e("MainActivity", "Empty response received");
                        runOnUiThread(() -> statusText.setText("Error: Server returned empty response"));
                    } else {
                        Log.e("MainActivity", "Network error: " + e.getMessage());
                        runOnUiThread(() -> statusText.setText("Error: Network error"));
                    }
                }
            } catch (Exception e) {
                Log.e("MainActivity", "Unexpected error: " + e.getMessage());
                runOnUiThread(() -> statusText.setText("Error: Unexpected error occurred"));
            }
        }).start();
    }
}
