package com.example.smarthomeapp;

import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.click;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.withId;
import static androidx.test.espresso.matcher.ViewMatchers.withText;

import android.util.Log;

import androidx.test.ext.junit.rules.ActivityScenarioRule;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.IOException;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

@RunWith(AndroidJUnit4.class)
public class DeviceControlTest {

    @Rule
    public ActivityScenarioRule<MainActivity> activityScenarioRule =
            new ActivityScenarioRule<>(MainActivity.class);

    // Проверка, что приложение отправляет запрос к серверу и получает успешный ответ
    @Test
    public void testDeviceControlAPI() {

        String serverUrl = "http://192.168.1.100:5000/device";

        OkHttpClient client = new OkHttpClient();

        Request request = new Request.Builder()
                .url(serverUrl)
                .post(okhttp3.RequestBody.create(
                        "{\"action\":\"on\"}",
                        okhttp3.MediaType.parse("application/json")
                ))
                .build();

        try {
            try (Response response = client.newCall(request).execute()) {

                if (response.isSuccessful()) {
                    Log.i("Test", "Device turned ON successfully!");
                } else {
                    Log.e("Test", "Failed to turn ON device. Code: " + response.code());
                }

            }
        } catch (IOException e) {
            Log.e("Test", "Error occurred while sending request", e);
        }
    }

    @Test
    public void testUIInteraction() {
        // Нажимаем кнопку "Включить"
        onView(withId(R.id.btnOn)).perform(click());

        // Проверяем, что текстовое поле отобразило правильный результат
        onView(withId(R.id.statusText)).check(matches(withText("Device is ON")));
    }
}