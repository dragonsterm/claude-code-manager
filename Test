// Data Template dan Device Blynk
#define BLYNK_TEMPLATE_ID "TMPL6ZajecpIV"
#define BLYNK_TEMPLATE_NAME "LatihanResponsi"
#define BLYNK_AUTH_TOKEN "AUTH_TOKEN"

#include <Arduino.h>
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT22 //  Penganti DHT11.

char ssid[] = "Wokwi-GUEST";
char pass[] = "";
const int pTrig = 16;
const int pEcho = 17;
const int buzzerPin = 14;
const int tombolPin = 15;
const int sdaPin = 22;
const int sclPin = 23;

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);
BlynkTimer timer;

unsigned long durasi = 0; 
float jarak = 0;
float suhu = 0;
float kelembaban = 0;
bool echoDiterima = false;
bool dhtDibaca = false;
bool dhtValid = false;
bool objekTerdeteksi = false;
bool alarmDiizinkan = true; // Tombol dan switch Blynk awalnya ON.
bool buzzerAktif = false;
bool blynkDiisi = false;
String kondisi = "Menunggu Sensor";

int tombolTerakhir = HIGH;
int tombolStabil = HIGH;
unsigned long waktuTombol = 0;

void aturBuzzer() {
  bool bunyi = alarmDiizinkan && objekTerdeteksi;
  if (bunyi != buzzerAktif) {
    buzzerAktif = bunyi;
    if (buzzerAktif) {
      tone(buzzerPin, 1000);
    } else {
      noTone(buzzerPin);
    }
    if (Blynk.connected()) {
      Blynk.virtualWrite(V5, buzzerAktif);
    }
  }
}

void kontrolBuzzer(bool diizinkan) {
  alarmDiizinkan = diizinkan;
  aturBuzzer();
  if (Blynk.connected()) {
    Blynk.virtualWrite(V0, alarmDiizinkan);
    Blynk.virtualWrite(V7, !alarmDiizinkan);
  }
  Serial.print("Tombol: ");
  Serial.println(alarmDiizinkan ? "ON" : "OFF");
}

void bacaTombol() {
  int nilaiTombol = digitalRead(tombolPin);
  if (nilaiTombol != tombolTerakhir) {
    waktuTombol = millis();
    tombolTerakhir = nilaiTombol;
  }
  // Debounce
  if (millis() - waktuTombol >= 30 && nilaiTombol != tombolStabil) {
    tombolStabil = nilaiTombol;
    if (tombolStabil == LOW) {
      kontrolBuzzer(!alarmDiizinkan);
    }
  }
}

void bacaDHT() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  dhtDibaca = true;
  if (isnan(t) || isnan(h)) {
    dhtValid = false;
    Serial.println("Gagal membaca DHT");
  } else {
    suhu = t;
    kelembaban = h;
    dhtValid = true;
  }
}

void bacaJarak() {
  digitalWrite(pTrig, LOW);
  delayMicroseconds(2);
  digitalWrite(pTrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(pTrig, LOW);
  durasi = pulseIn(pEcho, HIGH, 30000UL);

  if (durasi == 0) {
    jarak = 0;
    echoDiterima = false;
    objekTerdeteksi = false;
  } else {
    jarak = (durasi * 0.034) / 2;
    echoDiterima = true;
    objekTerdeteksi = jarak < 80;
  }
  aturBuzzer();
}

void tentukanKondisi() {
  bool suhuNormal = suhu >= 18 && suhu <= 25;
  bool kelembabanNormal = kelembaban > 75;

  if (!dhtDibaca) {
    kondisi = "Menunggu DHT";
  } else if (!dhtValid) {
    kondisi = "DHT Error";
  } else if (!suhuNormal && !kelembabanNormal && objekTerdeteksi) {
    kondisi = "Bahaya";
  } else if (!suhuNormal) {
    kondisi = "Suhu Abnormal";
  } else if (!kelembabanNormal) {
    kondisi = "Kelemb Abnormal";
  } else if (objekTerdeteksi) {
    kondisi = "Objek Terdeteksi";
  } else {
    kondisi = "Normal";
  }
}

void tulisBaris(int baris, String teks) {
  while (teks.length() < 16) {
    teks += " ";
  }
  lcd.setCursor(0, baris);
  lcd.print(teks.substring(0, 16));
}

void tampilLCD() {
  tentukanKondisi();
  tulisBaris(0, kondisi);
  if ((millis() / 2000) % 2 == 0) {
    if (dhtValid) {
      tulisBaris(1, "T:" + String(suhu, 1) + " H:" + String(kelembaban, 1));
    } else {
      tulisBaris(1, kondisi);
    }
  } else {
    tulisBaris(1, "J:" + String(jarak, 0) + "cm BZ:" + (buzzerAktif ? "ON" : "OFF"));
  }
}

void kirimData() {
  tentukanKondisi();
  Serial.print("Suhu: ");
  if (dhtValid) {
    Serial.print(suhu);
    Serial.print(" C | Kelembaban: ");
    Serial.print(kelembaban);
    Serial.print(" %");
  } else {
    Serial.print(kondisi);
  }
  Serial.print(" | Jarak: ");
  Serial.print(jarak, 0);
  Serial.print(" cm");
  Serial.print(" | Kondisi: ");
  Serial.print(kondisi);
  Serial.print(" | Buzzer: ");
  Serial.print(buzzerAktif ? "ON" : "OFF");
  Serial.print(" | Tombol: ");
  Serial.println(alarmDiizinkan ? "ON" : "OFF");

  if (Blynk.connected()) {
    Blynk.virtualWrite(V0, alarmDiizinkan);
    Blynk.virtualWrite(V1, dhtValid ? suhu : -41);
    Blynk.virtualWrite(V2, dhtValid ? kelembaban : -1);
    Blynk.virtualWrite(V3, roundf(jarak));
    Blynk.virtualWrite(V4, kondisi);
    Blynk.virtualWrite(V5, buzzerAktif);
    Blynk.virtualWrite(V6, objekTerdeteksi);
    Blynk.virtualWrite(V7, !alarmDiizinkan);
  }
}

BLYNK_WRITE(V0) {
  int nilaiTombol = param.asInt();
  kontrolBuzzer(nilaiTombol == 1);
}

BLYNK_CONNECTED() {
  kirimData();
}

void hubungkanBlynk() {
  if (blynkDiisi && WiFi.status() == WL_CONNECTED && !Blynk.connected()) {
    Blynk.connect(500);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(pTrig, OUTPUT);
  pinMode(pEcho, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(tombolPin, INPUT_PULLUP);
  digitalWrite(pTrig, LOW);
  digitalWrite(buzzerPin, LOW);
  dht.begin();
  Wire.begin(sdaPin, sclPin);
  lcd.init();
  lcd.backlight();
  tulisBaris(0, "Menunggu Sensor");
  tulisBaris(1, "Tombol: ON");

  // Koneksi terpisah agar tetap bekerja ketika Blynk offline.
  blynkDiisi = strcmp(BLYNK_TEMPLATE_ID, "ISI_TEMPLATE_ID") != 0 &&
               strcmp(BLYNK_TEMPLATE_NAME, "ISI_TEMPLATE_NAME") != 0 &&
               strcmp(BLYNK_AUTH_TOKEN, "ISI_AUTH_TOKEN") != 0;
  if (blynkDiisi) {
    WiFi.begin(ssid, pass);
    Blynk.config(BLYNK_AUTH_TOKEN);
  }
  timer.setInterval(200L, bacaJarak);
  timer.setInterval(2000L, bacaDHT);
  timer.setInterval(500L, tampilLCD);
  timer.setInterval(2000L, kirimData);
  timer.setInterval(5000L, hubungkanBlynk);
}

void loop() {
  bacaTombol();
  if (Blynk.connected()) {
    Blynk.run();
  }
  timer.run();
}
